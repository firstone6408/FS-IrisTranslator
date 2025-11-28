# ==========================================================
# overlay.py
# จัดการหน้าต่างโปร่งใสที่ใช้ลากกรอบ OCR/Translation
# มีฟีเจอร์ auto OCR ตามเวลาที่กำหนด และ bubble แสดงคำแปล
# ==========================================================

from PyQt6 import QtWidgets, QtGui, QtCore
from modules.workers.cor_worker import OCRWorker


class Overlay(QtWidgets.QWidget):
    """
    Overlay = หน้าต่างโปร่งใสที่แสดงกรอบ OCR และคำแปล
    รองรับ:
    - ลากกรอบ
    - auto OCR ทุก X วินาที
    - bubble คำแปลพร้อมระบบกันล้ำขอบจอ
    """

    finished_signal = QtCore.pyqtSignal(object)
    closed_signal = QtCore.pyqtSignal(object)

    def __init__(self, font_size_getter, delay_getter):
        """
        font_size_getter: ฟังก์ชันที่คืนค่าขนาดฟอนต์ปัจจุบัน
        delay_getter: ฟังก์ชันคืนค่า delay (วินาที) สำหรับ auto OCR
        """
        super().__init__()

        self.font_size_getter = font_size_getter
        self.delay_getter = delay_getter

        # ตั้งหน้าต่างแบบโปร่งใสและคลิกทะลุได้
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint |
            QtCore.Qt.WindowType.Tool
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(QtWidgets.QApplication.primaryScreen().geometry())

        # scale factor สำหรับจอ 4K หรือ HiDPI
        self.scale = self.devicePixelRatioF()

        # states ต่าง ๆ
        self.start = None
        self.rect = None
        self.persistent_rect = None
        self.text = ""
        self.text_pos = None
        self.worker = None
        self.last_bbox = None
        
        # เก็บผลลัพธ์ก่อนหน้า เพื่อใช้เช็กว่าซ้ำไหม
        self.last_raw_text = None
        self.last_translated_text = None

        # Timer สำหรับ Auto OCR
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.auto_ocr)

        self.set_mouse_passthrough(False)
        self.show()

    # =============================
    # เปิด/ปิดการคลิกทะลุ
    # =============================
    def set_mouse_passthrough(self, enable: bool):
        self.setWindowFlag(QtCore.Qt.WindowType.WindowTransparentForInput, enable)
        self.show()

    # =============================
    # วาด UI ทั้งหมดบน Overlay
    # =============================
    def paintEvent(self, e):
        qp = QtGui.QPainter(self)

        # กรอบตอนลากอยู่
        if self.rect:
            qp.fillRect(self.rect, QtGui.QColor(0, 200, 255, 40))
            qp.setPen(QtGui.QPen(QtGui.QColor(0, 180, 255, 180), 2))
            qp.drawRect(self.rect)

        # กรอบหลังลากเสร็จ
        if self.persistent_rect:
            qp.fillRect(self.persistent_rect, QtGui.QColor(0, 200, 255, 40))
            qp.setPen(QtGui.QPen(QtGui.QColor(0, 180, 255, 180), 2))
            qp.drawRect(self.persistent_rect)

        # วาด bubble ถ้ามีข้อความ
        if self.text and self.persistent_rect:
            self.draw_bubble(qp)

    # =============================
    # วาด bubble คำแปล + กันล้ำขอบจอ
    # =============================
    def draw_bubble(self, qp):
        font_size = self.font_size_getter()
        qp.setFont(QtGui.QFont("Arial", font_size))
        fm = QtGui.QFontMetrics(qp.font())

        max_width = max(50, self.persistent_rect.width() - 20)
        wrapped = fm.boundingRect(
            0, 0, max_width, 9999,
            QtCore.Qt.TextFlag.TextWordWrap,
            self.text
        )

        x, y = self.text_pos
        sw, sh = self.width(), self.height()

        bubble_w = wrapped.width() + 20
        bubble_h = wrapped.height() + 10

        # ----- ระบบกันล้ำขอบจอ -----

        # บน → ลงล่าง
        if y - bubble_h < 0:
            y = self.persistent_rect.bottom() + bubble_h + 5

        # ล่าง → ขึ้นบน
        elif y > sh - 5:
            y = self.persistent_rect.top() - 5

        # # ซ้าย → ไปขวา
        # if x - 10 < 0:
        #     x = self.persistent_rect.right() + 10

        # # ขวา → ไปซ้าย
        # elif x + bubble_w > sw:
        #     x = self.persistent_rect.left() - bubble_w - 5

        bg = QtCore.QRect(x - 10, y - bubble_h + 5, bubble_w, bubble_h)
        qp.fillRect(bg, QtGui.QColor(30, 30, 30, 180))

        qp.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255)))
        qp.drawText(
            QtCore.QRect(
                x - 5,
                y - wrapped.height(),
                wrapped.width(),
                wrapped.height()
            ),
            QtCore.Qt.TextFlag.TextWordWrap,
            self.text
        )

    # =============================
    # Mouse Events
    # =============================
    def mousePressEvent(self, e):
        """
        เริ่มลากกรอบใหม่
        """
        self.set_mouse_passthrough(False)
        self.text = ""
        self.rect = None
        self.start = e.position().toPoint()
        self.rect = QtCore.QRect(self.start, QtCore.QSize())
        self.update()

    def mouseMoveEvent(self, e):
        """
        อัพเดทกรอบระหว่างลาก
        """
        if self.start:
            self.rect = QtCore.QRect(self.start, e.position().toPoint()).normalized()
            self.update()

    def mouseReleaseEvent(self, e):
        """
        เมื่อปล่อยเมาส์: บันทึกกรอบ + เริ่ม OCR
        """
        if not self.rect:
            return

        lx, ly, lw, lh = self.rect.left(), self.rect.top(), self.rect.width(), self.rect.height()

        px = int(lx * self.scale)
        py = int(ly * self.scale)
        pw = int(lw * self.scale)
        ph = int(lh * self.scale)

        self.text_pos = (lx, ly - 10)  # จุดแสดง bubble
        self.persistent_rect = QtCore.QRect(lx, ly, lw, lh)
        self.rect = None

        self.last_bbox = (px, py, pw, ph)

        # OCR ครั้งแรก
        self.worker = OCRWorker(self.last_bbox)
        self.worker.finished_signal.connect(self.on_text_ready)
        self.worker.start()

        # ตั้งเวลา auto OCR
        delay = self.delay_getter()
        self.timer.setInterval(delay * 1000)
        self.timer.start()

        self.start = None
        self.set_mouse_passthrough(True)

    # =============================
    # Auto OCR
    # =============================
    def auto_ocr(self):
        """
        ทำ OCR ซ้ำทุก X วินาทีตาม delay
        """
        if not self.last_bbox:
            return
        if self.worker and self.worker.isRunning():
            return

        self.worker = OCRWorker(self.last_bbox)
        self.worker.finished_signal.connect(self.on_text_ready)
        self.worker.start()

    # ======================================================
    # เมื่อ OCRWorker ส่งข้อมูลกลับมาที่ overlay
    # ======================================================
    def on_text_ready(self, data):
        """
        ถูกเรียกเมื่อ OCRWorker เสร็จ
        เช็กก่อนว่าข้อความเหมือนเดิมหรือไม่
        ถ้าเหมือนเดิม → ไม่ต้อง update และไม่ต้อง log
        """

        raw = data["raw"]
        th = data["th"]

        # ======= ป้องกัน log ซ้ำ =======
        if raw == self.last_raw_text and th == self.last_translated_text:
            return  # ไม่ส่ง signal → Panel ไม่ log

        # ======= บันทึก state ล่าสุด =======
        self.last_raw_text = raw
        self.last_translated_text = th

        # ======= อัปเดตข้อความแปลบน overlay =======
        self.text = th
        self.worker = None
        self.update()

        # ======= ส่งสัญญาณไป Panel เพื่อสร้าง log =======
        self.finished_signal.emit(data)

    def closeEvent(self, e):
        """
        เมื่อ Overlay ปิด → หยุด timer
        """
        self.timer.stop()
        self.closed_signal.emit(self)
        super().close()

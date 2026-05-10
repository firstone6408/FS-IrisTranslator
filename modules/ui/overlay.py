# ==========================================================
# overlay.py — Safe QThread Version (No crash)
# ==========================================================

from PyQt6 import QtWidgets, QtGui, QtCore
from modules.workers.cor_worker import OCRWorker


class Overlay(QtWidgets.QWidget):
    """
    Overlay = หน้าต่างโปร่งใสที่ใช้ลากกรอบ OCR + แปลภาษา
    เวอร์ชันนี้ถูกปรับปรุงใหม่ให้:
    - ใช้ worker pool ป้องกัน QThread crash
    - ปิด overlay ได้ปลอดภัย (quit + wait)
    - ไม่มีการทับตัวแปร worker จนโดนลบทิ้ง
    """

    finished_signal = QtCore.pyqtSignal(object)
    closed_signal = QtCore.pyqtSignal(object)

    def __init__(self, font_size_getter, delay_getter, src_lang_getter, dst_lang_getter):
        super().__init__()

        self.font_size_getter = font_size_getter
        self.delay_getter = delay_getter
        self.src_lang_getter = src_lang_getter
        self.dst_lang_getter = dst_lang_getter

        # ตั้งหน้าต่างใส + ทะลุเมาส์ได้
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint |
            QtCore.Qt.WindowType.WindowStaysOnTopHint |
            QtCore.Qt.WindowType.Tool
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(QtWidgets.QApplication.primaryScreen().geometry())

        self.scale = self.devicePixelRatioF() - 0.25

        # state
        self.start = None
        self.rect = None
        self.persistent_rect = None
        self.text = ""
        self.text_pos = None
        self.last_bbox = None

        self.last_raw_text = None
        self.last_translated_text = None

        # ===== worker pool (safe QThread) =====
        self.workers = []

        # Auto OCR timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.auto_ocr)

        self.set_mouse_passthrough(False)
        self.show()

    # =====================================================
    # ควบคุมคลิกทะลุ
    # =====================================================
    def set_mouse_passthrough(self, enable: bool):
        self.setWindowFlag(QtCore.Qt.WindowType.WindowTransparentForInput, enable)
        self.show()

    # =====================================================
    # วาด overlay
    # =====================================================
    def paintEvent(self, e):
        qp = QtGui.QPainter(self)

        if self.rect:
            qp.fillRect(self.rect, QtGui.QColor(0, 200, 255, 40))
            qp.setPen(QtGui.QPen(QtGui.QColor(0, 180, 255, 180), 2))
            qp.drawRect(self.rect)

        if self.persistent_rect:
            qp.fillRect(self.persistent_rect, QtGui.QColor(0, 200, 255, 40))
            qp.setPen(QtGui.QPen(QtGui.QColor(0, 180, 255, 180), 2))
            qp.drawRect(self.persistent_rect)

        if self.text and self.persistent_rect:
            self.draw_bubble(qp)

    # =====================================================
    # วาด bubble คำแปล
    # =====================================================
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

        if y - bubble_h < 0:
            y = self.persistent_rect.bottom() + bubble_h + 5
        elif y > sh - 5:
            y = self.persistent_rect.top() - 5

        bg = QtCore.QRect(x - 10, y - bubble_h + 5, bubble_w, bubble_h)
        qp.fillRect(bg, QtGui.QColor(30, 30, 30, 180))

        qp.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255)))
        qp.drawText(
            QtCore.QRect(
                x - 5, y - wrapped.height(),
                wrapped.width(), wrapped.height()
            ),
            QtCore.Qt.TextFlag.TextWordWrap,
            self.text
        )

    # =====================================================
    # Mouse events
    # =====================================================
    def mousePressEvent(self, e):
        self.set_mouse_passthrough(False)
        self.text = ""
        self.rect = None

        self.start = e.position().toPoint()
        self.rect = QtCore.QRect(self.start, QtCore.QSize())
        self.update()

    def mouseMoveEvent(self, e):
        if self.start:
            self.rect = QtCore.QRect(self.start, e.position().toPoint()).normalized()
            self.update()

    def mouseReleaseEvent(self, e):
        if not self.rect:
            return

        lx, ly, lw, lh = (
            self.rect.left(),
            self.rect.top(),
            self.rect.width(),
            self.rect.height(),
        )

        # scale → real pixel
        px = int(lx * self.scale)
        py = int(ly * self.scale)
        pw = int(lw * self.scale)
        ph = int(lh * self.scale)

        self.text_pos = (lx, ly - 10)
        self.persistent_rect = QtCore.QRect(lx, ly, lw, lh)
        self.rect = None

        self.last_bbox = (px, py, pw, ph)

        # ===== เริ่ม OCR ครั้งแรก =====
        self.start_worker(self.last_bbox, self.src_lang_getter(), self.dst_lang_getter())

        delay = self.delay_getter()
        self.timer.setInterval(delay * 1000)
        self.timer.start()

        self.start = None
        self.set_mouse_passthrough(True)

    # =====================================================
    # Worker Management (safe)
    # =====================================================
    def start_worker(self, bbox, src_lang, dest_lang):
        worker = OCRWorker(bbox, src_lang, dest_lang)

        worker.finished_signal.connect(self.on_text_ready)
        worker.finished_signal.connect(lambda _: self.cleanup_worker(worker))

        self.workers.append(worker)
        worker.start()

    def cleanup_worker(self, worker):
        """ลบ worker ที่ทำงานเสร็จแล้ว"""
        if worker in self.workers:
            worker.wait()  # ปิดอย่างปลอดภัย
            self.workers.remove(worker)

    # =====================================================
    # Auto OCR
    # =====================================================
    def auto_ocr(self):
        if not self.last_bbox:
            return

        # ห้ามสร้างถ้ายังมี worker กำลังทำงาน
        if any(w.isRunning() for w in self.workers):
            return

        self.start_worker(self.last_bbox, self.src_lang_getter(), self.dst_lang_getter())

    # =====================================================
    # Worker ส่งผลลัพธ์กลับมา
    # =====================================================
    def on_text_ready(self, data):
        raw = data["raw"]
        th = data["th"]

        # ถ้าข้อความเดิม → ไม่ต้อง update
        if raw == self.last_raw_text and th == self.last_translated_text:
            return

        self.last_raw_text = raw
        self.last_translated_text = th
        self.text = th

        self.update()
        self.finished_signal.emit(data)

    # =====================================================
    # ปิด overlay → หยุดทุก worker
    # =====================================================
    def closeEvent(self, e):
        self.timer.stop()

        # ปิด worker ทั้งหมด (quit + wait)
        for w in list(self.workers):
            try:
                w.finished_signal.disconnect()
            except:
                pass

            w.quit()
            w.wait()

        self.workers.clear()

        self.closed_signal.emit(self)
        super().close()

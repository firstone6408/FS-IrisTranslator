# ==========================================================
# ocr_worker.py
# Thread สำหรับทำ OCR แบบ background
# แยกออกจาก UI เพื่อไม่ให้โปรแกรมค้างขณะประมวลผล
# ==========================================================

from PyQt6 import QtCore
import mss
from PIL import Image
import pytesseract
from datetime import datetime
from modules.core.translator import translate_text


class OCRWorker(QtCore.QThread):
    """
    ทำ OCR ใน background thread
    เมื่อ OCR เสร็จจะส่งสัญญาณ finished_signal พร้อมผลลัพธ์กลับไปที่ Overlay
    """
    finished_signal = QtCore.pyqtSignal(object)

    def __init__(self, bbox):
        """
        bbox: (x, y, w, h) พื้นที่สกรีนที่ต้องการจับภาพเพื่อนำไป OCR
        """
        super().__init__()
        self.bbox = bbox

    def run(self):
        """
        ทำงานเมื่อ thread เริ่มทำงาน
        1. จับภาพจากหน้าจอ
        2. OCR
        3. แปลภาษา
        4. ส่งผลกลับไปให้ Overlay
        """
        x, y, w, h = self.bbox

        # ดึงภาพหน้าจอตำแหน่งที่เลือก
        with mss.mss() as sct:
            cap = sct.grab({"top": y, "left": x, "width": w, "height": h})
            img = Image.frombytes("RGB", cap.size, cap.rgb)

        raw = pytesseract.image_to_string(img, lang="eng").strip()

        if raw == "":
            # ไม่เจอข้อความ
            self.finished_signal.emit({
                "raw": "(empty)",
                "th": "(ไม่พบข้อความ)",
                "bbox": self.bbox,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            return

        # แปลข้อความ
        th = translate_text(raw)

        # ส่งกลับให้ Overlay
        self.finished_signal.emit({
            "raw": raw,
            "th": th,
            "bbox": self.bbox,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

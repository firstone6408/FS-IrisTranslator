# ==========================================================
# ocr_worker.py
# Thread สำหรับทำ OCR แบบ background + Translation Cache
# ถ้าข้อความเหมือนเดิม → ไม่ต้องแปลซ้ำ
# ==========================================================

from PyQt6 import QtCore
import mss
from PIL import Image
import pytesseract
from datetime import datetime
from modules.core.translator import translate_text


class OCRWorker(QtCore.QThread):
    """
    ทำ OCR ใน background thread และใช้ cache เพื่อเพิ่มความเร็ว
    finished_signal จะคืน dict ข้อมูล OCR + แปล
    """
    finished_signal = QtCore.pyqtSignal(object)

    # ===== Static Cache (ใช้ร่วมกันทุก overlay) =====
    last_raw = None
    last_translated = None

    def __init__(self, bbox):
        super().__init__()
        self.bbox = bbox
        
    def clean_text(self, text):
        """
        รวมข้อความหลายบรรทัดให้เป็นบรรทัดเดียว
        ตัด \n, \r และแทนด้วย space เดียว
        """
        return " ".join(text.split())

    def run(self):
        """
        ทำงานเมื่อ thread เริ่มทำงาน:
        1. จับภาพจากหน้าจอ
        2. OCR
        3. ใช้ cache ถ้าข้อความเดิม
        4. แปลภาษา (ถ้าจำเป็น)
        5. ส่งผลกลับไปให้ Overlay
        """
        x, y, w, h = self.bbox

        # ===== 1) Capture screen =====
        with mss.mss() as sct:
            cap = sct.grab({"top": y, "left": x, "width": w, "height": h})
            img = Image.frombytes("RGB", cap.size, cap.rgb)

        # ===== 2) OCR =====
        raw = pytesseract.image_to_string(img, lang="eng").strip()
        
        # ทำความสะอาด: รวมทุกบรรทัดให้เป็นบรรทัดเดียว
        clean_raw = self.clean_text(raw)

        # ===== ถ้าไม่เจอข้อความ =====
        if clean_raw == "":
            self.finished_signal.emit({
                "raw": "(empty)",
                "th": "(ไม่พบข้อความ)",
                "bbox": self.bbox,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            return

        # ===== 3) เช็กว่าข้อความซ้ำไหม → ใช้ cache =====
        if OCRWorker.last_raw == clean_raw:
            th = OCRWorker.last_translated
        else:
            # ===== 4) แปลใหม่ถ้าข้อความเปลี่ยน =====
            th = translate_text(clean_raw)

            # อัปเดต cache
            OCRWorker.last_raw = clean_raw
            OCRWorker.last_translated = th

        # ===== 5) ส่งผลลัพธ์กลับ =====
        self.finished_signal.emit({
            "raw": clean_raw,
            "th": th,
            "bbox": self.bbox,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

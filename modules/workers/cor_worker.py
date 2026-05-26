# ==========================================================
# ocr_worker.py
# Thread สำหรับทำ OCR แบบ background + Translation Cache
# ถ้าข้อความเหมือนเดิม → ไม่ต้องแปลซ้ำ
# ==========================================================

from PyQt6 import QtCore
import pyscreenshot as ImageGrab
import pytesseract
import threading
from datetime import datetime
from modules.core.translator import translate_text


class OCRWorker(QtCore.QThread):
    """
    ทำ OCR ใน background thread และใช้ cache เพื่อเพิ่มความเร็ว
    finished_signal จะคืน dict ข้อมูล OCR + แปล
    """
    finished_signal = QtCore.pyqtSignal(object)

    # ===== Static Cache (ใช้ร่วมกันทุก overlay) =====
    translation_cache = {}
    cache_lock = threading.Lock()

    def __init__(self, bbox, src_lang, dest_lang):
        super().__init__()
        self.bbox = bbox
        self.src_lang = src_lang
        self.dest_lang = dest_lang
        
    def clean_text(self, text):
        """
        รวมข้อความหลายบรรทัดให้เป็นบรรทัดเดียว
        ตัด \n, \r และแทนด้วย space เดียว
        """
        return " ".join(text.split())

    def emit_result(self, raw, translated):
        self.finished_signal.emit({
            "raw": raw,
            "th": translated,
            "bbox": self.bbox,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

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

        try:
            # ===== 1) Capture screen =====
            img = ImageGrab.grab(
                bbox=(x, y, x + w, y + h)
            )

            # ===== 2) OCR =====
            # เลือกภาษา OCR ตามภาษาที่ผู้ใช้เลือก
            # ===== dict สำหรับ Detect ภาษาให้ pytesseract จากที่ User เลือก =====
            TESS_LANG_MAP = {
                "en": "eng",
                "th": "tha",
                "ja": "jpn"
            }
            tess_lang = TESS_LANG_MAP.get(self.src_lang, "eng")
            # เพิ่ม eng สำรองเพื่อให้ตรวจเจอตัวอักษรภาษาอังกฤษด้วย
            if tess_lang != "eng":
                tess_lang = f"{tess_lang}+eng"
            raw = pytesseract.image_to_string(img, lang=tess_lang).strip()

        except Exception as err:
            self.emit_result("(error)", f"(OCR error: {err})")
            return

        # ทำความสะอาด: รวมทุกบรรทัดให้เป็นบรรทัดเดียว
        clean_raw = self.clean_text(raw)

        # ===== ถ้าไม่เจอข้อความ =====
        if clean_raw == "":
            self.emit_result("(empty)", "(ไม่พบข้อความ)")
            return

        # ===== 3) เช็กว่าข้อความซ้ำไหม → ใช้ cache =====
        cache_key = (self.src_lang, self.dest_lang, clean_raw)
        with OCRWorker.cache_lock:
            th = OCRWorker.translation_cache.get(cache_key)

        if th is None:
            # ===== 4) แปลใหม่ถ้าข้อความเปลี่ยน =====
            th = translate_text(clean_raw, self.src_lang, self.dest_lang)

            # อัปเดต cache
            with OCRWorker.cache_lock:
                OCRWorker.translation_cache[cache_key] = th

        # ===== 5) ส่งผลลัพธ์กลับ =====
        self.emit_result(clean_raw, th)

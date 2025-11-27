# ==========================================================
# translator.py
# โมดูลสำหรับจัดการการแปลข้อความ (ใช้ Google Translate API)
# ทำเป็นฟังก์ชันกลาง เพื่อให้เปลี่ยน API ได้ง่ายในอนาคต
# ==========================================================

from googletrans import Translator

# ใช้ instance เดียวตลอดเพื่อลด overhead
_translator = Translator()


def translate_text(raw: str) -> str:
    """
    ฟังก์ชันแปลข้อความเป็นภาษาไทย
    รับข้อความภาษาอังกฤษ -> ส่งกลับข้อความภาษาไทย
    """
    try:
        return _translator.translate(raw, dest="th").text
    except Exception:
        return "(เกิดข้อผิดพลาดขณะแปลข้อความ)"

# ==========================================================
# translator.py
# โมดูลสำหรับจัดการการแปลข้อความ (ใช้ Google Translate API)
# ทำเป็นฟังก์ชันกลาง เพื่อให้เปลี่ยน API ได้ง่ายในอนาคต
# ==========================================================

from googletrans import Translator

# ใช้ instance เดียวตลอดเพื่อลด overhead
_translator = Translator()


def translate_text(raw: str, src: str, dest: str) -> str:
    """
    ฟังก์ชันแปลข้อความด้วย source/destination language
    """
    try:
        print("raw:", raw)
        print("src:", src)
        print("dest:", dest)
        return _translator.translate(raw, src=src, dest=dest).text
    except Exception:
        return "(เกิดข้อผิดพลาดขณะทำการแปล)"
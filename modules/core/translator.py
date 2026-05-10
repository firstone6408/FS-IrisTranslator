# ==========================================================
# translator.py
# โมดูลสำหรับจัดการการแปลข้อความ
# ระบบหลัก: Argos Translate (ออฟไลน์)
# ระบบสำรอง: Googletrans (ออนไลน์)
# ทำเพื่อให้แปลได้เสถียร + fallback อัตโนมัติ
# ==========================================================

import argostranslate.package
import argostranslate.translate

from googletrans import Translator as GoogleTranslator
_google = GoogleTranslator()   # instance เดียว ลด overhead


# ----------------------------------------------------------
# โหลดโมเดลอัตโนมัติ หากยังไม่มีโมเดลคู่ภาษานั้นบนเครื่อง
# ----------------------------------------------------------
def _ensure_model_installed(src: str, dest: str):
    """
    ตรวจสอบว่ามีโมเดลคู่ภาษาที่ต้องการหรือยัง
    ถ้ายัง → ดาวน์โหลดและติดตั้งอัตโนมัติ
    """
    installed = argostranslate.package.get_installed_packages()
    for pkg in installed:
        if pkg.from_code == src and pkg.to_code == dest:
            # print(pkg.argos_version)
            return  # มีแล้ว → ใช้ได้ทันที

    # ถ้าไม่มี ให้โหลดรายการโมเดลจาก server
    argostranslate.package.update_package_index()
    available = argostranslate.package.get_available_packages()

    match = next(
        (p for p in available if p.from_code == src and p.to_code == dest),
        None
    )

    if match is None:
        raise Exception(f"ไม่มีโมเดลแปล {src} → {dest} ให้ใช้งาน")

    model_path = match.download()
    argostranslate.package.install_from_path(model_path)


# ----------------------------------------------------------
# ฟังก์ชันแปลข้อความ
# ----------------------------------------------------------
def translate_text(raw: str, src: str, dest: str) -> str:
    """
    แปลข้อความด้วย:
    1) Argos Translate (ออฟไลน์)
    2) ถ้า Argos ใช้งานไม่ได้ → googletrans (ออนไลน์)
    """
    # 1) พยายามใช้ Argos ก่อน
    try:
        _ensure_model_installed(src, dest)
        return argostranslate.translate.translate(raw, src, dest)

    except Exception as argos_err:
        # ถ้า argos แปลไม่ได้ → ไปใช้ Google
        try:
            result = _google.translate(raw, src=src, dest=dest).text
            return result + " (google)"
        except Exception as google_err:
            return f"(แปลไม่ได้ทั้ง Argos และ Google: {argos_err}, {google_err})"

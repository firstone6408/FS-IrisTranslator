# 🌙 Iris Translator

แอปแปลภาษาบนหน้าจอแบบ Overlay พร้อม OCR จากพื้นที่ที่ผู้ใช้ลากเลือก ใช้งานง่าย เหมาะกับเกม/แอป/เว็บที่ไม่มีภาษาไทย

---

## ✨ ฟีเจอร์หลัก

- 🖼️ **ลากกรอบบนหน้าจอเพื่อ OCR**
- 🔤 รองรับ OCR 3 ภาษา: English, Thai, Japanese
- 🌐 **แปลภาษาแบบออนไลน์ผ่าน Google Translate (googletrans)**
- ⚡ **Translation Cache** — ไม่แปลซ้ำถ้าข้อความเดิม
- 🕒 **Auto OCR Timer** ดึงข้อความรอบใหม่ทุก X วินาที
- 🪟 **Log Viewer แยก** กดปุ่มแล้วเปิดหน้าต่าง log ใหม่
- 🎨 ธีมมืดแบบ **Nord Dark Mode**
- 📌 แอปมีไอคอนของตัวเอง
- 🔧 GUI ตั้งค่าได้ครบ: ฟอนต์, ภาษา, ดีเลย์, จัดการ Overlay

---

## 🗂️ โครงสร้างโปรเจกต์

```
Iris-Translator/
│
├── assets/
│ └── logo.png # ไอคอนโปรแกรม
│
├── modules/
│ ├── core/
│ │ └── translator.py # ระบบแปล (googletrans)
│ │
│ ├── workers/
│ │ └── ocr_worker.py # OCR + Translation cache
│ │
│ └── ui/
│ ├── panel.py # Control Panel UI
│ └── overlay.py # Overlay สำหรับลากกรอบ OCR
│
├── main.py # จุดเริ่มโปรแกรม
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🛠️ การติดตั้ง

### 1) Clone โปรเจกต์

```bash
git clone https://github.com/your-repo/iris-translator
cd iris-translator
```

### 2) ติดตั้ง dependencies

```bash
pip install -r requirements.txt
```

ปัจจุบันระบบแปลใช้ **googletrans** (unofficial Google Translate client) — อาจมีปัญหา/จำกัดการใช้งานในบางช่วง เนื่องจากเป็น API ไม่เป็นทางการ

### 3) ติดตั้ง Tesseract OCR

Linux Mint / Ubuntu:

```bash
sudo apt install tesseract-ocr
```

ดาวน์โหลดภาษาเพิ่มเติม: https://github.com/tesseract-ocr/tessdata_best

### 3.1) การติดตั้ง ภาษา Tesseract OCR

ดาวน์โหลดไฟล์ <ภาษา>.traineddata เช่น jpn.traineddata แล้วย้ายไฟล์ไปที่ /usr/share/tesseract-ocr/5/tessdata/ ตัวอย่างดังนี้:

```bash
sudo mv jpn.traineddata /usr/share/tesseract-ocr/5/tessdata/
tesseract --list-langs # แสดงรายการภาษา
```

## ▶️ วิธีรันโปรแกรม

```bash
python main.py
```

จะเปิด **Iris Translator Control Panel** ขึ้นมา — จากนั้น:

- ตั้งค่า Font / Source / Target / Delay

- กด **Add Selection** เพื่อสร้าง overlay แล้วลากกรอบบนหน้าจอเพื่อ OCR+Translate

- กด 📄 **Open Log Window** เพื่อเปิดหน้าต่างแสดง Log แบบเต็ม

## 🖼️ วิธีใช้งาน Overlay (สั้น ๆ)

1. กด **Add Selection**

2. ลากกรอบบริเวณข้อความบนหน้าจอ

3. โปรแกรมจะ OCR ข้อความและส่งไปแปล (googletrans)

4. คำแปลจะแสดงใน bubble ใกล้กรอบ และถูกเก็บเป็น log

## 🔧 เทคโนโลยีที่ใช้

- **PyQt6** — GUI และ Overlay บนหน้าจอ

- **googletrans** — Translation Engine (online; unofficial)

- **Tesseract OCR** — อ่านตัวอักษรจากภาพ

- **mss** — จับภาพหน้าจออย่างรวดเร็ว

- **QThread + Worker Pool** — จัดการ worker ปลอดภัย

- **Pillow (PIL)** — จัดการภาพ

## 📝 คำสั่งสำคัญ

รันแอป:

```bash
python main.py
```

## 👤 ผู้พัฒนา

**Iris Translator © 2025 — Designed with ♡ by FirstOne**

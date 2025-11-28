# ==========================================================
# panel.py
# UI ควบคุมหลักของโปรแกรม (Dark Mode + Soft Button Theme)
# พร้อมฟีเจอร์:
# - นับจำนวน Overlay
# - นับจำนวน Log
# - เพิ่มวันเวลาที่ Log ถูกสร้าง
# - Footer credit
# ==========================================================

from PyQt6 import QtWidgets, QtGui, QtCore
from datetime import datetime
from modules.ui.overlay import Overlay


class Panel(QtWidgets.QWidget):
    """
    หน้าต่างควบคุมหลักของโปรแกรม (Control Panel)
    ฟีเจอร์:
    - ตั้งขนาดฟอนต์คำแปล
    - ตั้ง delay auto OCR
    - เพิ่ม / ปิด overlay
    - แสดงจำนวน overlay
    - แสดงจำนวน log
    - Log แบบมี timestamp
    """

    def __init__(self):
        super().__init__()

        # =======================
        # ตั้งค่าหน้าต่าง
        # =======================
        self.setWindowTitle("Iris Translator")
        self.setFixedSize(440, 720)

        # ใช้ธีมสีเข้มแบบ soft (Nord theme)
        self.apply_dark_theme()

        # Layout หลัก
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # =======================
        # ชื่อโปรแกรม
        # =======================
        title = QtWidgets.QLabel("Iris Translator Control Panel")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #E5E9F0;")
        layout.addWidget(title)

        # =======================
        # ส่วนตั้งค่าฟอนต์
        # =======================
        font_group = QtWidgets.QGroupBox("Font Settings")
        font_group.setStyleSheet("QGroupBox { font-weight: bold; }")

        font_layout = QtWidgets.QHBoxLayout()
        font_label = QtWidgets.QLabel("Font size:")

        self.font_spin = QtWidgets.QSpinBox()
        self.font_spin.setRange(10, 60)
        self.font_spin.setValue(17)
        self.font_spin.setFixedWidth(70)

        font_layout.addWidget(font_label)
        font_layout.addWidget(self.font_spin)
        font_group.setLayout(font_layout)

        layout.addWidget(font_group)
        
        # =======================
        # Language Settings
        # =======================
        LANGS = {
            "English": "en",
            "Thai": "th",
            "Japanese": "ja",
        }

        lang_group = QtWidgets.QGroupBox("Language Settings")
        lang_group.setStyleSheet("QGroupBox { font-weight: bold; }")

        lang_layout = QtWidgets.QHBoxLayout()

        self.combo_src = QtWidgets.QComboBox()
        self.combo_dst = QtWidgets.QComboBox()

        for name, code in LANGS.items():
            self.combo_src.addItem(name, code)
            self.combo_dst.addItem(name, code)

        # default
        self.combo_src.setCurrentText("English")
        self.combo_dst.setCurrentText("Thai")

        lang_layout.addWidget(QtWidgets.QLabel("From:"))
        lang_layout.addWidget(self.combo_src)

        lang_layout.addWidget(QtWidgets.QLabel("To:"))
        lang_layout.addWidget(self.combo_dst)

        lang_group.setLayout(lang_layout)
        layout.addWidget(lang_group)

        # =======================
        # ส่วนตั้งค่า delay
        # =======================
        delay_group = QtWidgets.QGroupBox("Auto OCR Settings")
        delay_group.setStyleSheet("QGroupBox { font-weight: bold; }")

        delay_layout = QtWidgets.QHBoxLayout()
        delay_label = QtWidgets.QLabel("Delay (sec):")

        self.delay_spin = QtWidgets.QSpinBox()
        self.delay_spin.setRange(1, 60)
        self.delay_spin.setValue(2)
        self.delay_spin.setFixedWidth(70)

        delay_layout.addWidget(delay_label)
        delay_layout.addWidget(self.delay_spin)
        delay_group.setLayout(delay_layout)

        layout.addWidget(delay_group)

        # =======================
        # ปุ่มควบคุม
        # =======================
        btn_group = QtWidgets.QGroupBox("Controls")
        btn_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        btn_layout = QtWidgets.QVBoxLayout()
        btn_layout.setSpacing(8)

        self.btn_add = self.create_button("➕ Add Selection (0)", "#4C566A")
        self.btn_clear = self.create_button("🗑️ Clear All Selections", "#BF616A")
        self.btn_clear_log = self.create_button("✖️ Clear Log", "#D08770")
        self.btn_exit = self.create_button("🚪 Exit Program", "#5E81AC")

        self.btn_add.clicked.connect(self.add_overlay)
        self.btn_clear.clicked.connect(self.clear_all)
        self.btn_clear_log.clicked.connect(self.clear_log)
        self.btn_exit.clicked.connect(self.exit_program)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_clear)
        btn_layout.addWidget(self.btn_clear_log)
        btn_layout.addWidget(self.btn_exit)

        btn_group.setLayout(btn_layout)
        layout.addWidget(btn_group)

        # =======================
        # Log Header
        # =======================
        log_header_layout = QtWidgets.QHBoxLayout()
        log_label = QtWidgets.QLabel("Log Output")
        log_label.setStyleSheet("font-weight: bold;")

        self.log_count = QtWidgets.QLabel("Logs: 0")
        self.log_count.setStyleSheet("color: #88C0D0; font-weight: bold;")

        log_header_layout.addWidget(log_label)
        log_header_layout.addStretch(1)
        log_header_layout.addWidget(self.log_count)
        layout.addLayout(log_header_layout)

        # =======================
        # Log Window
        # =======================
        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("""
            QTextEdit {
                background-color: #2E3440;
                color: #ECEFF4;
                border: 1px solid #4C566A;
                padding: 8px;
                font-family: Consolas, monospace;
            }
        """)
        layout.addWidget(self.log, stretch=1)

        # =======================
        # Footer Credit
        # =======================
        footer = QtWidgets.QLabel("Iris Translator © 2025 — Designed with ♡")
        footer.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #616E88; font-size: 12px; margin-top: 10px;")
        layout.addWidget(footer)

        self.setLayout(layout)

        # เก็บ overlay ทั้งหมดที่เปิดอยู่
        self.overlays = []
        self.log_counter = 0  # จำนวน log ที่เกิดขึ้น

        self.show()

    # ======================================================
    # Theme (Nord Dark)
    # ======================================================
    def apply_dark_theme(self):
        """
        ใช้ชุดสี dark mode แบบ Nord Theme
        """
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor("#2E3440"))
        palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor("#ECEFF4"))
        palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor("#3B4252"))
        palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor("#ECEFF4"))
        palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor("#434C5E"))
        palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor("#ECEFF4"))
        self.setPalette(palette)

    # ======================================================
    # สร้างปุ่มสไตล์ soft dark
    # ======================================================
    def create_button(self, text, color):
        """
        สร้างปุ่มด้วยสี muted (soft) ให้เข้ากับ dark mode
        """
        btn = QtWidgets.QPushButton(text)
        btn.setFixedHeight(42)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: 1px solid #3B4252;
                border-radius: 6px;
                color: #ECEFF4;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #ECEFF4;
                color: #2E3440;
            }}
        """)
        return btn

    # ======================================================
    # Getter ฟอนต์ / ดีเลย์
    # ======================================================
    def get_font_size(self):
        return self.font_spin.value()

    def get_delay(self):
        return self.delay_spin.value()
    
    # ======================================================
    # Getter ภาษา ต้น/ปลาย ทาง
    # ======================================================
    def get_src_lang(self):
        return self.combo_src.currentData()

    def get_dst_lang(self):
        return self.combo_dst.currentData()

    # ======================================================
    # Overlay Management
    # ======================================================
    def add_overlay(self):
        """
        สร้าง overlay ใหม่และเชื่อมสัญญาณ log + remove
        """
        ov = Overlay(self.get_font_size, self.get_delay, self.get_src_lang, self.get_dst_lang)
        ov.finished_signal.connect(self.add_log)
        ov.closed_signal.connect(self.remove_overlay)

        self.overlays.append(ov)
        self.update_add_button()

    def clear_all(self):
        """
        ปิด overlay ทั้งหมด
        """
        for ov in list(self.overlays):
            ov.close()

        self.overlays.clear()
        self.update_add_button()

        self.log.append("<b>All overlays cleared</b><hr>")

    def remove_overlay(self, ov):
        """
        ถูกเรียกเมื่อ overlay ปิดเองหรือถูกปิด
        """
        if ov in self.overlays:
            self.overlays.remove(ov)
        self.update_add_button()

    def update_add_button(self):
        """
        อัปเดตข้อความของปุ่ม Add Selection ให้แสดงจำนวน overlay
        """
        count = len(self.overlays)
        self.btn_add.setText(f"➕ Add Selection ({count})")

    # ======================================================
    # Logging
    # ======================================================
    def add_log(self, data):
        """
        เพิ่มข้อมูล OCR ลง log พร้อม timestamp สองแบบ:
        - เวลาเกิด event จริง (จาก worker)
        - เวลา panel log ถูกสร้าง
        """
        self.log_counter += 1
        self.log_count.setText(f"Logs: {self.log_counter}")

        panel_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.log.append(
            f"<b>Log Time:</b> {panel_time}"
            f"<br><b>Event Time:</b> {data['timestamp']}"
            f"<br><b>BBox:</b> {data['bbox']}"
            f"<br>Raw:<pre>{data['raw']}</pre>"
            f"<br>Translated:<pre>{data['th']}</pre>"
            "<hr>"
        )

    def clear_log(self):
        """
        ล้าง log ทั้งหมด + รีเซ็ต counter
        """
        self.log.clear()
        self.log_counter = 0
        self.log_count.setText("Logs: 0")

    # ======================================================
    # Exit Program
    # ======================================================
    def exit_program(self):
        """
        ปิด overlay ทั้งหมดและออกจากโปรแกรม
        """
        for ov in self.overlays:
            ov.close()
        QtWidgets.QApplication.quit()

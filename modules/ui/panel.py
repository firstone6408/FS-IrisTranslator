# ==========================================================
# panel.py
# UI ควบคุมหลักของโปรแกรม
# ใช้สั่ง:
# - เพิ่ม overlay
# - ลบ overlay ทั้งหมด
# - ตั้ง delay auto OCR
# - ตั้งขนาดฟอนต์
# - แสดง log
# ==========================================================

from PyQt6 import QtWidgets
from modules.ui.overlay import Overlay


class Panel(QtWidgets.QWidget):
    """
    หน้าต่างควบคุม (Control Panel)
    ผู้ใช้สามารถ:
    - ปรับขนาดฟอนต์คำแปล
    - เลือก delay สำหรับ auto OCR
    - เพิ่ม overlay ใหม่
    - ล้าง log
    - ล้างทุก overlay
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("iris_translator")
        self.setFixedSize(380, 600)

        layout = QtWidgets.QVBoxLayout()

        # =======================
        # Font Size Setting
        # =======================
        font_row = QtWidgets.QHBoxLayout()
        font_row.addWidget(QtWidgets.QLabel("Font size:"))

        self.font_spin = QtWidgets.QSpinBox()
        self.font_spin.setRange(10, 60)
        self.font_spin.setValue(17)

        font_row.addWidget(self.font_spin)

        # =======================
        # Delay Setting
        # =======================
        delay_row = QtWidgets.QHBoxLayout()
        delay_row.addWidget(QtWidgets.QLabel("Delay (sec):"))

        self.delay_spin = QtWidgets.QSpinBox()
        self.delay_spin.setRange(1, 60)
        self.delay_spin.setValue(2)

        delay_row.addWidget(self.delay_spin)

        # =======================
        # Buttons
        # =======================
        self.btn_add = QtWidgets.QPushButton("Add Selection")
        self.btn_clear = QtWidgets.QPushButton("Clear All Selections")
        self.btn_clear_log = QtWidgets.QPushButton("Clear Log")
        self.btn_exit = QtWidgets.QPushButton("Exit Program")

        self.btn_add.clicked.connect(self.add_overlay)
        self.btn_clear.clicked.connect(self.clear_all)
        self.btn_clear_log.clicked.connect(self.clear_log)
        self.btn_exit.clicked.connect(self.exit_program)

        layout.addLayout(font_row)
        layout.addLayout(delay_row)
        layout.addWidget(self.btn_add)
        layout.addWidget(self.btn_clear)
        layout.addWidget(self.btn_clear_log)
        layout.addWidget(self.btn_exit)

        # =======================
        # Log Window
        # =======================
        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        self.setLayout(layout)
        self.overlays = []
        self.show()

    # =======================
    # Getter functions
    # =======================
    def get_font_size(self):
        return self.font_spin.value()

    def get_delay(self):
        return self.delay_spin.value()

    # =======================
    # Overlay management
    # =======================
    def add_overlay(self):
        """
        สร้าง overlay ใหม่และเชื่อม signal ต่างๆ
        """
        ov = Overlay(self.get_font_size, self.get_delay)
        ov.finished_signal.connect(self.add_log)
        ov.closed_signal.connect(self.remove_overlay)
        self.overlays.append(ov)

    def clear_all(self):
        """
        ปิด overlay ทั้งหมด
        """
        for ov in list(self.overlays):
            ov.close()
        self.overlays.clear()
        self.log.append("<b>All overlays cleared</b><br>")

    def clear_log(self):
        """
        ล้าง log text ทั้งหมด
        """
        self.log.clear()

    def remove_overlay(self, ov):
        """
        เอา overlay ออกจาก list เมื่อถูกปิด
        """
        if ov in self.overlays:
            self.overlays.remove(ov)

    # =======================
    # Logging
    # =======================
    def add_log(self, data):
        """
        เพิ่มผล OCR และคำแปลลงไปใน log
        """
        self.log.append(
            f"<b>{data['timestamp']}</b>"
            f"<br><b>BBox {data['bbox']}</b>"
            f"<br>Raw:<pre>{data['raw']}</pre>"
            f"<br>Translated:<pre>{data['th']}</pre>"
            "<hr>"
        )

    # =======================
    # Exit
    # =======================
    def exit_program(self):
        """
        ปิด overlay ทั้งหมด และออกจากโปรแกรม
        """
        for ov in self.overlays:
            ov.close()
        QtWidgets.QApplication.quit()

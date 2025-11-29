# ============================================
# main.py
# จุดเริ่มโปรแกรม สร้าง QApplication และโหลด Panel (หน้าควบคุมหลัก)
# ============================================

from PyQt6 import QtWidgets, QtGui
import sys

# โหลด Panel จาก modules/ui/panel.py
from modules.ui.panel import Panel


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon("assets/logo.png"))

    # เปิดหน้า Panel หลัก
    p = Panel()

    # เริ่ม event loop ของ Qt
    sys.exit(app.exec())

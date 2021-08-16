from PyQt5.QtWidgets import QApplication
from app_modules.widget import WaterMartWidget
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WaterMartWidget()
    win.show()
    sys.exit(app.exec_())


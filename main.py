import sys
from PyQt5.QtWidgets import QApplication
from start_window import StartWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    start_window = StartWindow()
    start_window.show()
    sys.exit(app.exec_())

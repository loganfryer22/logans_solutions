import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle('Hello, World!')

    label = QLabel('Hello, World!', window)
    label.move(60, 100)

    window.setGeometry(100, 100, 300, 200)
    window.show()

    sys.exit(app.exec_())
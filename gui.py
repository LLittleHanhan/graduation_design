from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton


class mywindow(QMainWindow, ):
    def __init__(self):
        super().__init__()


if __name__ == '__main__':
    app = QApplication()
    window = mywindow()
    window.show()
    app.exec()

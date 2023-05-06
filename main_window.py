import os

from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Qt, QEvent, QTimer
from PySide6.QtGui import QIcon, QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QGraphicsDropShadowEffect, QSizeGrip

from ui_main import Ui_MainWindow
from ui_settings import Settings

os.environ["QT_FONT_DPI"] = "144"


class Mywindow(QMainWindow, Ui_MainWindow):
    # normal为false 最大化为true
    maximize_restore_state = False

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.uiDefinitions()
        self.stackedWidget.setCurrentWidget(self.home)
        self.btn_home.setStyleSheet(self.selectMenu(self.btn_home.styleSheet()))
        # button
        self.toggleButton.clicked.connect(self.toggleMenu)
        self.btn_home.clicked.connect(self.buttonClick)
        self.btn_get_news.clicked.connect(self.buttonClick)
        self.btn_cloud.clicked.connect(self.buttonClick)
        self.btn_event.clicked.connect(self.buttonClick)

        self.show()

    # menu处理
    def toggleMenu(self):
        # GET WIDTH
        width = self.leftMenuBg.width()
        maxExtend = Settings.MENU_WIDTH
        standard = 60

        # SET MAX WIDTH
        if width == 60:
            change = maxExtend
        else:
            change = standard
        # ANIMATION
        self.animation = QPropertyAnimation(self.leftMenuBg, b"minimumWidth")
        self.animation.setDuration(Settings.TIME_ANIMATION)
        self.animation.setStartValue(width)
        self.animation.setEndValue(change)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()

    # button处理
    def buttonClick(self):
        btn = self.sender()
        btnName = btn.objectName()
        # SHOW PAGE
        if btnName == "btn_home":
            self.stackedWidget.setCurrentWidget(self.home)
            self.resetStyle(btnName)
            btn.setStyleSheet(self.selectMenu(btn.styleSheet()))

        if btnName == "btn_get_news":
            self.stackedWidget.setCurrentWidget(self.page_get_news)
            self.resetStyle(btnName)
            btn.setStyleSheet(self.selectMenu(btn.styleSheet()))

        if btnName == "btn_cloud":
            self.stackedWidget.setCurrentWidget(self.page_cloud)
            self.resetStyle(btnName)
            btn.setStyleSheet(self.selectMenu(btn.styleSheet()))

        if btnName == "btn_event":
            self.stackedWidget.setCurrentWidget(self.page_event)
            self.resetStyle(btnName)
            btn.setStyleSheet(self.selectMenu(btn.styleSheet()))
        print(f'Button "{btnName}" pressed!')

    def resetStyle(self, widget):
        for w in self.topMenu.findChildren(QPushButton):
            if w.objectName() != widget:
                w.setStyleSheet(self.deselectMenu(w.styleSheet()))

    def deselectMenu(self, getStyle):
        deselect = getStyle.replace(Settings.MENU_SELECTED_STYLESHEET, "")
        return deselect

    def selectMenu(self, getStyle):
        select = getStyle + Settings.MENU_SELECTED_STYLESHEET
        return select

    # 隐藏丑丑的系统框，重写逻辑
    def maximize_restore(self):
        if not self.maximize_restore_state:
            self.showMaximized()
            self.maximize_restore_state = True
            self.appMargins.setContentsMargins(0, 0, 0, 0)
            self.maximizeRestoreAppBtn.setToolTip("Restore")
            self.maximizeRestoreAppBtn.setIcon(QIcon(u":/icons/images/icons/icon_restore.png"))
            self.frame_size_grip.hide()
        else:
            self.maximize_restore_state = False
            self.showNormal()
            self.resize(self.width() + 1, self.height() + 1)
            self.appMargins.setContentsMargins(10, 10, 10, 10)
            self.maximizeRestoreAppBtn.setToolTip("Maximize")
            self.maximizeRestoreAppBtn.setIcon(QIcon(u":/icons/images/icons/icon_maximize.png"))
            self.frame_size_grip.show()

    def uiDefinitions(self):
        def doubleClickMaximizeRestore(event):
            if event.type() == QEvent.MouseButtonDblClick:
                QTimer.singleShot(250, self.maximize_restore)
        self.titleRightInfo.mouseDoubleClickEvent = doubleClickMaximizeRestore

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        def moveWindow(event):
            if self.maximize_restore_state:
                self.maximize_restore()
            # MOVE WINDOW
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()
        self.titleRightInfo.mouseMoveEvent = moveWindow

        # DROP SHADOW
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(17)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        self.bgApp.setGraphicsEffect(self.shadow)

        # RESIZE WINDOW
        self.sizegrip = QSizeGrip(self.frame_size_grip)
        self.sizegrip.setStyleSheet("width: 20px; height: 20px; margin 0px; padding: 0px;")

        # MINIMIZE
        self.minimizeAppBtn.clicked.connect(self.showMinimized)

        # MAXIMIZE/RESTORE
        self.maximizeRestoreAppBtn.clicked.connect(self.maximize_restore)

        # CLOSE APPLICATION
        self.closeAppBtn.clicked.connect(self.close)

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()


if __name__ == '__main__':
    app = QApplication()
    window = Mywindow()
    app.exec()

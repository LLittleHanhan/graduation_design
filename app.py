import os
import datetime
import time

from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Qt, QEvent, QTimer, Signal, QObject, QThread
from PySide6.QtGui import QIcon, QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QGraphicsDropShadowEffect, QSizeGrip, QHeaderView, \
    QTableWidgetItem, QDialog, QAbstractItemView

from ui_main import Ui_MainWindow
from ui_select_date import Ui_selec_date
from app_data import Data

os.environ["QT_FONT_DPI"] = "144"


class APP(QMainWindow, Ui_MainWindow):
    # normal为false 最大化为true
    maximize_restore_state = False
    time_animation = 500
    menu_width = 240
    menu_selected_stylesheet = """
            border-left: 22px solid qlineargradient(spread:pad, x1:0.034, y1:0, x2:0.216, y2:0, stop:0.499 rgba(255, 121, 198, 255), stop:0.5 rgba(85, 170, 255, 0));
            background-color: rgb(40, 44, 52);
            """

    def __init__(self):
        super().__init__()
        self.appData = Data()
        self.setupUi(self)

        self.uiDefinitions()
        self.stackedWidget.setCurrentWidget(self.home)
        self.btn_home.setStyleSheet(self.selectMenu(self.btn_home.styleSheet()))

        # get_news
        self.news_table.verticalHeader().setHidden(True)
        self.news_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.news_table.setColumnCount(5)
        self.news_table.setHorizontalHeaderLabels(['index', 'title', 'date', 'platform', 'class'])
        self.news_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.news_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.news_table.itemDoubleClicked.connect(self.show_text)

        today = datetime.datetime.today()
        tomorrow = today + datetime.timedelta(days=1)
        self.lb_begin.setText(today.strftime('%Y-%m-%d'))
        self.lb_end.setText(tomorrow.strftime('%Y-%m-%d'))
        self.cb_all.setChecked(True)

        self.btn_begin.clicked.connect(self.select_date)
        self.btn_end.clicked.connect(self.select_date)
        self.btn_search.clicked.connect(self.get_news)

        self.btn_return.clicked.connect(self.return_news_table)
        self.textEdit.setReadOnly(True)

        # menu
        self.toggleButton.clicked.connect(self.toggleMenu)
        self.btn_home.clicked.connect(self.buttonClick)
        self.btn_get_news.clicked.connect(self.buttonClick)
        self.btn_cloud.clicked.connect(self.buttonClick)
        self.btn_event.clicked.connect(self.buttonClick)

        self.show()

    # menu button
    def toggleMenu(self):
        # GET WIDTH
        width = self.leftMenuBg.width()
        maxExtend = self.menu_width
        standard = 60

        # SET MAX WIDTH
        if width == 60:
            change = maxExtend
        else:
            change = standard
        # ANIMATION
        self.animation = QPropertyAnimation(self.leftMenuBg, b"minimumWidth")
        self.animation.setDuration(self.time_animation)
        self.animation.setStartValue(width)
        self.animation.setEndValue(change)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.animation.start()

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
        deselect = getStyle.replace(self.menu_selected_stylesheet, "")
        return deselect

    def selectMenu(self, getStyle):
        select = getStyle + self.menu_selected_stylesheet
        return select

    # get_news 界面逻辑
    def select_date(self):
        btn = self.sender()
        btnName = btn.objectName()
        if btnName == 'btn_begin':
            parent = self.lb_begin
        else:
            parent = self.lb_end
        self.subwindow = Subwindow(parent)
        self.subwindow.show()

    def get_news(self):
        self.btn_search.setEnabled(False)
        self.btn_search.setText('正在查询，耐心等待。。。')

        begin = self.lb_begin.text()
        end = self.lb_end.text()

        begin_data = time.strptime(begin, "%Y-%m-%d")
        end_data = time.strptime(end, "%Y-%m-%d")
        if begin_data < end_data:
            print('日期合法')
            self.spider = spider(self.appData, begin, end)
            self.thread = QThread()
            self.spider.moveToThread(self.thread)

            self.thread.started.connect(self.spider.get_news)
            self.spider.ready.connect(self.show_news)
            self.spider.ready.connect(self.thread.quit)
            self.thread.finished.connect(self.spider.deleteLater)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.destroyed.connect(lambda: print('thread已销毁'))
            self.thread.start()
        else:
            print('日期不合法')
            self.btn_search.setEnabled(True)
            self.btn_search.setText('search')

    def show_news(self):
        self.btn_search.setEnabled(True)
        self.btn_search.setText('search')
        news_list = self.appData.get_news_list()
        self.news_table.setRowCount(len(news_list))
        for row, news in enumerate(news_list):
            self.news_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.news_table.setItem(row, 1, QTableWidgetItem(str(news['title'])))
            self.news_table.setItem(row, 2, QTableWidgetItem(str(news['date'])))
            self.news_table.setItem(row, 3, QTableWidgetItem(str(news['platform'])))
            self.news_table.setItem(row, 4, QTableWidgetItem('class'))

    def show_text(self):
        row = self.news_table.selectedItems()[0].row()
        title = self.appData.get_news_list()[row]['title']
        text = self.appData.get_news_list()[row]['text']
        html = '<!DOCTYPE html><html><body><h1 align="center">' + title + '</h1><p style="text-indent:28px">' + text + '</body></html>'
        self.textEdit.setHtml(html)
        self.stackedWidget.setCurrentWidget(self.page_text)

    def return_news_table(self):
        self.stackedWidget.setCurrentWidget(self.page_get_news)

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
                self.move(self.pos() + event.globalPosition().toPoint() - self.dragPos)
                self.dragPos = event.globalPosition().toPoint()
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
        self.dragPos = event.globalPosition().toPoint()


class spider(QObject):
    ready = Signal()

    def __init__(self, appData, begin, end):
        super().__init__()
        self.appData = appData
        self.begin = begin
        self.end = end

    def get_news(self):
        print('spider线程开始')
        self.appData.get_news(self.begin, self.end)
        self.ready.emit()


class Subwindow(QDialog, Ui_selec_date):
    send_date_to_main = Signal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setupUi(self)
        self.buttonBox.accepted.connect(self.send)

    def send(self):
        date = self.calendarWidget.selectedDate().toString('yyyy-MM-dd')
        self.send_date_to_main.emit(self.parent.setText(date))


if __name__ == '__main__':
    app = QApplication()
    window = APP()
    app.exec()

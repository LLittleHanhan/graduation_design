# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'select_date.ui'
##
## Created by: Qt User Interface Compiler version 6.5.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCalendarWidget, QDialog,
    QDialogButtonBox, QSizePolicy, QVBoxLayout, QWidget)

class Ui_selec_date(object):
    def setupUi(self, selec_date):
        if not selec_date.objectName():
            selec_date.setObjectName(u"selec_date")
        selec_date.resize(384, 309)
        self.verticalLayout = QVBoxLayout(selec_date)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.calendarWidget = QCalendarWidget(selec_date)
        self.calendarWidget.setObjectName(u"calendarWidget")

        self.verticalLayout.addWidget(self.calendarWidget)

        self.buttonBox = QDialogButtonBox(selec_date)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(selec_date)
        self.buttonBox.accepted.connect(selec_date.accept)
        self.buttonBox.rejected.connect(selec_date.reject)

        QMetaObject.connectSlotsByName(selec_date)
    # setupUi

    def retranslateUi(self, selec_date):
        selec_date.setWindowTitle(QCoreApplication.translate("selec_date", u"Dialog", None))
    # retranslateUi


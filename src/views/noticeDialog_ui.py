# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'noticeDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
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
from PySide6.QtWidgets import (QApplication, QFrame, QPlainTextEdit, QPushButton,
    QSizePolicy, QWidget)

class Ui_FormNoticeDialog(object):
    def setupUi(self, FormNoticeDialog):
        if not FormNoticeDialog.objectName():
            FormNoticeDialog.setObjectName(u"FormNoticeDialog")
        FormNoticeDialog.resize(600, 380)
        self.plainTextEditDetail = QPlainTextEdit(FormNoticeDialog)
        self.plainTextEditDetail.setObjectName(u"plainTextEditDetail")
        self.plainTextEditDetail.setGeometry(QRect(0, 10, 601, 301))
        self.plainTextEditDetail.setMinimumSize(QSize(0, 250))
        font = QFont()
        font.setFamilies([u"Arial"])
        font.setPointSize(22)
        font.setBold(True)
        self.plainTextEditDetail.setFont(font)
        self.plainTextEditDetail.setFrameShape(QFrame.Shape.NoFrame)
        self.plainTextEditDetail.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.plainTextEditDetail.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.plainTextEditDetail.setUndoRedoEnabled(False)
        self.plainTextEditDetail.setReadOnly(True)
        self.pushButton = QPushButton(FormNoticeDialog)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(200, 320, 200, 50))
        font1 = QFont()
        font1.setPointSize(27)
        font1.setBold(True)
        self.pushButton.setFont(font1)

        self.retranslateUi(FormNoticeDialog)

        QMetaObject.connectSlotsByName(FormNoticeDialog)
    # setupUi

    def retranslateUi(self, FormNoticeDialog):
        FormNoticeDialog.setWindowTitle(QCoreApplication.translate("FormNoticeDialog", u"Error", None))
        self.pushButton.setText(QCoreApplication.translate("FormNoticeDialog", u"OK", None))
    # retranslateUi


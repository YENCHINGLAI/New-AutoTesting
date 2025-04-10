# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'inputDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QWidget)

class Ui_FormInputDialog(object):
    def setupUi(self, FormInputDialog):
        if not FormInputDialog.objectName():
            FormInputDialog.setObjectName(u"FormInputDialog")
        FormInputDialog.resize(602, 302)
        self.pushButton = QPushButton(FormInputDialog)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(190, 200, 200, 91))
        font = QFont()
        font.setPointSize(27)
        font.setBold(True)
        self.pushButton.setFont(font)
        self.lineBarcodeInput = QLineEdit(FormInputDialog)
        self.lineBarcodeInput.setObjectName(u"lineBarcodeInput")
        self.lineBarcodeInput.setGeometry(QRect(0, 110, 601, 61))
        self.label = QLabel(FormInputDialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 10, 581, 71))

        self.retranslateUi(FormInputDialog)

        QMetaObject.connectSlotsByName(FormInputDialog)
    # setupUi

    def retranslateUi(self, FormInputDialog):
        FormInputDialog.setWindowTitle(QCoreApplication.translate("FormInputDialog", u"Input", None))
        self.pushButton.setText(QCoreApplication.translate("FormInputDialog", u"OK", None))
        self.label.setText(QCoreApplication.translate("FormInputDialog", u"TextLabel", None))
    # retranslateUi


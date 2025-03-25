# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'updateDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QGridLayout,
    QHBoxLayout, QLabel, QPlainTextEdit, QProgressBar,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_FormUpdateDialog(object):
    def setupUi(self, FormUpdateDialog):
        FormUpdateDialog.setObjectName(u"FormUpdateDialog")
        FormUpdateDialog.resize(600, 448)
        self.verticalLayout = QVBoxLayout(FormUpdateDialog)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.widgetUpdate = QWidget(FormUpdateDialog)
        self.widgetUpdate.setObjectName(u"widgetUpdate")
        self.widgetUpdate.setProperty(u"active", True)
        self.verticalLayout_2 = QVBoxLayout(self.widgetUpdate)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.dialogTitlebar = QWidget(self.widgetUpdate)
        self.dialogTitlebar.setObjectName(u"dialogTitlebar")
        self.horizontalLayout = QHBoxLayout(self.dialogTitlebar)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 1, 1, 0)
        self.labelTitle = QLabel(self.dialogTitlebar)
        self.labelTitle.setObjectName(u"labelTitle")
        self.labelTitle.setIndent(6)

        self.horizontalLayout.addWidget(self.labelTitle)

        self.horizontalSpacer_4 = QSpacerItem(260, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_4)

        self.buttonClose = QPushButton(self.dialogTitlebar)
        self.buttonClose.setObjectName(u"buttonClose")
        self.buttonClose.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.buttonClose)


        self.verticalLayout_2.addWidget(self.dialogTitlebar)

        self.widgetUpdateBg = QWidget(self.widgetUpdate)
        self.widgetUpdateBg.setObjectName(u"widgetUpdateBg")
        self.gridLayout = QGridLayout(self.widgetUpdateBg)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setVerticalSpacing(15)
        self.gridLayout.setContentsMargins(30, 30, 30, 30)
        self.progressBarUpdate = QProgressBar(self.widgetUpdateBg)
        self.progressBarUpdate.setObjectName(u"progressBarUpdate")
        self.progressBarUpdate.setMinimumSize(QSize(0, 40))
        self.progressBarUpdate.setValue(0)
        self.progressBarUpdate.setTextVisible(False)

        self.gridLayout.addWidget(self.progressBarUpdate, 2, 0, 1, 2)

        self.labelMessage = QLabel(self.widgetUpdateBg)
        self.labelMessage.setObjectName(u"labelMessage")

        self.gridLayout.addWidget(self.labelMessage, 1, 0, 1, 2)

        self.plainTextEditDetail = QPlainTextEdit(self.widgetUpdateBg)
        self.plainTextEditDetail.setObjectName(u"plainTextEditDetail")
        self.plainTextEditDetail.setMinimumSize(QSize(0, 250))
        self.plainTextEditDetail.setFrameShape(QFrame.NoFrame)
        self.plainTextEditDetail.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.plainTextEditDetail.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.plainTextEditDetail.setUndoRedoEnabled(False)
        self.plainTextEditDetail.setReadOnly(True)

        self.gridLayout.addWidget(self.plainTextEditDetail, 0, 0, 1, 1)


        self.verticalLayout_2.addWidget(self.widgetUpdateBg)


        self.verticalLayout.addWidget(self.widgetUpdate)


        self.retranslateUi(FormUpdateDialog)
        self.buttonClose.clicked.connect(FormUpdateDialog.reject)

        QMetaObject.connectSlotsByName(FormUpdateDialog)
    # setupUi

    def retranslateUi(self, FormUpdateDialog):
        FormUpdateDialog.setWindowTitle(QCoreApplication.translate("FormUpdateDialog", u"Update", None))
        self.labelTitle.setText(QCoreApplication.translate("FormUpdateDialog", u"Update", None))
        self.buttonClose.setText("")
        self.labelMessage.setText("")
    # retranslateUi


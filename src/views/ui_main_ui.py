# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_main.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QGroupBox, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QProgressBar, QPushButton,
    QSizePolicy, QStatusBar, QTableWidget, QTableWidgetItem,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1390, 920)
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionParamter = QAction(MainWindow)
        self.actionParamter.setObjectName(u"actionParamter")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.PBar_Items = QProgressBar(self.centralwidget)
        self.PBar_Items.setObjectName(u"PBar_Items")
        self.PBar_Items.setGeometry(QRect(300, 840, 731, 31))
        self.PBar_Items.setValue(0)
        self.Gbox_TX = QGroupBox(self.centralwidget)
        self.Gbox_TX.setObjectName(u"Gbox_TX")
        self.Gbox_TX.setGeometry(QRect(1050, 140, 331, 191))
        font = QFont()
        font.setFamilies([u"Open Sans"])
        font.setPointSize(14)
        font.setBold(True)
        self.Gbox_TX.setFont(font)
        self.label = QLabel(self.Gbox_TX)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 90, 81, 31))
        self.label.setFont(font)
        self.label_2 = QLabel(self.Gbox_TX)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(10, 60, 51, 31))
        self.label_2.setFont(font)
        self.label_3 = QLabel(self.Gbox_TX)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 150, 81, 31))
        self.label_3.setFont(font)
        self.label_4 = QLabel(self.Gbox_TX)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 120, 81, 31))
        self.label_4.setFont(font)
        self.Lb_T_SN = QLabel(self.Gbox_TX)
        self.Lb_T_SN.setObjectName(u"Lb_T_SN")
        self.Lb_T_SN.setGeometry(QRect(100, 60, 221, 31))
        font1 = QFont()
        font1.setFamilies([u"\u5fae\u8edf\u6b63\u9ed1\u9ad4"])
        font1.setPointSize(12)
        font1.setBold(False)
        self.Lb_T_SN.setFont(font1)
        self.Lb_T_SN.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.Lb_T_MAC1 = QLabel(self.Gbox_TX)
        self.Lb_T_MAC1.setObjectName(u"Lb_T_MAC1")
        self.Lb_T_MAC1.setGeometry(QRect(100, 90, 221, 31))
        self.Lb_T_MAC1.setFont(font1)
        self.Lb_T_MAC1.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.Lb_T_MAC2 = QLabel(self.Gbox_TX)
        self.Lb_T_MAC2.setObjectName(u"Lb_T_MAC2")
        self.Lb_T_MAC2.setGeometry(QRect(100, 120, 221, 31))
        self.Lb_T_MAC2.setFont(font1)
        self.Lb_T_MAC2.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.Lb_T_Version = QLabel(self.Gbox_TX)
        self.Lb_T_Version.setObjectName(u"Lb_T_Version")
        self.Lb_T_Version.setGeometry(QRect(100, 150, 131, 31))
        self.Lb_T_Version.setFont(font1)
        self.Lb_T_Version.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.Lb_T_Version.setScaledContents(False)
        self.Lb_T_Version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_14 = QLabel(self.Gbox_TX)
        self.label_14.setObjectName(u"label_14")
        self.label_14.setGeometry(QRect(10, 30, 51, 31))
        self.label_14.setFont(font)
        self.Lb_T_MO = QLabel(self.Gbox_TX)
        self.Lb_T_MO.setObjectName(u"Lb_T_MO")
        self.Lb_T_MO.setGeometry(QRect(100, 30, 221, 31))
        self.Lb_T_MO.setFont(font1)
        self.Lb_T_MO.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.Gbox_RX = QGroupBox(self.centralwidget)
        self.Gbox_RX.setObjectName(u"Gbox_RX")
        self.Gbox_RX.setGeometry(QRect(1050, 340, 331, 191))
        self.Gbox_RX.setFont(font)
        self.Gbox_RX.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.label_9 = QLabel(self.Gbox_RX)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setGeometry(QRect(10, 90, 81, 31))
        self.label_9.setFont(font)
        self.label_10 = QLabel(self.Gbox_RX)
        self.label_10.setObjectName(u"label_10")
        self.label_10.setGeometry(QRect(10, 60, 51, 31))
        self.label_10.setFont(font)
        self.label_11 = QLabel(self.Gbox_RX)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setGeometry(QRect(10, 150, 81, 31))
        self.label_11.setFont(font)
        self.label_12 = QLabel(self.Gbox_RX)
        self.label_12.setObjectName(u"label_12")
        self.label_12.setGeometry(QRect(10, 120, 81, 31))
        self.label_12.setFont(font)
        self.Lb_R_SN = QLabel(self.Gbox_RX)
        self.Lb_R_SN.setObjectName(u"Lb_R_SN")
        self.Lb_R_SN.setGeometry(QRect(100, 60, 221, 31))
        self.Lb_R_SN.setFont(font1)
        self.Lb_R_SN.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.Lb_R_MAC1 = QLabel(self.Gbox_RX)
        self.Lb_R_MAC1.setObjectName(u"Lb_R_MAC1")
        self.Lb_R_MAC1.setGeometry(QRect(100, 90, 221, 31))
        self.Lb_R_MAC1.setFont(font1)
        self.Lb_R_MAC1.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.Lb_R_MAC2 = QLabel(self.Gbox_RX)
        self.Lb_R_MAC2.setObjectName(u"Lb_R_MAC2")
        self.Lb_R_MAC2.setGeometry(QRect(100, 120, 221, 31))
        self.Lb_R_MAC2.setFont(font1)
        self.Lb_R_MAC2.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.Lb_R_Version = QLabel(self.Gbox_RX)
        self.Lb_R_Version.setObjectName(u"Lb_R_Version")
        self.Lb_R_Version.setGeometry(QRect(100, 150, 131, 31))
        self.Lb_R_Version.setFont(font1)
        self.Lb_R_Version.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.Lb_R_Version.setScaledContents(False)
        self.Lb_R_Version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Lb_R_MO = QLabel(self.Gbox_RX)
        self.Lb_R_MO.setObjectName(u"Lb_R_MO")
        self.Lb_R_MO.setGeometry(QRect(100, 30, 221, 31))
        self.Lb_R_MO.setFont(font1)
        self.Lb_R_MO.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.label_15 = QLabel(self.Gbox_RX)
        self.label_15.setObjectName(u"label_15")
        self.label_15.setGeometry(QRect(10, 30, 51, 31))
        self.label_15.setFont(font)
        self.Lb_DUT = QLabel(self.centralwidget)
        self.Lb_DUT.setObjectName(u"Lb_DUT")
        self.Lb_DUT.setGeometry(QRect(630, 150, 401, 61))
        font2 = QFont()
        font2.setPointSize(24)
        font2.setBold(True)
        self.Lb_DUT.setFont(font2)
        self.Lb_DUT.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)
        self.Table_TestResult = QTableWidget(self.centralwidget)
        if (self.Table_TestResult.columnCount() < 6):
            self.Table_TestResult.setColumnCount(6)
        __qtablewidgetitem = QTableWidgetItem()
        self.Table_TestResult.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.Table_TestResult.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        __qtablewidgetitem2 = QTableWidgetItem()
        self.Table_TestResult.setHorizontalHeaderItem(2, __qtablewidgetitem2)
        __qtablewidgetitem3 = QTableWidgetItem()
        self.Table_TestResult.setHorizontalHeaderItem(3, __qtablewidgetitem3)
        __qtablewidgetitem4 = QTableWidgetItem()
        self.Table_TestResult.setHorizontalHeaderItem(4, __qtablewidgetitem4)
        __qtablewidgetitem5 = QTableWidgetItem()
        self.Table_TestResult.setHorizontalHeaderItem(5, __qtablewidgetitem5)
        self.Table_TestResult.setObjectName(u"Table_TestResult")
        self.Table_TestResult.setGeometry(QRect(300, 210, 731, 621))
        self.GBox_PROGRESS = QGroupBox(self.centralwidget)
        self.GBox_PROGRESS.setObjectName(u"GBox_PROGRESS")
        self.GBox_PROGRESS.setGeometry(QRect(1050, 540, 331, 331))
        font3 = QFont()
        font3.setFamilies([u"Open Sans"])
        font3.setPointSize(16)
        font3.setBold(True)
        self.GBox_PROGRESS.setFont(font3)
        self.PBar_CurrentItem = QProgressBar(self.GBox_PROGRESS)
        self.PBar_CurrentItem.setObjectName(u"PBar_CurrentItem")
        self.PBar_CurrentItem.setGeometry(QRect(10, 100, 311, 31))
        self.PBar_CurrentItem.setValue(0)
        self.label_5 = QLabel(self.GBox_PROGRESS)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(10, 30, 51, 31))
        self.label_5.setFont(font3)
        self.label_13 = QLabel(self.GBox_PROGRESS)
        self.label_13.setObjectName(u"label_13")
        self.label_13.setGeometry(QRect(10, 30, 171, 31))
        font4 = QFont()
        font4.setFamilies([u"\u5fae\u8edf\u6b63\u9ed1\u9ad4"])
        font4.setPointSize(14)
        font4.setBold(False)
        self.label_13.setFont(font4)
        self.Btn_Start = QPushButton(self.GBox_PROGRESS)
        self.Btn_Start.setObjectName(u"Btn_Start")
        self.Btn_Start.setGeometry(QRect(10, 180, 311, 141))
        font5 = QFont()
        font5.setFamilies([u"Open Sans"])
        font5.setPointSize(24)
        font5.setBold(True)
        self.Btn_Start.setFont(font5)
        self.Btn_Start.setStyleSheet(u"")
        self.Lb_CountPass = QLabel(self.GBox_PROGRESS)
        self.Lb_CountPass.setObjectName(u"Lb_CountPass")
        self.Lb_CountPass.setGeometry(QRect(10, 140, 51, 31))
        self.Lb_CountPass.setFont(font4)
        self.Lb_CountFail = QLabel(self.GBox_PROGRESS)
        self.Lb_CountFail.setObjectName(u"Lb_CountFail")
        self.Lb_CountFail.setGeometry(QRect(170, 140, 51, 31))
        self.Lb_CountFail.setFont(font4)
        self.Tb_CountPass = QLineEdit(self.GBox_PROGRESS)
        self.Tb_CountPass.setObjectName(u"Tb_CountPass")
        self.Tb_CountPass.setGeometry(QRect(70, 140, 91, 31))
        self.Tb_CountPass.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Tb_CountPass.setReadOnly(True)
        self.Tb_CountFail = QLineEdit(self.GBox_PROGRESS)
        self.Tb_CountFail.setObjectName(u"Tb_CountFail")
        self.Tb_CountFail.setGeometry(QRect(230, 140, 91, 31))
        self.Tb_CountFail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Tb_CountFail.setReadOnly(True)
        self.Tb_CurrentItem = QLineEdit(self.GBox_PROGRESS)
        self.Tb_CurrentItem.setObjectName(u"Tb_CurrentItem")
        self.Tb_CurrentItem.setGeometry(QRect(10, 60, 311, 31))
        self.Tb_CurrentItem.setReadOnly(True)
        self.Gbox_USER = QGroupBox(self.centralwidget)
        self.Gbox_USER.setObjectName(u"Gbox_USER")
        self.Gbox_USER.setGeometry(QRect(1050, 0, 331, 131))
        font6 = QFont()
        font6.setFamilies([u"\u5fae\u8edf\u6b63\u9ed1\u9ad4"])
        font6.setPointSize(14)
        font6.setBold(True)
        self.Gbox_USER.setFont(font6)
        self.label_6 = QLabel(self.Gbox_USER)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setGeometry(QRect(10, 60, 81, 31))
        self.label_6.setFont(font6)
        self.label_7 = QLabel(self.Gbox_USER)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(10, 30, 81, 31))
        self.label_7.setFont(font6)
        self.Lb_User = QLabel(self.Gbox_USER)
        self.Lb_User.setObjectName(u"Lb_User")
        self.Lb_User.setGeometry(QRect(100, 30, 141, 31))
        self.Lb_User.setFont(font4)
        self.Lb_User.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.Lb_Level = QLabel(self.Gbox_USER)
        self.Lb_Level.setObjectName(u"Lb_Level")
        self.Lb_Level.setGeometry(QRect(100, 60, 141, 31))
        self.Lb_Level.setFont(font4)
        self.Lb_Level.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.Lb_Mode = QLabel(self.Gbox_USER)
        self.Lb_Mode.setObjectName(u"Lb_Mode")
        self.Lb_Mode.setGeometry(QRect(10, 90, 61, 31))
        self.Lb_Mode.setFont(font)
        self.Lb_Mode.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.Tb_Mode = QLabel(self.Gbox_USER)
        self.Tb_Mode.setObjectName(u"Tb_Mode")
        self.Tb_Mode.setGeometry(QRect(100, 90, 141, 31))
        self.Tb_Mode.setFont(font4)
        self.Tb_Mode.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.Btn_ItemsCheckAll = QPushButton(self.centralwidget)
        self.Btn_ItemsCheckAll.setObjectName(u"Btn_ItemsCheckAll")
        self.Btn_ItemsCheckAll.setGeometry(QRect(10, 130, 121, 51))
        self.Btn_ItemsUncheckAll = QPushButton(self.centralwidget)
        self.Btn_ItemsUncheckAll.setObjectName(u"Btn_ItemsUncheckAll")
        self.Btn_ItemsUncheckAll.setGeometry(QRect(150, 130, 121, 51))
        self.Lb_TestItems = QLabel(self.centralwidget)
        self.Lb_TestItems.setObjectName(u"Lb_TestItems")
        self.Lb_TestItems.setGeometry(QRect(10, 180, 131, 31))
        self.Lb_TestItems.setFont(font6)
        self.Lb_TestResult = QLabel(self.centralwidget)
        self.Lb_TestResult.setObjectName(u"Lb_TestResult")
        self.Lb_TestResult.setGeometry(QRect(300, 180, 131, 31))
        self.Lb_TestResult.setFont(font6)
        self.GBox_BUTTON = QGroupBox(self.centralwidget)
        self.GBox_BUTTON.setObjectName(u"GBox_BUTTON")
        self.GBox_BUTTON.setGeometry(QRect(10, 0, 731, 101))
        self.Btn_Exit = QPushButton(self.GBox_BUTTON)
        self.Btn_Exit.setObjectName(u"Btn_Exit")
        self.Btn_Exit.setGeometry(QRect(610, 30, 81, 51))
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.SystemLogOut))
        self.Btn_Exit.setIcon(icon)
        self.Btn_OpenScript = QPushButton(self.GBox_BUTTON)
        self.Btn_OpenScript.setObjectName(u"Btn_OpenScript")
        self.Btn_OpenScript.setGeometry(QRect(250, 30, 81, 51))
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.FolderOpen))
        self.Btn_OpenScript.setIcon(icon1)
        self.Btn_About = QPushButton(self.GBox_BUTTON)
        self.Btn_About.setObjectName(u"Btn_About")
        self.Btn_About.setGeometry(QRect(490, 30, 81, 51))
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.HelpAbout))
        self.Btn_About.setIcon(icon2)
        self.Btn_ReloadScript = QPushButton(self.GBox_BUTTON)
        self.Btn_ReloadScript.setObjectName(u"Btn_ReloadScript")
        self.Btn_ReloadScript.setGeometry(QRect(370, 30, 81, 51))
        icon3 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.SyncSynchronizing))
        self.Btn_ReloadScript.setIcon(icon3)
        self.Lb_logo = QLabel(self.GBox_BUTTON)
        self.Lb_logo.setObjectName(u"Lb_logo")
        self.Lb_logo.setGeometry(QRect(10, 10, 221, 91))
        font7 = QFont()
        font7.setPointSize(21)
        self.Lb_logo.setFont(font7)
        self.Lb_logo.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.Lb_logo.setScaledContents(False)
        self.Lb_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.Table_TestItems = QTableWidget(self.centralwidget)
        self.Table_TestItems.setObjectName(u"Table_TestItems")
        self.Table_TestItems.setGeometry(QRect(10, 210, 271, 661))
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionParamter.setText(QCoreApplication.translate("MainWindow", u"Open Paramter", None))
        self.Gbox_TX.setTitle(QCoreApplication.translate("MainWindow", u"Transmitter", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"MAC-1", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"SN", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Version", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"MAC-2", None))
        self.Lb_T_SN.setText("")
        self.Lb_T_MAC1.setText("")
        self.Lb_T_MAC2.setText("")
        self.Lb_T_Version.setText("")
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"MO", None))
        self.Lb_T_MO.setText("")
        self.Gbox_RX.setTitle(QCoreApplication.translate("MainWindow", u"Receive", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"MAC-1", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"SN", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Version", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"MAC-2", None))
        self.Lb_R_SN.setText("")
        self.Lb_R_MAC1.setText("")
        self.Lb_R_MAC2.setText("")
        self.Lb_R_Version.setText("")
        self.Lb_R_MO.setText("")
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"MO", None))
        self.Lb_DUT.setText("")
        ___qtablewidgetitem = self.Table_TestResult.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"\u6e2c\u8a66\u9805\u76ee", None));
        ___qtablewidgetitem1 = self.Table_TestResult.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"\u55ae\u4f4d", None));
        ___qtablewidgetitem2 = self.Table_TestResult.horizontalHeaderItem(2)
        ___qtablewidgetitem2.setText(QCoreApplication.translate("MainWindow", u"\u4e0b\u9650\u503c", None));
        ___qtablewidgetitem3 = self.Table_TestResult.horizontalHeaderItem(3)
        ___qtablewidgetitem3.setText(QCoreApplication.translate("MainWindow", u"\u4e0a\u9650\u503c", None));
        ___qtablewidgetitem4 = self.Table_TestResult.horizontalHeaderItem(4)
        ___qtablewidgetitem4.setText(QCoreApplication.translate("MainWindow", u"\u6e2c\u8a66\u503c", None));
        ___qtablewidgetitem5 = self.Table_TestResult.horizontalHeaderItem(5)
        ___qtablewidgetitem5.setText(QCoreApplication.translate("MainWindow", u"\u6e2c\u8a66\u7d50\u679c", None));
        self.GBox_PROGRESS.setTitle(QCoreApplication.translate("MainWindow", u"Progress", None))
        self.PBar_CurrentItem.setFormat(QCoreApplication.translate("MainWindow", u"%p%", None))
        self.label_5.setText("")
        self.label_5.setProperty(u"type", QCoreApplication.translate("MainWindow", u"sTitle", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"\u76ee\u524d\u6e2c\u8a66\u7684\u9805\u76ee", None))
        self.label_13.setProperty(u"type", QCoreApplication.translate("MainWindow", u"sTitle", None))
        self.Btn_Start.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.Btn_Start.setProperty(u"type", QCoreApplication.translate("MainWindow", u"secondary", None))
        self.Lb_CountPass.setText(QCoreApplication.translate("MainWindow", u"\u901a\u904e", None))
        self.Lb_CountPass.setProperty(u"type", QCoreApplication.translate("MainWindow", u"sTitle", None))
        self.Lb_CountFail.setText(QCoreApplication.translate("MainWindow", u"\u932f\u8aa4", None))
        self.Lb_CountFail.setProperty(u"type", QCoreApplication.translate("MainWindow", u"sTitle", None))
        self.Tb_CountPass.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.Tb_CountFail.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.Gbox_USER.setTitle(QCoreApplication.translate("MainWindow", u"\u4f7f\u7528\u8005", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"\u7b49\u7d1a", None))
        self.label_6.setProperty(u"type", QCoreApplication.translate("MainWindow", u"sTitle", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"\u5e33\u865f", None))
        self.label_7.setProperty(u"type", QCoreApplication.translate("MainWindow", u"sTitle", None))
        self.Lb_User.setText(QCoreApplication.translate("MainWindow", u"TEST_1", None))
        self.Lb_Level.setText(QCoreApplication.translate("MainWindow", u"Administrator", None))
        self.Lb_Mode.setText(QCoreApplication.translate("MainWindow", u"MODE", None))
        self.Lb_Mode.setProperty(u"type", QCoreApplication.translate("MainWindow", u"sTitle", None))
        self.Tb_Mode.setText("")
        self.Btn_ItemsCheckAll.setText(QCoreApplication.translate("MainWindow", u"\u5168\u90e8\u9078\u53d6", None))
        self.Btn_ItemsCheckAll.setProperty(u"type", QCoreApplication.translate("MainWindow", u"primary", None))
        self.Btn_ItemsUncheckAll.setText(QCoreApplication.translate("MainWindow", u"\u5168\u90e8\u53d6\u6d88", None))
        self.Btn_ItemsUncheckAll.setProperty(u"type", QCoreApplication.translate("MainWindow", u"primary", None))
        self.Lb_TestItems.setText(QCoreApplication.translate("MainWindow", u"\u6e2c\u8a66\u6e05\u55ae", None))
        self.Lb_TestItems.setProperty(u"type", QCoreApplication.translate("MainWindow", u"sTitle", None))
        self.Lb_TestResult.setText(QCoreApplication.translate("MainWindow", u"\u6e2c\u8a66\u7d50\u679c", None))
        self.Lb_TestResult.setProperty(u"type", QCoreApplication.translate("MainWindow", u"sTitle", None))
        self.GBox_BUTTON.setTitle("")
        self.Btn_Exit.setText(QCoreApplication.translate("MainWindow", u"\u96e2\u958b", None))
        self.Btn_Exit.setProperty(u"type", QCoreApplication.translate("MainWindow", u"primary", None))
        self.Btn_OpenScript.setText(QCoreApplication.translate("MainWindow", u"\u958b\u555f\u8173\u672c", None))
        self.Btn_OpenScript.setProperty(u"type", QCoreApplication.translate("MainWindow", u"primary", None))
        self.Btn_About.setText(QCoreApplication.translate("MainWindow", u"\u95dc\u65bc", None))
        self.Btn_About.setProperty(u"type", QCoreApplication.translate("MainWindow", u"primary", None))
        self.Btn_ReloadScript.setText(QCoreApplication.translate("MainWindow", u"\u91cd\u65b0\u8f09\u5165", None))
        self.Btn_ReloadScript.setProperty(u"type", QCoreApplication.translate("MainWindow", u"primary", None))
        self.Lb_logo.setText(QCoreApplication.translate("MainWindow", u"logo container", None))
    # retranslateUi


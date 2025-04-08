#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt,QFile, QTextStream
from PySide6.QtWidgets import QDialog
from src.config import config
from src.utils.commonUtils import UiUpdater
from src.views.noticeDialog_ui import Ui_FormNoticeDialog

class NoticeDialog(QDialog, Ui_FormNoticeDialog):

    def __init__(self, title, message, *args, **kwargs):
        super(NoticeDialog, self).__init__(*args, **kwargs)

        self.setupUi(self)
        # 关闭后自动销毁
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        # 背景透明
        # self.setAttribute(Qt.WA_TranslucentBackground, True)
        # 无边框
        # self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        self._loadStylesheet(config.STYLE_FILE)

        self.setWindowTitle(title)
        self.plainTextEditDetail.appendPlainText(message)
        self.plainTextEditDetail.setReadOnly(True)
        self.pushButton.clicked.connect(self.close)

    def _loadStylesheet(self, filename):
        """
        從指定文件加載並應用 Qt 樣式表

        Args:
            filename (str): 樣式表文件的路徑
        """
        style_file = QFile(filename)
        if style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(style_file)
            self.setStyleSheet(stream.readAll())
            style_file.close()
        else:
            print(f"無法打開樣式表文件: {filename}")
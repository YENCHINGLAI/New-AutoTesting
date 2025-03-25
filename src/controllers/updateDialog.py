#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt,QFile, QTextStream
from PySide6.QtWidgets import QDialog
from src.config import config
from src.utils.commonUtils import UiUpdater
from src.views.updateDialog_ui import Ui_FormUpdateDialog

class UpdateDialog(Ui_FormUpdateDialog, QDialog):

    def __init__(self):
        super(UpdateDialog, self).__init__()

        self.setupUi(self)
        # 关闭后自动销毁
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        # 背景透明
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        # 无边框
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)

        self._loadStylesheet(config.STYLE_FILE)

        UiUpdater.updateTextChanged.connect(self.onUpdateTextChanged)
        UiUpdater.updateProgressChanged.connect(self.onUpdateProgressChanged)
        UiUpdater.updateFinished.connect(self.labelMessage.setText)

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

    def onUpdateTextChanged(self, ver1, ver2, text):
        self.labelMessage.setText(
            self.tr('Update Version {} to Version {}'.format(ver1, ver2)))
        self.plainTextEditDetail.setPlainText(text)

    def onUpdateProgressChanged(self, currentValue, minValue, maxValue):
        self.progressBarUpdate.setRange(minValue, maxValue)
        self.progressBarUpdate.setValue(currentValue)
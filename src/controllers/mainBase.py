from PySide6.QtCore import QFile, QTextStream, Qt
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QMainWindow, QHeaderView

import res.res_rc
from src.utils.commonUtils import UiUpdater
from src.config import config
from src.utils.log import Log

class MainBase(QMainWindow):
    def _initUi(self):
        """初始化UI元件""" 
        self.setupUi(self)

        # 設定Logo
        self._setLogo()

        # 設定MianWindow Icon
        self.setWindowIcon(QIcon(config.ICON_FILE))

        # 載入QSS
        self._loadStylesheet(config.STYLE_FILE)

        # 初始化表格設置
        self._initTables()

    def _setLogo(self):
        """設定主程式LOGO"""
        pixmap = QPixmap(config.LOGO_FILE)
        scaled_pixmap = pixmap.scaled(
            self.Lb_logo.size(), 
            Qt.AspectRatioMode.KeepAspectRatio,  # 保持圖片比例
            Qt.TransformationMode.SmoothTransformation  # 使用平滑轉換
        )
        self.Lb_logo.setPixmap(scaled_pixmap)

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

    def _initTables(self):
        """初始化表格相關設置"""
        try:
            # TestItems表格設置
            items_label=["選擇", "項目"]
            self.Table_TestItems.setColumnCount(len(items_label))
            self.Table_TestItems.setHorizontalHeaderLabels(items_label)
            if hasattr(self, 'Table_TestItems'):
                self.Table_TestItems.horizontalHeader().setStretchLastSection(True)
                self.Table_TestItems.setColumnWidth(0, 40)
                self.Table_TestItems.horizontalHeader().setSectionResizeMode(
                    0, QHeaderView.ResizeMode.Fixed)
            
            # TestResult表格設置        
            test_label=["測試項目", "單位", "下限值", "上限值", "測試值", "測試結果"]
            self.Table_TestResult.setColumnCount(len(test_label))
            self.Table_TestResult.setHorizontalHeaderLabels(test_label)
            if hasattr(self, 'Table_TestResult'):
                # 設置第一欄自動填滿剩餘空間
                self.Table_TestResult.horizontalHeader().setStretchLastSection(False)
                self.Table_TestResult.horizontalHeader().setSectionResizeMode(
                    0, QHeaderView.ResizeMode.Stretch)
                
                # 設置其他欄位固定寬度為100
                for col in range(1, self.Table_TestResult.columnCount()):
                    self.Table_TestResult.setColumnWidth(col, 80)
                    self.Table_TestResult.horizontalHeader().setSectionResizeMode(
                        col, QHeaderView.ResizeMode.Fixed)                  
        except Exception as e:
            print(f"初始化表格時發生錯誤: {str(e)}")
    
    def _initSignals(self):
        """連接所有信號槽"""    
        try:
            # 將按鈕信號綁定
            self.Btn_Start.clicked.connect(self.start_test)
            # self.Btn_About.clicked.connect(self.show_about)
            self.Btn_About.clicked.connect(self._initUpdate)
            self.Btn_ItemsCheckAll.clicked.connect(self.select_all_items)
            self.Btn_ItemsUncheckAll.clicked.connect(self.deselect_all_items)
            self.Btn_OpenScript.clicked.connect(self.load_script)
            self.Btn_ReloadScript.clicked.connect(self.reload_script)
            self.Btn_Exit.clicked.connect(self.close)    
            self.actionExit.triggered.connect(self.close)

            # 將UI信號綁定ui_updater
            UiUpdater.items_bar_updated.connect(self.update_items_bar)
            UiUpdater.max_items_bar_updated.connect(self.set_max_items_bar_maximum)
            UiUpdater.max_current_bar_updated.connect(self.set_max_current_bar_maximum)
            UiUpdater.current_bar_updated.connect(self.update_current_bar)
            UiUpdater.current_line_updated.connect(self.update_current_line)
            UiUpdater.items_table_init.connect(self.init_result_table)
            UiUpdater.items_table_updated.connect(self.update_result_table)
            UiUpdater.qbox_message.connect(self.show_message_box)
            UiUpdater.fail_count.connect(self.set_fail_count)
            UiUpdater.pass_count.connect(self.set_pass_count)

            UiUpdater.updateDialogShowed.connect(self._initUpdate)
        except Exception as e:
            Log.error(f"連接信號槽時發生錯誤: {str(e)}")
    
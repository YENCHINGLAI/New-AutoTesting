from PySide6.QtCore import QFile, QTextStream, Qt
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import QMainWindow, QHeaderView

from src.views.ui_main_ui import Ui_MainWindow
from src.utils.commonUtils import UiUpdater
from src.utils.log import Log
from src.config import config
from res import res_rc

class MainBase(QMainWindow, Ui_MainWindow):
    def _initUi(self):
        """初始化UI元件""" 
        # 載入Ui
        self.setupUi(self)

        # 載入QSS
        self._loadStylesheet(config.STYLE_FILE)

        # 設定Logo
        self._setLogo()

        # 初始化表格設置
        self._initTables()

        # 設定視窗標題     
        self.setWindowTitle("Auto Testing System")
        # self.setWindowTitle("自動測試系統")

        # 設置最小視窗大小
        self.setMinimumSize(1390, 920)
        
        # 最大化
        self.showMaximized()

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

    def _setLogo(self):
        """設定主程式內及視窗LOGO"""
        pixmap = QPixmap(config.LOGO_FILE)
        scaled_pixmap = pixmap.scaled(
            self.Lb_logo.size(), 
            Qt.AspectRatioMode.KeepAspectRatio,  # 保持圖片比例
            Qt.TransformationMode.SmoothTransformation  # 使用平滑轉換
        )
        self.Lb_logo.setPixmap(scaled_pixmap)

        self.Lb_logo

        # 設定MianWindow Icon
        self.setWindowIcon(QIcon(config.ICON_FILE))

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
            self.Btn_OpenScript.clicked.connect(self._load_script)
            self.Btn_ReloadScript.clicked.connect(self._reload_script)
            self.Btn_Exit.clicked.connect(self.close)    
            self.actionExit.triggered.connect(self.close)

            # 將UI信號綁定ui_updater
            UiUpdater.startBtnChanged.connect(self.setStartBtnText)
            UiUpdater.scriptProgressChanged.connect(self.update_script_progress)
            UiUpdater.itemProgressChanged.connect(self.update_item_progress)
            UiUpdater.currentItemChanged.connect(self.update_current_line)
            UiUpdater.itemsTableInit.connect(self.init_result_table)
            UiUpdater.itemsTableChanged.connect(self.update_result_table)
            UiUpdater.messageBoxDialog.connect(self.show_message_box)
            UiUpdater.failCountChanged.connect(self.set_fail_count)
            UiUpdater.passCountChanged.connect(self.set_pass_count)

            # Update視窗
            UiUpdater.updateDialogShowed.connect(self._initUpdate)
        except Exception as e:
            Log.error(f"連接信號槽時發生錯誤: {str(e)}")

    def resizeEvent(self, event):
        """處理窗口大小改變事件"""
        super().resizeEvent(event)
        self._updateLayout()      
    
    def changeEvent(self, event):
        """處理窗口狀態改變事件"""
        super().changeEvent(event)
        if event.type() == event.Type.WindowStateChange:
            if self.windowState() == Qt.WindowState.WindowNoState:
                self._updateLayout()
            elif self.windowState() == Qt.WindowState.WindowMaximized:
                self._updateLayout()
      
    def keyPressEvent(self, event):
        """處理按鍵事件，按ESC鍵可以退出全螢幕模式"""
        if event.key() == Qt.Key.Key_Escape and (self.isMaximized() or self.isFullScreen()):
            self.showNormal()
        else:
            super().keyPressEvent(event)

    def _updateLayout(self):
        """更新控件位置"""
        # 獲取窗口尺寸
        window_width = self.width()
        window_height = self.height()

         # 如果有狀態欄，需要減去狀態欄高度
        if self.statusBar().isVisible():
            window_height -= self.statusBar().height()
        
        if self.menuBar().isVisible():
            window_height -= self.menuBar().height()

        # 基本參數
        margin = 10 # 邊距
        right_panel_width = self.Gbox_TX.width() # 右側面板寬度
        right_panel_height = self.Gbox_TX.height() # 右側面板高度
        bot_point_y = self.Table_TestItems.y() + self.Table_TestItems.height() # 表格底部Y軸位置  

        # 計算位置調整值
        right_panel_x = window_width - right_panel_width - margin # 右側面板X軸位置
        height_adjustment = window_height - margin - bot_point_y  # 設定右下Y軸位置

        #===================================================================================================
        # 右側物件位置處理
        #===================================================================================================   
        def adjust_x(widget, x):
            widget.setGeometry(x, widget.y() + height_adjustment, widget.width(), widget.height())   

        # Adjust right-side boxes (Gbox_TX, Gbox_RX, Gbox_USER)
        # adjust_x(self.Lb_Mode, right_panel_x)
        # adjust_x(self.Tb_Mode, right_panel_x + self.Lb_Mode.width() + margin)

        adjust_x(self.Gbox_TX, right_panel_x)
        adjust_x(self.Gbox_RX, right_panel_x)
        adjust_x(self.GBox_PROGRESS, right_panel_x)
        
        # 放在 GBox_BUTTON 右邊
        # self.Gbox_USER.setGeometry(self.GBox_BUTTON.x() + self.GBox_BUTTON.width() + 10, self.Gbox_USER.y(), 
        #                               self.Gbox_USER.width(), self.Gbox_USER.height())

        # User box 固定放在右上角
        self.Gbox_USER.setGeometry(right_panel_x, self.Gbox_USER.y(), 
                                      right_panel_width, self.Gbox_USER.height())
        
        #===================================================================================================
        # 左側物件位置處理
        #===================================================================================================       
        # 調整 'Items Table' 位置、大小
        self.Table_TestItems.setGeometry(
            self.Table_TestItems.x(),
            self.Table_TestItems.y(),
            self.Table_TestItems.width(),
            self.Table_TestItems.height() + height_adjustment
        )

        # 計算 'Result Table' 當前最大容許寬度
        table_width = right_panel_x - margin - self.Table_TestResult.x()

        # 調整 'Result Table' 位置、大小
        self.Table_TestResult.setGeometry(
            self.Table_TestResult.x(),  # Start after TestItems table + margin
            self.Table_TestResult.y(),
            table_width,
            self.Table_TestResult.height() + height_adjustment
        )

        # 將 '產品名稱' 對齊 'Result Table'
        dut_x = self.Table_TestResult.x() + table_width - self.Lb_DUT.width()
        self.Lb_DUT.setGeometry(
            dut_x,
            self.Lb_DUT.y(),
            self.Lb_DUT.width(),
            self.Lb_DUT.height()
        )
        
        # 將 '腳本ProgressBar' 對齊 'Result Table'
        self.PBar_Items.setGeometry(
            self.Table_TestResult.x(),
            self.PBar_Items.y() + height_adjustment,
            table_width,
            self.PBar_Items.height()
        )
    
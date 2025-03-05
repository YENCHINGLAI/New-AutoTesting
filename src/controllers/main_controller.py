#===================================================================================================
# Import the necessary modules
#===================================================================================================
import os
import sys
import PySide6
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QCheckBox, QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog)
from PySide6.QtCore import QFile, QTextStream, Qt
from PySide6.QtGui import QPixmap, QIcon, QBrush, QColor

import res.res_rc
import src.utils.setting as setting
from src.views.ui_main_ui import Ui_MainWindow
from src.utils.script import ScriptManager
from src.utils.perform import PerformManager
from src.utils.log import Log

#===================================================================================================
# Environment
#===================================================================================================
# 將項目根目錄添加到 Python 路徑
# ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
sys.path.append(ROOT_DIR)

# 獲取 PySide6 安裝路徑，並確保全部轉換為字符串
PYSIDE_PATH     = str(Path(PySide6.__file__).parent)  # 轉換為字符串
PLUGIN_PATH     = str(Path(PySide6.__file__).parent / "plugins")
PLATFORM_PATH   = str(Path(PySide6.__file__).parent / "plugins" / "platforms")

# 設定環境變數
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = PLATFORM_PATH
os.environ["QT_PLUGIN_PATH"] = PLUGIN_PATH

# 現在 PYSIDE_PATH 已經是字符串了
if PYSIDE_PATH not in os.environ["PATH"]:
    os.environ["PATH"] = PYSIDE_PATH + os.pathsep + os.environ["PATH"]

# 基礎路徑設置
# STYLE_FILE = os.path.join(ROOT_DIR, "res", "styles", "ui_main.qss")
# ICON_FILE  = os.path.join(ROOT_DIR, "res", "icons" , "cyp.ico")
# LOGO_FILE  = os.path.join(ROOT_DIR, "res", "images", "cyp.png")

# 改用rcc檔案
STYLE_FILE = ':styles/ui_main.qss'
ICON_FILE  = ':icons/cyp.ico'
LOGO_FILE  = ':images/cyp.png'
#===================================================================================================
# Window
#===================================================================================================
class MainWindow(QMainWindow, Ui_MainWindow):
    """主窗口類，處理UI界面和所有相關的操作邏輯"""
    loaded_script = None
    file_name = None

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        
        # 初始化 checkbox 狀態字典
        self.checkbox_states = {}

        # 初始化設定
        self.initialize_ui()

        # 連接所有信號槽
        self.connect_signals()

        # 設置最小視窗大小
        self.setMinimumSize(1390, 920)

        # 最後再最大化
        self.showMaximized()

    def initialize_ui(self):
        """初始化UI元件"""
        # 設定Logo
        pixmap = QPixmap(LOGO_FILE)
        scaled_pixmap = pixmap.scaled(
            self.Lb_logo.size(), 
            Qt.AspectRatioMode.KeepAspectRatio,  # 保持圖片比例
            Qt.TransformationMode.SmoothTransformation  # 使用平滑轉換
        )
        self.Lb_logo.setPixmap(scaled_pixmap)

        # 設定MianWindow Icon
        self.setWindowIcon(QIcon(ICON_FILE))

        # 載入QSS
        self.load_stylesheet(STYLE_FILE)

        # 初始化表格設置
        self.init_tables()
        
    def init_tables(self):
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

    def load_stylesheet(self, filename):
        """從指定文件加載並應用 Qt 樣式表。
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

    def update_layout(self):
        """更新布局"""
        # 獲取窗口尺寸
        window_width = self.width()
        window_height = self.height()

        def adjust_x(widget, x):
            widget.setGeometry(x, widget.y(), widget.width(), widget.height())
        
        def adjust_y(widget, y):
            widget.setGeometry(widget.x(), y, widget.width(), widget.height())
        
        def adjust_width(widget, width):
            widget.setGeometry(widget.x(), widget.y(), width, widget.height())
        
        def adjust_height(widget, height):
            widget.setGeometry(widget.x(), widget.y(), widget.width(), height)

         # 如果有狀態欄，需要減去狀態欄高度
        if self.statusBar().isVisible():
            window_height -= self.statusBar().height()
        
        if self.menuBar().isVisible():
            window_height -= self.menuBar().height()

        # 基本參數
        margin = 20 # 邊距
        right_panel_width = self.Gbox_USER.width() # 右側面板寬度
        right_panel_height = self.Gbox_USER.height() # 右側面板高度
        bot_point_y = self.Table_TestItems.y() + self.Table_TestItems.height() # 表格底部Y軸位置  

        # 計算位置調整值
        right_panel_x = window_width - right_panel_width - margin # 右側面板X軸位置
        height_adjustment = window_height - margin - bot_point_y # 高度調整值

        # Adjust right-side boxes (Gbox_TX, Gbox_RX, Gbox_USER)
        adjust_x(self.Lb_Mode, right_panel_x)
        adjust_x(self.Tb_Mode, right_panel_x + self.Lb_Mode.width() + margin)
        adjust_x(self.Gbox_USER, right_panel_x)
        
        self.Gbox_USER.setGeometry(right_panel_x, self.Gbox_USER.y(), 
                                      right_panel_width, right_panel_height)
        self.Gbox_TX.setGeometry(right_panel_x, self.Gbox_TX.y() + height_adjustment, 
                                    right_panel_width, right_panel_height)
        self.Gbox_RX.setGeometry(right_panel_x, self.Gbox_RX.y() + height_adjustment, 
                                    right_panel_width, right_panel_height)
        self.GBox_PROGRESS.setGeometry(right_panel_x, self.GBox_PROGRESS.y() + height_adjustment, 
                                          right_panel_width, self.GBox_PROGRESS.height())
        
        # Calculate the available width for 'Table_TestResult'
        table_width = right_panel_x - margin - self.Table_TestResult.x()

        # Adjust 'Table_TestResult' width
        self.Table_TestResult.setGeometry(
            self.Table_TestResult.x(),  # Start after TestItems table + margin
            self.Table_TestResult.y(),
            table_width,
            self.Table_TestResult.height() + height_adjustment
        )
        
        # Adjust progress bar width and position to match table
        self.PBar_Items.setGeometry(
            self.Table_TestResult.x(),
            self.PBar_Items.y() + height_adjustment,
            table_width,
            self.PBar_Items.height()
        )

        self.Table_TestItems.setGeometry(
            self.Table_TestItems.x(),  # Start after TestItems table + margin
            self.Table_TestItems.y(),
            self.Table_TestItems.width(),
            self.Table_TestItems.height() + height_adjustment
        )
        
        # Adjust DUT label to be centered above the table
        dut_x = self.Table_TestResult.x() + table_width - self.Lb_DUT.width()
        self.Lb_DUT.setGeometry(
            dut_x,
            self.Lb_DUT.y(),
            self.Lb_DUT.width(),
            self.Lb_DUT.height()
        )

    def resizeEvent(self, event):  # pylint: disable=invalid-name
        """處理窗口大小改變事件"""
        super().resizeEvent(event)
        self.update_layout()      
    
    def changeEvent(self, event):  # pylint: disable=invalid-name
        """處理窗口狀態改變事件"""
        super().changeEvent(event)
        if event.type() == event.Type.WindowStateChange:
            if self.windowState() == Qt.WindowState.WindowNoState:
                self.update_layout()
            elif self.windowState() == Qt.WindowState.WindowMaximized:
                self.update_layout()
      
    def keyPressEvent(self, event):
        """處理按鍵事件，按ESC鍵可以退出全螢幕模式"""
        if event.key() == Qt.Key.Key_Escape and (self.isMaximized() or self.isFullScreen()):
            self.showNormal()
        else:
            super().keyPressEvent(event)

    def create_centered_checkbox(self):     
        """創建居中的checkbox widget"""    
        checkbox = QCheckBox()
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        return widget
    
    def on_checkbox_changed(self, state, row):
        """checkbox事件"""
        is_checked = state == Qt.CheckState.Checked.value  # 獲取枚舉值
        self.checkbox_states[row] = is_checked
        print(f"Row {row} checkbox {'checked' if is_checked else 'unchecked'}")
        
        # 獲取該行的數據
        if state == Qt.CheckState.Checked:
            item = self.Table_TestItems.item(row, 1)
            if item:
                name = item.text()
                print(f"Selected: {name}")
#===================================================================================================
# Button function and signals
#===================================================================================================
    def connect_signals(self):
        """連接所有信號槽"""    
        try:
            self.Btn_About.clicked.connect(self.show_about)
            self.Btn_Start.clicked.connect(self.start_test)
            self.Btn_ItemsCheckAll.clicked.connect(self.select_all_items)
            self.Btn_ItemsUncheckAll.clicked.connect(self.deselect_all_items)
            self.Btn_OpenScript.clicked.connect(self.load_script)
            self.Btn_ReloadScript.clicked.connect(self.reload_script)
            self.Btn_Exit.clicked.connect(self.close)    
            self.actionExit.triggered.connect(self.close)
        except Exception as e:
            Log.error(f"連接信號槽時發生錯誤: {str(e)}")
    
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            '確認',
            '確定要關閉視窗嗎？',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def show_about(self):
        """關於視窗"""
        ver = '1.0.0000'
        user='TEST01'
        text = "<center>" \
           "<h1>Auto Testing</h1>" \
           "&#8291;" \
           "</center>" \
           f"<p>User {user}<br/>" \
           f"<p>Version {ver}<br/>" \
           "Copyright &copy; Cypress Technologies Inc.</p>"
        
        QMessageBox.about(self, "About Auto Testing", text)

    def start_test(self):
        """開始測試前的確認"""
        reply = QMessageBox.question(
            self,
            "確認開始測試",
            "是否開始執行測試？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 執行測試邏輯
            print("開始測試...")
            self.test_progress()
        else:
            print("取消測試")
        
    def stop_test(self):
        pass

    def select_all_items(self):
        """全選所有測試項目"""
        self.set_all_checkboxes(Qt.CheckState.Checked)

    def deselect_all_items(self):
        """取消全選測試項目"""
        self.set_all_checkboxes(Qt.CheckState.Unchecked)

    def set_all_checkboxes(self, state):
        """設置所有checkbox的狀態"""
        for row in range(self.Table_TestItems.rowCount()):
            widget = self.Table_TestItems.cellWidget(row, 0)
            if widget:
                checkbox = widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setCheckState(state)
#===================================================================================================
# Script
#===================================================================================================
    def read_script(self, file_name):
        script_manager = ScriptManager()

        if file_name:
            try:           
                loaded_script = script_manager.load_script(file_name)
                if not loaded_script:
                    QMessageBox.critical(self, "錯誤", f"載入錯誤: {file_name}")
                    return
                self.file_name = file_name
                self.loaded_script = loaded_script
                self.update_test_table(loaded_script)
                self.update_items_table(loaded_script)
                self.Lb_DUT.setText(loaded_script.product.model_name)
                self.Tb_Mode.setText(loaded_script.product.mode)

                Log.info(f'Load script successfully. {file_name}')
            except Exception as e:
                Log.error(f"連接信號槽時發生錯誤: {str(e)}")
                QMessageBox.critical(self, "錯誤", f"無法載入腳本: {str(e)}")
    
    def load_script(self):
        file_name, _ = QFileDialog.getOpenFileName(self, caption= "Open YAML File", dir= os.getcwd(), filter= "YAML Files (*.yaml *.yml)", options= QFileDialog.DontUseNativeDialog)
        if file_name:
            self.read_script(file_name)

    def reload_script(self):
        if self.file_name:
            self.read_script(self.file_name)
            Log.info(f'Reload script successfully.')

    def update_test_table(self, script):
        try:
            #if self.script_data and "Items" in script:
            set_table = self.Table_TestResult
            set_table.setRowCount(0)
            set_table.setRowCount(len(script.items))

            for index, item in enumerate(script.items):
                # 設置項目名稱 
                set_table.setItem(index, setting.TABLE_ENUM.TITLE.value, QTableWidgetItem(item.title))
                set_table.setItem(index, setting.TABLE_ENUM.UNIT.value, QTableWidgetItem(item.unit))
                set_table.setItem(index, setting.TABLE_ENUM.MIN_VALID.value, QTableWidgetItem(str(item.valid_min)))
                set_table.setItem(index, setting.TABLE_ENUM.MAX_VALID.value, QTableWidgetItem(str(item.valid_max)))        
            # 不可編輯    
            set_table.setEditTriggers(QTableWidget.NoEditTriggers)
            
            Log.info(f'Test table updated successfully.')
            return True
        except Exception as e:          
            Log.error(f"更新Test表格發生錯誤: {str(e)}")
            QMessageBox.critical(self, "錯誤", f"無法更新Test表格: {str(e)}")
            return False
        
    def update_items_table(self, script):
        try:
            set_table = self.Table_TestItems
            set_table.setRowCount(len(script.items))
            set_table.setColumnCount(2)
            
            for index, item in enumerate(script.items):
                # 創建checkbox
                checkbox_widget = self.create_centered_checkbox()
                set_table.setCellWidget(index, 0, checkbox_widget)
                
                # 設置項目名稱
                set_table.setItem(index, 1, QTableWidgetItem(item.title))
                
                # 連接checkbox信號
                checkbox = checkbox_widget.findChild(QCheckBox)
                if checkbox:  # 確保找到 checkbox
                    checkbox.stateChanged.connect(
                        lambda state, row=index: self.on_checkbox_changed(state, row))

            set_table.setEditTriggers(QTableWidget.NoEditTriggers)
            Log.info(f'Items table updated successfully.')
            return True
        except Exception as e:
            Log.error(f"更新Items表格發生錯誤: {str(e)}")
            QMessageBox.critical(self, "錯誤", f"無法更新Items表格: {str(e)}")
            return False
#===================================================================================================
# Perform
#===================================================================================================
    def test_progress(self):
        if not self.loaded_script:
            return None

        self.perform_manager = PerformManager()
        self.perform_manager.items_bar_updated.connect(self.update_items_bar)
        self.perform_manager.max_items_bar_updated.connect(self.set_max_items_bar_maximum)
        self.perform_manager.current_bar_updated.connect(self.update_current_bar)
        self.perform_manager.max_current_bar_updated.connect(self.set_max_current_bar_maximum)
        self.perform_manager.current_line_updated.connect(self.update_current_line)
        self.perform_manager.items_table_init.connect(self.init_result_table)
        self.perform_manager.items_table_updated.connect(self.update_result_table)
        self.perform_manager.qbox_message.connect(self.show_message_box)

        self.perform_manager.start_execution(self.loaded_script)

    def show_message_box(self, title, message):
        """Slot 方法，顯示Msg Box。"""
        QMessageBox.information(self, title, message)

    def update_items_bar(self, progress_percentage):
        """Slot 方法，更新 ProgressBar 值。"""
        self.PBar_Items.setValue(progress_percentage) # 設定 bar value 值

    def set_max_items_bar_maximum(self, max_value):
        """Slot 方法，設定 ProgressBar 的 maximum 值。"""
        self.PBar_Items.setMaximum(max_value) # 設定 maximum 值

    def update_current_bar(self, progress_percentage):
        """Slot 方法，更新 ProgressBar 值。"""
        self.PBar_CurrentItem.setValue(progress_percentage) # 設定 bar value 值

    def set_max_current_bar_maximum(self, max_value):
        """Slot 方法，設定 ProgressBar 的 maximum 值。"""
        self.PBar_CurrentItem.setMaximum(max_value) # 設定 maximum 值

    def update_current_line(self, current_item):
        """Slot 方法，更新 當下執行的Line"""
        self.Tb_CurrentItem.setText(current_item) # 設定 bar value 值

    def init_result_table(self):
        """Slot 方法，初始化 result table 狀態。"""
        table = self.Table_TestResult
        for row_index in range(table.rowCount()):
            for col in range(table.columnCount()):
                item = table.item(row_index, col)
                if not item:
                    item = QTableWidgetItem()
                    table.setItem(row_index, col, item)
                item.setBackground(QBrush(QColor(255, 255, 255)))
                if col == setting.TABLE_ENUM.VALUE.value or col == setting.TABLE_ENUM.RESULT.value:
                    item.setText('')

    def update_result_table(self, row_index, value, result):
        """Slot 方法，更新 result table 狀態。"""
        table = self.Table_TestResult
        
        if row_index >= 0 and row_index<table.rowCount():
            if result:
                background_color = QColor(77, 255, 77) # 綠色
            else:
                background_color = QColor(255, 77, 77) # 紅色

            for col in range(table.columnCount()):
                item = table.item(row_index, col)
                if not item:
                    item = QTableWidgetItem()
                    table.setItem(row_index, col, item)
                item.setBackground(QBrush(background_color))

            # 寫入測試值
            table.item(row_index, 4).setText(str(value))
            table.item(row_index, 5).setText(str(result))

    def update_current_label_table(self, current_item):
        """Slot 方法，設定 current label 的顯示。"""
        self.Tb_CurrentItem.setText(current_item)
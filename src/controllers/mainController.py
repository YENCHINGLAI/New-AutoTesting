#===================================================================================================
# Import the necessary modules
#===================================================================================================
import os
import sys
from pathlib import Path

import PySide6
import PySide6.QtCore
from PySide6.QtWidgets import (
    QCheckBox, QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QMessageBox, QFileDialog
    )
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor

from src.views.ui_main_ui import Ui_MainWindow
from src.controllers.mainBase import MainBase
from src.config import setting, config
from src.utils.application import QSingleApplication
from src.utils.script import ScriptManager
from src.utils.perform import PerformManager
from src.utils.report import TestReport
from src.utils.log import Log

from src.controllers.updateDialog import UpdateDialog

#===================================================================================================
# Environment
#===================================================================================================
# 將項目根目錄添加到 Python 路徑
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

#===================================================================================================
# Window
#===================================================================================================
class MainController(MainBase, Ui_MainWindow):
    """主窗口類，處理UI界面和所有相關的操作邏輯"""
    loaded_script = None
    file_name = None

    def __init__(self):
        super(MainController, self).__init__()

        # 初始化 checkbox 狀態字典
        self.checkbox_states = {}
        self.checkboxes = [] # 保存所有checkbox

        # 初始化
        self._initUi()
        self._initSignals()

        # 設置最小視窗大小
        self.setMinimumSize(1390, 920)

        # 最後再最大化
        self.showMaximized()

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

        def adjust_x(widget, x):
            widget.setGeometry(x, widget.y(), widget.width(), widget.height())

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

    def create_centered_checkbox(self):     
        """創建居中的checkbox widget"""    
        checkbox = QCheckBox()
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        return widget, checkbox
    
    def on_checkbox_changed(self, state, row):
        """checkbox事件"""
        is_checked = state == Qt.CheckState.Checked.value  # 獲取枚舉值
        self.checkbox_states[row] = is_checked
        Log.debug(f"Row {row} checkbox {'checked' if is_checked else 'unchecked'}")
        
        # 獲取該行的數據
        if state == Qt.CheckState.Checked.value:
            item = self.Table_TestItems.item(row, 1)
            if item:
                name = item.text()
                print(f"Selected: {name}")
    
    def collect_selected_items(self):
        """收集所有選中的測試項目索引"""
        selected_item_indices = []
        for row, checkbox in enumerate(self.checkboxes):
            if checkbox.isChecked():
                selected_item_indices.append(row) # 直接 append 行索引 row
        return selected_item_indices
    
#===================================================================================================
# Button function and signals
#===================================================================================================
    def _initUpdate(self):
        self.udialog = UpdateDialog()
        self.udialog.show()

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
        user='TEST_01'
        text = "<center>" \
            "<h1>Auto Testing</h1>" \
            "&#8291;" \
            "</center>" \
            f"<p>User: {user}<br/>" \
            f"<p>Version: {config.REAL_VERSION}<br/>" \
            f"<p>Qt: {config.QT_VERSION}<br/>" \
            f"<p>Py: {config.PY_VERSION}<br/>" \
            f"<p>Update: {config.TIME_VERSION}<br/>" \
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
            self.Run_Script(self.collect_selected_items())
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
    def load_script(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            caption= "Open Test Script File",           # 對話框標題
            dir= os.getcwd(),                           # 主程式所在目錄
            filter= "YAML Files (*.yaml *.yml)",        # 篩選副檔名yaml, yml
            options= QFileDialog.DontUseNativeDialog    # 使用Qt的對話框 (使用win10內建，會超級慢)
            )
        if file_name:
            self.read_script(file_name)

    def read_script(self, file_name):
        script_manager = ScriptManager()

        if file_name:
            try:           
                loaded_script = script_manager.load_script(file_name)
                if not loaded_script:
                    self.show_message_box("錯誤", f"腳本載入錯誤: {file_name}")
                    return
                self.file_name = file_name
                self.loaded_script = loaded_script
                self.update_test_table(loaded_script)
                self.update_items_table(loaded_script)
                self.Lb_DUT.setText(loaded_script.product.model_name)
                self.Tb_Mode.setText(loaded_script.product.mode)
                Log.info(f'Load script successfully. {file_name}')
            except Exception as e:
                Log.error(f"載入腳本時發生錯誤: {str(e)}")
                self.show_message_box("錯誤", f"無法載入腳本: {str(e)}")

    def reload_script(self):
        if self.file_name:
            self.read_script(self.file_name)
            Log.info(f'Reload script successfully.')
    
    def update_test_table(self, script):
        try:
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
            self.show_message_box("錯誤", f"無法更新Test表格: {str(e)}")
            return False
        
    def update_items_table(self, script):
        try:
            self.checkboxes = [] # Clear the checkboxes list for reload

            set_table = self.Table_TestItems     
            set_table.setRowCount(0)
            set_table.setRowCount(len(script.items))    # 設置行數
            set_table.setColumnCount(2)                 # checkbox, item name
            
            for index, item in enumerate(script.items):
                # 創建checkbox
                checkbox_widget, checkbox = self.create_centered_checkbox() 
                set_table.setCellWidget(index, 0, checkbox_widget)
                
                # 設置項目名稱
                set_table.setItem(index, 1, QTableWidgetItem(item.title))
                
                # 連接checkbox信號
                self.checkboxes.append(checkbox)
                checkbox.stateChanged.connect(
                    lambda state, row=index: self.on_checkbox_changed(state, row))

            set_table.setEditTriggers(QTableWidget.NoEditTriggers)
            Log.info(f'Items table updated successfully.')
            return True
        except Exception as e:
            Log.error(f"更新Items表格發生錯誤: {str(e)}")
            self.show_message_box("錯誤", f"無法更新Items表格: {str(e)}")
            return False
#===================================================================================================
# Perform
#===================================================================================================
    def Run_Script(self, selected_item_indices=None):
        """執行測試"""
        if not self.loaded_script:
            self.show_message_box("錯誤", f"無腳本可執行")
            return

        report = TestReport(self.Lb_Runcard.text(), self.Lb_DUT.text(), 
                            self.Lb_T_MAC1.text(), self.Lb_T_SN.text(), 
                            self.loaded_script.version, self.Lb_User.text(), 
                            config.HOST_NAME, self.Tb_Mode.text()
                            )
        self.perform_manager = PerformManager(report, self.loaded_script, selected_item_indices)
        self.perform_manager.start_execution(self.Lb_T_MAC1.text(), self.Lb_T_SN.text())
    
    def show_message_box(self, title, message):
        """Slot 方法，顯示Msg Box。"""
        QMessageBox.information(self, title, message)

    def set_fail_count(self, valid_count):
        """Slot 方法，Pass計數更新"""
        self.Tb_CountFail.setText(f'{valid_count}')

    def set_pass_count(self, valid_count):
        """Slot 方法，Fail計數更新"""
        self.Tb_CountPass.setText(f'{valid_count}')

    def update_items_bar(self, progress_percentage):
        """Slot 方法，更新 '腳本測試進度Bar' 值"""
        self.PBar_Items.setValue(progress_percentage) # 設定 bar value 值

    def set_max_items_bar_maximum(self, max_value):
        """Slot 方法，設定 '腳本測試進度Bar ' Max值"""
        self.PBar_Items.setMaximum(max_value) # 設定 maximum 值

    def update_current_bar(self, progress_percentage):
        """Slot 方法，更新 '當前測試項目進度Bar' 值"""
        self.PBar_CurrentItem.setValue(progress_percentage) # 設定 bar value 值

    def set_max_current_bar_maximum(self, max_value):
        """Slot 方法，設定 '當前測試項目進度Bar' Max值"""
        self.PBar_CurrentItem.setMaximum(max_value) # 設定 maximum 值

    def update_current_line(self, current_item):
        """Slot 方法，更新 當前測試項目的Title"""
        self.Tb_CurrentItem.setText(current_item) # 設定 bar value 值
        self.Tb_CurrentItem.setReadOnly(True) # 設定為唯讀

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

        self.Tb_CountFail.setText('0')
        self.Tb_CountPass.setText('0')
        self.Tb_CurrentItem.setText('')

    def update_result_table(self, row_index, value, result):
        """Slot 方法，更新 result table 測試結果"""
        table = self.Table_TestResult
        
        if row_index >= 0 and row_index<table.rowCount():
            background_color = QColor(77, 255, 77) if result else QColor(255, 77, 77)       # 綠色: 通過, 紅色: 失敗

            for col in range(table.columnCount()):
                item = table.item(row_index, col)
                if not item:
                    item = QTableWidgetItem()
                    table.setItem(row_index, col, item)
                item.setBackground(QBrush(background_color))

            # 寫入測試值
            table.item(row_index, setting.TABLE_ENUM.VALUE.value).setText(str(value))
            table.item(row_index, setting.TABLE_ENUM.RESULT.value).setText(str("Pass" if result else "Fail"))

    def main():
        app = QSingleApplication('qtsingleapp-New AutoTesting',sys.argv)
        if app.isRunning():
            app.sendMessage("app is running")
            sys.exit(0)
        window = MainController()
        app.setActivationWindow(window)
        window.show()
        sys.exit(app.exec())
#===================================================================================================
# Import the necessary modules
#===================================================================================================
import os
import sys

from PySide6.QtWidgets import (
    QCheckBox, QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QMessageBox, QFileDialog
    )
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor

from src.config import setting, config
from src.utils.application import QSingleApplication
from src.utils.script import ScriptManager
from src.utils.perform import PerformManager
from src.utils.record import TestReport
from src.utils.log import Log
from src.controllers.mainBase import MainBase
from src.controllers.dialog.updateDialog import UpdateDialog
from src.controllers.dialog.noticeDialog import NoticeDialog
#===================================================================================================
# Window
#===================================================================================================
class MainController(MainBase):
    """主窗口類，處理UI界面和所有相關的操作邏輯"""
    _loaded_script = None
    _file_name = None

    def __init__(self):
        super(MainController, self).__init__()

        # 初始化 checkbox 狀態字典
        self.checkbox_states = {}
        self.checkboxes = [] # 保存所有checkbox
        self._perform_manager : PerformManager

        # 初始化
        self._initUi()
        self._initSignals()

    def _create_centered_checkbox(self):     
        """創建居中的checkbox widget"""    
        checkbox = QCheckBox()
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(checkbox)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        return widget, checkbox
    
    def _on_checkbox_changed(self, state, row):
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
    
    def _collect_selected_items(self):
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
        """檢查更新"""
        # self.udialog = UpdateDialog(self)
        # self.udialog.show()

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
        if self.getStartBtnText()=='Stop':
            reply = QMessageBox.question(
                self,
                "確認停止測試",
                "是否停止執行測試？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.setStartBtnText('Start')
                self._perform_manager.stop_execution()
        else:
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
                self.setStartBtnText('Stop')
                self.Run_Script()

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
    def _load_script(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, 
            caption= "Open Test Script File",           # 對話框標題
            dir= os.getcwd(),                           # 主程式所在目錄
            filter= "YAML Files (*.yaml *.yml)",        # 篩選副檔名yaml, yml
            options= QFileDialog.DontUseNativeDialog    # 使用Qt的對話框 (使用win10內建，會超級慢)
            )
        if file_name:
            self._read_script(file_name)

    def _read_script(self, file_name):
        script_manager = ScriptManager()

        if file_name:
            try:           
                loaded_script = script_manager.load_script(file_name)
                if not loaded_script:
                    self.show_message_box("錯誤", f"腳本載入錯誤: {file_name}")
                    return
                
                self._file_name = file_name
                self._loaded_script = loaded_script

                # Update Table
                self.update_test_table(loaded_script)
                self.update_items_table(loaded_script)
                
                # Update UI
                self.Lb_DUT.setText(loaded_script.name)                
                self.Tb_Mode.setText(loaded_script.pairing == 1 and "Pairing" or "Single")

                Log.info(f'Load script successfully. {file_name}')
            except Exception as e:
                Log.error(f"載入腳本時發生錯誤: {str(e)}")
                self.show_message_box("錯誤", f"無法載入腳本: {str(e)}")

    def _reload_script(self):
        if self._file_name:
            self._read_script(self._file_name)
            Log.info(f'Reload script successfully.')
    
    def update_test_table(self, script):
        try:
            set_table = self.Table_TestResult

            set_table.setRowCount(0)
            set_table.setRowCount(len(script.items))
            
            # 設置項目名稱 
            for index, item in enumerate(script.items):
                set_table.setItem(index, setting.TABLE_ENUM.TITLE.value, QTableWidgetItem(item.title))
                set_table.setItem(index, setting.TABLE_ENUM.UNIT.value,  QTableWidgetItem(item.unit))
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
                checkbox_widget, checkbox = self._create_centered_checkbox() 
                set_table.setCellWidget(index, 0, checkbox_widget)
                
                # 設置項目名稱
                set_table.setItem(index, 1, QTableWidgetItem(item.title))
                
                # 連接checkbox信號
                self.checkboxes.append(checkbox)
                checkbox.stateChanged.connect(
                    lambda state, row=index: self._on_checkbox_changed(state, row))

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
    def Run_Script(self):
        """執行測試"""
        if not self._loaded_script:
            self.show_message_box("錯誤", f"無腳本可執行")
            return

        product_info = {
            '$mo1': self.Lb_T_MO.text(),
            '$mo2': self.Lb_R_MO.text(),
            '$sn1': self.Lb_T_SN.text(),
            '$sn2': self.Lb_R_SN.text(),
            '$mac11': self.Lb_T_MAC1.text(),
            '$mac12': self.Lb_T_MAC2.text(),
            '$mac21': self.Lb_R_MAC1.text(),
            '$mac22': self.Lb_R_MAC2.text()
            }

        report = TestReport(
            self._loaded_script,
            product_info,
            self.Lb_User.text(),
            config.STATION_NAME,
            self.Tb_Mode.text()
            )
        
        self._perform_manager = PerformManager(report, self._loaded_script, self._collect_selected_items())
        self._perform_manager.start_execution(product_info)
    
    def getStartBtnText(self):
        return self.Btn_Start.text()

    def setStartBtnText(self,text):
        self.Btn_Start.setText(text)

    def update_item_progress(self, currentValue, maxValue):
        """Slot，更新 '當前測試項目進度Bar' 值"""
        self.PBar_CurrentItem.setMaximum(maxValue)
        self.PBar_CurrentItem.setValue(currentValue)
    
    def update_script_progress(self, currentValue, maxValue):
        """Slot，更新 '腳本測試進度Bar' 值"""
        self.PBar_Items.setMaximum(maxValue)
        self.PBar_Items.setValue(currentValue)

    def show_message_box(self, title, message):
        """Slot 方法，顯示Msg Box。"""
        # QMessageBox.information(self, title, message)
        NoticeDialog(title, message, self).exec_()

    def set_fail_count(self, valid_count):
        """
        Slot 方法
        
        Args:
            valid_count (int): Fail計數更新
        """
        self.Tb_CountFail.setText(f'{valid_count}')

    def set_pass_count(self, valid_count):
        """
        Slot 方法
        
        Args:
            valid_count (int): Pass計數更新
        """
        self.Tb_CountPass.setText(str(valid_count))

    def update_current_line(self, current_item):
        """
        Slot 方法

        Args:
            current_line (str): 目前執行item的title 
        """
        Log.debug(f"Current item: {current_item}")
        self.Tb_CurrentItem.setText(current_item) # 設定 bar value 值
        self.Tb_CurrentItem.setReadOnly(True) # 設定為唯讀

    def init_result_table(self):
        """Slot 方法，初始化 result table 狀態。"""
        Log.debug(f"Init result table.")

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
        Log.debug(f"Update table index: {row_index}, result: {value}, check_result: {result}")
        table = self.Table_TestResult
        
        if row_index >= 0 and row_index < table.rowCount():
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

#===================================================================================================
# Main
#===================================================================================================
    def main():
        app = QSingleApplication('QtSingleApp-AutoTesting', sys.argv)
        if app.isRunning():
            app.sendMessage("app is running")
            sys.exit(0)
        window = MainController()
        app.setActivationWindow(window)
        window.show()
        sys.exit(app.exec())
import os
import sys
from pathlib import Path
import PySide6

# 獲取 PySide6 安裝路徑，並確保全部轉換為字符串
PYSIDE_PATH = str(Path(PySide6.__file__).parent)  # 轉換為字符串
PLUGIN_PATH = str(Path(PySide6.__file__).parent / "plugins")
PLATFORM_PATH = str(Path(PySide6.__file__).parent / "plugins" / "platforms")

# 設定環境變數
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = PLATFORM_PATH
os.environ["QT_PLUGIN_PATH"] = PLUGIN_PATH

# 現在 PYSIDE_PATH 已經是字符串了
if PYSIDE_PATH not in os.environ["PATH"]:
    os.environ["PATH"] = PYSIDE_PATH + os.pathsep + os.environ["PATH"]
import yaml
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QTextEdit, QTreeWidget, QTreeWidgetItem,
                             QLabel, QLineEdit, QComboBox, QDialog, QDialogButtonBox,
                             QFormLayout, QMessageBox, QFileDialog, QTableWidget, QTableWidgetItem,
                             QHeaderView, QProgressBar)
from PySide6.QtCore import Qt, QThreadPool, QRunnable, Signal, QObject, QTimer
from PySide6.QtGui import QColor
import subprocess

class ScriptEditorDialog(QDialog):
    def __init__(self, script_data=None, parent=None):
        super().__init__(parent)
        self.script_data = script_data or {}
        self.setWindowTitle("腳本編輯器")
        self.setGeometry(100, 100, 600, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Script Info
        script_info_group = QWidget()
        script_info_layout = QFormLayout(script_info_group)
        self.version_edit = QLineEdit(self.script_data.get("Script Info", {}).get("Version", ""))
        self.release_edit = QLineEdit(self.script_data.get("Script Info", {}).get("Release", ""))
        script_info_layout.addRow("Version:", self.version_edit)
        script_info_layout.addRow("Release:", self.release_edit)
        layout.addWidget(script_info_group)

        # DUT Info
        dut_info_group = QWidget()
        dut_info_layout = QFormLayout(dut_info_group)
        self.model_name_edit = QLineEdit(self.script_data.get("DUT Info", {}).get("Model Name", ""))
        self.mac_count_edit = QLineEdit(str(self.script_data.get("DUT Info", {}).get("Mac 數量", "")))
        self.serial_number_edit = QLineEdit(self.script_data.get("DUT Info", {}).get("Serial Number", ""))
        self.version_dut_edit = QLineEdit(self.script_data.get("DUT Info", {}).get("Version", ""))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Transmitter", "Receiver", "Pairing"])
        self.mode_combo.setCurrentText(self.script_data.get("DUT Info", {}).get("Mode", "Transmitter"))
        self.other_message_edit = QTextEdit(self.script_data.get("DUT Info", {}).get("Other Message", ""))

        dut_info_layout.addRow("Model Name:", self.model_name_edit)
        dut_info_layout.addRow("Mac 數量:", self.mac_count_edit)
        dut_info_layout.addRow("Serial Number:", self.serial_number_edit)
        dut_info_layout.addRow("Version:", self.version_dut_edit)
        dut_info_layout.addRow("Mode:", self.mode_combo)
        dut_info_layout.addRow("Other Message:", self.other_message_edit)
        layout.addWidget(dut_info_group)

        # Items
        self.items_tree = QTreeWidget()
        self.items_tree.setHeaderLabels(["項目", "值"])
        self.populate_items_tree()
        layout.addWidget(self.items_tree)

        # Buttons
        button_layout = QHBoxLayout()
        add_item_button = QPushButton("添加項目")
        add_item_button.clicked.connect(self.add_item)
        edit_item_button = QPushButton("編輯項目")
        edit_item_button.clicked.connect(self.edit_item)
        remove_item_button = QPushButton("刪除項目")
        remove_item_button.clicked.connect(self.remove_item)
        button_layout.addWidget(add_item_button)
        button_layout.addWidget(edit_item_button)
        button_layout.addWidget(remove_item_button)
        layout.addLayout(button_layout)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def populate_items_tree(self):
        self.items_tree.clear()
        for item in self.script_data.get("Item", []):
            item_widget = QTreeWidgetItem(self.items_tree)
            item_widget.setText(0, item.get("Title Message", ""))
            item_widget.setText(1, "")
            for key, value in item.items():
                child = QTreeWidgetItem(item_widget)
                child.setText(0, key)
                child.setText(1, str(value))

    def add_item(self):
        dialog = ItemDialog(parent=self)
        if dialog.exec():
            new_item = dialog.get_item_data()
            self.script_data.setdefault("Item", []).append(new_item)
            self.populate_items_tree()

    def edit_item(self):
        selected = self.items_tree.currentItem()
        if selected and selected.parent() is None:
            index = self.items_tree.indexOfTopLevelItem(selected)
            item_data = self.script_data["Item"][index]
            dialog = ItemDialog(item_data, parent=self)
            if dialog.exec():
                self.script_data["Item"][index] = dialog.get_item_data()
                self.populate_items_tree()

    def remove_item(self):
        selected = self.items_tree.currentItem()
        if selected and selected.parent() is None:
            index = self.items_tree.indexOfTopLevelItem(selected)
            del self.script_data["Item"][index]
            self.populate_items_tree()

    def get_script_data(self):
        self.script_data.setdefault("Script Info", {})["Version"] = self.version_edit.text()
        self.script_data["Script Info"]["Release"] = self.release_edit.text()

        self.script_data.setdefault("DUT Info", {})["Model Name"] = self.model_name_edit.text()
        self.script_data["DUT Info"]["Mac 數量"] = int(self.mac_count_edit.text()) if self.mac_count_edit.text().isdigit() else 0
        self.script_data["DUT Info"]["Serial Number"] = self.serial_number_edit.text()
        self.script_data["DUT Info"]["Version"] = self.version_dut_edit.text()
        self.script_data["DUT Info"]["Mode"] = self.mode_combo.currentText()
        self.script_data["DUT Info"]["Other Message"] = self.other_message_edit.toPlainText()

        return self.script_data

class ItemDialog(QDialog):
    def __init__(self, item_data=None, parent=None):
        super().__init__(parent)
        self.item_data = item_data or {}
        self.setWindowTitle("項目編輯器")
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        
        self.title_edit = QLineEdit(self.item_data.get("Title Message", ""))
        self.retry_edit = QLineEdit(self.item_data.get("Retry Message", ""))
        self.value_range_edit = QLineEdit(self.item_data.get("Value range", ""))
        self.unit_edit = QLineEdit(self.item_data.get("unit", ""))
        self.delay_edit = QLineEdit(str(self.item_data.get("Delay", "")))
        self.execute_edit = QLineEdit(self.item_data.get("Execute", ""))

        layout.addRow("Title Message:", self.title_edit)
        layout.addRow("Retry Message:", self.retry_edit)
        layout.addRow("Value range:", self.value_range_edit)
        layout.addRow("unit:", self.unit_edit)
        layout.addRow("Delay:", self.delay_edit)
        layout.addRow("Execute:", self.execute_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_item_data(self):
        return {
            "Title Message": self.title_edit.text(),
            "Retry Message": self.retry_edit.text(),
            "Value range": self.value_range_edit.text(),
            "unit": self.unit_edit.text(),
            "Delay": int(self.delay_edit.text()) if self.delay_edit.text().isdigit() else 0,
            "Execute": self.execute_edit.text()
        }

class WorkerSignals(QObject):
    finished = Signal(int, str)
    error = Signal(int, str)

# 將工作丟進Qt thread pool
class CommandWorker(QRunnable):
    def __init__(self, index, command):
        super().__init__()
        self.index = index
        self.command = command
        self.signals = WorkerSignals()

    def run(self):
        try:
            print(self.command)
            result = subprocess.check_output(self.command, shell=True, text=True).strip()
            self.signals.finished.emit(self.index, result)
            print(result)
        except subprocess.CalledProcessError as e:
            self.signals.error.emit(self.index, str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YAML腳本編輯器")
        self.setGeometry(100, 100, 1200, 600)
        self.setup_ui()
        self.script_data = None
        self.threadpool = QThreadPool()
        self.current_item_index = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.execute_next_item)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        layout.addWidget(left_panel)

        button_layout = QHBoxLayout()
        new_button = QPushButton("新建腳本")
        new_button.clicked.connect(self.new_script)
        load_button = QPushButton("載入腳本")
        load_button.clicked.connect(self.load_script)
        save_button = QPushButton("保存腳本")
        save_button.clicked.connect(self.save_script)
        button_layout.addWidget(new_button)
        button_layout.addWidget(load_button)
        button_layout.addWidget(save_button)
        left_layout.addLayout(button_layout)

        self.script_text = QTextEdit()
        left_layout.addWidget(self.script_text)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        layout.addWidget(right_panel)

        self.item_table = QTableWidget()
        self.item_table.setColumnCount(3)
        self.item_table.setHorizontalHeaderLabels(["Title", "Expected", "Value"])
        self.item_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        right_layout.addWidget(self.item_table)

        self.progress_bar = QProgressBar()
        right_layout.addWidget(self.progress_bar)

        execute_button = QPushButton("執行所有項目")
        #execute_button.clicked.connect(self.execute_all_items)
        execute_button.clicked.connect(self.start_execution)
        right_layout.addWidget(execute_button)

    def new_script(self):
        dialog = ScriptEditorDialog(parent=self)
        if dialog.exec():
            self.script_data = dialog.get_script_data()
            yaml_str = yaml.dump(self.script_data, allow_unicode=True, sort_keys=False)
            self.script_text.setPlainText(yaml_str)
            self.update_item_table()

    def load_script(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open YAML File", "", "YAML Files (*.yaml *.yml)")
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as file:
                    self.script_data = yaml.safe_load(file)
                # dialog = ScriptEditorDialog(self.script_data, parent=self)
                # if dialog.exec():
                #     self.script_data = dialog.get_script_data()
                    yaml_str = yaml.dump(self.script_data, allow_unicode=True, sort_keys=False)
                    self.script_text.setPlainText(yaml_str)
                    self.update_item_table()
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"無法載入腳本: {str(e)}")

    def save_script(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save YAML File", "", "YAML Files (*.yaml *.yml)")
        if file_name:
            try:
                yaml_str = self.script_text.toPlainText()
                self.script_data = yaml.safe_load(yaml_str)
                with open(file_name, 'w', encoding='utf-8') as file:
                    yaml.dump(self.script_data, file, allow_unicode=True, sort_keys=False)
                QMessageBox.information(self, "成功", "腳本已保存")
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"無法保存腳本: {str(e)}")

    def update_item_table(self):
        self.item_table.setRowCount(0)
        if self.script_data and "Items" in self.script_data:
            self.item_table.setRowCount(len(self.script_data["Items"]))
            for index, item in enumerate(self.script_data["Items"]):
                #self.item_table.setItem(index, 0, QTableWidgetItem(str(index + 1)))
                self.item_table.setItem(index, 0, QTableWidgetItem(item.get("Title Message", "")))
                self.item_table.setItem(index, 1, QTableWidgetItem(item.get("Value range", "")))
                self.item_table.setItem(index, 2, QTableWidgetItem(""))  # 實際值初始為空

    # def execute_all_items(self):
    #     if not self.script_data or "Item" not in self.script_data:
    #         return

    #     self.progress_bar.setMaximum(len(self.script_data["Item"]))
    #     self.progress_bar.setValue(0)

    #     for index, item in enumerate(self.script_data["Item"]):
    #         execute_command = item.get("Execute", "")
    #         worker = CommandWorker(index, execute_command)
    #         worker.signals.finished.connect(self.handle_result)
    #         worker.signals.error.connect(self.handle_error)
    #         self.threadpool.start(worker)

    def start_execution(self):
        if not self.script_data or "Item" not in self.script_data:
            return

        self.progress_bar.setMaximum(len(self.script_data["Item"]))
        self.progress_bar.setValue(0)
        self.current_item_index = 0
        self.execute_next_item()

    def execute_next_item(self):
        if self.current_item_index < len(self.script_data["Item"]):
            item = self.script_data["Item"][self.current_item_index]
            execute_command = item.get("Execute", "")
            worker = CommandWorker(self.current_item_index, execute_command)
            worker.signals.finished.connect(self.handle_result)
            worker.signals.error.connect(self.handle_error)
            self.threadpool.start(worker)
        else:
            self.timer.stop()
            self.show_test_completed_message()

    def show_test_completed_message(self):
        QMessageBox.information(self, "測試完成", "所有項目已執行完畢，測試完成。")

    # 測試Pass處理
    def handle_result(self, index, result):
        self.item_table.setItem(index, 2, QTableWidgetItem(result))
        value_range = self.script_data["Item"][index].get("Value range", "")
        
        if self.check_value_range(result, value_range):
            for col in range(3):
                self.item_table.item(index, col).setBackground(QColor(144, 238, 144))  # Light green color
        else:
            for col in range(3):
                self.item_table.item(index, col).setBackground(QColor(255, 200, 200))  # Light red color
        
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        self.current_item_index += 1
        self.timer.singleShot(10, self.execute_next_item)  # 延迟100毫秒后执行下一个item
    
    # 測試Fail處理
    def handle_error(self, index, error):
        self.item_table.setItem(index, 3, QTableWidgetItem("執行錯誤"))
        for col in range(3):
            self.item_table.item(index, col).setBackground(QColor(255, 200, 200))  # Light red color
        
        self.progress_bar.setValue(self.progress_bar.value() + 1)
        self.current_item_index += 1
        self.timer.singleShot(100, self.execute_next_item)  # 延迟100毫秒后执行下一个item

    def check_value_range(self, result, value_range):
        try:
            if '-' in value_range:
                min_val, max_val = map(float, value_range.split('-'))
                return min_val <= float(result) <= max_val
            elif value_range:
                return float(result) == float(value_range)
        except ValueError:
            pass
        return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
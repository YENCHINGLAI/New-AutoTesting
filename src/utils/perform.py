import os
import sys
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QRunnable,Signal,QThreadPool,QTimer,QObject
import subprocess
from src.utils.script import Script
from src.utils.log import Log

class WorkerSignals:
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
            Log.info(f'Execute item, index:{self.index}, command:{self.command}')
            result = subprocess.check_output(self.command, shell=True, text=True).strip()
            self.signals.finished.emit(self.index, result)
        except subprocess.CalledProcessError as e:
            self.signals.error.emit(self.index, str(e))

class PerformManager(QObject):                   # 繼承 QObject，如果需要使用 signal/slot
    # Progress Bar 更新
    items_bar_updated = Signal(int)
    max_items_bar_updated = Signal(int)
    current_bar_updated = Signal(int)
    max_current_bar_updated = Signal(int)

    # Table 更新
    items_table_updated = Signal(int, str, bool)

    # 即時訊息更新
    current_label_updated = Signal(str)

    def __init__(self, main_controller=None):
        super().__init__()                      # 初始化 QObject (如果繼承自 QObject)
        self._is_running = False                # 標記測試是否正在執行，用於 stop_execution 功能
        self.main_controller = main_controller  # 保存 main_controller 的參考 (如果需要)
        self.script_data = None
        self.threadpool = QThreadPool()
        self.current_item_index = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.execute_next_item)

    def start_execution(self, script):
        Log.info('Start execution')
        if not script:
            Log.error('Script is None')
            return
        
        Log.info('Execution inited')
        self.script_data = script
        self._set_max_bar(self.max_items_bar_updated, len(self.script_data.items))      # 依照腳本item數量
        self._set_max_bar(self.max_current_bar_updated, 5)                              # 將單一測試項目拆分為五階段
        self._update_bar(self.items_bar_updated, 0)                                     # 初始化
        self._update_bar(self.current_bar_updated, 0)
        self.current_item_index = 0
        # self.execute_next_item()

    def execute_next_item(self):
        if self.current_item_index < len(self.script_data.items):
            item = self.script_data.items[self.current_item_index]
            execute_command = item.execute
            worker = CommandWorker(self.current_item_index, execute_command)
            # worker.signals.finished.connect(self.handle_result)
            # worker.signals.error.connect(self.handle_error)
            self.threadpool.start(worker)
        else:
            self.timer.stop()
            self.show_test_completed_message()

    def show_test_completed_message(self):
        QMessageBox.information(self, "測試完成", "所有項目已執行完畢，測試完成。")

    # # 測試Pass處理
    # def handle_result(self, index, result):
    #     self.item_table.setItem(index, 4, QTableWidgetItem(result))
    #     value_range = self.script_data["Item"][index].get("Value range", "")
        
    #     if self.check_value_range(result, value_range):
    #         for col in range(3):
    #             self.item_table.item(index, col).setBackground(QColor(144, 238, 144))  # Light green color
    #     else:
    #         for col in range(3):
    #             self.item_table.item(index, col).setBackground(QColor(255, 200, 200))  # Light red color
        
    #     self.progress_bar.setValue(self.progress_bar.value() + 1)
    #     self.current_item_index += 1
    #     self.timer.singleShot(10, self.execute_next_item)  # 延迟100毫秒后执行下一个item
    
    # # 測試Fail處理
    # def handle_error(self, index, error):
    #     self.item_table.setItem(index, 3, QTableWidgetItem("執行錯誤"))
    #     for col in range(3):
    #         self.item_table.item(index, col).setBackground(QColor(255, 200, 200))  # Light red color
        
    #     self.progress_bar.setValue(self.progress_bar.value() + 1)
    #     self.current_item_index += 1
    #     self.timer.singleShot(100, self.execute_next_item)  # 延迟100毫秒后执行下一个item

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

    def _update_bar(self, bar: Signal, progress_percentage):
        """
        更新測試進度。 使用 signal 發射進度更新訊息，讓 UI 介面可以接收並更新進度條。

        Args:
            progress_percentage (int): 進度百分比 (0-100)。
        """
        Log.debug(f"更新測試進度: {progress_percentage}")
        # --- 使用 signal 發射進度更新訊息 ---
        bar.emit(progress_percentage) # 發射 signal，傳遞進度百分比

    
    def _set_max_bar(self, bar: Signal, max_value):
        """
        設置進度條的最大值

        Args:
            max_value (int): Progressbar最大值
        """
        Log.debug(f"set bar max: {max_value}")
        # --- 使用 signal 發射進度更新訊息 ---
        bar.emit(max_value) # 發射 signal，傳遞進度百分比

    def _update_result_table(self, index, result):
        pass
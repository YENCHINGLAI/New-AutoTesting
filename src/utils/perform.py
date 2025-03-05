#===================================================================================================
# Import the necessary modules
#===================================================================================================
import os
import sys
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QRunnable, Signal, QThreadPool, QTimer, QObject
import subprocess
from src.utils.script import Script
from src.utils.log import Log

#===================================================================================================
# Environment
#===================================================================================================
TOOLS_PATH = 'tools'

#===================================================================================================
# Model
#===================================================================================================
class Perform:
    def __init__(self):
        self.mac: str = None                       #Mac address
        self.sn: str = None                        #Serial number
        self.script: Script = None                 #腳本

#===================================================================================================
# Execute
#===================================================================================================
class WorkerSignals(QObject):
    """
    進入pool前須先建立物件
    """
    finished = Signal(int, str)
    error = Signal(int, str)

class CommandWorker(QRunnable):
    """
    thread pool worker
    """
    def __init__(self, index, command):
        super().__init__()
        self.index = index
        self.command = command
        self.result = None
        self.signals = WorkerSignals()

    def run(self):
        try:
            # Execute the command
            execut_command = os.path.join(TOOLS_PATH, self.command)
            self.result = subprocess.check_output(execut_command, text=True).strip()
            Log.info(f'Execute item, index: {self.index}, command: {execut_command}, result: {self.result}')
            self.signals.finished.emit(self.index, self.result)
        except subprocess.CalledProcessError as e:
            self.signals.error.emit(self.index, str(e))

class PerformManager(QObject):                   # 繼承 QObject，如果需要使用 signal/slot
    """
    執行 Items
    """
    # Progress Bar 更新
    items_bar_updated = Signal(int)
    max_items_bar_updated = Signal(int)
    current_bar_updated = Signal(int)
    max_current_bar_updated = Signal(int)

    # Table 更新
    items_table_init = Signal()
    items_table_updated = Signal(int, str, bool)

    # 即時訊息更新
    current_line_updated = Signal(str)
    qbox_message = Signal(str, str)

    def __init__(self):
        super().__init__()                      # 初始化 QObject (如果繼承自 QObject)
        self._is_running = False                # 標記測試是否正在執行，用於 stop_execution 功能
        self.perform_data = Perform()           # Perform 物件
        # self.script_data: Script = None
        self.threadpool = QThreadPool()
        self.current_item_index = 0
        self.total_items = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.execute_next_item)

    def start_execution(self, script: Script):
        """
        開始測試 初始化
        """
        Log.info(f'Working dir: {os.getcwd()}')
        Log.info('Start execution')
        if not script:
            Log.error('Script is None')
            return
        
        Log.info('Execution inited')
        # self.script_data = script
        self.perform_data.script = script
        # self.total_items = len(self.script_data.items) 
        self.total_items = len(self.perform_data.script.items)
        self._init_result_table()
        self._set_max_bar(self.max_items_bar_updated, self.total_items)                 # 依照腳本item數量
        self._set_max_bar(self.max_current_bar_updated, 5)                              # 將單一測試項目拆分為五階段
        self._update_bar(self.items_bar_updated, 0)                                     # 初始化
        self._update_bar(self.current_bar_updated, 0)
        self.current_item_index = 0
        # self.bar_test()
        self.execute_next_item()
        
    def bar_test(self):
        Log.info('Progress bar test')
        for i in range(self.total_items):
            self._update_bar(self.items_bar_updated, i+1)
        for j in range(5):
            self._update_bar(self.current_bar_updated, i+1)

    def execute_next_item(self):
        """
        執行下一個測試項目。
        """
        self.current_bar_updated.emit(0)       # 刷新Current bar
        
        if self.current_item_index < self.total_items:
            self.current_bar_updated.emit(1)
            # item = self.script_data.items[self.current_item_index]
            item = self.perform_data.script.items[self.current_item_index]
            execute_command = item.execute
            current_item_name = item.title
            self._update_current_line(self.current_line_updated, current_item_name)

            self.current_bar_updated.emit(2)
            execute_command = self._command_mac_sn_replace(execute_command, self.perform_data.mac, self.perform_data.sn)
            worker = CommandWorker(self.current_item_index, execute_command)
            worker.signals.finished.connect(self.handle_result)
            worker.signals.error.connect(self.handle_error)
            self.threadpool.start(worker)
        else:
            self.timer.stop()
            self.show_test_completed_message("測試完成", "所有測試項目已完成。")
            Log.info('All items completed')

    def show_test_completed_message(self, title, message):
        """
        顯示測試完成訊息。
        """
        self.qbox_message.emit(title, message)

    # 測試Pass處理
    def handle_result(self, index, value):
        """
        處理執行完的結果
        """
        # Get valid value
        self._update_bar(self.current_bar_updated, 3)
        valid_max = self.perform_data.script.items[index].valid_max
        valid_min = self.perform_data.script.items[index].valid_min
        executed_delay = self.perform_data.script.items[index].delay
        
        # Valid result
        self._update_bar(self.current_bar_updated, 4)
        check_result = self._check_value_range(value, valid_min, valid_max)

        # Update UI status
        self._update_bar(self.current_bar_updated, 5)
        self._update_result_table(index, value, check_result)
        self._update_bar(self.items_bar_updated, index + 1)

        # Next item
        self.current_item_index += 1
        self.timer.singleShot(executed_delay, self.execute_next_item)  # 延迟100毫秒后执行下一个item
    
    # 測試Fail處理
    def handle_error(self, index, error):
        Log.debug(f"Handle error: {index}, err: {error}")
    #     self.item_table.setItem(index, 3, QTableWidgetItem("執行錯誤"))
    #     for col in range(3):
    #         self.item_table.item(index, col).setBackground(QColor(255, 200, 200))  # Light red color
        
    #     self.progress_bar.setValue(self.progress_bar.value() + 1)
    #     self.current_item_index += 1
    #     self.timer.singleShot(100, self.execute_next_item)  # 延迟100毫秒后执行下一个item

    def _command_mac_sn_replace(self, command_template, mac_value, sn_value):
        # 替換命令中的 $mac 和 $sn 變數
        return command_template.replace('$mac', mac_value or '$mac')\
            .replace('$sn', sn_value or '{$sn}')

    def _check_value_range(self, result, min_val, max_val):
        try:
            if min_val and max_val:
                return min_val <= int(result) <= max_val
            else:
                return False
        except ValueError:
            pass
        return False

    def _update_bar(self, setting_bar: Signal, progress_percentage):
        """
        更新測試進度。 使用 signal 發射進度更新訊息，讓 UI 介面可以接收並更新進度條。

        Args:
            progress_percentage (int): 進度百分比 (0-100)。
        """
        Log.debug(f"update {setting_bar} bar value: {progress_percentage}")
        # --- 使用 signal 發射進度更新訊息 ---
        setting_bar.emit(progress_percentage) # 發射 signal，傳遞進度百分比

    
    def _set_max_bar(self, setting_bar: Signal, max_value):
        """
        設置進度條的最大值

        Args:
            max_value (int): Progressbar最大值
        """
        Log.debug(f"set {setting_bar} bar max: {max_value}")
        # --- 使用 signal 發射進度更新訊息 ---
        setting_bar.emit(max_value) # 發射 signal，傳遞進度百分比

    def _update_current_line(self, line: Signal, current_line):
        """
        設置進度條的最大值

        Args:
            max_value (int): Progressbar最大值
        """
        Log.debug(f"Current item: {current_line}")
        line.emit(current_line)

    def _update_result_table(self, index:int, check_value:int, check_result:bool):
        """

        """
        Log.debug(f"Update table index: {index}, result: {check_value}, check_result: {check_result}")
        self.items_table_updated.emit(index, check_value, check_result)

    def _init_result_table(self):
        """

        """
        Log.debug(f"Init result table.")
        self.items_table_init.emit()
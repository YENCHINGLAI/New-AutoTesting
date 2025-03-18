#===================================================================================================
# Import the necessary modules
#===================================================================================================
import os
import subprocess

from PySide6.QtCore import QRunnable, Signal, QThreadPool, QTimer, QObject

from src.utils.script import Script, ScriptItems
from src.utils.log import Log
from src.utils.report import TestReport, ItemResult
from src.utils.ui_update import UIUpdater
from src.config import config

#===================================================================================================
# Work Model
#===================================================================================================
class Perform:
    def __init__(self):
        self.mac: str = None                       #Mac address
        self.sn: str = None                        #Serial number
        self.script: Script = None                 #腳本
        self.report: TestReport = None             #報告

class WorkerSignals(QObject):
    """
    進入pool前須先建立物件
    """
    finished = Signal(int, str)
    error = Signal(int, str)        

#===================================================================================================
# Execute
#===================================================================================================
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
            execute_command = os.path.join(config.API_TOOLS_PATH, self.command)
            self.result = subprocess.check_output(execute_command, text=True).strip()
            Log.info(f'Execute item, index: {self.index}, command: {execute_command}, result: {self.result}')
            self.signals.finished.emit(self.index, self.result)
        except Exception as e:
            self.signals.error.emit(self.index, str(e))

class PerformManager(QObject):                   # 繼承 QObject，如果需要使用 signal/slot
    """
    執行 Items
    """
    def __init__(self, ui_updater: UIUpdater):
        super().__init__()                      # 初始化 QObject (如果繼承自 QObject)
        self._is_running = False                # 標記測試是否正在執行，用於 stop_execution 功能
        self.perform_data = Perform()           # Perform 物件
        self.threadpool = QThreadPool()
        self.current_item_index = 0
        self.total_items = 0
        self.execute_items = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._execute_next_item)
    
        # 創建 UI 更新器
        self.ui_updater = ui_updater

    def convert_execute_items(self, all_items:list[ScriptItems], selected_item_indices=None):
        """
        轉換執行項目
        """
        # 默認使用所有項目的索引，如果提供了特定索引則使用指定的索引
        indices_to_process = selected_item_indices or range(len(all_items))
    
        return [(idx, all_items[idx]) 
                for idx in indices_to_process 
                if self._is_valid_index(idx, all_items)]
    
    def _is_valid_index(self, index, all_items):
        """檢查索引是否有效的輔助方法"""
        return index in range(len(all_items))

    def start_execution(self, script: Script, selected_item_indices=None):
        """
        開始測試 初始化
        """
        if not script:
            Log.error('Script is None')
            return
        
        Log.info('Start execution')
        self.perform_data.script = script
        self.execute_items = self.convert_execute_items(self.perform_data.script.items, selected_item_indices)
        self.total_items = len(self.execute_items)

        # 初始化 Perform 物件
        self.perform_data.report = TestReport(self.perform_data.script.product.model_name, "00:11:22:33:44:55", "SN1234567890", "v1.0", "Tester A", "Station A", "Auto")

        self._is_running = True
        self.current_item_index = 0

        # 初始化 UI
        self.ui_updater.init_result_table()
        self.ui_updater.set_max_bar(self.ui_updater.max_items_bar_updated, self.total_items)                 # 依照腳本item數量
        self.ui_updater.set_max_bar(self.ui_updater.max_current_bar_updated, 5)                              # 將單一測試項目拆分為五階段
        self.ui_updater.update_bar(self.ui_updater.items_bar_updated, 0)                                     # Item bar
        self.ui_updater.update_bar(self.ui_updater.current_bar_updated, 0)                                   # Current bar

        self._execute_next_item()
    
    def _execute_next_item(self):
        """
        執行下一個測試項目。
        """
        self.ui_updater.update_bar(self.ui_updater.current_bar_updated, 0)
        
        if self.current_item_index < self.total_items:
            current_item_name, execute_command = self._get_current_item_details()     

            self.ui_updater.update_bar(self.ui_updater.current_bar_updated, 1)
            self.ui_updater.update_current_line(self.ui_updater.current_line_updated, current_item_name)
   
            execute_command = self._command_mac_sn_replace(
                execute_command, 
                self.perform_data.mac, 
                self.perform_data.sn
                )
            worker = CommandWorker(self.current_item_index, execute_command)
            worker.signals.finished.connect(self._handle_result)
            worker.signals.error.connect(self._handle_error)
            self.ui_updater.update_bar(self.ui_updater.current_bar_updated, 2)
            self.threadpool.start(worker)
        else:       
            self._stop_execution()  
            self.ui_updater.show_message("測試完成", "已停止測試")
    
    def _stop_execution(self):
        """
        停止測試
        """
        self.timer.stop()
        self.perform_data.report.End_Record_and_Create_Report(self.total_items)
        Log.info('Stop execution')

    # 測試Pass處理
    def _handle_result(self, index, value):
        """
        處理執行完的結果
        """
        # Get valid value
        self.ui_updater.update_bar(self.ui_updater.current_bar_updated, 3)
        tuple_item = self.execute_items[index]      # Get the tuple (index, ScriptItem)
        original_index, current_item = tuple_item   # Unpack the tuple!
        valid_max = current_item.valid_max
        valid_min = current_item.valid_min
        executed_delay = current_item.delay
        # valid_max = self.execute_items.items[index].valid_max
        # valid_min = self.perform_data.script.items[index].valid_min
        # executed_delay = self.perform_data.script.items[index].delay
        
        # Valid result
        self.ui_updater.update_bar(self.ui_updater.current_bar_updated, 4)
        validation_result = self._check_value_range(value, valid_min, valid_max)

        # Update UI status
        self.ui_updater.update_result_table(original_index, value, validation_result )
        self.ui_updater.update_bar(self.ui_updater.items_bar_updated, index + 1)
        self.ui_updater.increment_pass_count() if validation_result  else self.ui_updater.increment_fail_count()

        # Save result
        self._save_result(current_item, value, validation_result )
        # self._save_result(self.perform_data.script.items[index], value, check_result)
        self.ui_updater.update_bar(self.ui_updater.current_bar_updated, 5)

        # Next item
        self.current_item_index += 1
        self.timer.singleShot(executed_delay*1000, self._execute_next_item)      
    
    # 測試Fail處理
    def _handle_error(self, index, error):
        Log.debug(f"Handle error: {index}, err: {error}")
        self.ui_updater.show_message("API 執行發生問題，已停止測試", error)
        self._stop_execution()

    def _save_result(self, item: ScriptItems, value, check_result):
        """
        保存測試結果。
        """
        Log.info('add result')
        self.perform_data.report.add_test_result(
            ItemResult(item.title, item.unit, item.valid_min, item.valid_max, value, check_result))

    def _command_mac_sn_replace(self, command_template:str, mac_value:str, sn_value:str):
        """
        替換執行指令中的 $mac, $sn 變數
        """
        return command_template.replace('$mac', mac_value or '$mac')\
            .replace('$sn', sn_value or '{$sn}')

    def _check_value_range(self, result, min_val, max_val):
        """
        檢查執行結果是否在範圍內
        """
        try:
            return min_val <= int(result) <= max_val
        except ValueError:
            pass
        return False
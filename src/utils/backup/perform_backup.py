#===================================================================================================
# Import the necessary modules
#===================================================================================================
import os
import subprocess
from queue import Queue

from PySide6.QtCore import QRunnable, Signal, QThreadPool, QTimer, QObject

from src.utils.script import Script, TestItems
from src.utils.log import Log
from src.utils.record import ReportGenerator, ItemResult
from src.config import config
from src.utils.commonUtils import UiUpdater

#===================================================================================================
# Execute
#===================================================================================================
class Perform:
    def __init__(self):
        self.mac: str = None                       #Mac address
        self.sn: str = None                        #Serial number
        self.station: str = None                   #測試站
        self.script: Script = None                 #腳本
        self.report: ReportGenerator = None             #報告

class WorkerSignals(QObject):
    """
    進入pool前須先建立物件
    """
    finished = Signal(int, str, TestItems)
    error = Signal(int, str)        

class CommandWorker(QRunnable):
    """
    thread pool worker
    """
    def __init__(self, index, command, item):
        super().__init__()
        self.index = index
        self.command = command
        self.item = item
        self.result = None
        self.signals = WorkerSignals()

    def run(self):
        try:
            # Execute the command
            execute_command = os.path.join(config.API_TOOLS_PATH, self.command)
            self.result = subprocess.check_output(execute_command, text=True).strip()

            Log.info(f'Execute item, index: {self.index}, command: {execute_command}, result: {self.result}')
            self.signals.finished.emit(self.index, self.result, self.item)
        except Exception as e:
            self.signals.error.emit(self.index, str(e))

class PerformManager(QObject):                   # 繼承 QObject，如果需要使用 signal/slot
    """
    執行 Items
    """
    def __init__(self, report: ReportGenerator, script: Script, selected_item_indices=None):
        super().__init__()                      # 初始化 QObject (如果繼承自 QObject)
        self._perform_data = Perform()           # Perform 物件    
        self._perform_data.report = report       # 報告
        self._perform_data.script = script       # 腳本
        self._selected_item_indices = selected_item_indices

        self._threadpool = QThreadPool()
        self._timer = QTimer(self)
        self._execution_queue = Queue()         # 執行隊列
        self._is_running = False                # 標記測試是否正在執行，用於 stop_execution 功能
        self._pass_count = 0                     # 通過次數
        self._fail_count = 0                     # 失敗次數
        self._total_items_to_run = 0             # 實際要運行的項目數
        self._completed_items_count = 0          # 已完成 (pass/fail after retries) 的項目數
        self._timer.timeout.connect(self._execute_next_item)

    def start_execution(self, mac=None, sn=None):
        """
        開始測試 初始化
        """
        if not self._perform_data.script:
            Log.error('Script is None')
            return
        
        # 設置MAC和SN
        self._perform_data.mac = mac or None  # 預設值
        self._perform_data.sn = sn or None  # 預設值
        
        # 創建測試項目隊列
        convert_execute_items = self._convert_execute_items(self._perform_data.script.items, self._selected_item_indices)
        self._execution_queue = self._create_execution_queue(convert_execute_items)
        self._total_items_to_run = len(convert_execute_items)
        
        # 初始化 UI
        UiUpdater.itemsTableInit.emit()
        UiUpdater.scriptProgressChanged.emit(0,self._total_items_to_run)
        UiUpdater.itemProgressChanged.emit(0,5)

        Log.info('Start execution')
        self._is_running = True
        self._execute_next_item()

    def _convert_execute_items(self, all_items:list[TestItems], selected_item_indices=None):
        """
        執行項目，加上新index用於執行
        """
        # 默認使用所有項目的索引，如果提供了特定索引則使用指定的索引
        indices_to_process = selected_item_indices or range(len(all_items))
    
        return [(idx, all_items[idx]) 
                for idx in indices_to_process 
                if self._is_valid_index(idx, all_items)]
       
    def _is_valid_index(self, index, all_items):
        """檢查索引是否有效的輔助方法"""
        return index in range(len(all_items))
    
    def _create_execution_queue(self, execute_items):
        """創建執行隊列，避免使用全域索引"""
        queue = Queue()
        for index, item in enumerate(execute_items):
            queue.put((index, item))
        return queue
    
    def _execute_next_item(self):
        """
        執行下一個測試項目。
        """
        if not self._is_running or self._execution_queue.empty():
            self._handle_execution_complete(self._total_items_to_run == self._pass_count)
            return
        
        try:
            UiUpdater.itemProgressChanged.emit(0,5)
            _, (original_index, item) = self._execution_queue.get()
            self._execution_queue.task_done()
            self._prepare_and_execute_item(original_index, item)

        except Exception as e:
            Log.error(f'Error executing next item: {e}')

    def _prepare_and_execute_item(self, original_index, item):
        """
        準備並執行項目
        """
        # 提取項目詳情
        item_name = item.title
        execute_command = item.execute
        execute_command = self._command_mac_sn_replace(
            execute_command, 
            self._perform_data.mac, 
            self._perform_data.sn
            )
        
        UiUpdater.itemProgressChanged.emit(1,5)
        UiUpdater.currentItemChanged.emit(item_name)

        # 創建工作線程，使用閉包來傳遞上下文
        worker = CommandWorker(original_index, execute_command, item)
        worker.signals.finished.connect(self._handle_execution_result)
        worker.signals.error.connect(self._handle_execution_error)

        # 啟動工作線程
        UiUpdater.itemProgressChanged.emit(2,5)
        self._threadpool.start(worker)
        
    def _command_mac_sn_replace(self, command_template:str, mac_value:str, sn_value:str):
        """
        替換執行指令中的 $mac, $sn 變數
        """
        return command_template.replace('$mac', mac_value or '$mac')\
            .replace('$sn', sn_value or '{$sn}')

    # 測試Pass處理
    def _handle_execution_result(self, index, value, item:TestItems):
        """
        處理執行完的結果
        """
        # Valid result
        validation_result = self._check_value_range(value, item.valid_min, item.valid_max)
        UiUpdater.itemProgressChanged.emit(3,5)
 
        # Save result
        self._save_execution_result(item, value, validation_result)
        UiUpdater.itemProgressChanged.emit(4,5)

        # Update UI status
        self._update_result_with_ui(index, value, validation_result)
        UiUpdater.itemProgressChanged.emit(5,5)

        # Next item
        self._timer.singleShot(item.delay*1000, self._execute_next_item)

    def _check_value_range(self, result, min_val, max_val):
        """
        檢查執行結果是否在範圍內
        """
        try:
            return min_val <= int(result) <= max_val
        except ValueError:
            pass
        except Exception:
            pass
        return False
    
    def _update_result_with_ui(self, index, value, check_result):
        """
        更新結果到UI
        """
        # 更新結果表格
        UiUpdater.itemsTableChanged.emit(index, value, check_result)
        
        # 更新通過/失敗計數
        if check_result:
            self._pass_count += 1
            UiUpdater.passCountChanged.emit(self._pass_count)
        else:
            self._fail_count += 1
            UiUpdater.failCountChanged.emit(self._fail_count)

        # 更新測試項進度
        completed_count = self._pass_count + self._fail_count
        UiUpdater.scriptProgressChanged.emit(completed_count, self._total_items_to_run)
    
    def _save_execution_result(self, item: TestItems, value, check_result):
        """
        保存測試結果。
        """
        self._perform_data.report.add_test_result(
            ItemResult(item.title, item.unit, item.valid_min, item.valid_max, value, check_result))

    def _handle_execution_error(self, index, error):
        """
        處理測試錯誤
        """
        Log.debug(f"Handle error: {index}, err: {error}")
        UiUpdater.messageBoxDialog.emit("API 執行發生問題，已停止測試", error)
        self.stop_execution()

    def _handle_execution_complete(self, result:bool):
        """
        處理測試完成
        """  
        self.stop_execution()
        if result:
            UiUpdater.messageBoxDialog.emit("測試結束", "已完成所有測試項目")
        else:
            UiUpdater.messageBoxDialog.emit("測試結束", "未完成所有測試項目")

    def stop_execution(self):
        """
        停止測試
        """
        self._is_running = False
        self._timer.stop()
        self._perform_data.report.End_Record_and_Create_Report(self._total_items_to_run)
        Log.info('Stop execution')
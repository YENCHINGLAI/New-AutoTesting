#===================================================================================================
# Import the necessary modules
#===================================================================================================
import os
import subprocess
from queue import Queue

from PySide6.QtCore import QRunnable, Signal, QProcess, QTimer, QObject

from src.utils.log import Log
from src.utils.script import Script, ScriptItems
from src.utils.record import TestReport, ItemResult
from src.utils.commonUtils import UiUpdater
from src.config import config

#===================================================================================================
# Execute
#===================================================================================================
class Perform:
    def __init__(self):
        self.mac: str = None                       #Mac address
        self.sn: str = None                        #Serial number
        self.station: str = None                   #測試站
        self.script: Script = None                 #腳本
        self.report: TestReport = None             #報告

class PerformManager(QObject):                   # 繼承 QObject，如果需要使用 signal/slot
    """
    執行 Items
    """
    def __init__(self, report: TestReport, script: Script, selected_item_indices=None):
        super().__init__()                      # 初始化 QObject (如果繼承自 QObject)
        self._perform_data = Perform()           # Perform 物件    
        self._perform_data.report = report       # 報告
        self._perform_data.script = script       # 腳本
        self._selected_item_indices = selected_item_indices

        self._process = QProcess(self)           # QProcess instance for executing commands
        self._timer = QTimer(self)
        self._execution_queue = Queue()         # 執行隊列
        self._is_running = False                # 標記測試是否正在執行，用於 stop_execution 功能
        self._pass_count = 0                     # 通過次數
        self._fail_count = 0                     # 失敗次數
        self._total_items_to_run = 0             # 實際要運行的項目數
        self._completed_items_count = 0          # 已完成 (pass/fail after retries) 的項目數

        # State for the currently executing item and retries
        self._current_item_original_index = -1
        self._current_item_object: ScriptItems = None
        self._current_retry_count = 0
        self._current_command = ""
        self._retry_limit = 2 # Default retry limit

        # Connect QProcess signals
        self._process.finished.connect(self._on_process_finished)
        self._process.errorOccurred.connect(self._on_process_error_occurred) # Renamed slot
        self._timer.timeout.connect(self._execute_next_item)

    def start_execution(self, mac=None, sn=None):
        """
        開始測試 初始化
        """
        if not self._perform_data.script:
            Log.error('Script is None or empty')      
            UiUpdater.messageBoxDialog.emit("錯誤", "腳本未載入或為空")
            return
        
        if self._is_running:
            Log.warn("Execution already in progress.")
            return
        
        # Reset state
        self._pass_count = 0
        self._fail_count = 0
        self._completed_items_count = 0
        self._current_item_original_index = -1
        self._current_item_object = None
        self._current_retry_count = 0

        # 設置MAC和SN
        self._perform_data.mac = mac or ""  # 預設值
        self._perform_data.sn = sn or ""    # 預設值
        
        # 將Items轉換為queueue，並加上index用於執行
        convert_execute_items = self._convert_execute_items(
            self._perform_data.script.items, 
            self._selected_item_indices
            )
        self._execution_queue = self._create_execution_queue(convert_execute_items)
        self._total_items_to_run = len(convert_execute_items)
        
        # 初始化 UI
        UiUpdater.itemsTableInit.emit() # Consider passing the actual items for init
        UiUpdater.passCountChanged.emit(0)
        UiUpdater.failCountChanged.emit(0)
        UiUpdater.scriptProgressChanged.emit(0, self._total_items_to_run)
        UiUpdater.itemProgressChanged.emit(0,5) # 5 steps: Prepare, Start, Running, Validate, Finish

        Log.info(f'Starting execution with {self._total_items_to_run} items.')
        self._is_running = True
        self._execute_next_item()   # Start the first item

    def _convert_execute_items(self, all_items:list[ScriptItems], selected_item_indices=None):
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
        for item_tuple in enumerate(execute_items):
            queue.put(item_tuple)
        return queue
    
    def _execute_next_item(self):
        """
        執行下一個測試項目。
        """
        self._timer.stop() # Stop timer in case it was running for delay/retry

        # 確認是否進入執行狀態
        if not self._is_running:
            Log.info("Execution stopped.")
            return
        
        # 檢查Queue是否為空
        # 如果是，則確認所有項目都已完成
        if self._execution_queue.empty():
            Log.info("Execution queue is empty.")
            self.stop_execution() # Stop execution if queue is empty
            return
        
        try:
            # Get next item: (original_index, item_object)
            UiUpdater.itemProgressChanged.emit(0,5)
            _, (self._current_item_original_index, self._current_item_object) = self._execution_queue.get()
            self._execution_queue.task_done()   # Mark task as done in the queue
            self._current_retry_count = 0       # Reset retry count for the new item

            Log.info(f"Executing item index {self._current_item_original_index}: '{self._current_item_object.title}'")
            self._prepare_and_run_process()
        except Exception as e:
            Log.error(f'Error executing next item: {e}', exc_info=True)

    def _prepare_and_run_process(self):
        """
        準備並執行項目
        """
        if not self._is_running or not self._current_item_object:
            return
        
        item = self._current_item_object
        original_index = self._current_item_original_index

        UiUpdater.itemProgressChanged.emit(0, 5) # Step 0: Prepare
        UiUpdater.currentItemChanged.emit(item.title + (f" (Retry {self._current_retry_count})" if self._current_retry_count > 0 else ""))

        # Prepare command
        command_template = item.execute
        self._current_command = self._command_mac_sn_replace(
            command_template,
            self._perform_data.mac,
            self._perform_data.sn
        )

        executable_path = os.path.join(config.API_TOOLS_PATH, self._current_command.split()[0]) # Basic split, might need refinement
        args = self._current_command.split()[1:]

        Log.debug(f"Attempting to run command: '{executable_path}' with args: {args}")
        UiUpdater.itemProgressChanged.emit(1, 5) # Step 1: Start

        # Ensure QProcess is not already running
        if self._process.state() != QProcess.NotRunning:
            Log.warn("QProcess was still running. Killing previous process.")
            self._process.kill()
            self._process.waitForFinished(20000) # Wait briefly

        # Start the process
        # self._process.start(executable_path, args)
        # Using startCommand for simplicity if commands are simple scripts/executables in the path
        # Note: startCommand might rely on shell execution, be mindful of security/quoting.
        full_command_path = os.path.join(config.API_TOOLS_PATH, self._current_command)
        self._process.startCommand(full_command_path)
        # If startCommand fails immediately, errorOccurred will be emitted.

        UiUpdater.itemProgressChanged.emit(2, 5) # Step 2: Running (Process started)
        
    def _command_mac_sn_replace(self, command_template:str, mac_value:str, sn_value:str):
        """
        替換執行指令中的 $mac, $sn 變數
        """
        return command_template.replace('$mac', mac_value or '$mac')\
            .replace('$sn', sn_value or '{$sn}')

    def _on_process_finished(self, exitCode, exitStatus):
        """
        Slot called when the QProcess finishes. Handles success, failure, and retries.
        """
        if self._current_item_object is None:
            Log.warn("Process finished but no current item tracked.")
            return # Should not happen in normal flow

        UiUpdater.itemProgressChanged.emit(3, 5) # Step 3: Validate

        # Read output
        output_bytes = self._process.readAllStandardOutput()
        error_bytes = self._process.readAllStandardError()
        result_value = output_bytes.data().decode(errors='ignore').strip() # Decode ignoring potential errors
        error_output = error_bytes.data().decode(errors='ignore').strip()

        item_title = self._current_item_object.title
        item_index = self._current_item_original_index

        Log.info(f"Item '{self._current_item_object.title}' finished.")
        Log.debug(f"  Exit Code: {exitCode}, Exit Status: {exitStatus}")
        Log.debug(f"  Stdout: {result_value}")
        if error_output:
            Log.warn(f"  Stderr: {error_output}")

        # --- Unified Failure Handling Logic ---
        failure_reason = None
        validation_passed = False

        # Check process execution status
        if exitStatus == QProcess.CrashExit:
            failure_reason = f"Process crashed. Stderr: {error_output}"
            Log.error(f"Process crashed for item {item_index}: {failure_reason}")
            # self._handle_item_failure(f"Process crashed. Stderr: {error_output}", False) # Crashes are likely not retryable
        elif exitCode != 0:
            failure_reason = f"Non-zero exit code ({exitCode}). Stderr: {error_output}"
            Log.error(f"Process exited abnormally for item {item_index}: {failure_reason}")
            # Non-zero exit might be retryable depending on the script's design
            # Let's assume for now it means failure, but check retry logic
            # self._handle_item_failure(f"Exit code {exitCode}. Stderr: {error_output}", True) # Check if retryable
        else:
            # Process exited normally (exitCode == 0)
            validation_passed = self._check_value_range(
                result_value,
                self._current_item_object.valid_min,
                self._current_item_object.valid_max
            )

            # --- Decision Point ---
            if not validation_passed:
                failure_reason = f"Validation failed (Value: '{result_value}')"
                Log.warn(f"Item {item_index} FAILED validation: {failure_reason}")

            if validation_passed and failure_reason is None:
                Log.info(f"Item {self._current_item_original_index} PASSED validation.")
                self._handle_item_success(result_value)
            else:
                self._handle_item_failure(result_value, allow_retry=True) # Always allow retry check

    def _on_process_error_occurred(self, error: QProcess.ProcessError):
        """
        Slot called ONLY when QProcess fails to START.
        This will now also trigger the standard retry mechanism.
        """
        if not self._is_running or self._current_item_object is None:
             Log.warn("QProcess start error occurred but execution stopped or no current item.")
             return # Ignore errors if we stopped manually or have no item context

        error_string = self._process.errorString()
        item_title = self._current_item_object.title
        item_index = self._current_item_original_index

        Log.error(f"QProcess start error for item {item_index} ('{item_title}'): {error} - {error_string}")

        # Treat process start error as a failure case that should attempt retries
        failure_reason = f"Process start error: {error_string}"
        self._handle_item_failure(failure_reason, allow_retry=True) # Always allow retry check
        
    def _check_value_range(self, result_str, min_val_str, max_val_str):
        """
        檢查執行結果是否在範圍內
        """
        # Basic check: If result is exactly "PASS" (case-insensitive), treat as True
        if isinstance(result_str, str) and result_str.upper() == "PASS":
            return True
        # Basic check: If result is exactly "FAIL" (case-insensitive), treat as False
        if isinstance(result_str, str) and result_str.upper() == "FAIL":
            return False
        
        try:
            # Try converting result to a number (float allows for more flexibility)
            value = float(result_str)

            # Check lower bound
            if min_val_str is not None and str(min_val_str).strip() != "":
                min_val = float(min_val_str)
                if value < min_val:
                    return False

            # Check upper bound
            if max_val_str is not None and str(max_val_str).strip() != "":
                max_val = float(max_val_str)
                if value > max_val:
                    return False

            # If both checks passed (or were skipped), the value is in range
            return True

        except (ValueError, TypeError):
            # If conversion fails, it's not within a numerical range
            Log.warn(f"Cannot compare value '{result_str}' numerically with range [{min_val_str}, {max_val_str}]")
            # Optional: Could add string comparison logic here if needed
            # If min/max are also strings, maybe check for exact match?
            # if str(min_val_str).strip() != "" and str(min_val_str) == str(max_val_str):
            #     return result_str == str(min_val_str) # Check for exact match if min==max
            return False # Default to False if conversion fails
    
    def _handle_item_success(self, final_value: str):
        """Handles a successfully validated item."""
        item = self._current_item_object
        original_index = self._current_item_original_index

        # Save final result (Pass)
        self._save_execution_result(item, final_value, True)
        UiUpdater.itemProgressChanged.emit(4, 5) # Step 4: Save Result

        # Update UI status
        self._update_ui_final_result(original_index, final_value, True)
        UiUpdater.itemProgressChanged.emit(5, 5) # Step 5: Finish Item

        # Schedule next item after delay
        delay_ms = int(item.delay * 1000) if item.delay > 0 else 10 # Minimum delay to allow UI update
        self._timer.singleShot(delay_ms, self._execute_next_item)

    def _handle_item_failure(self, result_or_error: str, allow_retry: bool):
        """Handles a failed item, checking for retries."""
        if not self._is_running or self._current_item_object is None:
            Log.warn("Attempted to handle item failure, but execution stopped or no current item.")
            return
        
        item = self._current_item_object
        original_index = self._current_item_original_index
        retry_limit = self._retry_limit # Use a default retry limit

        # --- Retry Logic ---
        # Note: allow_retry is effectively always True when called from failure points now
        if allow_retry and self._current_retry_count < retry_limit:
            # Perform retry
            self._current_retry_count += 1
            Log.info(f"Retrying item {original_index} (Attempt {self._current_retry_count}/{retry_limit})")

            # Update UI Table to show "Retrying" or similar? (Optional)
            UiUpdater.itemsTableChanged.emit(original_index, f"Retrying...", False) # Indicate retry in table

            # Retry message
            retry_message = f"{item.retry_message} "
            UiUpdater.messageBoxDialog.emit(f"錯誤! (Attempt {self._current_retry_count}/{retry_limit})", retry_message)

            # Schedule the retry attempt after a short delay (e.g., 500ms)
            retry_delay_ms = 1000
            self._timer.singleShot(retry_delay_ms, self._prepare_and_run_process)
            # Don't proceed to save/update final counts yet
        else:
            # No more retries allowed or needed
            Log.error(f"Item {original_index} definitively FAILED after {self._current_retry_count} retries.")

             # Save final result (Fail)
            self._save_execution_result(item, result_or_error, False)
            UiUpdater.itemProgressChanged.emit(4, 5) # Step 4: Save Result

            # Update UI status
            self._update_ui_final_result(original_index, result_or_error, False)
            UiUpdater.itemProgressChanged.emit(5, 5) # Step 5: Finish Item
            
            # Retry 次數已達上限，停止測試
            self.stop_execution()
            # self._handle_execution_complete(False)
            # # Schedule next item after delay (even for failed items)
            # delay_ms = int(item.delay * 1000) if item.delay > 0 else 10
            # self._timer.singleShot(delay_ms, self._execute_next_item)
    
    def _update_ui_final_result(self, index, value, check_result):
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
        self._completed_items_count += 1
        UiUpdater.scriptProgressChanged.emit(self._completed_items_count, self._total_items_to_run)
    
    def _save_execution_result(self, item: ScriptItems, value, check_result):
        """
        保存測試結果。
        """
        if not self._perform_data.report:
            Log.warn("Report object not available, cannot save result.")
            return
        
        try:
            self._perform_data.report.add_test_result(
                ItemResult(item.title, item.unit, item.valid_min, item.valid_max, value, check_result)
            )
        except Exception as e:
            Log.error(f"Error saving result for item '{item.title}': {e}", exc_info=True)

    def _handle_execution_complete(self, overall_success: bool):
        """Handles the completion of the entire test sequence."""
        Log.info(f"Execution sequence complete. Overall Success: {overall_success}")
        result = f"測試結束。\n成功: {self._pass_count}, 失敗: {self._fail_count}, 總計: {self._total_items_to_run}"
        Log.info(result)

        self._is_running = False # Ensure state is updated
        # Final report generation is now handled in stop_execution

        # Show final message based on success/failure and counts
        if overall_success:
            UiUpdater.messageBoxDialog.emit("測試完成", f"所有 {self._total_items_to_run} 個項目均已成功完成。")
        else:
            UiUpdater.messageBoxDialog.emit("測試完成", result)

    def stop_execution(self):
        """
        Stops the test execution immediately.
        """
        if not self._is_running:
            return # Already stopped

        Log.info('Stopping execution...')
        self._is_running = False
        self._timer.stop() # Stop any pending delays/retries

        # Terminate the running process, if any
        if self._process.state() != QProcess.NotRunning:
            Log.info("Terminating active process...")
            self._process.kill() # Use kill for forceful stop
            self._process.waitForFinished(500) # Wait briefly for termination

        # Clear the queue to prevent further execution if stop was called mid-sequence
        while not self._execution_queue.empty():
            try:
                self._execution_queue.get_nowait()
                self._execution_queue.task_done()
            except Queue.Empty:
                break

        # Finalize report
        if self._perform_data.report:
             # Pass counts accurately reflecting completed items before stop
             final_item_count = self._total_items_to_run
             self._perform_data.report.End_Record_and_Create_Report(final_item_count, self._pass_count, self._fail_count)
             Log.info(f"Final report generated: {self._perform_data.report.final_result}")
        else:
             Log.warn("No report object to finalize.")

        # Reset current item state
        self._current_item_original_index = -1
        self._current_item_object = None
        self._current_retry_count = 0

        Log.info('Execution stopped.')
        # Optionally, update UI to indicate stopped status
        UiUpdater.currentItemChanged.emit("已停止測試")
        # Reset progress bars maybe?
        # UiUpdater.itemProgressChanged.emit(0, 5)
        # UiUpdater.scriptProgressChanged.emit(self._completed_items_count, self._total_items_to_run) # Show final progress before stop
        UiUpdater.startBtnChanged.emit("Start") # Reset button state to "Start"
        
        self._handle_execution_complete(
                self._completed_items_count == self._total_items_to_run 
                and self._fail_count == 0)
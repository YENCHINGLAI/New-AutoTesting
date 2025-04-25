import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
sys.path.append(project_root)

import unittest
from unittest.mock import patch, MagicMock, ANY, call
from queue import Queue

# Mock Qt classes
QtCoreMock = MagicMock()
QtNetworkMock = MagicMock()
QtWidgetsMock = MagicMock()

QtCoreMock.QObject = MagicMock
QtCoreMock.QProcess = MagicMock()
QtCoreMock.QTimer = MagicMock()
QtCoreMock.Signal = MagicMock() # For UiUpdater if needed

sys.modules['PySide6.QtCore'] = QtCoreMock
sys.modules['PySide6.QtNetwork'] = QtNetworkMock
sys.modules['PySide6.QtWidgets'] = QtWidgetsMock

# Mock other dependencies
mock_log = MagicMock()
mock_script_module = MagicMock()
mock_record_module = MagicMock()
mock_common_utils = MagicMock()
mock_config = MagicMock()
mock_setting = MagicMock()

sys.modules['src.utils.log'] = mock_log
sys.modules['src.utils.script'] = mock_script_module
sys.modules['src.utils.record'] = mock_record_module
sys.modules['src.utils.commonUtils'] = mock_common_utils
sys.modules['src.config'] = mock_config
sys.modules['src.config.setting'] = mock_setting

# Import the class AFTER mocks are in place
from src.utils.perform import PerformManager, Perform, TestItems, ItemResult

# Define dummy TestItems for convenience
def create_dummy_item(title="Item", execute="cmd", delay=0.1, valid_min=None, valid_max=None, unit="", retry_msg="Retry"):
    item = MagicMock(spec=TestItems)
    item.title = title
    item.execute = execute
    item.delay = delay
    item.valid_min = valid_min
    item.valid_max = valid_max
    item.unit = unit
    item.retry_message = retry_msg
    return item

class TestPerformManager(unittest.TestCase):

    def setUp(self):
        self.mock_report = MagicMock(spec=mock_record_module.ReportGenerator)
        self.mock_script = MagicMock(spec=mock_script_module.Script)
        self.mock_script.items = [create_dummy_item(f"Item {i}") for i in range(3)]
        self.mock_script.pairing = 0 # Default
        self.mock_script.test_mode = MagicMock() # Mock the enum value

        # Mock UiUpdater signals (optional, but good practice)
        self.mock_ui_updater = MagicMock()
        mock_common_utils.UiUpdater = self.mock_ui_updater

        # Mock setting.SKIP_MODE
        mock_setting.SKIP_MODE = {} # Start with empty skip mode

        # Mock config paths
        mock_config.API_TOOLS_PATH = "/fake/tools"

        # Create instance and mock its internal Qt objects
        self.manager = PerformManager(self.mock_report, self.mock_script)
        self.manager._process = MagicMock(spec=QtCoreMock.QProcess)
        self.manager._timer = MagicMock(spec=QtCoreMock.QTimer)

        # Mock QProcess state methods
        self.manager._process.state.return_value = QtCoreMock.QProcess.NotRunning
        self.manager._process.readAllStandardOutput.return_value.data.return_value.decode.return_value = "PASS" # Default success output
        self.manager._process.readAllStandardError.return_value.data.return_value.decode.return_value = "" # Default no error output
        self.manager._process.errorString.return_value = "Fake process error"

    def test_init(self):
        self.assertIsInstance(self.manager._perform_data, Perform)
        self.assertEqual(self.manager._perform_data.report, self.mock_report)
        self.assertEqual(self.manager._perform_data.script, self.mock_script)
        self.assertIsNone(self.manager._selected_item_indices)
        self.assertIsInstance(self.manager._process, MagicMock)
        self.assertIsInstance(self.manager._timer, MagicMock)
        self.assertIsInstance(self.manager._execution_queue, Queue)
        self.assertFalse(self.manager._is_running)
        # Check signal connections
        self.manager._process.finished.connect.assert_called_once_with(self.manager._on_process_finished)
        self.manager._process.errorOccurred.connect.assert_called_once_with(self.manager._on_process_error_occurred)
        self.manager._timer.timeout.connect.assert_called_once_with(self.manager._execute_next_item)

    def test_start_execution_no_script(self):
        manager = PerformManager(self.mock_report, None)
        manager.start_execution()
        mock_log.Log.error.assert_called_with('Script is None or empty')
        self.mock_ui_updater.messageBoxDialog.emit.assert_called_with("錯誤", "腳本未載入或為空")
        self.assertFalse(manager._is_running)

    def test_start_execution_already_running(self):
        self.manager._is_running = True
        self.manager.start_execution()
        mock_log.Log.warn.assert_called_with("Execution already in progress.")
        # Ensure execute_next_item was not called again
        self.manager._timer.singleShot.assert_not_called() # Assuming start calls _execute_next_item via timer or directly

    @patch.object(PerformManager, '_execute_next_item') # Patch the method on the class
    def test_start_execution_success(self, mock_execute_next):
        product_info = {"$sn1": "SN123"}
        self.mock_script.items = [create_dummy_item("Item 1"), create_dummy_item("Item 2")]
        self.mock_script.pairing = 0 # 1 DUT

        self.manager.start_execution(product_info)

        self.assertTrue(self.manager._is_running)
        self.assertEqual(self.manager._perform_data.product_info, product_info)
        self.assertEqual(self.manager._pass_count, 0)
        self.assertEqual(self.manager._fail_count, 0)
        self.assertEqual(self.manager._completed_items_count, 0)
        self.assertEqual(self.manager._total_items_to_run, 2)
        self.assertEqual(self.manager._real_total_items_to_run, 2)
        self.assertFalse(self.manager._execution_queue.empty())
        self.assertEqual(self.manager._execution_queue.qsize(), 2)

        # Check UI initialization calls
        self.mock_ui_updater.itemsTableInit.emit.assert_called_once()
        self.mock_ui_updater.passCountChanged.emit.assert_called_once_with(0)
        self.mock_ui_updater.failCountChanged.emit.assert_called_once_with(0)
        self.mock_ui_updater.scriptProgressChanged.emit.assert_called_once_with(0, 2)
        self.mock_ui_updater.itemProgressChanged.emit.assert_called_once_with(0, 5)

        mock_log.Log.info.assert_any_call('Starting execution with 2 items.')
        mock_execute_next.assert_called_once() # Check that execution starts

    @patch.object(PerformManager, '_execute_next_item')
    def test_start_execution_with_selected_indices(self, mock_execute_next):
        self.mock_script.items = [create_dummy_item(f"Item {i}") for i in range(5)]
        selected_indices = [0, 2, 4]
        manager = PerformManager(self.mock_report, self.mock_script, selected_indices)

        manager.start_execution()

        self.assertTrue(manager._is_running)
        self.assertEqual(manager._total_items_to_run, 3) # Only selected items
        self.assertEqual(manager._real_total_items_to_run, 5) # Still know the total
        self.assertEqual(manager._execution_queue.qsize(), 3)
        # Check first item in queue has original index 0
        _, (original_index, _) = manager._execution_queue.queue[0][1] # Access underlying queue tuple
        self.assertEqual(original_index, 0)
        _, (original_index, _) = manager._execution_queue.queue[1][1]
        self.assertEqual(original_index, 2)
        _, (original_index, _) = manager._execution_queue.queue[2][1]
        self.assertEqual(original_index, 4)

        mock_execute_next.assert_called_once()

    def test_convert_execute_items(self):
        items = [create_dummy_item(f"Item {i}") for i in range(4)]
        # Test with no selection
        result = self.manager._convert_execute_items(items)
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], (0, items[0]))
        self.assertEqual(result[3], (3, items[3]))
        # Test with selection
        result = self.manager._convert_execute_items(items, [1, 3])
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], (1, items[1]))
        self.assertEqual(result[1], (3, items[3]))
        # Test with invalid selection
        result = self.manager._convert_execute_items(items, [0, 5, 2]) # Index 5 is invalid
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], (0, items[0]))
        self.assertEqual(result[1], (2, items[2]))

    @patch.object(PerformManager, 'stop_execution')
    def test_execute_next_item_empty_queue(self, mock_stop):
        self.manager._is_running = True
        # Ensure queue is empty
        while not self.manager._execution_queue.empty():
             self.manager._execution_queue.get()

        self.manager._execute_next_item()

        mock_log.Log.info.assert_called_with("Execution queue is empty.")
        mock_stop.assert_called_once()
        self.manager._timer.stop.assert_called_once()

    def test_execute_next_item_not_running(self):
        self.manager._is_running = False
        self.manager._execute_next_item()
        mock_log.Log.info.assert_called_with("Execution stopped.")
        self.manager._timer.stop.assert_called_once()
        # Ensure prepare_and_run not called
        self.manager._process.startCommand.assert_not_called()

    @patch.object(PerformManager, '_should_skip_item', return_value=True)
    @patch.object(PerformManager, '_execute_next_item') # Mock recursive call
    def test_execute_next_item_skip(self, mock_recursive_call, mock_should_skip):
        self.manager._is_running = True
        item0 = create_dummy_item("Item 0")
        item1 = create_dummy_item("Item 1 TO SKIP")
        item2 = create_dummy_item("Item 2")
        self.manager._execution_queue = Queue()
        # Use internal structure for testing: (running_index, (original_index, item_object))
        self.manager._execution_queue.put((0, (0, item0)))
        self.manager._execution_queue.put((1, (1, item1)))
        self.manager._execution_queue.put((2, (2, item2)))

        self.manager._execute_next_item() # Should process Item 0 (assuming _should_skip returns False first time)

        # Let's refine the test: Assume first item should be skipped
        self.manager._execution_queue = Queue()
        self.manager._execution_queue.put((0, (0, item1))) # Put skippable item first
        self.manager._execution_queue.put((1, (1, item2)))
        mock_recursive_call.reset_mock() # Reset mock before second call

        self.manager._execute_next_item() # Call for Item 1

        mock_should_skip.assert_called_once_with("Item 1 TO SKIP")
        mock_recursive_call.assert_called_once() # Called itself to process next item
        self.manager._process.startCommand.assert_not_called() # Skipped item not executed

    @patch.object(PerformManager, '_should_skip_item', return_value=False)
    @patch.object(PerformManager, '_prepare_and_run_process')
    def test_execute_next_item_run(self, mock_prepare, mock_should_skip):
        self.manager._is_running = True
        item0 = create_dummy_item("Item 0")
        self.manager._execution_queue = Queue()
        self.manager._execution_queue.put((0, (0, item0)))

        self.manager._execute_next_item()

        mock_should_skip.assert_called_once_with("Item 0")
        self.assertEqual(self.manager._current_item_original_index, 0)
        self.assertEqual(self.manager._current_item_object, item0)
        self.assertEqual(self.manager._current_retry_count, 0)
        mock_prepare.assert_called_once()
        self.mock_ui_updater.itemProgressChanged.emit.assert_any_call(0,5) # Reset progress

    def test_should_skip_item(self):
        # Setup skip modes
        mock_tx_mode = MagicMock()
        mock_rx_mode = MagicMock()
        mock_pair_mode = MagicMock()
        mock_tx_mode.name = 'TX'
        mock_rx_mode.name = 'RX'
        mock_pair_mode.name = 'PAIR'
        mock_setting.TEST_MODE = MagicMock() # Mock the enum class itself if needed
        mock_setting.TEST_MODE.TX = mock_tx_mode
        mock_setting.TEST_MODE.RX = mock_rx_mode
        mock_setting.TEST_MODE.PAIR = mock_pair_mode

        mock_setting.SKIP_MODE = {
            mock_tx_mode: "TESTING_RX",
            mock_rx_mode: "TESTING_TX",
            mock_pair_mode: ""
        }

        # Test cases
        self.manager._perform_data.script.test_mode = mock_tx_mode
        self.assertTrue(self.manager._should_skip_item("Some TESTING_RX Step"))
        self.assertFalse(self.manager._should_skip_item("Some TESTING_TX Step"))
        self.assertFalse(self.manager._should_skip_item("Pairing Step"))

        self.manager._perform_data.script.test_mode = mock_rx_mode
        self.assertFalse(self.manager._should_skip_item("Some TESTING_RX Step"))
        self.assertTrue(self.manager._should_skip_item("Some TESTING_TX Step"))
        self.assertFalse(self.manager._should_skip_item("Pairing Step"))

        self.manager._perform_data.script.test_mode = mock_pair_mode
        self.assertFalse(self.manager._should_skip_item("Some TESTING_RX Step"))
        self.assertFalse(self.manager._should_skip_item("Some TESTING_TX Step"))
        self.assertFalse(self.manager._should_skip_item("Pairing Step")) # Empty skip keyword

        # Test case where test_mode is not in SKIP_MODE (should not happen with enum)
        self.manager._perform_data.script.test_mode = MagicMock(name='UNKNOWN')
        self.assertFalse(self.manager._should_skip_item("Some TESTING_RX Step"))


    @patch('os.path.join', side_effect=lambda *args: "/".join(args)) # Simple mock for os.path.join
    def test_prepare_and_run_process(self, mock_join):
        self.manager._is_running = True
        item = create_dummy_item(title="Run Tool", execute="tool.exe -p $sn1 --mac $mac11")
        self.manager._current_item_object = item
        self.manager._perform_data.product_info = {"$sn1": "SN123", "$mac11": "AA:BB:CC:DD:EE:FF"}
        self.manager._current_retry_count = 1 # Test retry display

        self.manager._prepare_and_run_process()

        # Check UI updates
        self.mock_ui_updater.itemProgressChanged.emit.assert_any_call(0, 5) # Prepare
        self.mock_ui_updater.currentItemChanged.emit.assert_called_once_with("Run Tool (Retry 1)")

        # Check command replacement and path construction
        expected_command = "tool.exe -p SN123 --mac AA:BB:CC:DD:EE:FF"
        expected_full_path = "/fake/tools/tool.exe -p SN123 --mac AA:BB:CC:DD:EE:FF" # Based on mock_join
        self.assertEqual(self.manager._current_command, expected_command)
        mock_join.assert_called_with(mock_config.API_TOOLS_PATH, expected_command)

        # Check process start
        self.manager._process.state.assert_called() # Check if state was checked
        self.manager._process.startCommand.assert_called_once_with(expected_full_path)
        self.mock_ui_updater.itemProgressChanged.emit.assert_any_call(1, 5) # Start
        self.mock_ui_updater.itemProgressChanged.emit.assert_any_call(2, 5) # Running

    def test_command_mac_sn_replace(self):
        cmd = "tool.exe --sn $sn1 --mac $mac11 -x $sn2 --y $mac21"
        info = {"$sn1": "S1", "$mac11": "M1", "$sn2": "S2"} # $mac21 missing
        expected = "tool.exe --sn S1 --mac M1 -x S2 --y $mac21"
        result = self.manager._command_mac_sn_replace(cmd, info)
        self.assertEqual(result, expected)

        cmd_no_replace = "tool2.exe -a -b"
        result = self.manager._command_mac_sn_replace(cmd_no_replace, info)
        self.assertEqual(result, cmd_no_replace)

        cmd_empty_info = "tool.exe --sn $sn1"
        result = self.manager._command_mac_sn_replace(cmd_empty_info, {})
        self.assertEqual(result, cmd_empty_info)


    @patch.object(PerformManager, '_check_value_range', return_value=True)
    @patch.object(PerformManager, '_handle_item_success')
    @patch.object(PerformManager, '_handle_item_failure')
    def test_on_process_finished_success(self, mock_handle_fail, mock_handle_success, mock_check_range):
        self.manager._is_running = True
        item = create_dummy_item(valid_min="1", valid_max="5")
        self.manager._current_item_object = item
        self.manager._current_item_original_index = 0
        self.manager._process.readAllStandardOutput.return_value.data.return_value.decode.return_value = "3" # Value in range
        exit_code = 0
        exit_status = QtCoreMock.QProcess.NormalExit

        self.manager._on_process_finished(exit_code, exit_status)

        # Check validation call
        mock_check_range.assert_called_once_with("3", "1", "5")
        # Check correct handler called
        mock_handle_success.assert_called_once_with("3")
        mock_handle_fail.assert_not_called()
        self.mock_ui_updater.itemProgressChanged.emit.assert_any_call(3, 5) # Validate step

    @patch.object(PerformManager, '_check_value_range', return_value=False) # Simulate validation fail
    @patch.object(PerformManager, '_handle_item_success')
    @patch.object(PerformManager, '_handle_item_failure')
    def test_on_process_finished_validation_fail(self, mock_handle_fail, mock_handle_success, mock_check_range):
        self.manager._is_running = True
        item = create_dummy_item(valid_min="1", valid_max="5")
        self.manager._current_item_object = item
        self.manager._current_item_original_index = 1
        self.manager._process.readAllStandardOutput.return_value.data.return_value.decode.return_value = "6" # Value out of range
        exit_code = 0
        exit_status = QtCoreMock.QProcess.NormalExit

        self.manager._on_process_finished(exit_code, exit_status)

        mock_check_range.assert_called_once_with("6", "1", "5")
        mock_handle_fail.assert_called_once_with("6", allow_retry=True)
        mock_handle_success.assert_not_called()
        mock_log.Log.warn.assert_any_call("Item 1 FAILED validation: Validation failed (Value: '6')")


    @patch.object(PerformManager, '_check_value_range')
    @patch.object(PerformManager, '_handle_item_success')
    @patch.object(PerformManager, '_handle_item_failure')
    def test_on_process_finished_exit_code_fail(self, mock_handle_fail, mock_handle_success, mock_check_range):
        self.manager._is_running = True
        item = create_dummy_item()
        self.manager._current_item_object = item
        self.manager._current_item_original_index = 2
        self.manager._process.readAllStandardError.return_value.data.return_value.decode.return_value = "Error occurred"
        exit_code = 1 # Non-zero exit code
        exit_status = QtCoreMock.QProcess.NormalExit

        self.manager._on_process_finished(exit_code, exit_status)

        mock_check_range.assert_not_called() # Should not validate if exit code is bad
        mock_handle_fail.assert_called_once_with("Non-zero exit code (1). Stderr: Error occurred", allow_retry=True)
        mock_handle_success.assert_not_called()
        mock_log.Log.error.assert_any_call("Process exited abnormally for item 2: Non-zero exit code (1). Stderr: Error occurred")

    @patch.object(PerformManager, '_check_value_range')
    @patch.object(PerformManager, '_handle_item_success')
    @patch.object(PerformManager, '_handle_item_failure')
    def test_on_process_finished_crash_fail(self, mock_handle_fail, mock_handle_success, mock_check_range):
        self.manager._is_running = True
        item = create_dummy_item()
        self.manager._current_item_object = item
        self.manager._current_item_original_index = 3
        self.manager._process.readAllStandardError.return_value.data.return_value.decode.return_value = "Segfault"
        exit_code = 0 # Exit code might be 0 on crash depending on OS/how it crashes
        exit_status = QtCoreMock.QProcess.CrashExit

        self.manager._on_process_finished(exit_code, exit_status)

        mock_check_range.assert_not_called()
        # In the code, crash calls _handle_item_failure directly, but let's assume it goes through the main logic path for testing
        # Based on the current code structure, the exitCode != 0 check might run first if exit code is non-zero after crash
        # If exit code IS 0, then validation would be attempted.
        # Let's refine the test based on the *actual* code flow: CrashExit is checked first.
        mock_handle_fail.assert_called_once_with("Process crashed. Stderr: Segfault", allow_retry=True) # Crash calls fail handler
        mock_handle_success.assert_not_called()
        mock_log.Log.error.assert_any_call("Process crashed for item 3: Process crashed. Stderr: Segfault")

    @patch.object(PerformManager, '_handle_item_failure')
    def test_on_process_error_occurred(self, mock_handle_fail):
        """ Test QProcess failing to start """
        self.manager._is_running = True
        item = create_dummy_item()
        self.manager._current_item_object = item
        self.manager._current_item_original_index = 0
        error_code = QtCoreMock.QProcess.FailedToStart

        self.manager._on_process_error_occurred(error_code)

        self.manager._process.errorString.assert_called_once()
        mock_handle_fail.assert_called_once_with("Process start error: Fake process error", allow_retry=True)
        mock_log.Log.error.assert_called_once_with(
            "QProcess start error for item 0 ('Item'): FailedToStart - Fake process error"
        )

    def test_check_value_range(self):
        # Exact PASS/FAIL
        self.assertTrue(self.manager._check_value_range("PASS", None, None))
        self.assertTrue(self.manager._check_value_range("pass", None, None))
        self.assertFalse(self.manager._check_value_range("FAIL", None, None))
        self.assertFalse(self.manager._check_value_range("fail", None, None))

        # Numerical range
        self.assertTrue(self.manager._check_value_range("10", "5", "15"))
        self.assertTrue(self.manager._check_value_range("5.0", "5", "15")) # Boundary min
        self.assertTrue(self.manager._check_value_range("15", "5", "15")) # Boundary max
        self.assertFalse(self.manager._check_value_range("4.9", "5", "15"))
        self.assertFalse(self.manager._check_value_range("15.1", "5", "15"))

        # Numerical - only min
        self.assertTrue(self.manager._check_value_range("10", "5", None))
        self.assertTrue(self.manager._check_value_range("10", "5", "")) # Empty string max
        self.assertTrue(self.manager._check_value_range("5", "5", None))
        self.assertFalse(self.manager._check_value_range("4", "5", None))

        # Numerical - only max
        self.assertTrue(self.manager._check_value_range("10", None, "15"))
        self.assertTrue(self.manager._check_value_range("10", "", "15")) # Empty string min
        self.assertTrue(self.manager._check_value_range("15", None, "15"))
        self.assertFalse(self.manager._check_value_range("16", None, "15"))

        # Numerical - no range (always true if conversion succeeds)
        self.assertTrue(self.manager._check_value_range("10", None, None))
        self.assertTrue(self.manager._check_value_range("-5.5", "", ""))

        # Non-numerical
        self.assertFalse(self.manager._check_value_range("abc", "5", "10"))
        self.assertFalse(self.manager._check_value_range("abc", None, None)) # Fails conversion
        self.assertFalse(self.manager._check_value_range("10", "a", "b")) # Fails min/max conversion

    @patch.object(PerformManager, '_save_execution_result')
    @patch.object(PerformManager, '_update_ui_final_result')
    @patch.object(PerformManager, '_execute_next_item')
    def test_handle_item_success(self, mock_execute_next, mock_update_ui, mock_save):
        item = create_dummy_item(delay=0.5)
        self.manager._current_item_object = item
        self.manager._current_item_original_index = 0
        final_value = "PASS"

        self.manager._handle_item_success(final_value)

        mock_save.assert_called_once_with(item, final_value, True)
        self.mock_ui_updater.itemProgressChanged.emit.assert_any_call(4, 5) # Save step
        mock_update_ui.assert_called_once_with(0, final_value, True)
        self.mock_ui_updater.itemProgressChanged.emit.assert_any_call(5, 5) # Finish step
        self.manager._timer.singleShot.assert_called_once_with(500, mock_execute_next) # Check delay

    @patch.object(PerformManager, '_prepare_and_run_process')
    def test_handle_item_failure_retry(self, mock_prepare):
        self.manager._is_running = True
        item = create_dummy_item(retry_msg="Please check connection")
        self.manager._current_item_object = item
        self.manager._current_item_original_index = 1
        self.manager._current_retry_count = 0
        self.manager._retry_limit = 2 # Allow retries

        self.manager._handle_item_failure("Error Value", allow_retry=True)

        self.assertEqual(self.manager._current_retry_count, 1) # Incremented
        mock_log.Log.info.assert_called_with("Retrying item 1 (Attempt 1/2)")
        self.mock_ui_updater.itemsTableChanged.emit.assert_called_with(1, "Retrying...", False)
        self.mock_ui_updater.messageBoxDialog.emit.assert_called_with("錯誤! (Attempt 1/2)", "Please check connection ")
        self.manager._timer.singleShot.assert_called_once_with(1000, mock_prepare) # Schedule retry

    @patch.object(PerformManager, '_save_execution_result')
    @patch.object(PerformManager, '_update_ui_final_result')
    @patch.object(PerformManager, 'stop_execution')
    def test_handle_item_failure_no_more_retries(self, mock_stop, mock_update_ui, mock_save):
        self.manager._is_running = True
        item = create_dummy_item()
        self.manager._current_item_object = item
        self.manager._current_item_original_index = 2
        self.manager._retry_limit = 1
        self.manager._current_retry_count = 1 # Already at retry limit

        self.manager._handle_item_failure("Final Error", allow_retry=True)

        mock_log.Log.error.assert_called_with("Item 2 definitively FAILED after 1 retries.")
        mock_save.assert_called_once_with(item, "Final Error", False)
        self.mock_ui_updater.itemProgressChanged.emit.assert_any_call(4, 5) # Save step
        mock_update_ui.assert_called_once_with(2, "Final Error", False)
        self.mock_ui_updater.itemProgressChanged.emit.assert_any_call(5, 5) # Finish step
        mock_stop.assert_called_once() # Should stop execution

    @patch.object(PerformManager, '_handle_execution_complete')
    def test_stop_execution(self, mock_handle_complete):
        self.manager._is_running = True
        self.manager._total_items_to_run = 5
        self.manager._real_total_items_to_run = 5
        self.manager._completed_items_count = 3
        self.manager._fail_count = 1
        self.manager._pass_count = 2
        self.manager._process.state.return_value = QtCoreMock.QProcess.Running # Simulate running process

        # Add items to queue to test clearing
        self.manager._execution_queue.put((0, (0, create_dummy_item())))
        self.manager._execution_queue.put((1, (1, create_dummy_item())))

        self.manager.stop_execution()

        self.assertFalse(self.manager._is_running)
        self.manager._timer.stop.assert_called_once()
        self.manager._process.kill.assert_called_once()
        self.manager._process.waitForFinished.assert_called_once_with(500)
        self.assertTrue(self.manager._execution_queue.empty()) # Queue should be cleared

        # Check report finalization (result should be False because fail_count > 0)
        self.mock_report.End_Record_and_Create_Report.assert_called_once_with(
            False, # final_result
            5,     # total_items (was _total_items_to_run)
            2,     # pass_items
            1      # fail_items
        )

        # Check UI updates
        self.mock_ui_updater.currentItemChanged.emit.assert_called_with("已停止測試")
        self.mock_ui_updater.startBtnChanged.emit.assert_called_with("Start")
        mock_handle_complete.assert_called_once_with(False) # Overall result


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
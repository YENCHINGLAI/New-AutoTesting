import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
sys.path.append(project_root)

import unittest
from unittest.mock import patch, MagicMock, ANY, call

# Mock Qt classes BEFORE importing barcode
QtWidgetsMock = MagicMock()
QtCoreMock = MagicMock()

QtWidgetsMock.QWidget = MagicMock # Mock base class for type checking
QtWidgetsMock.QMessageBox = MagicMock()
QtWidgetsMock.QInputDialog = MagicMock()
QtCoreMock.Qt = MagicMock()

sys.modules['PySide6.QtWidgets'] = QtWidgetsMock
sys.modules['PySide6.QtCore'] = QtCoreMock

# Mock other dependencies
mock_common_utils = MagicMock()
mock_script_module = MagicMock()
mock_log = MagicMock()

sys.modules['src.utils.commonUtils'] = mock_common_utils
sys.modules['src.utils.script'] = mock_script_module
sys.modules['src.utils.log'] = mock_log

# Import the functions/classes AFTER mocks
from src.utils.barcode import _scan_with_input_dialog, _maybe_allow_na, collect_product_barcodes

# Define dummy Script/Product for tests
def create_barcode_script(pairing=0, sn_counts=[1], mac_counts=[1]):
    script = MagicMock(spec=mock_script_module.Script)
    script.pairing = pairing
    script.product = []
    num_dev = pairing + 1
    for i in range(num_dev):
        p = MagicMock()
        p.sn_count = sn_counts[i] if i < len(sn_counts) else 0
        p.mac_count = mac_counts[i] if i < len(mac_counts) else 0
        script.product.append(p)
    return script

class TestBarcodeFunctions(unittest.TestCase):

    def setUp(self):
        QtWidgetsMock.QInputDialog.getText.reset_mock()
        QtWidgetsMock.QMessageBox.critical.reset_mock()
        QtWidgetsMock.QMessageBox.warning.reset_mock()
        mock_log.Log.info.reset_mock()
        mock_log.Log.warn.reset_mock()
        mock_log.Log.error.reset_mock()
        # Reset common utils mocks if they were called
        mock_common_utils.is_mo.reset_mock()
        mock_common_utils.is_sn_nosign.reset_mock()
        mock_common_utils.is_mac.reset_mock()
        mock_common_utils.is_mac_nosign.reset_mock()
        mock_common_utils.is_pcb.reset_mock()
        mock_common_utils.is_testjig.reset_mock()


    def test_scan_with_input_dialog_ok(self):
        parent = MagicMock(spec=QtWidgetsMock.QWidget)
        prompt = "Scan now:"
        title = "Scanner"
        # Simulate user entering text and clicking OK
        QtWidgetsMock.QInputDialog.getText.return_value = ("USER_INPUT", True)

        result = _scan_with_input_dialog(parent, prompt, title)

        self.assertEqual(result, "USER_INPUT")
        QtWidgetsMock.QInputDialog.getText.assert_called_once_with(
            parent, title, prompt, inputMethodHints=ANY
        )
        mock_log.Log.info.assert_called_with(f"Input dialog received: 'USER_INPUT' for prompt: '{prompt}'")

    def test_scan_with_input_dialog_ok_empty(self):
        parent = MagicMock(spec=QtWidgetsMock.QWidget)
        prompt = "Scan optional:"
        # Simulate user entering nothing and clicking OK
        QtWidgetsMock.QInputDialog.getText.return_value = ("", True)

        result = _scan_with_input_dialog(parent, prompt)

        self.assertEqual(result, "") # Returns empty string now
        mock_log.Log.warn.assert_called_with(f"Input dialog received empty input for prompt: '{prompt}', treating as N/A.")

    def test_scan_with_input_dialog_cancel(self):
        parent = MagicMock(spec=QtWidgetsMock.QWidget)
        prompt = "Scan required:"
        # Simulate user clicking Cancel
        QtWidgetsMock.QInputDialog.getText.return_value = ("SomeTextIgnored", False)

        result = _scan_with_input_dialog(parent, prompt)

        self.assertEqual(result, "N/A")
        mock_log.Log.warn.assert_called_with(f"Input dialog cancelled by user for prompt: '{prompt}'. Returning N/A.")

    def test_scan_with_input_dialog_invalid_parent(self):
        result = _scan_with_input_dialog(None, "Prompt") # Not a QWidget
        self.assertEqual(result, "N/A")
        mock_log.Log.error.assert_called_with("Invalid parent widget provided for QInputDialog.")

    def test_scan_with_input_dialog_exception(self):
        parent = MagicMock(spec=QtWidgetsMock.QWidget)
        QtWidgetsMock.QInputDialog.getText.side_effect = Exception("Test Boom!")

        result = _scan_with_input_dialog(parent, "Prompt")

        self.assertEqual(result, "N/A")
        mock_log.Log.error.assert_called_with("Error displaying input dialog: Test Boom!", exc_info=True)
        QtWidgetsMock.QMessageBox.critical.assert_called_once()

    def test_maybe_allow_na(self):
        self.assertFalse(_maybe_allow_na("MO"))
        self.assertTrue(_maybe_allow_na("SN"))
        self.assertTrue(_maybe_allow_na("MAC"))
        self.assertTrue(_maybe_allow_na("MAC-1"))
        self.assertTrue(_maybe_allow_na("OTHER"))

    @patch('src.utils.barcode._scan_with_input_dialog')
    def test_collect_product_barcodes_single_dev_success(self, mock_scan):
        parent = MagicMock(spec=QtWidgetsMock.QWidget)
        script = create_barcode_script(pairing=0, sn_counts=[1], mac_counts=[2])
        # Mock validator return values
        mock_common_utils.is_mo.return_value = True
        mock_common_utils.is_sn_nosign.return_value = True
        mock_common_utils.is_mac.return_value = True
        mock_common_utils.is_mac_nosign.return_value = False # Assume is_mac passes

        # Define scan results in order
        scan_results = ["M123", "SN123", "MAC1", "MAC2"]
        mock_scan.side_effect = scan_results

        result = collect_product_barcodes(parent, script)

        expected_info = {
            "$mo1": "M123",
            "$sn1": "SN123",
            "$mac11": "MAC1",
            "$mac12": "MAC2",
        }
        self.assertEqual(result, expected_info)

        # Check scan calls
        expected_scan_calls = [
            call(parent, "[1] 請掃描 MO 條碼:"),
            call(parent, "[1] 請掃描 SN 條碼:"),
            call(parent, "[1] 請掃描 MAC-1 條碼:"),
            call(parent, "[1] 請掃描 MAC-2 條碼:"),
        ]
        self.assertEqual(mock_scan.call_args_list, expected_scan_calls)

        # Check validator calls (assuming is_mo is combined with others now)
        mock_common_utils.is_mo.assert_called_with("M123")
        mock_common_utils.is_pcb.assert_called_with("M123") # Called by lambda
        mock_common_utils.is_testjig.assert_called_with("M123") # Called by lambda
        mock_common_utils.is_sn_nosign.assert_called_once_with("SN123")
        self.assertEqual(mock_common_utils.is_mac.call_count, 2)
        mock_common_utils.is_mac.assert_has_calls([call("MAC1"), call("MAC2")])


    @patch('src.utils.barcode._scan_with_input_dialog')
    def test_collect_product_barcodes_pair_dev_success(self, mock_scan):
        parent = MagicMock(spec=QtWidgetsMock.QWidget)
        # Dev1: SN+MAC1, Dev2: SN only
        script = create_barcode_script(pairing=1, sn_counts=[1, 1], mac_counts=[1, 0])
        # Mock validators
        mock_common_utils.is_mo.return_value = True
        mock_common_utils.is_sn_nosign.return_value = True
        mock_common_utils.is_mac.return_value = True

        # Define scan results
        scan_results = ["MO1", "SN1", "MAC11", "MO2", "SN2"]
        mock_scan.side_effect = scan_results

        result = collect_product_barcodes(parent, script)

        expected_info = {
            "$mo1": "MO1", "$sn1": "SN1", "$mac11": "MAC11",
            "$mo2": "MO2", "$sn2": "SN2",
        }
        self.assertEqual(result, expected_info)

        expected_scan_calls = [
            call(parent, "[1] 請掃描 MO 條碼:"),
            call(parent, "[1] 請掃描 SN 條碼:"),
            call(parent, "[1] 請掃描 MAC-1 條碼:"),
            call(parent, "[2] 請掃描 MO 條碼:"),
            call(parent, "[2] 請掃描 SN 條碼:"),
        ]
        self.assertEqual(mock_scan.call_args_list, expected_scan_calls)

    @patch('src.utils.barcode._scan_with_input_dialog')
    def test_collect_product_barcodes_skip_sn_mac(self, mock_scan):
        parent = MagicMock(spec=QtWidgetsMock.QWidget)
        # Dev1: MO only
        script = create_barcode_script(pairing=0, sn_counts=[0], mac_counts=[0])
        mock_common_utils.is_mo.return_value = True

        mock_scan.side_effect = ["MO123"] # Only MO should be scanned

        result = collect_product_barcodes(parent, script)

        expected_info = {"$mo1": "MO123", "$sn1": "N/A"} # Ensure SN key exists even if skipped
        self.assertEqual(result, expected_info)
        # Only MO scan should happen
        mock_scan.assert_called_once_with(parent, "[1] 請掃描 MO 條碼:")
        # Validators for SN/MAC should not be called
        mock_common_utils.is_sn_nosign.assert_not_called()
        mock_common_utils.is_mac.assert_not_called()


    @patch('src.utils.barcode._scan_with_input_dialog')
    def test_collect_product_barcodes_validation_retry(self, mock_scan):
        parent = MagicMock(spec=QtWidgetsMock.QWidget)
        script = create_barcode_script(pairing=0, sn_counts=[1], mac_counts=[0])
        # Simulate MO fails validation once, then succeeds
        mock_scan.side_effect = ["INVALID_MO", "M123", "SN123"]
        # Validator returns False then True for MO
        mock_common_utils.is_mo.side_effect = [False, True] # is_pcb/is_testjig assumed False first time too
        mock_common_utils.is_pcb.return_value = False
        mock_common_utils.is_testjig.return_value = False
        mock_common_utils.is_sn_nosign.return_value = True # SN validator succeeds

        result = collect_product_barcodes(parent, script)

        expected_info = {"$mo1": "M123", "$sn1": "SN123"}
        self.assertEqual(result, expected_info)

        # Check scan calls (MO scan called twice)
        expected_scan_calls = [
            call(parent, "[1] 請掃描 MO 條碼:"), # Fails validation
            call(parent, "[1] 請掃描 MO 條碼:"), # Succeeds validation
            call(parent, "[1] 請掃描 SN 條碼:"),
        ]
        self.assertEqual(mock_scan.call_args_list, expected_scan_calls)
        # Check warning message box was shown
        QtWidgetsMock.QMessageBox.warning.assert_called_once_with(
            parent, "輸入格式錯誤", "掃描的 MO 'INVALID_MO' 格式不正確。\n請重新掃描。"
        )
        # Check validator calls
        self.assertEqual(mock_common_utils.is_mo.call_count, 2)

    @patch('src.utils.barcode._scan_with_input_dialog')
    def test_collect_product_barcodes_required_scan_cancelled(self, mock_scan):
        parent = MagicMock(spec=QtWidgetsMock.QWidget)
        script = create_barcode_script(pairing=0, sn_counts=[1], mac_counts=[0])
        # Simulate MO scan being cancelled (required field)
        mock_scan.return_value = "N/A" # _scan_with_input_dialog returns N/A on cancel

        result = collect_product_barcodes(parent, script)

        self.assertIsNone(result) # Should abort
        mock_scan.assert_called_once_with(parent, "[1] 請掃描 MO 條碼:")
        # Check critical message box
        QtWidgetsMock.QMessageBox.critical.assert_called_once_with(
            parent, "掃描失敗", "設備 1 的必要 MO 條碼掃描失敗或被取消，流程中止。"
        )

    @patch('src.utils.barcode._scan_with_input_dialog')
    def test_collect_product_barcodes_script_config_error(self, mock_scan):
        parent = MagicMock(spec=QtWidgetsMock.QWidget)
        script = create_barcode_script(pairing=1, sn_counts=[1], mac_counts=[1]) # Expects 2 products, sn_counts ok, mac_counts ok

        # Simulate Attribute Error when accessing script.product[1]
        def get_product(script, index):
            if index == 0:
                p = MagicMock()
                p.sn_count = 1
                p.mac_count = 1
                return p
            else:
                raise AttributeError("Test attribute error")
        # This mocking is complex, simpler to just provide incomplete config
        script_bad = create_barcode_script(pairing=1) # default has one product config
        script_bad.product = [script_bad.product[0]] # Only one product config

        result = collect_product_barcodes(parent, script_bad)
        self.assertIsNone(result)
        mock_log.Log.error.assert_any_call("腳本配置錯誤：找不到第 2 個產品的配置信息。")
        QtWidgetsMock.QMessageBox.critical.assert_called_once_with(
             parent, "配置錯誤", "腳本配置錯誤：找不到第 2 個產品的配置信息。"
         )


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
sys.path.append(project_root)

import unittest
from unittest.mock import patch, MagicMock, ANY, mock_open
from datetime import datetime, timedelta

# Mock Qt classes if needed (for _load_template)
QtCoreMock = MagicMock()
QtCoreMock.QFile = MagicMock()
QtCoreMock.QIODevice = MagicMock()
QtCoreMock.QIODevice.OpenModeFlag = MagicMock() # Mock nested class

sys.modules['PySide6.QtCore'] = QtCoreMock

# Mock dependencies
mock_jinja2 = MagicMock()
mock_res_rc = MagicMock() # Assuming res.res_rc is generated resource file
mock_config = MagicMock()
mock_setting = MagicMock()
mock_log = MagicMock()
mock_common_utils = MagicMock()
mock_db_manager_module = MagicMock()
mock_script_module = MagicMock()

sys.modules['jinja2'] = mock_jinja2
sys.modules['res'] = MagicMock(res_rc=mock_res_rc)
sys.modules['src.config'] = mock_config
sys.modules['src.config.setting'] = mock_setting
sys.modules['src.utils.log'] = mock_log
sys.modules['src.utils.commonUtils'] = mock_common_utils
sys.modules['src.utils.database'] = mock_db_manager_module
sys.modules['src.utils.script'] = mock_script_module

# Mock ItemResult specifically
mock_common_utils.ItemResult = MagicMock()

# Mock config values
mock_config.REPORT_FILE_PATH = "/fake/reports"
mock_config.REPORT_FILE = ":/templates/report_template.html" # Example resource path

# Mock Setting enum TEST_MODE if used in _create_file logic
mock_setting.TEST_MODE = MagicMock()
mock_setting.TEST_MODE.TX = 'MODE_TX'
mock_setting.TEST_MODE.RX = 'MODE_RX'
mock_setting.TEST_MODE.PAIR = 'MODE_PAIR' # Assuming PAIR is used for BOTH

# Now import the class
from src.utils.record import ReportGenerator

# Define dummy Script/Product for tests
def create_dummy_script(pairing=0, version="1.0", name="DummyScript"):
    script = MagicMock(spec=mock_script_module.Script)
    script.pairing = pairing
    script.version = version
    script.name = name
    # Simulate product list based on pairing
    script.product = []
    if pairing >= 0:
        p1 = MagicMock()
        p1.model_name = "ModelTX"
        p1.version = "1.0.T"
        script.product.append(p1)
    if pairing >= 1:
        p2 = MagicMock()
        p2.model_name = "ModelRX"
        p2.version = "1.0.R"
        script.product.append(p2)
    script.items = [] # For total_tests count in db_init
    return script

class TestReportGenerator(unittest.TestCase):

    def setUp(self):
        self.mock_db_manager_instance = MagicMock()
        mock_db_manager_module.DatabaseManager.return_value = self.mock_db_manager_instance
        self.mock_db_manager_instance.create_test_session.return_value = 555 # Mock session ID
        mock_common_utils.ItemResult.reset_mock() # Reset ItemResult mock if needed

        self.product_info = {
            "$mo1": "MO_TX1", "$sn1": "SN_TX1", "$mac11": "MAC_TX11", "$mac12": "MAC_TX12",
            "$mo2": "MO_RX1", "$sn2": "SN_RX1", "$mac21": "MAC_RX11", "$mac22": "MAC_RX12",
        }
        self.tester_name = "TestUser"
        self.station = "Station01"
        self.mode = "PAIR"
        self.start_dt = datetime(2023, 10, 27, 10, 0, 0)
        self.end_dt = self.start_dt + timedelta(minutes=5, seconds=30, milliseconds=500)

    @patch('src.utils.record.datetime')
    def test_init_and_db_init_pair_mode(self, mock_datetime):
        """Test initialization in PAIR mode."""
        mock_datetime.now.return_value = self.start_dt
        mock_script = create_dummy_script(pairing=1) # Pair mode

        generator = ReportGenerator(mock_script, self.product_info, self.tester_name, self.station, self.mode)

        # Check basic info
        self.assertEqual(generator.product_name, "DummyScript")
        self.assertEqual(generator.product_info, self.product_info)
        self.assertEqual(generator.version, "1.0")
        self.assertEqual(generator.tester_name, self.tester_name)
        self.assertEqual(generator.station, self.station)
        self.assertEqual(generator.mode, self.mode)
        self.assertEqual(generator.start_time, self.start_dt)
        self.assertEqual(generator.start_time_str, "10:00:00")

        # Check DB initialization
        self.mock_db_manager_instance.initialize_database.assert_called_once()
        # Check session creation call arguments
        self.mock_db_manager_instance.create_test_session.assert_called_once()
        call_args = self.mock_db_manager_instance.create_test_session.call_args[1] # Get kwargs

        expected_script_info = {"script_name": "DummyScript", "script_version": "1.0", "total_tests": 0}
        expected_tester_info = {"user": "TestUser", "station": "Station01"}
        # _get_db_product_fields should be called twice
        expected_prod_info = {
            "mo_tx": "MO_TX1", "sn_tx": "SN_TX1", "mac_tx_1": "MAC_TX11", "mac_tx_2": "MAC_TX12",
            "mo_rx": "MO_RX1", "sn_rx": "SN_RX1", "mac_rx_1": "MAC_RX11", "mac_rx_2": "MAC_RX12",
        }

        self.assertEqual(call_args['script_info'], expected_script_info)
        self.assertEqual(call_args['product_info'], expected_prod_info)
        self.assertEqual(call_args['tester_info'], expected_tester_info)
        self.assertEqual(call_args['mode'], self.mode)

        self.assertEqual(generator.db_session_id, 555)
        mock_log.Log.info.assert_any_call("Database test session created successfully with ID: 555")

    @patch('src.utils.record.datetime')
    def test_init_and_db_init_single_mode(self, mock_datetime):
        """Test initialization in single (TX/RX) mode."""
        mock_datetime.now.return_value = self.start_dt
        mock_script = create_dummy_script(pairing=0) # Single mode

        generator = ReportGenerator(mock_script, self.product_info, self.tester_name, self.station, "TX")

        self.mock_db_manager_instance.create_test_session.assert_called_once()
        call_args = self.mock_db_manager_instance.create_test_session.call_args[1]

        # Only TX fields should be populated from product_info, RX fields should be N/A
        expected_prod_info = {
            "mo_tx": "MO_TX1", "sn_tx": "SN_TX1", "mac_tx_1": "MAC_TX11", "mac_tx_2": "MAC_TX12",
            "mo_rx": "N/A", "sn_rx": "N/A", "mac_rx_1": "N/A", "mac_rx_2": "N/A",
        }
        self.assertEqual(call_args['product_info'], expected_prod_info)
        self.assertEqual(call_args['mode'], "TX")
        self.assertEqual(generator.db_session_id, 555)

    @patch('src.utils.record.datetime')
    def test_init_db_session_fail(self, mock_datetime):
        """Test init when DB session creation fails."""
        mock_datetime.now.return_value = self.start_dt
        self.mock_db_manager_instance.create_test_session.return_value = None # Simulate failure
        mock_script = create_dummy_script()

        generator = ReportGenerator(mock_script, self.product_info, self.tester_name, self.station, self.mode)

        self.assertIsNone(generator.db_session_id)
        mock_log.Log.error.assert_any_call("Failed to create database test session.")

    def test_get_db_product_fields(self):
        mock_script = create_dummy_script() # Doesn't matter for this method
        generator = ReportGenerator(mock_script, self.product_info, self.tester_name, self.station, self.mode)

        # Test DUT 1 (TX)
        result_tx = generator._get_db_product_fields(dut_id=1, db_prefix='tx')
        expected_tx = {"mo_tx": "MO_TX1", "sn_tx": "SN_TX1", "mac_tx_1": "MAC_TX11", "mac_tx_2": "MAC_TX12"}
        self.assertEqual(result_tx, expected_tx)

        # Test DUT 2 (RX)
        result_rx = generator._get_db_product_fields(dut_id=2, db_prefix='rx')
        expected_rx = {"mo_rx": "MO_RX1", "sn_rx": "SN_RX1", "mac_rx_1": "MAC_RX11", "mac_rx_2": "MAC_RX12"}
        self.assertEqual(result_rx, expected_rx)

        # Test missing key in product_info
        product_info_missing = {"$mo1": "MO1"}
        generator.product_info = product_info_missing
        result_missing = generator._get_db_product_fields(dut_id=1, db_prefix='tx')
        expected_missing = {"mo_tx": "MO1", "sn_tx": "N/A", "mac_tx_1": "N/A", "mac_tx_2": "N/A"}
        self.assertEqual(result_missing, expected_missing)

        # Test product_info is None
        generator.product_info = None
        result_none = generator._get_db_product_fields(dut_id=1, db_prefix='tx')
        expected_none = {"mo_tx": "N/A", "sn_tx": "N/A", "mac_tx_1": "N/A", "mac_tx_2": "N/A"}
        self.assertEqual(result_none, expected_none)

    def test_add_test_result(self):
        mock_script = create_dummy_script()
        generator = ReportGenerator(mock_script, self.product_info, self.tester_name, self.station, self.mode)
        item_res = MagicMock(spec=mock_common_utils.ItemResult)
        item_res.title = "Voltage Check"

        generator.add_test_result(item_res)

        self.assertIn(item_res, generator.items_result)
        mock_log.Log.debug.assert_any_call("Added item result 'Voltage Check' to internal list.")
        # Check DB add called
        self.mock_db_manager_instance.insert_test_item_result.assert_called_once_with(555, item_res)

    def test_add_test_result_no_db_session(self):
        mock_script = create_dummy_script()
        generator = ReportGenerator(mock_script, self.product_info, self.tester_name, self.station, self.mode)
        generator.db_session_id = None # Simulate no session
        item_res = MagicMock(spec=mock_common_utils.ItemResult)
        item_res.title = "Current Check"

        generator.add_test_result(item_res)

        self.assertIn(item_res, generator.items_result)
        # Check DB add NOT called
        self.mock_db_manager_instance.insert_test_item_result.assert_not_called()
        mock_log.Log.warn.assert_called_with("Cannot save item result 'Current Check' to database: DB session not available.")

    @patch('src.utils.record.datetime')
    @patch.object(ReportGenerator, '_generator_report')
    def test_end_record_and_create_report(self, mock_generate, mock_datetime):
        mock_datetime.now.side_effect = [self.start_dt, self.end_dt] # Start time, End time
        mock_script = create_dummy_script()
        generator = ReportGenerator(mock_script, self.product_info, self.tester_name, self.station, self.mode)

        final_result = True
        total = 10
        passed = 10
        failed = 0

        mock_generate.return_value = True # Simulate report generated ok

        result = generator.End_Record_and_Create_Report(final_result, total, passed, failed)

        self.assertTrue(result)
        self.assertEqual(generator.end_time, self.end_dt)
        self.assertEqual(generator.end_time_str, "10:05:30")
        self.assertEqual(generator.total_tests_count, total)
        self.assertEqual(generator.pass_tests_count, passed)
        self.assertEqual(generator.fail_tests_count, failed)
        self.assertTrue(generator.final_result)
        self.assertEqual(generator.total_time_str, "00:05:30.500") # Check formatting

        # Check DB update called
        self.mock_db_manager_instance.update_test_session_end.assert_called_once_with(555, self.end_dt, True)
        mock_generate.assert_called_once()

    def test_calculate_total_time(self):
        mock_script = create_dummy_script()
        generator = ReportGenerator(mock_script, self.product_info, self.tester_name, self.station, self.mode)
        generator.start_time = datetime(2023, 1, 1, 10, 0, 0, 100000) # 10:00:00.100
        generator.end_time = datetime(2023, 1, 1, 10, 1, 30, 750000)   # 10:01:30.750
        # Duration: 1 min 30.650 sec

        generator._calculate_total_time()
        self.assertEqual(generator.total_time_str, "00:01:30.650")

        generator.start_time = None
        generator._calculate_total_time()
        self.assertEqual(generator.total_time_str, "N/A")


    @patch.object(ReportGenerator, '_load_template')
    @patch.object(ReportGenerator, '_create_data')
    @patch.object(ReportGenerator, '_create_file')
    def test_generator_report(self, mock_create_file, mock_create_data, mock_load_template):
        mock_script = create_dummy_script()
        generator = ReportGenerator(mock_script, self.product_info, self.tester_name, self.station, self.mode)
        mock_template = MagicMock()
        mock_load_template.return_value = mock_template
        mock_data = {"title": "TestData"}
        mock_create_data.return_value = mock_data
        mock_template.render.return_value = "<html>Rendered</html>"
        mock_create_file.return_value = True

        result = generator._generator_report("output.html")

        self.assertTrue(result)
        mock_load_template.assert_called_once()
        mock_create_data.assert_called_once()
        mock_template.render.assert_called_once_with(**mock_data)
        mock_create_file.assert_called_once_with("output.html", "<html>Rendered</html>")

    def test_load_template(self):
        # Mock the QFile interactions
        mock_file_instance = MagicMock(spec=QtCoreMock.QFile)
        QtCoreMock.QFile.return_value = mock_file_instance
        mock_file_instance.open.return_value = True
        mock_file_instance.readAll.return_value.data.return_value.decode.return_value = "Template content {{ var }}"

        # Mock Jinja2 Environment and Template
        mock_env_instance = MagicMock(spec=mock_jinja2.Environment)
        mock_template_instance = MagicMock(spec=mock_jinja2.Template)
        mock_jinja2.Environment.return_value = mock_env_instance
        mock_env_instance.from_string.return_value = mock_template_instance

        mock_script = create_dummy_script()
        generator = ReportGenerator(mock_script, self.product_info, self.tester_name, self.station, self.mode)

        template = generator._load_template()

        self.assertIsNotNone(template)
        self.assertIs(template, mock_template_instance)
        QtCoreMock.QFile.assert_called_once_with(mock_config.REPORT_FILE)
        mock_file_instance.open.assert_called_once_with(QtCoreMock.QIODevice.OpenModeFlag.ReadOnly | QtCoreMock.QIODevice.OpenModeFlag.Text)
        mock_file_instance.readAll.assert_called_once()
        mock_file_instance.close.assert_called_once()
        mock_jinja2.Environment.assert_called_once_with(loader=ANY) # Check it was called
        mock_env_instance.from_string.assert_called_once_with("Template content {{ var }}")

    def test_create_data(self):
        mock_script = create_dummy_script(pairing=1) # Pair mode
        mock_script.product[0].model_name = "TX_Model"
        mock_script.product[1].model_name = "RX_Model"
        generator = ReportGenerator(mock_script, self.product_info, self.tester_name, self.station, self.mode)
        generator.items_result = [MagicMock()] # Add a dummy result
        generator.total_tests_count = 5
        generator.pass_tests_count = 4
        generator.fail_tests_count = 1
        generator.final_result = False
        generator.test_date_str = "2023-10-27"
        generator.start_time_str = "10:00:00"
        generator.end_time_str = "10:05:00"
        generator.total_time_str = "00:05:00.000"

        data = generator._create_data()

        self.assertEqual(data['report_title'], "Test Report")
        self.assertEqual(data['product_name'], mock_script.name)
        self.assertEqual(len(data['duts']), 2) # Both DUTs should be present
        self.assertEqual(data['duts'][0]['name'], "TX_Model")
        self.assertEqual(data['duts'][0]['sn'], "SN_TX1")
        self.assertEqual(data['duts'][0]['macs'], ["MAC_TX11", "MAC_TX12"])
        self.assertEqual(data['duts'][1]['name'], "RX_Model")
        self.assertEqual(data['duts'][1]['sn'], "SN_RX1")
        self.assertEqual(data['duts'][1]['macs'], ["MAC_RX11", "MAC_RX12"])
        self.assertEqual(data['tester_name'], self.tester_name)
        self.assertEqual(data['station'], self.station)
        self.assertEqual(data['mode'], self.mode)
        self.assertEqual(data['test_date'], "2023-10-27")
        # ... check other fields ...
        self.assertEqual(data['total_tests'], 5)
        self.assertFalse(data['final_result'])
        self.assertEqual(len(data['test_results']), 1)

    # @patch('src.utils.record.datetime')
    # @patch('os.makedirs')
    # @patch('builtins.open', new_callable=mock_open) # Mock open function
    # def test_create_file_pair_mode(self, mock_file_open, mock_makedirs, mock_datetime):
    #     """ Test file creation in PAIR mode (should save both) """
    #     mock_datetime.now.return_value = self.start_dt # For timestamp in filename
    #     mock_script = create_dummy_script(pairing=1)
    #     # Mock the test_mode on the generator's perform_data reference if needed
    #     # This requires ReportGenerator to actually store perform_data
    #     # Let's assume test_mode is passed or accessible somehow
    #     # For now, we test based on the hardcoded logic in the provided _create_file

    #     # Simulate TEST_MODE.PAIR - this requires access to perform_data.script.test_mode
    #     # We need to inject this dependency or mock it cleverly.
    #     # Let's assume the generator gets the test_mode somehow, e.g. in __init__
    #     # or we mock the getattr call
    #     mock_perform_data = MagicMock()
    #     mock_perform_data.script.test_mode = mock_setting.TEST_MODE.PAIR
    #     generator = ReportGenerator(mock_script, self.product_info, self.tester_name, self.station, self.mode)
    #     generator._perform_data = mock_perform_data # Inject mock perform_data

    #     html_data = "<html>Report Data</html>"
    #     result = generator._create_file(None, html_data) # No specific filename

    #     self.assertTrue(result)
    #     mock_makedirs.assert_called_once_with(mock_config.REPORT_FILE_PATH, exist_ok=True)

    #     # Check file open calls (should be called for each DUT in PAIR mode)
    #     expected_filename1 = f"Station01_MO_TX1_{self.start_dt.strftime('%Y%m%d_%H%M%S')}.html"
    #     expected_filename2 = f"Station01_MO_RX1_{self.start_dt.strftime('%Y%m%d_%H%M%S')}.html"
    #     expected_path1 = os.path.join(mock_config.REPORT_FILE_PATH, expected_filename1)
    #     expected_path2 = os.path.join(mock_config.REPORT_FILE_PATH, expected_filename2)

    #     # Check if open was called with the expected paths
    #     calls = [call(expected_path1, 'w', encoding='utf-8'),
    #              call(expected_path2, 'w', encoding='utf-8')]
    #     mock_file_open.assert_has_calls(calls, any_order=True) # Order might vary slightly
    #     self.assertEqual(mock_file_open.call_count, 2)

    #     # Check write calls
    #     handle1 = mock_file_open(expected_path1, 'w', encoding='utf-8')
    #     handle2 = mock_file_open(expected_path2, 'w', encoding='utf-8')
    #     handle1.write.assert_called_once_with(html_data)
    #     handle2.write.assert_called_once_with(html_data)

    @patch('src.utils.record.datetime')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_create_file_tx_mode(self, mock_file_open, mock_makedirs, mock_datetime):
        """ Test file creation in TX mode (should save only mo1) """
        mock_datetime.now.return_value = self.start_dt
        mock_script = create_dummy_script(pairing=1) # Assume pairing=1 but mode is TX
        mock_perform_data = MagicMock()
        mock_perform_data.script.test_mode = mock_setting.TEST_MODE.TX
        generator = ReportGenerator(mock_script, self.product_info, self.tester_name, self.station, self.mode)
        generator._perform_data = mock_perform_data

        html_data = "<html>Report Data</html>"
        result = generator._create_file(None, html_data)

        self.assertTrue(result)
        expected_filename1 = f"Station01_MO_TX1_{self.start_dt.strftime('%Y%m%d_%H%M%S')}.html"
        expected_path1 = os.path.join(mock_config.REPORT_FILE_PATH, expected_filename1)

        # Should only open and write the TX file
        mock_file_open.assert_called_once_with(expected_path1, 'w', encoding='utf-8')
        handle1 = mock_file_open()
        handle1.write.assert_called_once_with(html_data)


    @patch('src.utils.record.datetime')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_create_file_rx_mode(self, mock_file_open, mock_makedirs, mock_datetime):
        """ Test file creation in RX mode (should save only mo2) """
        mock_datetime.now.return_value = self.start_dt
        mock_script = create_dummy_script(pairing=1)
        mock_perform_data = MagicMock()
        mock_perform_data.script.test_mode = mock_setting.TEST_MODE.RX
        generator = ReportGenerator(mock_script, self.product_info, self.tester_name, self.station, self.mode)
        generator._perform_data = mock_perform_data

        html_data = "<html>Report Data</html>"
        result = generator._create_file(None, html_data)

        self.assertTrue(result)
        expected_filename2 = f"Station01_MO_RX1_{self.start_dt.strftime('%Y%m%d_%H%M%S')}.html"
        expected_path2 = os.path.join(mock_config.REPORT_FILE_PATH, expected_filename2)

        # Should only open and write the RX file
        mock_file_open.assert_called_once_with(expected_path2, 'w', encoding='utf-8')
        handle2 = mock_file_open()
        handle2.write.assert_called_once_with(html_data)

    @patch('src.utils.record.datetime')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_create_file_pairing_0(self, mock_file_open, mock_makedirs, mock_datetime):
        """ Test file creation when pairing is 0 (should save only mo1 regardless of mode) """
        mock_datetime.now.return_value = self.start_dt
        mock_script = create_dummy_script(pairing=0) # Pairing is 0
        mock_perform_data = MagicMock()
        mock_perform_data.script.test_mode = mock_setting.TEST_MODE.RX # Mode is RX, but pairing=0 takes precedence
        generator = ReportGenerator(mock_script, self.product_info, self.tester_name, self.station, self.mode)
        generator._perform_data = mock_perform_data

        html_data = "<html>Report Data</html>"
        result = generator._create_file(None, html_data)

        self.assertTrue(result)
        expected_filename1 = f"Station01_MO_TX1_{self.start_dt.strftime('%Y%m%d_%H%M%S')}.html"
        expected_path1 = os.path.join(mock_config.REPORT_FILE_PATH, expected_filename1)

        # Should only open and write the first DUT file
        mock_file_open.assert_called_once_with(expected_path1, 'w', encoding='utf-8')
        handle1 = mock_file_open()
        handle1.write.assert_called_once_with(html_data)


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
sys.path.append(project_root)

import unittest
from unittest.mock import patch, MagicMock, mock_open
import yaml # 導入 yaml 模組

# Mock dependencies
mock_yaml = MagicMock()
mock_log = MagicMock()
mock_setting = MagicMock()

sys = MagicMock()
sys.modules['yaml'] = mock_yaml
sys.modules['src.utils.log'] = mock_log
sys.modules['src.config.setting'] = mock_setting
# Mock the enum directly if needed for type hints or default values
mock_setting.TEST_MODE = MagicMock()
mock_setting.TEST_MODE.BOTH = "BOTH_MODE" # Example mock value

# Import after mocking
from src.utils.script import ScriptManager, Script, Product, TestItems, ScriptValidationError, TEST_MODE

# Sample YAML content
VALID_YAML_CONTENT = """
Script:
  Name: MyTestScript
  Version: 1.1
  ReleaseNote: "Added feature X"
  Pairing: 1 # Pair mode
Product:
  - Name: ProductTX
    UseMac: 2
    UseSn: 1
    Version: "HW1.0"
    OtherMessage: "TX Device"
  - Name: ProductRX
    UseMac: 1
    UseSn: 1
    Version: "HW1.1"
    OtherMessage: "RX Device"
Items:
  - Title: "Voltage Check"
    Retry: "Check power supply"
    Valid: "4,6" # Range 4 to 6
    Unit: "V"
    Delay: 0.5
    Execute: "measure_voltage.exe"
  - Title: "RSSI Check"
    Valid: "-60,-30"
    Unit: "dBm"
    Execute: "check_rssi.py --mode $sn1" # Example with variable
"""

INVALID_YAML_STRUCTURE = """
Name: InvalidScript
Items: []
# Missing Product section
"""

EMPTY_YAML_CONTENT = ""

INVALID_YAML_FORMAT = """
Script: Name: BadFormat
"""

class TestScriptDataClasses(unittest.TestCase):
    def test_product_dataclass(self):
        p = Product("ModelA", 1, 1, "v1", "Note")
        self.assertEqual(p.model_name, "ModelA")
        self.assertEqual(p.mac_count, 1)
        self.assertEqual(p.sn_count, 1)
        self.assertEqual(p.version, "v1")
        self.assertEqual(p.other_message, "Note")
        p_default = Product()
        self.assertEqual(p_default.model_name, "")
        self.assertEqual(p_default.mac_count, 0)

    def test_testitems_dataclass(self):
        i = TestItems("ItemA", "RetryA", 10, 20, "UnitA", 0.1, "ExecA")
        self.assertEqual(i.title, "ItemA")
        self.assertEqual(i.retry_message, "RetryA")
        self.assertEqual(i.valid_min, 10)
        self.assertEqual(i.valid_max, 20)
        self.assertEqual(i.unit, "UnitA")
        self.assertEqual(i.delay, 0.1)
        self.assertEqual(i.execute, "ExecA")
        i_default = TestItems()
        self.assertEqual(i_default.title, "")
        self.assertIsNone(i_default.valid_min)

    def test_script_dataclass(self):
        s = Script("ScriptA", "v2", "NoteA", "fileA", 1, TEST_MODE.BOTH, [], [])
        self.assertEqual(s.name, "ScriptA")
        self.assertEqual(s.version, "v2")
        self.assertEqual(s.release_note, "NoteA")
        self.assertEqual(s.file_name, "fileA")
        self.assertEqual(s.pairing, 1)
        self.assertEqual(s.test_mode, TEST_MODE.BOTH)
        self.assertEqual(s.product, [])
        self.assertEqual(s.items, [])
        s_default = Script()
        self.assertEqual(s_default.name, "")
        self.assertEqual(s_default.pairing, 0)
        self.assertEqual(s_default.test_mode, TEST_MODE.BOTH) # Check default

class TestScriptManager(unittest.TestCase):

    def setUp(self):
        self.manager = ScriptManager()
        mock_log.Log.error.reset_mock()
        mock_log.Log.debug.reset_mock() # Reset if used
        mock_yaml.safe_load.reset_mock()
        mock_yaml.YAMLError = yaml.YAMLError # Use real exception for type check if needed

    @patch('os.path.exists', return_value=False)
    def test_load_script_file_not_found(self, mock_exists):
        filename = "nonexistent.yaml"
        result = self.manager.load_script(filename)
        self.assertIsNone(result)
        mock_exists.assert_called_once_with(filename)
        mock_log.Log.error.assert_called_once_with("Script file not found: %s", filename)

    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data=INVALID_YAML_FORMAT)
    def test_load_script_yaml_error(self, mock_file, mock_exists):
        filename = "invalid_format.yaml"
        # Simulate YAMLError during safe_load
        mock_yaml.safe_load.side_effect = yaml.YAMLError("Parsing failed")

        result = self.manager.load_script(filename)

        self.assertIsNone(result)
        mock_exists.assert_called_once_with(filename)
        mock_file.assert_called_once_with(filename, 'r', encoding='utf-8')
        mock_yaml.safe_load.assert_called_once()
        mock_log.Log.error.assert_called_once_with(f"YAML 格式錯誤: {filename}. Error: Parsing failed")

    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data=EMPTY_YAML_CONTENT)
    def test_load_script_empty_yaml(self, mock_file, mock_exists):
        filename = "empty.yaml"
        mock_yaml.safe_load.return_value = None # Simulate empty file result

        result = self.manager.load_script(filename)

        self.assertIsNone(result)
        mock_exists.assert_called_once_with(filename)
        mock_file.assert_called_once_with(filename, 'r', encoding='utf-8')
        # mock_yaml.safe_load.assert_called_once()
        mock_log.Log.error.assert_called_once_with("Script validation error: 驗證錯誤: YAML 檔案為空或僅包含空白字元")

    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data=INVALID_YAML_STRUCTURE)
    def test_load_script_invalid_structure(self, mock_file, mock_exists):
        filename = "invalid_structure.yaml"
        # Simulate loaded data
        invalid_data = {"Name": "InvalidScript", "Items": []} # Missing Product
        mock_yaml.safe_load.return_value = invalid_data

        result = self.manager.load_script(filename)

        self.assertIsNone(result)
        mock_exists.assert_called_once_with(filename)
        mock_file.assert_called_once_with(filename, 'r', encoding='utf-8')
        mock_yaml.safe_load.assert_called_once()
        # Check that validation failed
        mock_log.Log.error.assert_called_once_with("Script validation error: Missing 'Product' section in script data.")

    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data=VALID_YAML_CONTENT)
    def test_load_script_success(self, mock_file, mock_exists):
        filename = "valid.yaml"
        # Simulate successful YAML load
        valid_data = yaml.safe_load(VALID_YAML_CONTENT) # Use real yaml to parse test data
        mock_yaml.safe_load.return_value = valid_data

        script = self.manager.load_script(filename)

        self.assertIsNotNone(script)
        self.assertIsInstance(script, Script)
        mock_exists.assert_called_once_with(filename)
        mock_file.assert_called_once_with(filename, 'r', encoding='utf-8')
        mock_yaml.safe_load.assert_called_once()
        mock_log.Log.error.assert_not_called() # No errors expected

        # Verify Script attributes
        self.assertEqual(script.name, "MyTestScript")
        self.assertEqual(script.version, "1.1")
        self.assertEqual(script.release_note, "Added feature X")
        self.assertEqual(script.pairing, 1)
        self.assertEqual(script.file_name, filename)
        self.assertEqual(script.test_mode, TEST_MODE.BOTH) # Default

        # Verify Product list
        self.assertEqual(len(script.product), 2)
        self.assertIsInstance(script.product[0], Product)
        self.assertEqual(script.product[0].model_name, "ProductTX")
        self.assertEqual(script.product[0].mac_count, 2)
        self.assertEqual(script.product[0].sn_count, 1)
        self.assertEqual(script.product[0].version, "HW1.0")
        self.assertEqual(script.product[1].model_name, "ProductRX")
        self.assertEqual(script.product[1].mac_count, 1)

        # Verify Items list
        self.assertEqual(len(script.items), 2)
        self.assertIsInstance(script.items[0], TestItems)
        self.assertEqual(script.items[0].title, "Voltage Check")
        self.assertEqual(script.items[0].retry_message, "Check power supply")
        self.assertEqual(script.items[0].valid_min, 4)
        self.assertEqual(script.items[0].valid_max, 6)
        self.assertEqual(script.items[0].unit, "V")
        self.assertEqual(script.items[0].delay, 0.5)
        self.assertEqual(script.items[0].execute, "measure_voltage.exe")
        self.assertEqual(script.items[1].title, "RSSI Check")
        self.assertEqual(script.items[1].valid_min, -60)
        self.assertEqual(script.items[1].valid_max, -30)
        self.assertEqual(script.items[1].execute, "check_rssi.py --mode $sn1")
        
        # Verify that script is stored in the manager
        self.assertIs(self.manager.script, script)

    def test_validate_script_structure(self):
        valid_data = {"Script": {}, "Product": [{}], "Items": [{}]}
        self.assertIsNone(self.manager._validate_script_structure(valid_data)) # No exception

        with self.assertRaisesRegex(ScriptValidationError, "must be a YAML object"):
            self.manager._validate_script_structure([]) # Not a dict

        with self.assertRaisesRegex(ScriptValidationError, "Missing 'Product'"):
            self.manager._validate_script_structure({"Script": {}, "Items": []})

        with self.assertRaisesRegex(ScriptValidationError, "Missing 'Product'"):
            self.manager._validate_script_structure({"Script": {}, "Product": "not a list", "Items": []})

        with self.assertRaisesRegex(ScriptValidationError, "contain an 'Items' list"):
            self.manager._validate_script_structure({"Script": {}, "Product": []})

        with self.assertRaisesRegex(ScriptValidationError, "contain an 'Items' list"):
            self.manager._validate_script_structure({"Script": {}, "Product": [], "Items": "not a list"})

    def test_parse_product(self):
        product_data = [
            {"Name": "P1", "UseMac": 1, "UseSn": 1, "Version": "v1"},
            {"Name": "P2", "UseMac": 0, "UseSn": 1, "Version": "v2", "OtherMessage": "note"}
        ]
        products = self.manager._parse_product(product_data)
        self.assertEqual(len(products), 2)
        self.assertIsInstance(products[0], Product)
        self.assertEqual(products[0].model_name, "P1")
        self.assertEqual(products[0].mac_count, 1)
        self.assertEqual(products[1].model_name, "P2")
        self.assertEqual(products[1].mac_count, 0)
        self.assertEqual(products[1].other_message, "note")

        with self.assertRaisesRegex(ScriptValidationError, "must be a YAML object"):
            self.manager._parse_product([{"Name": "P1"}, "not a dict"])

    def test_parse_items(self):
        items_data = [
            {"Title": "T1", "Valid": "10,20", "Delay": 1.2, "Execute": "E1"},
            {"Title": "T2", "Valid": "PASS", "Unit": "U2"}, # Invalid range for split
            {"Title": "T3", "Valid": "30,40", "Delay": "invalid", "Execute": "E3"} # Invalid delay
        ]
        items = self.manager._parse_items(items_data)
        self.assertEqual(len(items), 3)
        self.assertIsInstance(items[0], TestItems)
        self.assertEqual(items[0].title, "T1")
        self.assertEqual(items[0].valid_min, 10)
        self.assertEqual(items[0].valid_max, 20)
        self.assertEqual(items[0].delay, 1.2)
        self.assertEqual(items[0].execute, "E1")

        self.assertEqual(items[1].title, "T2")
        self.assertIsNone(items[1].valid_min) # Split failed
        self.assertIsNone(items[1].valid_max)
        self.assertEqual(items[1].unit, "U2")
        
        # Test handling of invalid delay value
        self.assertEqual(items[2].title, "T3")
        self.assertEqual(items[2].delay, 0.0) # Should default to 0.0 for invalid delay
        mock_log.Log.error.assert_called_with("Invalid delay value: invalid. Using default value 0.0")

        with self.assertRaisesRegex(ScriptValidationError, "must be a YAML object"):
            self.manager._parse_items([{"Title": "T1"}, "not a dict"])

    def test_valid_split(self):
        self.assertEqual(self.manager._valid_split("10,20"), (10, 20))
        self.assertEqual(self.manager._valid_split("-5,5"), (-5, 5))
        self.assertEqual(self.manager._valid_split(" 0 , 100 "), (0, 100)) # With spaces
        self.assertEqual(self.manager._valid_split("10,"), (None, None))
        self.assertEqual(self.manager._valid_split(",20"), (None, None))
        self.assertEqual(self.manager._valid_split("abc,def"), (None, None))
        self.assertEqual(self.manager._valid_split("10"), (None, None))
        self.assertEqual(self.manager._valid_split(""), (None, None))
        self.assertEqual(self.manager._valid_split(None), (None, None))
    
if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
import unittest
import re
from unittest.mock import patch, MagicMock

import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
sys.path.append(project_root)

# Assuming commonUtils.py is in a reachable path, adjust import as needed
from src.utils import commonUtils
from src.utils.commonUtils import ItemResult, validate_barcode

# Mock QObject and Signal for _Signals if strict Qt testing isn't needed
commonUtils.QObject = MagicMock()
commonUtils.Signal = MagicMock()

class TestItemResult(unittest.TestCase):
    def test_initialization(self):
        item = ItemResult("Title", "Unit", "10", "20", "15", True)
        self.assertEqual(item.title, "Title")
        self.assertEqual(item.unit, "Unit")
        self.assertEqual(item.min, "10")
        self.assertEqual(item.max, "20")
        self.assertEqual(item.value, "15")
        self.assertTrue(item.result)

class TestCommonUtilsValidators(unittest.TestCase):

    # --- is_mac ---
    def test_is_mac_valid(self):
        self.assertTrue(commonUtils.is_mac("00:1A:2B:3C:4D:5E"))
        self.assertTrue(commonUtils.is_mac("00-1A-2B-3C-4D-5E"))
        self.assertTrue(commonUtils.is_mac("fa:fb:fc:fd:fe:ff"))

    def test_is_mac_invalid(self):
        self.assertFalse(commonUtils.is_mac("00:1A:2B:3C:4D")) # Too short
        self.assertFalse(commonUtils.is_mac("00:1A:2B:3C:4D:5E:6F")) # Too long
        self.assertFalse(commonUtils.is_mac("00:1G:2B:3C:4D:5E")) # Invalid char G
        self.assertFalse(commonUtils.is_mac("001A2B3C4D5E")) # No separators
        self.assertFalse(commonUtils.is_mac("00:1A-2B:3C-4D:5E")) # Mixed separators
        self.assertFalse(commonUtils.is_mac(12345)) # Not a string
        self.assertFalse(commonUtils.is_mac(None))

    # --- is_mac_nosign ---
    def test_is_mac_nosign_valid(self):
        self.assertTrue(commonUtils.is_mac_nosign("001A2B3C4D5E"))
        self.assertTrue(commonUtils.is_mac_nosign("FAFBFCFDFEFF"))

    def test_is_mac_nosign_invalid(self):
        self.assertFalse(commonUtils.is_mac_nosign("001A2B3C4D5")) # Too short
        self.assertFalse(commonUtils.is_mac_nosign("001A2B3C4D5E6")) # Too long
        self.assertFalse(commonUtils.is_mac_nosign("001G2B3C4D5E")) # Invalid char G
        self.assertFalse(commonUtils.is_mac_nosign("00:1A:2B:3C:4D:5E")) # Has separators
        self.assertFalse(commonUtils.is_mac_nosign(12345)) # Not a string
        self.assertFalse(commonUtils.is_mac_nosign(None))

    # --- compare_macs ---
    def test_compare_macs_valid(self):
        self.assertTrue(commonUtils.compare_macs("00:00:00:00:00:01", "00:00:00:00:00:02"))
        self.assertTrue(commonUtils.compare_macs("000000000001", "000000000002"))
        self.assertTrue(commonUtils.compare_macs("00:00:00:00:00:FF", "00:00:00:00:01:00"))
        self.assertFalse(commonUtils.compare_macs("00:00:00:00:00:02", "00:00:00:00:00:01"))
        self.assertFalse(commonUtils.compare_macs("00:00:00:00:00:01", "00:00:00:00:00:01")) # Equal
        self.assertTrue(commonUtils.compare_macs("AABBCCDDEEFF", "aabbccddeeff0")) # Case insensitive compare value

    def test_compare_macs_invalid_format(self):
        self.assertFalse(commonUtils.compare_macs("invalid", "00:00:00:00:00:01"))
        self.assertFalse(commonUtils.compare_macs("00:00:00:00:00:01", "invalid"))
        self.assertFalse(commonUtils.compare_macs("invalid", "invalid"))

    # --- is_mac_bci ---
    def test_is_mac_bci_valid(self):
        self.assertTrue(commonUtils.is_mac_bci("00:19:AA:BB:CC:DD"))
        self.assertTrue(commonUtils.is_mac_bci("00-19-AA-BB-CC-DD"))

    def test_is_mac_bci_invalid(self):
        self.assertFalse(commonUtils.is_mac_bci("01:19:AA:BB:CC:DD")) # Wrong prefix
        self.assertFalse(commonUtils.is_mac_bci("00:1A:AA:BB:CC:DD")) # Wrong prefix
        self.assertFalse(commonUtils.is_mac_bci("0019AABBCCDD")) # No separators
        self.assertFalse(commonUtils.is_mac_bci("00:19:AA:BB:CC")) # Too short

    # --- is_mac_bci_nosign ---
    def test_is_mac_bci_nosign_valid(self):
        self.assertTrue(commonUtils.is_mac_bci_nosign("0019AABBCCDD"))

    def test_is_mac_bci_nosign_invalid(self):
        self.assertFalse(commonUtils.is_mac_bci_nosign("0119AABBCCDD")) # Wrong prefix
        self.assertFalse(commonUtils.is_mac_bci_nosign("001AAABBCCDD")) # Wrong prefix
        self.assertFalse(commonUtils.is_mac_bci_nosign("00:19:AA:BB:CC:DD")) # Has separators
        self.assertFalse(commonUtils.is_mac_bci_nosign("0019AABBCC")) # Too short

    # --- is_version ---
    def test_is_version_valid(self):
        self.assertTrue(commonUtils.is_version("1.23"))
        self.assertTrue(commonUtils.is_version("0.00"))
        self.assertTrue(commonUtils.is_version("9.99"))
        self.assertTrue(commonUtils.is_version("1-23")) # Allowing hyphen

    def test_is_version_invalid(self):
        self.assertFalse(commonUtils.is_version("1.2")) # Too short minor
        self.assertFalse(commonUtils.is_version("1.234")) # Too long minor
        self.assertFalse(commonUtils.is_version("12.34")) # Too long major
        self.assertFalse(commonUtils.is_version("1.2a")) # Invalid char
        self.assertFalse(commonUtils.is_version("1_23")) # Wrong separator

    # --- is_sn_nosign ---
    def test_is_sn_nosign_valid(self):
        self.assertTrue(commonUtils.is_sn_nosign("12345678901")) # Default length 11
        self.assertTrue(commonUtils.is_sn_nosign("12345", length=5))

    def test_is_sn_nosign_invalid(self):
        self.assertFalse(commonUtils.is_sn_nosign("1234567890")) # Too short (default)
        self.assertFalse(commonUtils.is_sn_nosign("123456789012")) # Too long (default)
        self.assertFalse(commonUtils.is_sn_nosign("1234567890A")) # Contains letter
        self.assertFalse(commonUtils.is_sn_nosign("1234", length=5)) # Too short (custom)
        self.assertFalse(commonUtils.is_sn_nosign("123456", length=5)) # Too long (custom)

    # --- is_mo ---
    def test_is_mo_valid(self):
        self.assertTrue(commonUtils.is_mo("M1234567890"))
        self.assertTrue(commonUtils.is_mo("m0987654321"))

    def test_is_mo_invalid(self):
        self.assertFalse(commonUtils.is_mo("M123456789")) # Too short
        self.assertFalse(commonUtils.is_mo("M12345678901")) # Too long
        self.assertFalse(commonUtils.is_mo("A1234567890")) # Wrong prefix
        self.assertFalse(commonUtils.is_mo("M123456789A")) # Contains letter

    # --- is_pcb ---
    def test_is_pcb_valid(self):
        self.assertTrue(commonUtils.is_pcb("Mabcdefghijklmnopqrstu")) # 21 chars
        self.assertTrue(commonUtils.is_pcb("m0123456789ABCDEFGHIJ-")) # 21 chars with numbers/hyphen
        self.assertTrue(commonUtils.is_pcb("M" + "a" * 21))

    def test_is_pcb_invalid(self):
        self.assertFalse(commonUtils.is_pcb("M" + "a" * 20)) # Too short
        self.assertFalse(commonUtils.is_pcb("M" + "a" * 22)) # Too long
        self.assertFalse(commonUtils.is_pcb("A" + "a" * 21)) # Wrong prefix
        self.assertFalse(commonUtils.is_pcb("M" + "a" * 20 + "?")) # Invalid char '?'

    # --- is_testjig ---
    def test_is_testjig_valid(self):
        self.assertTrue(commonUtils.is_testjig("TestJig123"))
        self.assertTrue(commonUtils.is_testjig("TestJig_abc"))
        self.assertTrue(commonUtils.is_testjig("TestJig")) # Matches start only

    def test_is_testjig_invalid(self):
        self.assertFalse(commonUtils.is_testjig("testjig123")) # Case sensitive if not careful (regex is case sensitive by default)
        # Let's adjust the regex in the original code to be case-insensitive
        # Or test assuming current case-sensitive:
        self.assertFalse(commonUtils.is_testjig("Test Jig 123")) # Space
        self.assertFalse(commonUtils.is_testjig("OtherTestJig")) # Doesn't start correctly

    # --- is_ip ---
    def test_is_ip_valid(self):
        self.assertTrue(commonUtils.is_ip("192.168.1.1"))
        self.assertTrue(commonUtils.is_ip("10.0.0.1"))
        self.assertTrue(commonUtils.is_ip("255.255.255.255"))
        self.assertTrue(commonUtils.is_ip("0.0.0.0"))

    def test_is_ip_invalid(self):
        self.assertFalse(commonUtils.is_ip("192.168.1.256")) # > 255
        self.assertFalse(commonUtils.is_ip("192.168.1")) # Too short
        self.assertFalse(commonUtils.is_ip("192.168.1.1.1")) # Too long
        self.assertFalse(commonUtils.is_ip("192.168.1.a")) # Invalid char
        self.assertFalse(commonUtils.is_ip("192 .168.1.1")) # Contains space

    # --- is_local_ip ---
    def test_is_local_ip_valid(self):
        self.assertTrue(commonUtils.is_local_ip("192.168.100.1"))
        self.assertTrue(commonUtils.is_local_ip("192.168.100.255"))
        self.assertTrue(commonUtils.is_local_ip("192.168.100.0"))

    def test_is_local_ip_invalid(self):
        self.assertFalse(commonUtils.is_local_ip("192.168.1.100")) # Wrong third octet
        self.assertFalse(commonUtils.is_local_ip("192.168.100.256")) # > 255
        self.assertFalse(commonUtils.is_local_ip("10.168.100.1")) # Wrong first octet

    # --- is_valid_filename --- (Basic tests, platform specifics are hard to test universally)
    @patch('platform.system')
    def test_is_valid_filename_valid(self, mock_system):
        mock_system.return_value = "Linux" # Assume Linux for base tests
        self.assertTrue(commonUtils.is_valid_filename("myfile.txt"))
        self.assertTrue(commonUtils.is_valid_filename("my_file-123"))
        self.assertTrue(commonUtils.is_valid_filename("報告")) # Unicode allowed

    @patch('platform.system')
    def test_is_valid_filename_invalid_chars(self, mock_system):
        mock_system.return_value = "Linux"
        self.assertFalse(commonUtils.is_valid_filename("my<file>.txt"))
        self.assertFalse(commonUtils.is_valid_filename("my:file.txt"))
        self.assertFalse(commonUtils.is_valid_filename("my/file.txt"))
        self.assertFalse(commonUtils.is_valid_filename("my\\file.txt"))
        self.assertFalse(commonUtils.is_valid_filename("my|file.txt"))
        self.assertFalse(commonUtils.is_valid_filename("my?file.txt"))
        self.assertFalse(commonUtils.is_valid_filename("my*file.txt"))
        self.assertFalse(commonUtils.is_valid_filename("my\"file.txt"))
        self.assertFalse(commonUtils.is_valid_filename("\x00file.txt")) # NUL char

    @patch('platform.system')
    def test_is_valid_filename_windows_specific(self, mock_system):
        mock_system.return_value = "Windows"
        self.assertFalse(commonUtils.is_valid_filename("myfile.txt.")) # Ends with dot
        self.assertFalse(commonUtils.is_valid_filename("myfile.txt ")) # Ends with space
        self.assertFalse(commonUtils.is_valid_filename("CON")) # Reserved name
        self.assertFalse(commonUtils.is_valid_filename("prn")) # Reserved name (case insensitive)
        self.assertTrue(commonUtils.is_valid_filename("ConMan")) # Not exactly reserved

    @patch('platform.system')
    def test_is_valid_filename_empty_or_dots(self, mock_system):
        mock_system.return_value = "Linux"
        self.assertFalse(commonUtils.is_valid_filename(""))
        self.assertFalse(commonUtils.is_valid_filename("."))
        self.assertFalse(commonUtils.is_valid_filename("..")) # Often problematic though allowed by regex

class TestValidateBarcode(unittest.TestCase):

    @patch('src.utils.commonUtils.is_mo')
    def test_validate_barcode_mo(self, mock_is_mo):
        validate_barcode("MO", "M1234567890")
        mock_is_mo.assert_called_once_with("M1234567890")

    @patch('src.utils.commonUtils.is_sn_nosign')
    def test_validate_barcode_sn_default_length(self, mock_is_sn):
        validate_barcode("SN", "12345678901")
        mock_is_sn.assert_called_once_with("12345678901", length=11)

    @patch('src.utils.commonUtils.is_sn_nosign')
    def test_validate_barcode_sn_custom_length(self, mock_is_sn):
        validate_barcode("SN", "12345", config={"sn_length": 5})
        mock_is_sn.assert_called_once_with("12345", length=5)

    @patch('src.utils.commonUtils.is_mac')
    @patch('src.utils.commonUtils.is_mac_nosign')
    def test_validate_barcode_mac(self, mock_is_mac_nosign, mock_is_mac):
        mock_is_mac.return_value = True
        validate_barcode("MAC", "AA:BB:CC:DD:EE:FF")
        mock_is_mac.assert_called_once_with("AA:BB:CC:DD:EE:FF")
        mock_is_mac_nosign.assert_not_called() # Short circuits

        mock_is_mac.reset_mock()
        mock_is_mac_nosign.reset_mock()
        mock_is_mac.return_value = False
        mock_is_mac_nosign.return_value = True
        validate_barcode("MAC", "AABBCCDDEEFF")
        mock_is_mac.assert_called_once_with("AABBCCDDEEFF")
        mock_is_mac_nosign.assert_called_once_with("AABBCCDDEEFF")

    @patch('src.utils.commonUtils.is_mac_bci')
    @patch('src.utils.commonUtils.is_mac_bci_nosign')
    def test_validate_barcode_mac_bci(self, mock_is_bci_nosign, mock_is_bci):
        mock_is_bci.return_value = True
        validate_barcode("MAC_BCI", "00:19:AA:BB:CC:DD")
        mock_is_bci.assert_called_once_with("00:19:AA:BB:CC:DD")
        mock_is_bci_nosign.assert_not_called()

    def test_validate_barcode_unknown_type(self):
        # Default behavior is True for unknown types in the provided code
        self.assertTrue(validate_barcode("UNKNOWN", "some_value"))

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
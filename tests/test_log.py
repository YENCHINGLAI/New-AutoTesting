import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
sys.path.append(project_root)

import unittest
import logging
import os
import time
from unittest.mock import patch, MagicMock, ANY

# Mock dependencies before import
mock_setting = MagicMock()
mock_setting.Setting = MagicMock()
mock_setting.Setting.GetLogPath = MagicMock(return_value="/fake/log/path")

sys.modules['src.config.setting'] = mock_setting

# Now import the module
from src.utils.log import Log

# Prevent actual logging setup during testing unless intended
@patch('logging.getLogger')
@patch('logging.Formatter')
@patch('logging.StreamHandler')
@patch('logging.FileHandler')
@patch('os.path.isdir')
@patch('os.makedirs')
@patch('time.strftime')
class TestLogInitialization(unittest.TestCase):

    def setUp(self):
        # Reset the initialized flag before each test
        Log._initialized = False
        Log.logger = MagicMock() # Use a fresh mock logger for each test
        Log.ch = None
        Log.fh = None
        # Reset call counts on the patched modules/functions if needed
        logging.getLogger.reset_mock()
        logging.Formatter.reset_mock()
        logging.StreamHandler.reset_mock()
        logging.FileHandler.reset_mock()
        os.path.isdir.reset_mock()
        os.makedirs.reset_mock()
        time.strftime.reset_mock()
        mock_setting.Setting.GetLogPath.reset_mock()

    def test_init_first_call(self, mock_strftime, mock_makedirs, mock_isdir,
                             mock_filehandler, mock_streamhandler, mock_formatter,
                             mock_getlogger):
        """Test the first initialization creates handlers."""
        mock_isdir.return_value = False # Simulate directory doesn't exist
        mock_strftime.return_value = "20230101"
        mock_logger_instance = MagicMock()
        mock_getlogger.return_value = mock_logger_instance
        mock_ch_instance = MagicMock()
        mock_fh_instance = MagicMock()
        mock_streamhandler.return_value = mock_ch_instance
        mock_filehandler.return_value = mock_fh_instance

        Log.init()

        mock_getlogger.assert_called_once_with('src.utils.log') # Check logger name
        mock_formatter.assert_called() # Check formatter created
        mock_formatter_instance = mock_formatter.return_value

        # Stream Handler Checks
        mock_streamhandler.assert_called_once()
        mock_ch_instance.setLevel.assert_called_once_with(logging.DEBUG)
        mock_ch_instance.setFormatter.assert_called_once_with(mock_formatter_instance)
        mock_logger_instance.addHandler.assert_any_call(mock_ch_instance)

        # File Handler Checks
        mock_setting.Setting.GetLogPath.assert_called_once()
        mock_isdir.assert_called_once_with("/fake/log/path")
        mock_makedirs.assert_called_once_with("/fake/log/path") # Called because isdir was False
        mock_strftime.assert_called_once()
        expected_log_file = "/fake/log/path/20230101.log"
        mock_filehandler.assert_called_once_with(expected_log_file, mode='a', encoding='utf-8')
        mock_fh_instance.setLevel.assert_called_once_with(logging.INFO)
        # Check formatter used for file handler (it creates a new one in the code)
        self.assertEqual(mock_formatter.call_count, 2) # One for stream, one for file
        file_formatter_instance = mock_formatter.call_args_list[1][0][0] # Get the second formatter created
        mock_fh_instance.setFormatter.assert_called_once_with(ANY) # Check setFormatter was called
        mock_logger_instance.addHandler.assert_any_call(mock_fh_instance)

        self.assertTrue(Log._initialized)
        self.assertIsNotNone(Log.ch)
        self.assertIsNotNone(Log.fh)

    def test_init_second_call(self, mock_strftime, mock_makedirs, mock_isdir,
                              mock_filehandler, mock_streamhandler, mock_formatter,
                              mock_getlogger):
        """Test that the second call to init does nothing."""
        # Simulate first call
        Log._initialized = True
        Log.logger = MagicMock()
        Log.ch = MagicMock()
        Log.fh = MagicMock()

        # Call init again
        Log.init()

        # Ensure no logging setup methods were called again
        mock_getlogger.assert_not_called()
        mock_formatter.assert_not_called()
        mock_streamhandler.assert_not_called()
        mock_filehandler.assert_not_called()
        mock_isdir.assert_not_called()
        mock_makedirs.assert_not_called()
        Log.logger.addHandler.assert_not_called()

    def test_init_directory_exists(self, mock_strftime, mock_makedirs, mock_isdir,
                                  mock_filehandler, mock_streamhandler, mock_formatter,
                                  mock_getlogger):
        """Test initialization when log directory already exists."""
        mock_isdir.return_value = True # Simulate directory exists
        mock_strftime.return_value = "20230101"
        mock_getlogger.return_value = MagicMock() # Provide logger instance

        Log.init()

        mock_setting.Setting.GetLogPath.assert_called_once()
        mock_isdir.assert_called_once_with("/fake/log/path")
        mock_makedirs.assert_not_called() # Should not be called if isdir is True
        mock_filehandler.assert_called_once() # Should still create file handler
        self.assertTrue(Log._initialized)

class TestLogMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Perform minimal init for testing methods, avoid file IO
        Log._initialized = True # Pretend it's initialized
        Log.logger = MagicMock(spec=logging.Logger) # Mock the logger object
        Log.ch = MagicMock(spec=logging.StreamHandler)
        Log.fh = MagicMock(spec=logging.FileHandler)

    def test_update_logging_level(self):
        Log.update_logging_level() # Currently hardcoded to DEBUG
        Log.logger.setLevel.assert_called_once_with(logging.DEBUG)
        Log.ch.setLevel.assert_called_once_with(logging.DEBUG)
        Log.fh.setLevel.assert_called_once_with(logging.DEBUG)

    def test_debug(self):
        Log.debug("Debug message")
        Log.logger.debug.assert_called_once_with("Debug message")

    def test_info(self):
        Log.info("Info message")
        Log.logger.info.assert_called_once_with("Info message")

    def test_warn(self):
        Log.warn("Warn message")
        Log.logger.warning.assert_called_once_with("Warn message") # Note: maps to warning

    def test_error(self):
        Log.error("Error message")
        Log.logger.error.assert_called_once_with("Error message", exc_info=False)

    def test_error_with_exc_info(self):
        Log.error("Error message with info", exc_info=True)
        Log.logger.error.assert_called_once_with("Error message with info", exc_info=True)

    @patch('logging.Formatter')
    @patch('src.utils.log.Stream2Handler') # Patch the custom handler class
    def test_install_filter(self, mock_stream2handler_class, mock_formatter):
        """Test installing the filter stream."""
        mock_stream = MagicMock() # Mock the stream object (e.g., QTextEdit)
        mock_handler_instance = MagicMock()
        mock_stream2handler_class.return_value = mock_handler_instance
        mock_formatter_instance = MagicMock()
        mock_formatter.return_value = mock_formatter_instance

        Log.install_filter(mock_stream)

        mock_stream2handler_class.assert_called_once_with(mock_stream)
        mock_formatter.assert_called_once()
        mock_handler_instance.setLevel.assert_called_once_with(logging.DEBUG)
        mock_handler_instance.setFormatter.assert_called_once_with(mock_formatter_instance)
        Log.logger.addHandler.assert_called_once_with(mock_handler_instance)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
sys.path.append(project_root)

import unittest
from unittest.mock import patch, MagicMock, ANY
from datetime import datetime

# Mock dependencies before import
mock_sqlalchemy = MagicMock()
mock_sqlalchemy_orm = MagicMock()
mock_declarative = MagicMock()

sys.modules['sqlalchemy'] = mock_sqlalchemy
sys.modules['sqlalchemy.orm'] = mock_sqlalchemy_orm
sys.modules['sqlalchemy.ext.declarative'] = mock_declarative
sys.modules['sqlalchemy.orm.session'] = MagicMock() # Mock session module if needed

# Mock other dependencies
mock_log = MagicMock()
mock_config = MagicMock()
mock_setting = MagicMock()
mock_item_result = MagicMock()
mock_setting.Setting = MagicMock()
mock_setting.Setting.GetConfigPath = MagicMock(return_value="/fake/config/path")
mock_config.config.DATABASE_PATH = "/fake/db/path/test.db"

sys.modules['src.utils.log'] = mock_log
sys.modules['src.config'] = mock_config
sys.modules['src.config.setting'] = mock_setting
sys.modules['src.utils.commonUtils'] = MagicMock()
sys.modules['src.utils.commonUtils'].ItemResult = mock_item_result

# Now import the module
from src.utils.database import DatabaseManager, TestSession, TestItemResult

# Make Base a MagicMock so Base.metadata works
mock_declarative.declarative_base.return_value = MagicMock()

class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        # Reset mocks and instance for singleton testing
        DatabaseManager._instance = None
        mock_sqlalchemy.create_engine.reset_mock()
        mock_sqlalchemy_orm.sessionmaker.reset_mock()
        mock_declarative.declarative_base.return_value.metadata.create_all.reset_mock()
        mock_log.Log.info.reset_mock()
        mock_log.Log.error.reset_mock()
        mock_setting.Setting.GetConfigPath.reset_mock()

        # Mock session object behavior
        self.mock_session_instance = MagicMock()
        self.mock_session_maker = MagicMock(return_value=self.mock_session_instance)
        mock_sqlalchemy_orm.sessionmaker.return_value = self.mock_session_maker

        # Mock engine
        self.mock_engine = MagicMock()
        mock_sqlalchemy.create_engine.return_value = self.mock_engine

    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('os.path.isdir')
    def test_singleton(self, mock_isdir, mock_makedirs, mock_exists):
        """Test that DatabaseManager follows the singleton pattern."""
        mock_exists.return_value = True # Assume DB exists for simplicity
        mock_isdir.return_value = True
        instance1 = DatabaseManager()
        instance2 = DatabaseManager()
        self.assertIs(instance1, instance2)
        # Check initialization only happened once
        mock_sqlalchemy.create_engine.assert_called_once()

    @patch('os.path.exists', return_value=False) # DB does not exist
    @patch('os.makedirs')
    @patch('os.path.isdir', return_value=False) # Dir does not exist
    def test_initialize_database_creates_new(self, mock_isdir, mock_makedirs, mock_exists):
        """Test initialization when database and directory do not exist."""
        db_manager = DatabaseManager()

        mock_setting.Setting.GetConfigPath.assert_called_once()
        mock_isdir.assert_called_once_with("/fake/config/path")
        mock_makedirs.assert_called_once_with("/fake/config/path")
        mock_exists.assert_called_once_with(mock_config.config.DATABASE_PATH)
        mock_sqlalchemy.create_engine.assert_called_once_with(f'sqlite:///{mock_config.config.DATABASE_PATH}')
        mock_sqlalchemy_orm.sessionmaker.assert_called_once_with(bind=self.mock_engine)
        # Base.metadata.create_all should be called
        mock_declarative.declarative_base.return_value.metadata.create_all.assert_called_once_with(self.mock_engine)
        mock_log.Log.info.assert_any_call("Database created and tables initialized.")
        self.assertIsNotNone(db_manager.engine)
        self.assertIsNotNone(db_manager.Session)

    @patch('os.path.exists', return_value=True) # DB exists
    @patch('os.makedirs')
    @patch('os.path.isdir', return_value=True) # Dir exists
    def test_initialize_database_connects_existing(self, mock_isdir, mock_makedirs, mock_exists):
        """Test initialization when database already exists."""
        db_manager = DatabaseManager()

        mock_makedirs.assert_not_called()
        mock_exists.assert_called_once_with(mock_config.config.DATABASE_PATH)
        mock_sqlalchemy.create_engine.assert_called_once_with(f'sqlite:///{mock_config.config.DATABASE_PATH}')
        mock_sqlalchemy_orm.sessionmaker.assert_called_once_with(bind=self.mock_engine)
        # Base.metadata.create_all should NOT be called
        mock_declarative.declarative_base.return_value.metadata.create_all.assert_not_called()
        mock_log.Log.info.assert_any_call("Database connected.")

    def test_create_test_session_success(self):
        """Test successful creation of a test session."""
        db_manager = DatabaseManager() # Initialize first
        # Mock the session ID assignment after commit
        def commit_effect():
             self.mock_session_instance.add.call_args[0][0].session_id = 123 # Assign ID to the object passed to add()
        self.mock_session_instance.commit.side_effect = commit_effect

        script_info = {'total_tests': 10, 'script_name': 'TestScript', 'script_version': '1.0'}
        product_info = {'mo_tx': 'M1', 'sn_tx': 'S1', 'mac_tx_1': 'MAC1', 'mac_tx_2': 'MAC2',
                        'mo_rx': 'M2', 'sn_rx': 'S2', 'mac_rx_1': 'MAC3', 'mac_rx_2': 'MAC4'}
        tester_info = {'user': 'tester', 'station': 'ST01'}
        mode = 'PAIR'

        session_id = db_manager.create_test_session(script_info, product_info, tester_info, mode)

        self.assertEqual(session_id, 123)
        self.mock_session_maker.assert_called_once() # Get a session
        self.mock_session_instance.add.assert_called_once()
        # Check the added object's attributes (optional but good)
        added_obj = self.mock_session_instance.add.call_args[0][0]
        self.assertIsInstance(added_obj, TestSession)
        self.assertEqual(added_obj.script_name, 'TestScript')
        self.assertEqual(added_obj.product_sn_tx, 'S1')
        self.assertEqual(added_obj.product_sn_rx, 'S2')
        self.assertEqual(added_obj.mode, 'PAIR')
        self.mock_session_instance.commit.assert_called_once()
        self.mock_session_instance.close.assert_called_once()
        self.mock_session_instance.rollback.assert_not_called()

    def test_create_test_session_error(self):
        """Test error handling during session creation."""
        db_manager = DatabaseManager()
        self.mock_session_instance.commit.side_effect = Exception("Commit failed")

        script_info = {}
        product_info = {}
        tester_info = {}
        mode = 'TX'

        session_id = db_manager.create_test_session(script_info, product_info, tester_info, mode)

        self.assertIsNone(session_id)
        self.mock_session_maker.assert_called_once()
        self.mock_session_instance.add.assert_called_once()
        self.mock_session_instance.commit.assert_called_once()
        self.mock_session_instance.rollback.assert_called_once() # Should rollback on error
        self.mock_session_instance.close.assert_called_once() # Should close even on error
        mock_log.Log.error.assert_called_once_with("Database session creation error: Commit failed")

    def test_update_test_session_end_success(self):
        """Test successfully updating session end time and result."""
        db_manager = DatabaseManager()
        mock_found_session = MagicMock(spec=TestSession)
        mock_query = MagicMock()
        mock_filter_by = MagicMock(return_value=mock_query)
        mock_query.first.return_value = mock_found_session
        self.mock_session_instance.query.return_value.filter_by = mock_filter_by

        session_id = 123
        end_time = datetime(2023, 1, 1, 12, 30, 0)
        final_result = True
        # Assume start_time was set during creation
        mock_found_session.start_time = datetime(2023, 1, 1, 12, 0, 0)

        db_manager.update_test_session_end(session_id, end_time, final_result)

        self.mock_session_maker.assert_called_once()
        self.mock_session_instance.query.assert_called_once_with(TestSession)
        mock_filter_by.assert_called_once_with(session_id=session_id)
        mock_query.first.assert_called_once()

        self.assertEqual(mock_found_session.end_time, end_time)
        self.assertEqual(mock_found_session.total_time_sec, 1800.0) # 30 minutes
        self.assertTrue(mock_found_session.final_result)
        self.mock_session_instance.commit.assert_called_once()
        self.mock_session_instance.close.assert_called_once()

    def test_update_test_session_end_not_found(self):
        """Test updating when session ID is not found."""
        db_manager = DatabaseManager()
        mock_query = MagicMock()
        mock_filter_by = MagicMock(return_value=mock_query)
        mock_query.first.return_value = None # Simulate not found
        self.mock_session_instance.query.return_value.filter_by = mock_filter_by

        db_manager.update_test_session_end(999, datetime.now(), False)

        self.mock_session_maker.assert_called_once()
        self.mock_session_instance.query.assert_called_once_with(TestSession)
        mock_filter_by.assert_called_once_with(session_id=999)
        mock_query.first.assert_called_once()
        self.mock_session_instance.commit.assert_not_called() # Not found, no commit
        self.mock_session_instance.close.assert_called_once()

    def test_insert_test_item_result_success(self):
        """Test successful insertion of an item result."""
        db_manager = DatabaseManager()
        item_res = mock_item_result() # Use the mocked class instance
        item_res.title = "Test Item 1"
        item_res.unit = "V"
        item_res.min = "1.0"
        item_res.max = "2.0"
        item_res.value = "1.5"
        item_res.result = True

        db_manager.insert_test_item_result(123, item_res)

        self.mock_session_maker.assert_called_once()
        self.mock_session_instance.add.assert_called_once()
        added_obj = self.mock_session_instance.add.call_args[0][0]
        self.assertIsInstance(added_obj, TestItemResult)
        self.assertEqual(added_obj.session_id, 123)
        self.assertEqual(added_obj.item_title, "Test Item 1")
        self.assertEqual(added_obj.item_value, "1.5")
        self.assertTrue(added_obj.item_result)
        self.mock_session_instance.commit.assert_called_once()
        self.mock_session_instance.close.assert_called_once()

    def test_close_connection(self):
        """Test closing the database connection."""
        db_manager = DatabaseManager() # Ensure engine is created
        db_manager.close_connection()
        self.mock_engine.dispose.assert_called_once()

    def test_close_connection_error(self):
        """Test error handling when closing connection."""
        db_manager = DatabaseManager()
        self.mock_engine.dispose.side_effect = Exception("Dispose error")
        db_manager.close_connection()
        self.mock_engine.dispose.assert_called_once()
        mock_log.Log.error.assert_called_once_with("Error closing database connection: Dispose error")

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
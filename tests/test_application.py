import unittest
from unittest.mock import patch, MagicMock, ANY
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
sys.path.append(project_root)

# Mock Qt classes before they are imported by the module under test
QtGuiMock = MagicMock()
QtCoreMock = MagicMock()
QtNetworkMock = MagicMock()

# Specific Qt classes needed
QtCoreMock.QSharedMemory = MagicMock()
QtCoreMock.Signal = MagicMock()
QtCoreMock.Qt = MagicMock()
QtNetworkMock.QLocalSocket = MagicMock()
QtNetworkMock.QLocalServer = MagicMock()
QtWidgetsMock = MagicMock()
QtWidgetsMock.QApplication = MagicMock() # Mock base class

# --- Patch the modules in sys.modules BEFORE importing application ---
import sys
sys.modules['PySide6.QtGui'] = QtGuiMock
sys.modules['PySide6.QtCore'] = QtCoreMock
sys.modules['PySide6.QtNetwork'] = QtNetworkMock
sys.modules['PySide6.QtWidgets'] = QtWidgetsMock

# Now import the module under test
from src.utils.application import SharedApplication, QSingleApplication, __version__

class TestSharedApplication(unittest.TestCase):

    def setUp(self):
        # Reset mocks for each test
        QtCoreMock.QSharedMemory.reset_mock()
        self.mock_memory_instance = QtCoreMock.QSharedMemory.return_value
        self.mock_memory_instance.isAttached.reset_mock()
        self.mock_memory_instance.detach.reset_mock()
        self.mock_memory_instance.create.reset_mock()
        self.mock_memory_instance.error.reset_mock()
        QtWidgetsMock.QApplication.reset_mock() # Reset base class mock

    def test_init_first_instance(self):
        """Test initialization when no other instance exists."""
        self.mock_memory_instance.isAttached.return_value = False
        self.mock_memory_instance.create.return_value = True
        self.mock_memory_instance.error.return_value = QtCoreMock.QSharedMemory.NoError # Or some other value != AlreadyExists

        app = SharedApplication([])

        QtCoreMock.QSharedMemory.assert_called_once_with("SharedApplication" + __version__, app)
        self.mock_memory_instance.isAttached.assert_called_once()
        self.mock_memory_instance.detach.assert_not_called() # Not attached, so no detach
        self.mock_memory_instance.create.assert_called_once_with(1)
        self.assertFalse(app.isRunning()) # Should not be running if create succeeded

    def test_init_already_exists(self):
        """Test initialization when another instance seems to exist (create fails)."""
        self.mock_memory_instance.isAttached.return_value = False
        self.mock_memory_instance.create.return_value = False # Simulate creation failure
        # Error code doesn't strictly matter here if create returns False, but we can set it
        self.mock_memory_instance.error.return_value = QtCoreMock.QSharedMemory.UnknownError

        app = SharedApplication([])

        QtCoreMock.QSharedMemory.assert_called_once_with("SharedApplication" + __version__, app)
        self.mock_memory_instance.isAttached.assert_called_once()
        self.mock_memory_instance.detach.assert_not_called()
        self.mock_memory_instance.create.assert_called_once_with(1)
        self.assertTrue(app.isRunning()) # Should be running if create failed

    def test_init_already_exists_specific_error(self):
        """Test initialization when create succeeds but error is AlreadyExists."""
        self.mock_memory_instance.isAttached.return_value = False
        self.mock_memory_instance.create.return_value = True # Simulate create success
        self.mock_memory_instance.error.return_value = QtCoreMock.QSharedMemory.AlreadyExists

        app = SharedApplication([])

        QtCoreMock.QSharedMemory.assert_called_once_with("SharedApplication" + __version__, app)
        self.mock_memory_instance.isAttached.assert_called_once()
        self.mock_memory_instance.detach.assert_not_called()
        self.mock_memory_instance.create.assert_called_once_with(1)
        self.assertTrue(app.isRunning()) # Should be running if error is AlreadyExists

    def test_init_detaches_if_attached(self):
        """Test that detach is called if isAttached returns True."""
        self.mock_memory_instance.isAttached.return_value = True
        self.mock_memory_instance.detach.return_value = True # Assume detach succeeds
        self.mock_memory_instance.create.return_value = True
        self.mock_memory_instance.error.return_value = QtCoreMock.QSharedMemory.NoError

        app = SharedApplication([])

        QtCoreMock.QSharedMemory.assert_called_once_with("SharedApplication" + __version__, app)
        self.mock_memory_instance.isAttached.assert_called_once()
        self.mock_memory_instance.detach.assert_called_once() # Should be called now
        self.mock_memory_instance.create.assert_called_once_with(1)
        self.assertFalse(app.isRunning())

class TestQSingleApplication(unittest.TestCase):

    def setUp(self):
        # Reset mocks
        QtNetworkMock.QLocalSocket.reset_mock()
        QtNetworkMock.QLocalServer.reset_mock()
        QtWidgetsMock.QApplication.reset_mock() # Reset base class mock

        self.mock_socket_out = QtNetworkMock.QLocalSocket.return_value
        self.mock_socket_out.connectToServer.reset_mock()
        self.mock_socket_out.waitForConnected.reset_mock()
        self.mock_socket_out.errorOccurred.connect.reset_mock()
        self.mock_socket_out.close.reset_mock()

        self.mock_server = QtNetworkMock.QLocalServer.return_value
        self.mock_server.listen.reset_mock()
        self.mock_server.newConnection.connect.reset_mock()
        self.mock_server.close.reset_mock()
        self.mock_server.removeServer.reset_mock()

        # Mock the QApplication instance passed to QSingleApplication
        self.app_instance = QtWidgetsMock.QApplication.return_value
        self.app_instance.aboutToQuit.connect.reset_mock()


    def test_init_first_instance(self):
        """Test when connection fails, it becomes the server."""
        self.mock_socket_out.waitForConnected.return_value = False # Simulate connection failure

        app = QSingleApplication("myApp", [])

        # Verify connection attempt
        QtNetworkMock.QLocalSocket.assert_called_once_with(app)
        self.mock_socket_out.connectToServer.assert_called_once_with("myApp")
        self.mock_socket_out.waitForConnected.assert_called_once()
        self.mock_socket_out.errorOccurred.connect.assert_called_once_with(app.handleError)
        self.mock_socket_out.close.assert_called_once() # Should close the failed outgoing socket

        # Verify server setup
        QtNetworkMock.QLocalServer.assert_called_once_with(app)
        self.mock_server.listen.assert_called_once_with("myApp")
        self.mock_server.newConnection.connect.assert_called_once_with(app._onNewConnection)
        # Verify aboutToQuit connection
        # Accessing the instance directly might be tricky if it's not stored
        # Instead, check if the connect method was called on the signal mock
        # This assumes QSingleApplication inherits from the mocked QApplication
        app.aboutToQuit.connect.assert_called_once_with(app.removeServer)

        self.assertFalse(app.isRunning())
        self.assertIsNotNone(app._socketServer)
        self.assertIsNone(app._socketOut) # Should have been deleted

    def test_init_second_instance(self):
        """Test when connection succeeds, it knows another instance is running."""
        self.mock_socket_out.waitForConnected.return_value = True # Simulate connection success

        app = QSingleApplication("myApp", [])

        # Verify connection attempt
        QtNetworkMock.QLocalSocket.assert_called_once_with(app)
        self.mock_socket_out.connectToServer.assert_called_once_with("myApp")
        self.mock_socket_out.waitForConnected.assert_called_once()
        self.mock_socket_out.errorOccurred.connect.assert_called_once_with(app.handleError)
        self.mock_socket_out.close.assert_not_called() # Should not close if connected

        # Verify server NOT setup
        QtNetworkMock.QLocalServer.assert_not_called()
        self.mock_server.listen.assert_not_called()
        app.aboutToQuit.connect.assert_not_called() # No server, no need to remove on quit

        self.assertTrue(app.isRunning())
        self.assertIsNone(app._socketServer)
        self.assertIsNotNone(app._socketOut)

    # Testing sendMessage, activateWindow, _onNewConnection, _onReadyRead etc.
    # becomes very complex due to mocking signal emissions and socket interactions
    # without a Qt event loop. Focus on the core startup logic (`isRunning`).

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
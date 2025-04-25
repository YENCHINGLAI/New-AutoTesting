import os
import sys
import socket
from enum import Enum, auto
from PySide6.QtCore import __version__ as qt_version
from src.config.setting import Setting

# general info
APP_NAME = "AutoTestingSystem"
STATION_NAME = socket.gethostname() # 取得主機名稱
REAL_VERSION = "1.00"
TIME_VERSION = "2025-04-11"
QT_VERSION = qt_version
PY_VERSION = sys.version.split()[0] # 取得 Python 版本字串
API_TOOLS_PATH = 'tools'

# rcc 路徑
STYLE_FILE  = ':styles/ui_main.qss'
ICON_FILE   = ':icons/cyp.ico'
LOGO_FILE   = ':images/cyp.png'
REPORT_FILE = ':report/report_template.html'

# log
LOG_PATH = os.path.join(Setting.GetDataPath(), Setting.GetLogPath()) 

# report
REPORT_FILE_PATH = os.path.join(Setting.GetDataPath(), 'report')
REPORT_TEMPLATE_PATH = os.path.join('res', 'report')
REPORT_TEMPLATE_FILE = 'report_template.html'
REPORT_UPLOAD_PATH = r"\\cypress\fs\生產部\公用區域\MA-Test Report"

# database
DATABASE_NAME = "results.db"
DATABASE_PATH = os.path.join(Setting.GetDataPath(),'database')

# testing mode
TESTING_BOTH = "TESTING_BOTH"
TESTING_TX_SKIP_RX = "TESTING_RX"
TESTING_RX_SKIP_TX = "TESTING_TX"
TESTING_MODE = TESTING_BOTH

#===================================================================================================
# Enums
#===================================================================================================    
class TABLE_COL(Enum):
    TITLE = 0
    UNIT = 1
    MIN_VALID = 2
    MAX_VALID = 3
    VALUE = 4
    RESULT = 5

class TEST_MODE(Enum):
    TX = auto()
    RX = auto()
    BOTH = auto()

SKIP_MODE = {
    TEST_MODE.TX: "TESTING_RX",
    TEST_MODE.RX: "TESTING_TX",
    TEST_MODE.BOTH: ""
}
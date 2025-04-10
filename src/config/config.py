import os
import sys
import socket
from PySide6.QtCore import __version__ as qt_version
from src.config.setting import Setting

# general info
UPDATE_VERSION = "1.0.0.0000"
REAL_VERSION = "1.0.0.0000"
TIME_VERSION = "2025-03-10"
QT_VERSION = qt_version
PY_VERSION = sys.version.split()[0] # 取得 Python 版本字串

API_TOOLS_PATH = 'tools'

HOST_NAME = socket.gethostname()

# report
REPORT_FILE_PATH = 'report'
REPORT_TEMPLATE_PATH = os.path.join('res', 'report')
REPORT_TEMPLATE_FILE = 'report_template_Test.html'

# database
DATABASE_NAME = "results.db"
DATABASE_PATH = os.path.join(Setting.GetConfigPath(), DATABASE_NAME)

# rcc 路徑
STYLE_FILE = ':styles/ui_main.qss'
ICON_FILE  = ':icons/cyp.ico'
LOGO_FILE  = ':images/cyp.png'
REPORT_FILE = ':report/report_template_Test.html'
import os
import enum

class Setting:
    @staticmethod
    def GetConfigPath():
        import sys
        if sys.platform == "win32":
            return "data"
        else:
            from PySide6.QtCore import QDir
            homePath = QDir.homePath()
            projectName = ".picacg"
            return os.path.join(homePath, projectName)

    @staticmethod
    def GetLogPath():
        import sys
        if sys.platform == "win32":
            return "logs"
        else:
            return os.path.join(Setting.GetConfigPath(), "logs")
        
class Result_Table(enum.Enum):
    TITLE = 0
    UNIT = 1
    MIN_VALID = 2
    MAX_VALID = 3
    VALUE = 4
    RESULT = 5
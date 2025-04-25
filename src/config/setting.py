import os
from PySide6.QtCore import QSettings

CONFIG_FILE = 'res/data/config.ini'

class Setting:
    _Setting = None     
    
    @classmethod
    def init(cls, parent=None):
        """初始化配置实例
        :param cls:
        :param parent:
        """
        if not cls._Setting:
            cls._Setting = QSettings(CONFIG_FILE, QSettings.Format.IniFormat, parent)

    @classmethod
    def value(cls, key, default=None, typ=None):
        """获取配置中的值
        :param cls:
        :param key:        键名
        :param default:    默认值
        :param typ:        类型
        """
        cls.init()
        if default is not None and typ is not None:
            return cls._Setting.value(key, default, typ)
        if default is not None:
            return cls._Setting.value(key, default)
        return cls._Setting.value(key)

    @classmethod
    def setValue(cls, key, value):
        """更新配置中的值
        :param cls:
        :param key:        键名
        :param value:      键值
        """
        cls.init()
        cls._Setting.setValue(key, value)
        cls._Setting.sync()

    @staticmethod
    def GetDataPath():
        import sys
        if sys.platform == "win32":
            return "data"
        else:
            from PySide6.QtCore import QDir
            homePath = QDir.homePath()
            projectName = ".autoTesting"
            return os.path.join(homePath, projectName)
        
    @staticmethod
    def GetLogPath():
        """
        Get the log path
        """
        import sys
        if sys.platform == "win32":
            return "logs"
        else:
            return os.path.join(Setting.GetDataPath(), "logs")
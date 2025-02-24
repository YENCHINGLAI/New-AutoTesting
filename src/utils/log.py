import logging
import os
import sys
import time
from src.utils.setting import Setting

class Log:
    logger = logging.getLogger(__name__) # 使用 __name__ 作為 logger 名稱，更清晰
    logger.setLevel(logging.DEBUG) # 預設 logger 等級

    _initialized = False # 標記是否已初始化
    ch = None # StreamHandler
    fh = None # FileHandler
        
    @classmethod # 使用 classmethod，如果需要存取 class 屬性
    def init(cls): # 方法名改為小寫開頭，更符合 Python 慣例
        if cls._initialized: # 檢查是否已初始化
            return # 如果已初始化，直接返回，避免重複初始化

        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")

        # StreamHandler (輸出到控制台)
        cls.ch = logging.StreamHandler()
        cls.ch.setLevel(logging.DEBUG) # StreamHandler 預設等級
        cls.ch.setFormatter(formatter)
        cls.logger.addHandler(cls.ch)

        # FileHandler (輸出到檔案)
        log_path = Setting.GetLogPath() # 從 Setting 取得日誌路徑
        if not os.path.isdir(log_path):
            os.makedirs(log_path)
        day = time.strftime('%Y%m%d', time.localtime(time.time()))
        log_file = os.path.join(log_path, day + ".log")
        cls.fh = logging.FileHandler(log_file, mode='a', encoding="utf-8")
        cls.fh.setLevel(logging.INFO) # FileHandler 預設等級
        file_formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s") # 變數名修改
        cls.fh.setFormatter(file_formatter)
        cls.logger.addHandler(cls.fh)

        cls._initialized = True # 標記為已初始化

    @classmethod
    def update_logging_level(cls): # 方法名改為小寫
        log_level = logging.DEBUG # 預設等級

        cls.logger.setLevel(log_level) # 直接設定 logger 的等級
        if cls.ch:
            cls.ch.setLevel(log_level) # 同步 StreamHandler 等級
        if cls.fh:
            cls.fh.setLevel(log_level) # 同步 FileHandler 等級

    @staticmethod # 如果 Debug, Info, Warn, Error 確實不需要存取 class 狀態，可以保留 staticmethod
    def debug(message): # 方法名改為小寫
        Log.logger.debug(message) # 直接使用 Log.logger

    @staticmethod
    def info(message): # 方法名改為小寫
        Log.logger.info(message) # 直接使用 Log.logger, 移除 exc_info=True

    @staticmethod
    def warn(message): # 方法名改為小寫
        Log.logger.warning(message) # 直接使用 Log.logger, 移除 exc_info=True

    @staticmethod
    def error(message, exc_info=False): # 方法名改為小寫, error 方法預設不包含 exc_info，需要時再傳入 True
        Log.logger.error(message, exc_info=exc_info) # 直接使用 Log.logger, 根據需要傳入 exc_info

    @staticmethod
    def install_filter(stream2): # 方法名改為小寫
        class Stream2Handler(logging.StreamHandler):
            def __init__(self, stream=stream2): # 直接將 stream2 傳遞給父類別
                super().__init__(stream) # 使用 super() 呼叫父類別 __init__

            def emit(self, record):
                try:
                    msg = self.format(record)
                    stream = self.stream
                    stream.write(msg + self.terminator) # 標準 stream.write 寫法，只傳遞訊息字串
                    stream.flush()
                except RecursionError:
                    raise
                except Exception:
                    self.handleError(record)

        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s", datefmt=logging.Formatter.default_time_format)
        ch2 = Stream2Handler(stream2) # 變數名修改，避免與 Init 方法中的 ch 衝突
        ch2.setLevel(logging.DEBUG)
        ch2.setFormatter(formatter)
        Log.logger.addHandler(ch2)

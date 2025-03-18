#===================================================================================================
# Import the necessary modules
#===================================================================================================
import sqlite3
import datetime
import os
# from src.utils.log import Log
# from src.config.setting import Setting

#===================================================================================================
# Execute
#===================================================================================================
class ItemResult:
    def __init__(self, title, unit, min, max, value, result):
        self.title = title
        self.unit = unit
        self.min = min
        self.max = max
        self.value = value
        self.result = result

def GetConfigPath():
        """
        Get the configuration path
        """
        import sys
        if sys.platform == "win32":
            return "data"
        else:
            from PySide6.QtCore import QDir
            homePath = QDir.homePath()
            projectName = ".picacg"
            return os.path.join(homePath, projectName)
        
class DatabaseManager:
    """
    負責 SQLite 資料庫操作的類別。
    """
    DATABASE_NAME = "results.db"
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.initialize_database()
        return cls._instance
    
    def __init__(self):
        self.conn = None
        self.cursor = None
        # self.db_path = os.path.join(Setting.GetConfigPath(), self.DATABASE_NAME) # 資料庫檔案路徑
        self.db_path = os.path.join(GetConfigPath(), self.DATABASE_NAME)

    def initialize_database(self):
        """
        初始化資料庫，如果資料庫檔案不存在則建立，並建立必要的表格。
        """
        # db_dir = Setting.GetConfigPath()
        db_dir = GetConfigPath()
        if not os.path.isdir(db_dir):
            os.makedirs(db_dir)

        db_exists = os.path.exists(self.db_path)

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        if not db_exists:
            self._create_tables()
            # Log.info("Database created and tables initialized.")
        # else:
        #     Log.info("Database connected.")

    def _create_tables(self):
        """
        建立資料庫表格 (如果不存在)。
        """
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_sessions (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    script_name TEXT NOT NULL,
                    product_model TEXT,
                    product_sn TEXT,
                    product_mac TEXT,
                    tester_user TEXT,
                    station TEXT,
                    mode TEXT,
                    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    end_time DATETIME,
                    final_result TEXT
                )
            ''')
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_items_results (
                    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    item_title TEXT NOT NULL,
                    item_unit TEXT,
                    item_min_valid TEXT,
                    item_max_valid TEXT,
                    item_value TEXT,
                    item_result TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES test_sessions(session_id)
                )
            ''')
            self.conn.commit()
            # Log.info("Tables 'test_sessions' and 'test_items_results' created.")
        except sqlite3.Error as e:
            # Log.error(f"Database table creation error: {e}")
            if self.conn:
                self.conn.rollback()
            raise

    def create_test_session(self, script_name, product_info, tester_info, mode):
        """
        建立新的測試 Session，並返回 session_id。
        """
        try:
            self.cursor.execute('''
                INSERT INTO test_sessions (script_name, product_model, product_sn, product_mac, tester_user, station, mode)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (script_name, product_info.get('model_name'), product_info.get('serial_number'), product_info.get('mac_address'), tester_info.get('user'), tester_info.get('station'), mode))
            self.conn.commit()
            return self.cursor.lastrowid # 返回剛剛插入的 rowid (session_id)
        except sqlite3.Error as e:
            # Log.error(f"Database session creation error: {e}")
            if self.conn:
                self.conn.rollback()
            return None

    def update_test_session_end(self, session_id, final_result):
        """
        更新測試 Session 的結束時間和最終結果。
        """
        try:
            self.cursor.execute('''
                UPDATE test_sessions
                SET end_time = ?, final_result = ?
                WHERE session_id = ?
            ''', (datetime.datetime.now(), final_result, session_id))
            self.conn.commit()
        except sqlite3.Error as e:
            # Log.error(f"Database session update error: {e}")
            if self.conn:
                self.conn.rollback()

    def insert_test_item_result(self, session_id, item_result):
        """
        插入單個測試項目的結果。
        """
        try:
            self.cursor.execute('''
                INSERT INTO test_items_results (session_id, item_title, item_unit, item_min_valid, item_max_valid, item_value, item_result)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, item_result.title, item_result.unit, item_result.min, item_result.max, item_result.value, item_result.result))
            self.conn.commit()
        except sqlite3.Error as e:
            # Log.error(f"Database item result insertion error: {e}")
            if self.conn:
                self.conn.rollback()

    def close_connection(self):
        """
        關閉資料庫連線。
        """
        if self.conn:
            try:
                self.conn.commit()
                self.conn.close()
            except sqlite3.Error as e:
                Log.error(f"Error closing database connection: {e}")

if __name__ == "__main__":
    db_manager = DatabaseManager()
    db_manager.initialize_database()

    product_info = { # 產品資訊，之後可以從UI介面取得
                'model_name': 'N2612345',
                'serial_number': 'S1234567890', # 假設使用 TX 模組的 SN 作為產品 SN
                'mac_address': "F8:12:34:56:78:90" # 假設使用 TX 模組的 MAC1 作為產品 MAC
            }
    
    tester_info = {  # 測試人員資訊，之後可以從登入資訊或設定檔取得
                'user': "TESTER_01", # 假設 User GroupBox 的 帳號 作為使用者名稱
                'station': 'AUTOTEST_01' # 假設 User GroupBox 的 標題 作為站點名稱
            }

     # 建立測試 session 並取得 session_id
    test_session_id = db_manager.create_test_session(
        script_name="TestScript",
        product_info=product_info, # 使用 MainWindow 傳遞的 product_info
        tester_info=tester_info ,   # 使用 MainWindow 傳遞的 tester_info
        mode="Auto"
        )
    if test_session_id is None:
        print("Failed to create test session in database.")

    item_result_obj = ItemResult("Item_01", "N/A", "99", "1000", "123", "Pass") 

    db_manager.insert_test_item_result(test_session_id, item_result_obj) # 寫入資料庫

    db_manager.update_test_session_end(test_session_id, "Pass") # 更新 session 結束時間和結果

    db_manager.close_connection()
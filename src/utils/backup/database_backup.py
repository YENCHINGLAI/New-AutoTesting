#===================================================================================================
# Import the necessary modules
#===================================================================================================

import os
import datetime
import sqlite3

from src.utils.log import Log
from src.config import config
from src.config.setting import Setting
from src.utils.commonUtils import ItemResult

#===================================================================================================
# Execute
#===================================================================================================
class DatabaseManager:
    """
    負責 SQLite 資料庫操作的類別。
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.initialize_database()
        return cls._instance
    
    def __init__(self):
        self.conn = None
        self.cursor = None

    def initialize_database(self):
        """
        初始化資料庫，如果資料庫檔案不存在則建立，並建立必要的表格。
        """
        db_dir = Setting.GetDataPath()
        if not os.path.isdir(db_dir):
            os.makedirs(db_dir)

        db_exists = os.path.exists(config.DATABASE_PATH)
        
        self.conn = sqlite3.connect(config.DATABASE_PATH)
        self.cursor = self.conn.cursor()

        if not db_exists:
            self._create_tables()
            Log.info("Database created and tables initialized.")
        else:
            Log.info("Database connected.")

    def _create_tables(self):
        """
        建立資料庫表格 (如果不存在)。
        """
        try:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_sessions (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    runcard TEXT NOT NULL,
                    total_tests INTEGER,                    
                    script_version TEXT NOT NULL,      
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
        except sqlite3.Error as e:
            if self.conn:
                self.conn.rollback()
            raise

    def create_test_session(self, script_info, product_info, tester_info, mode):
        """
        建立新的測試 Session，並返回 session_id。
        """
        try:
            self.cursor.execute('''
                INSERT INTO test_sessions (
                                runcard, total_tests, script_version, 
                                product_model, product_sn, product_mac, 
                                tester_user, station, mode
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (script_info.get('runcard'), script_info.get('total_tests'), script_info.get('script_version'),
                  product_info.get('model_name'), product_info.get('serial_number'), product_info.get('mac_address'), 
                  tester_info.get('user'), tester_info.get('station'), mode))
            self.conn.commit()
            return self.cursor.lastrowid # 返回剛剛插入的 rowid (session_id)
        except sqlite3.Error as e:
            Log.error(f"Database session creation error: {e}")
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

    def insert_test_item_result(self, session_id, item_result: ItemResult):
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
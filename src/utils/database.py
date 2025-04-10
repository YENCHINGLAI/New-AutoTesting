#===================================================================================================
# Import the necessary modules
#===================================================================================================
import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func

from src.utils.log import Log
from src.config import config
from src.config.setting import Setting
from src.utils.commonUtils import ItemResult

#===================================================================================================
# Define SQLAlchemy Models
#===================================================================================================
Base = declarative_base()

class TestSession(Base):
    __tablename__ = 'test_sessions'
    
    session_id = Column(Integer, primary_key=True, autoincrement=True)
    runcard = Column(Text, nullable=False)
    total_tests = Column(Integer)
    script_version = Column(Text, nullable=False)
    product_model = Column(Text)
    product_sn = Column(Text)
    product_mac = Column(Text)
    tester_user = Column(Text)
    station = Column(Text)
    mode = Column(Text)
    start_time = Column(DateTime, default=func.current_timestamp())
    end_time = Column(DateTime)
    final_result = Column(Text)
    
    # 定義與 TestItemResult 的關聯關係
    items = relationship("TestItemResult", back_populates="session")
    
class TestItemResult(Base):
    __tablename__ = 'test_items_results'
    
    result_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('test_sessions.session_id'))
    item_title = Column(Text, nullable=False)
    item_unit = Column(Text)
    item_min_valid = Column(Text)
    item_max_valid = Column(Text)
    item_value = Column(Text)
    item_result = Column(Text)
    timestamp = Column(DateTime, default=func.current_timestamp())
    
    # 定義與 TestSession 的關聯關係
    session = relationship("TestSession", back_populates="items")

#===================================================================================================
# Execute
#===================================================================================================

class DatabaseManager:
    """
    負責 SQLite 資料庫操作的類別，使用 SQLAlchemy ORM。
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.initialize_database()
        return cls._instance
    
    def __init__(self):
        self.engine = None
        self.Session = None
        self.db_session = None

    def initialize_database(self):
        """
        初始化資料庫，如果資料庫檔案不存在則建立，並建立必要的表格。
        """
        db_dir = Setting.GetConfigPath()
        if not os.path.isdir(db_dir):
            os.makedirs(db_dir)

        db_exists = os.path.exists(config.DATABASE_PATH)
        
        self.engine = create_engine(f'sqlite:///{config.DATABASE_PATH}')
        self.Session = sessionmaker(bind=self.engine)

        if not db_exists:
            Base.metadata.create_all(self.engine)  # 建立所有表格
            Log.info("Database created and tables initialized.")
        else:
            Log.info("Database connected.")

    def create_test_session(self, script_info, product_info, tester_info, mode):
        """
        建立新的測試 Session，並返回 session_id。
        """
        try:
            session = self.Session()
            new_session = TestSession(
                runcard=script_info.get('runcard'),
                total_tests=script_info.get('total_tests'),
                script_version=script_info.get('script_version'),
                product_model=product_info.get('model_name'),
                product_sn=product_info.get('serial_number'),
                product_mac=product_info.get('mac_address'),
                tester_user=tester_info.get('user'),
                station=tester_info.get('station'),
                mode=mode
            )

            session.add(new_session)
            session.commit()
            session_id = new_session.session_id  # 獲取剛剛插入的 session_id
            session.close()
            return session_id
        except Exception as e:
            Log.error(f"Database session creation error: {e}")
            if session:
                session.rollback()
                session.close()
            return None

    def update_test_session_end(self, session_id, final_result):
        """
        更新測試 Session 的結束時間和最終結果。
        """
        try:
            session = self.Session()
            test_session = session.query(TestSession).filter_by(session_id=session_id).first()
            if test_session:
                test_session.end_time = datetime.datetime.now()
                test_session.final_result = final_result
                session.commit()
            
            session.close()
        except Exception as e:
            Log.error(f"Database session update error: {e}")
            if session:
                session.rollback()
                session.close()
            return None

    def insert_test_item_result(self, session_id, item_result: ItemResult):
        """
        插入單個測試項目的結果。
        """
        try:
            session = self.Session()
            
            new_item_result = TestItemResult(
                session_id=session_id,
                item_title=item_result.title,
                item_unit=item_result.unit,
                item_min_valid=item_result.min,
                item_max_valid=item_result.max,
                item_value=item_result.value,
                item_result=item_result.result
            )
            
            session.add(new_item_result)
            session.commit()
            session.close()
        except Exception as e:
            Log.error(f"Database item result insertion error: {e}")
            if session:
                session.rollback()
                session.close()

    def close_connection(self):
        """
        關閉資料庫連線。
        """
        if self.engine:
            try:
                self.engine.dispose()  # 關閉 SQLAlchemy 引擎
            except Exception as e:
                Log.error(f"Error closing database connection: {e}")
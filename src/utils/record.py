#===================================================================================================
# Import the necessary modules
#===================================================================================================
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from src.utils.log import Log
from src.config import config
from src.utils.commonUtils import ItemResult
from src.utils.database import DatabaseManager
from src.utils.script import Script

#===================================================================================================
# Execute
#===================================================================================================
class TestReport:
    def __init__(self, script: Script, runcard, mac, sn, tester_name, station, mode):
        """
        初始化測試報告。

        Args:
            script (Script):        腳本版本 (用於資料庫)
            runcard (str):          (Optional) Runcard info, currently not used here.
            product_name (str):     產品名稱
            mac (str):              MAC 位址
            sn (str):               序號
            version (str):          版本號
            tester_name (str):      測試人員名稱
            station (str):          測試站名稱
            mode (str):             測試模式
        """
        # --- Basic Info ---
        self.script = script
        self.product_name = self.script.product.model_name if script else 'N/A'
        self.mac = mac
        self.sn = sn
        self.version = self.script.version if script else 'N/A'
        self.runcard = runcard

        # --- Tester Info ---
        self.tester_name = tester_name
        self.station = station
        self.mode = mode

        # --- Date info ---
        self.test_date = datetime.now()  # 取得當前日期時間
        self.test_date_str = self.test_date.strftime("%Y-%m-%d")  # 格式化日期
        self.start_time = datetime.now()  # 取得當前日期時間
        self.start_time_str = self.start_time.strftime("%H:%M:%S")  # 格式化時間
        self.end_time = None
        self.end_time_str = None
        self.total_time = None
        self.total_time_str = None

        # --- Test Summary ---
        self.total_tests_count = 0
        self.fail_tests_count = 0
        self.pass_tests_count = 0
        self.final_result = True
        self.items_result = []

        # --- Database Integration ---
        self.db_manager = None
        self.db_session_id = None

        self.db_init()

    def db_init(self):
        """
        初始化資料庫連線，並建立新的測試 Session。
        """
        try:
            Log.debug("Initializing database connection...")
            self.db_manager = DatabaseManager()
            self.db_manager.initialize_database()

            ##db 還沒新增資料表，這邊會報錯##
            script_in_for_db = {
                "script_version": self.script.version,
                "total_tests": len(self.script.items),
                "runcard": self.runcard,
            }

            product_in_for_db = {
                "model_name": self.product_name,
                "serial_number": self.sn,
                "mac_address": self.mac
            }

            tester_in_for_db = {
                "user": self.tester_name,
                "station": self.station
            }

            # 建立資料庫連線
            Log.debug(f"Creating test session in database for '{self.script.version}'...")
            self.db_session_id = self.db_manager.create_test_session(
                script_info = script_in_for_db,
                product_info = product_in_for_db,
                tester_info = tester_in_for_db,
                mode = self.mode
                )
            
            if self.db_session_id is not None:
                Log.info(f"Database test session created successfully with ID: {self.db_session_id}")
            else:
                Log.error("Failed to create database test session.")
                # Continue without DB logging if session creation fails
        except Exception as e:
            Log.error(f"Unexpected error during TestReport initialization: {e}", exc_info=True)
            self.db_manager = None
            self.db_session_id = None

    def add_test_result(self, item_result : ItemResult):
        """
        新增測試結果

        Param:    items_result (ItemResult): 單個測試項目的結果對象
        """
        self.items_result.append(item_result)  # 將測試結果加入列表
        Log.debug(f"Added item result '{item_result.title}' to internal list.")

        self.db_add_test_result(item_result)  # 將測試結果寫入資料庫

    def db_add_test_result(self, item_result : ItemResult):
        """
        新增測試結果到資料庫

        Param:    items_result (ItemResult): 單個測試項目的結果對象
        """
        if self.db_manager and self.db_session_id is not None:
            try:
                db_items_result_str = "Pass" if item_result.result else "Fail"
                # 將測試結果轉換為資料庫格式
                db_item = ItemResult(
                    title=item_result.title,
                    unit=item_result.unit,
                    min_val=item_result.min,
                    max_val=item_result.max,
                    value=item_result.value,
                    result=db_items_result_str
                )
                # 將測試結果寫入資料庫
                Log.debug(f"Inserting item result '{item_result.title}' into database (Session ID: {self.db_session_id}).")
                self.db_manager.insert_test_item_result(self.db_session_id, db_item)
            except Exception as err:
                Log.error(f"Database error inserting item result '{item_result.title}': {err}", exc_info=True)
        else:
            Log.warn(f"Cannot save item result '{item_result.title}' to database: DB session not available.")
    
    def End_Record_and_Create_Report(self, final_result, total_items, pass_items, fail_items):
        """
        設定測試結束時間、最終結果，更新資料庫 Session，並生成 HTML 報告。

        Args:
            total_items (int): 執行的總項目數。
            pass_items (int): 通過的項目數。
            fail_items (int): 失敗的項目數。
        """
        Log.info("Ending test record and creating report...")

        self.end_time = datetime.now()  # 取得當前日期時間
        self.end_time_str = self.end_time.strftime("%H:%M:%S")  # 格式化時間
        self._calculate_total_time()  # 計算測試總時間

        self.total_tests_count = total_items  # 設定總測試次數
        self.fail_tests_count  = fail_items  # 設定失敗次數
        self.pass_tests_count  = pass_items  # 設定通過次數

        # 最終測試結果
        # self.final_result = (self.fail_tests_count == 0 and self.pass_tests_count == self.total_tests_count and self.total_tests_count > 0)
        self.final_result = final_result  # 使用傳入的最終結果
        Log.info(f"Test finished: {self.final_result}, {self.total_tests_count} tests, {self.fail_tests_count} failed, {self.pass_tests_count} Passed")
        
        # --- Update Database Session ---
        if self.db_manager and self.db_session_id is not None:
            try:
                final_result_db_str = "Pass" if self.final_result else "Fail"
                Log.info(f"Updating database test session {self.db_session_id} with end time and result '{final_result_db_str}'.")
                self.db_manager.update_test_session_end(self.db_session_id, final_result_db_str)
            except Exception as e:
                 Log.error(f"Unexpected error updating session end for ID {self.db_session_id}: {e}", exc_info=True)
        else:
            Log.warn("Cannot update database session end: DB session not available.")

        # --- Generate HTML Report ---
        return self._generate_report()  # 生成報告

    def _calculate_total_time(self):
        """
        計算測試總時間。
        """
        if self.start_time is not None and self.end_time is not None:
            time_diff = self.end_time - self.start_time
            # Format timedelta to hh:mm:ss.sss
            total_seconds = time_diff.total_seconds()
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.total_time_str = "{:02}:{:02}:{:06.3f}".format(int(hours), int(minutes), seconds)
            self.total_time = time_diff # Store the timedelta object if needed
            Log.debug(f"Calculated total time: {self.total_time_str}")
        else:
             self.total_time_str = "N/A"
             Log.warn("Could not calculate total time: start or end time missing.")

    def _generate_report(self, filename=None):
        """
        生成 HTML 報告 (使用更漂亮的模板)

        Args:
            test_results (list): 包含測試結果的列表。
        """
        try:
            template = self._load_template()        
            report_data = self._create_data() # 準備要傳遞給模板的資料       
            html_output = template.render(**report_data) # 渲染模板
            return self._create_file(filename, html_output)
        except Exception as e:
            Log.error(f"生成報告時發生錯誤: {e}")
            return False
        
    def _load_template(self):
        Log.debug(f"Loading report template from: {config.REPORT_TEMPLATE_PATH}, file: {config.REPORT_TEMPLATE_FILE}")
        env = Environment(loader=FileSystemLoader(config.REPORT_TEMPLATE_PATH))         # 設定 Jinja2 環境
        return env.get_template(config.REPORT_TEMPLATE_FILE)                            # 載入新的模板
    
    def _create_data(self):
        duts_for_template = [
             # Example: Using the primary info passed during init for the first DUT
            {'name': f"{self.product_name}-Primary", # Add descriptive name
             'sn': self.sn,
             'macs': [self.mac] if self.mac else [], # Make MACs a list
             'version': self.version},

            # Add other DUTs here if your application tracks them
             {'name': 'N2622-Secondary', # Placeholder for a second DUT
              'sn': 'SN_RX_PLACEHOLDER',
              'macs': ['MAC_RX_PLACEHOLDER'],
              'version': 'v2.PLACEHOLDER'}
        ]

         # Filter out DUTs with no useful info (optional)
        duts_for_template = [dut for dut in duts_for_template if dut.get('sn') or dut.get('macs')]

        report_data = {
            "report_title": "Test Report",  # 報告標題
            "product_name": self.product_name,

            # --- Pass the list of DUTs ---
            'duts': duts_for_template,
            
            # --- Tester Info ---
            "tester_name": self.tester_name,
            "station": self.station,
            "mode": self.mode,

            # --- Date info ---
            "test_date": self.test_date_str,
            "start_time": self.start_time_str,
            "end_time": self.end_time_str,
            "total_time": self.total_time_str,

            # --- Test Summary ---
            "total_tests": self.total_tests_count,
            "pass_tests": self.pass_tests_count,
            "fail_tests": self.fail_tests_count,
            "final_result": self.final_result,

            # --- Test Results ---
            "test_results": self.items_result,
        }
        return report_data
    
    def _create_file(self, filename, output_data):
        try:
            os.makedirs(config.REPORT_FILE_PATH, exist_ok=True)

            if filename is None:
                station_str = self.station if self.station else "NoStation"
                safe_sn = "".join(c if c.isalnum() else "_" for c in self.sn) if self.sn else "NoSN"
                timestamp_str = self.start_time.strftime("%Y%m%d_%H%M%S")
                filename = f"{station_str}_{safe_sn}_{timestamp_str}"      
            file_path = os.path.join(config.REPORT_FILE_PATH, f"{filename}.html")

            # 寫入檔案
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(output_data)
            
            Log.info(f"HTML 報告已生成: {file_path}")           
            return True
        except IOError as io_err:
            Log.error(f"File I/O error creating report file '{file_path}': {io_err}", exc_info=True)
            return False # Indicate failure
        except Exception as e:
            Log.error(f"生成報告時發生錯誤: '{file_path}': {e}", exc_info=True)
            return False # Indicate failure
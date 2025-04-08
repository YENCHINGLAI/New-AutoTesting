#===================================================================================================
# Import the necessary modules
#===================================================================================================
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from src.utils.log import Log
from src.config import config
from src.utils.database import DatabaseManager

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

class TestReport:
    def __init__(self, runcard, product_name, mac, sn, version, tester_name, station, mode):
        """
        初始化測試報告。

        Args:
            product_name (str):     產品名稱
            mac_address (str):      MAC 位址
            serial_number (str):    序號
            version (str):          版本號
            tester_name (str):      測試人員名稱
            station (str):          測試站名稱
            mode (str):             測試模式
        """
        # --- Device Info ---
        self.product_name = product_name
        self.mac_address = mac
        self.serial_number = sn
        self.version = version
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

        # --- database init ---
        # self.db = DatabaseManager()
        # self.db.initialize_database()

    def add_test_result(self, items_result : ItemResult):
        """
        新增測試結果

        Param:    items_result (ItemResult): 單個測試項目的結果對象
        """
        self.items_result.append(items_result)  # 將測試結果加入列表

    def End_Record_and_Create_Report(self, all_items, all_pass, all_fail):
        """
        設定測試結束
        """
        self.end_time = datetime.now()  # 取得當前日期時間
        self.end_time_str = self.end_time.strftime("%H:%M:%S")  # 格式化時間
        self._calculate_total_time()  # 計算測試總時間

        self.total_tests_count = all_items  # 設定總測試次數
        self.fail_tests_count= all_fail  # 設定失敗次數
        self.pass_tests_count = all_pass  # 設定通過次數

        # 最終測試結果
        self.final_result = (self.fail_tests_count == 0 and self.pass_tests_count == self.total_tests_count and self.total_tests_count > 0)

        Log.info(f"Test finished: {self.final_result}, {self.total_tests_count} tests, {self.fail_tests_count} failed, {self.pass_tests_count} Passed")
        
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

            # 準備要傳遞給模板的資料
            report_data = self._create_data()
            
            # 渲染模板
            html_output = template.render(**report_data)

            return self._create_file(filename, html_output)
        except Exception as e:
            Log.error(f"生成報告時發生錯誤: {e}")
            return False
        
    def _load_template(self):
        env = Environment(loader=FileSystemLoader(config.REPORT_TEMPLATE_PATH))         # 設定 Jinja2 環境
        return env.get_template(config.REPORT_TEMPLATE_FILE)                            # 載入新的模板
    
    def _create_data(self):
        return {
            "report_title": "Test Report",  # 報告標題
            # 'duts': [{'name': 'N2612', 'sn': '0987654321', 'macs': ['MAC1a', 'MAC1b'], 'version': 'v1.10'},],
            # Fake info
            'duts': [{'name': 'N2612', 'sn': '0987654321', 'macs': ['MAC1a', 'MAC1b'], 'version': 'v1.10'}, 
                                   {'name': 'N2622', 'sn': '1234567890', 'macs': ['MAC2a'], 'version': 'v2.10'}],

            # --- Device Info ---
            "product_name": self.product_name,
            "mac_address": self.mac_address,
            "serial_number": self.serial_number,
            "version": self.version,
            
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
    
    def _create_file(self, filename, output_data):
        try:
            os.makedirs(config.REPORT_FILE_PATH, exist_ok=True)
            if filename is None:
                filename = f"report_{self.test_date_str}_{self.start_time_str.replace(':', '-')}"      
            file_name = os.path.join(config.REPORT_FILE_PATH, f"{filename}.html")

            # 寫入檔案
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(output_data)
            
            Log.info(f"HTML 報告已生成: {file_name}")           
            return True
        except Exception as e:
            Log.error(f"生成報告時發生錯誤: {e}")
            return False
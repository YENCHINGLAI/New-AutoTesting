
import os
import datetime  # 導入 datetime 模組
from PySide6.QtCore import QFile, QTextStream
from jinja2 import Environment, FileSystemLoader
from src.utils.log import Log

FILE_PATH = 'report'
TEMPLATE_PATH = os.path.join('res', 'report')

class ItemResult:
    def __init__(self, title, unit, min, max, value, result):
        self.title = title
        self.unit = unit
        self.min = min
        self.max = max
        self.value = value
        self.result = result

class TestReport:
    def __init__(self, product_name, mac_address, serial_number, version, tester_name, station, mode):
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
        self.mac_address = mac_address
        self.serial_number = serial_number
        self.version = version
        # --- Tester Info ---
        self.tester_name = tester_name
        self.station = station
        self.mode = mode
        # --- Date info ---
        self.test_date = datetime.datetime.now()  # 取得當前日期時間
        self.test_date_str = self.test_date.strftime("%Y-%m-%d")  # 格式化日期
        self.start_time = datetime.datetime.now()  # 取得當前日期時間
        self.start_time_str = self.start_time.strftime("%H:%M:%S")  # 格式化時間
        self.end_time = None
        self.end_time_str = None
        self.total_time = None
        self.total_time_str = None
        # --- Test Summary ---
        self.total_tests_count = 0
        self.fail_tests_count = 0
        self.final_result_str = True
        self.test_results = []

    def add_test_result(self, items_result : ItemResult):
        """
        新增測試結果。

        Args:
            test_result (bool): 測試結果 (True: 通過, False: 失敗)
        """
        self.test_results.append(items_result)  # 將測試結果加入列表
        
        if not items_result.result:  # 如果測試結果為 False
            self.fail_tests_count += 1  # 失敗次數加 1
        self.total_tests_count += 1  # 總測試次數加 1

    def set_end(self, all_items):
        """
        設定測試結束
        """
        self.end_time = datetime.datetime.now()  # 取得當前日期時間
        self.end_time_str = self.end_time.strftime("%H:%M:%S")  # 格式化時間

        self.calculate_total_time()  # 計算測試總時間
        self.final_result_str = self.fail_tests_count == 0 and self.total_tests_count == all_items # 最終測試結果
        Log.info(f"Test finished: {self.final_result_str}, {self.total_tests_count} tests, {self.fail_tests_count} failed, {all_items} All items")
        
        return self.generate_report()  # 生成報告

    def calculate_total_time(self):
        """
        計算測試總時間。
        """
        if self.start_time is not None and self.end_time is not None:
            self.total_time = self.end_time - self.start_time
            self.total_time_str = str(self.total_time)

    def load_stylesheet(self, filename):
        """從指定文件加載並應用 Qt 樣式表。
        Args:
            filename (str): 樣式表文件的路徑
        """
        style_file = QFile(filename)
        if style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
            stream = QTextStream(style_file)
            source = stream.readAll()
            style_file.close()
            return source
        else:
            print(f"無法打開樣式表文件: {filename}")

    def generate_report(self):
        """
        生成 HTML 報告 (使用更漂亮的模板)。

        Args:
            test_results (list): 包含測試結果的列表。
        """
        try:
            # 設定 Jinja2 環境
            env = Environment(loader=FileSystemLoader(TEMPLATE_PATH))
            template = env.get_template('report_template.html') # 載入新的模板

            # 準備要傳遞給模板的資料
            report_data = {
                "report_title": "Cypress Test Report",  # 報告標題
                # --- Device Info ---
                "product_name": self.product_name, # 傳遞 Product Name 變數
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
                "fail_tests": self.fail_tests_count,
                "final_result": self.final_result_str,
                # --- Test Results ---
                "test_results": self.test_results,
            }

            # 渲染模板
            html_output = template.render(**report_data)

            os.makedirs(FILE_PATH, exist_ok=True)
            file_name = os.path.join(FILE_PATH,"test_report.html")

            # 寫入檔案
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(html_output)

            print(f"HTML 報告已生成: {file_name}")
            return True

        except Exception as e:
            print(f"生成報告時發生錯誤: {e}")
            return False
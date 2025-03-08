from jinja2 import Environment, FileSystemLoader
import datetime  # 導入 datetime 模組
import os
import sys
# 切換到程式所在目錄
abs_pth = os.path.abspath(sys.argv[0])
working_dir = os.path.dirname(abs_pth)
os.chdir(working_dir)

class TestReport:
    def __init__(self, product_name, mac_address, serial_number, version, tester_name, station, mode):
        """
        初始化測試報告。

        Args:
            product_name (str): 產品名稱。
            mac_address (str): MAC 位址。
            serial_number (str): 序號。
            version (str): 版本號。
            tester_name (str): 測試人員名稱。
            station (str): 測試站名稱。
            mode (str): 測試模式。
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

    def set_end_time(self):
        """
        設定測試結束時間。
        """
        self.end_time = datetime.datetime.now()  # 取得當前日期時間
        self.end_time_str = self.end_time.strftime("%H:%M:%S")  # 格式化時間

    def calculate_total_time(self):
        """
        計算測試總時間。
        """
        if self.start_time is not None and self.end_time is not None:
            self.total_time = self.end_time - self.start_time
            self.total_time_str = str(self.total_time)

    def generate_html_report(self, test_results):
        """
        生成 HTML 報告 (使用更漂亮的模板)。

        Args:
            test_results (list): 包含測試結果的列表。
        """
        # 設定 Jinja2 環境
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('report_template.html') # 載入新的模板

        # 準備要傳遞給模板的資料
        report_data = {
            "report_title": "Test Report",  # 報告標題
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
            "test_results": test_results,
        }

        # 渲染模板
        html_output = template.render(**report_data)

        file_name = f"test_report.html"

        # 寫入檔案
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(html_output)

        print(f"報告已生成: {file_name}")

if __name__ == "__main__":

    report = TestReport("CPHD-V4", "00:11:22:33:44:55", "SN123456", "v1.0", "Tester A", "Station A", "Auto")  # 初始化報告

    # 生成測試結果
    example_test_results = [
        {"title": "測試項目 A", "unit": "N/A", "min": "1", "max":"1", "value":"1",  "status": "Pass"},
        {"title": "測試項目 B", "unit": "N/A", "min": "1", "max":"1", "value":"-1", "status": "Fail"},
        {"title": "測試項目 C", "unit": "N/A", "min": "1", "max":"1", "value":"0",  "status": "Fail"},
    ]

    report.generate_html_report(example_test_results)  # 呼叫函數

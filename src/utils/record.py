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
    def __init__(self, script: Script, product_info, tester_name, station, mode):
        """
        初始化測試報告。

        Args:
            script (Script):        腳本版本 (用於資料庫)
            # runcard (str):          (Optional) Runcard info, currently not used here.
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
        self.product_name = self.script.name if script else 'N/A'
        self.product_info = product_info
        self.version = self.script.version if script else 'N/A'
        # self.runcard = runcard # Runcard info, currently not used here.

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

            # --- 準備 Script Info ---
            script_name = getattr(self,'product_name', 'N/A')
            script_version = getattr(self.script, 'version', 'N/A')
            script_items = getattr(self.script, 'items', [])
            script_in_for_db = {
                "script_name": script_name,
                "script_version": script_version,
                "total_tests": len(script_items),
            }

            # --- 準備 Product Info ---
            product_in_for_db = {}
            # 獲取 TX (DUT ID 1) 的資訊
            product_in_for_db.update(self._get_db_product_fields(dut_id=1, db_prefix='tx'))
            # 獲取 RX (DUT ID 2) 的資訊
            if self.script.pairing == 1:  # 如果是配對模式，則加入第二個產品的資訊
                product_in_for_db.update(self._get_db_product_fields(dut_id=2, db_prefix='rx'))
            else:
                product_in_for_db.update({"mo_rx": "N/A", "sn_rx": "N/A", "mac_rx_1": "N/A", "mac_rx_2": "N/A"})

            # product_in_for_db = {
            #     "script_name": self.product_name,
            #     "mo_tx": self.product_info.get('$mo1', 'N/A'),
            #     "sn_tx": self.product_info.get('$sn1', 'N/A'),  # 使用第一個產品的序號
            #     "mac_tx_1": self.product_info.get('$mac11', 'N/A'),  # 使用第一個產品的 MAC 位址
            #     "mac_tx_2": self.product_info.get('$mac12', 'N/A'),  # 使用第一個產品的 MAC 位址
                
            #     "mo_rx": self.product_info.get('$mo2', 'N/A'),
            #     "sn_rx": self.product_info.get('$sn2', 'N/A'),  # 使用第一個產品的序號
            #     "mac_rx_1": self.product_info.get('$mac21', 'N/A'),  # 使用第一個產品的 MAC 位址
            #     "mac_rx_2": self.product_info.get('$mac22', 'N/A'),  # 使用第一個產品的 MAC 位址
            # }

            # --- 準備 Tester Info ---
            tester_in_for_db = {
                "user": getattr(self, 'tester_name', 'Unknown'),
                "station": getattr(self, 'station', 'Unknown')
            }

            # --- 建立資料庫 Session ---
            Log.debug(f"Creating test session in database for '{self.script.version}'...")
            self.db_session_id = self.db_manager.create_test_session(
                script_info = script_in_for_db,
                product_info = product_in_for_db,
                tester_info = tester_in_for_db,
                mode = getattr(self, 'mode', 'N/A')
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

    def _get_db_product_fields(self, dut_id, db_prefix):
        """
        輔助函式，根據 DUT ID (1 or 2) 和資料庫欄位前綴 (tx or rx)
        從 self.product_info 獲取 MO, SN, MACs。

        Args:
            dut_id (int): DUT 的 ID (1 代表第一個產品/TX, 2 代表第二個產品/RX)。
            db_prefix (str): 資料庫欄位的前綴 ('tx' or 'rx').

        Returns:
            dict: 包含 'mo_<prefix>', 'sn_<prefix>', 'mac_<prefix>_1', 'mac_<prefix>_2' 的字典。
                  如果 self.product_info 不存在或找不到 key，則值為 'N/A'。
        """
        fields = {}
        default_na = 'N/A' # 預設值

        if self.product_info:
            # 取得 product_info 的 keys
            mo_key = f"$mo{dut_id}"
            sn_key = f"$sn{dut_id}"
            mac_key1 = f"$mac{dut_id}1"
            mac_key2 = f"$mac{dut_id}2"

            # db_keys
            db_mo_key = f"mo_{db_prefix}"
            db_sn_key = f"sn_{db_prefix}"
            db_mac_key1 = f"mac_{db_prefix}_1"
            db_mac_key2 = f"mac_{db_prefix}_2"

            fields[db_mo_key] = self.product_info.get(mo_key, '') or default_na # 使用產品資訊中的序號
            fields[db_sn_key] = self.product_info.get(sn_key, '') or default_na
            fields[db_mac_key1] = self.product_info.get(mac_key1, '') or default_na  # 使用產品資訊中的 MAC 位址
            fields[db_mac_key2] = self.product_info.get(mac_key2, '') or default_na  # 使用產品資訊中的 MAC 位址
        else:
            Log.warn(f"self.product_info is None or empty while processing DUT ID {dut_id}.")
            fields[f"mo_{db_prefix}"] = default_na
            fields[f"sn_{db_prefix}"] = default_na
            fields[f"mac_{db_prefix}_1"] = default_na
            fields[f"mac_{db_prefix}_2"] = default_na

        return fields

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
                # db_items_result_str = "Pass" if item_result.result else "Fail"
                # 將測試結果轉換為資料庫格式
                # db_item = ItemResult(
                #     title=item_result.title,
                #     unit=item_result.unit,
                #     min_val=item_result.min,
                #     max_val=item_result.max,
                #     value=item_result.value,
                #     result=db_items_result_str
                # )
                # 將測試結果寫入資料庫
                Log.debug(f"Inserting item result '{item_result.title}' into database (Session ID: {self.db_session_id}).")
                self.db_manager.insert_test_item_result(self.db_session_id, item_result)
            except Exception as err:
                Log.error(f"Database error inserting item result '{item_result.title}': {err}", exc_info=True)
        else:
            Log.warn(f"Cannot save item result '{item_result.title}' to database: DB session not available.")
    
    def End_Record_and_Create_Report(self, final_result, total_items, pass_items, fail_items):
        """
        設定測試結束時間、最終結果，更新資料庫 Session，並生成 HTML 報告。

        Args:
            final_result (bool): 測試的最終結果。
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
        self.db_end_record()  # 結束資料庫 Session
        
        # --- Generate HTML Report ---
        return self._generate_report()  # 生成報告
    
    def db_end_record(self):
        """
        結束測試記錄，並更新資料庫 Session。
        """
        if self.db_manager and self.db_session_id is not None:
            try:
                Log.info(f"Ending database test session {self.db_session_id}.")
                self.db_manager.update_test_session_end(self.db_session_id, self.end_time, self.final_result)
            except Exception as e:
                Log.error(f"Unexpected error ending session for ID {self.db_session_id}: {e}", exc_info=True)
        else:
            Log.warn("Cannot end database session: DB session not available.")

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
        duts_for_template = []
        num_duts = min(self.script.pairing + 1, len(self.script.product))

        for i in range(num_duts):
            # 確保產品資訊存在，並且有足夠的資料
            if i >= len(self.script.product):
                Log.warn(f"Product info for DUT {i+1} is not available.")
                continue
            
            pruduct = self.script.product[i]
            # 動態產生 product_info 的 key
            sn_key = f'$sn{i+1}'
            mac_key1 = f'$mac{i+1}1'
            mac_key2 = f'$mac{i+1}2'
            # 安全地取得 product_info 中的值
            sn_val = 'N/A'
            macs_val = ['N/A', 'N/A'] # 預設值

            if self.product_info:
                sn_val = self.product_info.get(sn_key, 'N/A')
                macs_val = [self.product_info.get(mac_key1, 'N/A'), 
                           self.product_info.get(mac_key2, 'N/A')]
            else:
                Log.warn(f"self.product_info is None or empty while processing DUT index {i}.")
            
            dut_info = {
                'name': pruduct.model_name, # 使用產品的名稱
                'version': pruduct.version, # 使用產品的版本             
                'sn': sn_val, # 使用產品資訊中的序號
                'macs': macs_val, # 使用產品資訊中的 MAC 位址
            }
            duts_for_template.append(dut_info) # 將產品資訊加入列表

        # --- 過濾掉沒有有效資訊的 DUT ---
         # 判斷標準：SN 不是 'N/A'，或者 MACs 列表中至少有一個不是 'N/A'
        def is_useful(dut):
            sn_is_useful = dut.get('sn') != 'N/A'
            macs_list = dut.get('macs', [])
            macs_are_useful = any(mac and mac != 'N/A' for mac in macs_list)
            return sn_is_useful or macs_are_useful
        
        filtered_duts = [dut for dut in duts_for_template if is_useful(dut)]

        # duts_for_template= [{
        #     'name': self.script.product[0].model_name, # 使用第一個產品的名稱
        #         'version': self.script.product[0].version, # 使用第一個產品的版本             
        #         'sn':  self.product_info.get('$sn1', 'N/A'), # 使用產品資訊中的序號
        #         'macs':  [self.product_info.get('$mac11', 'N/A'), self.product_info.get('$mac12', 'N/A')]\
        #               if self.product_info else [], # 使用產品資訊中的 MAC 位址
        # }]

        # if self.script.pairing == 1: # 如果是配對模式，則加入第二個產品的資訊
        #     duts_for_template.append(
        #     {
        #         'name': self.script.product[1].model_name, # 使用第一個產品的名稱
        #             'version': self.script.product[1].version, # 使用第一個產品的版本             
        #             'sn':  self.product_info.get('$sn2', 'N/A'), # 使用產品資訊中的序號
        #             'macs':  [self.product_info.get('$mac21', 'N/A'), self.product_info.get('$mac22', 'N/A')]\
        #                 if self.product_info else [], # 使用產品資訊中的 MAC 位址
        #     })

        #  # Filter out DUTs with no useful info (optional) ， 無 sn 或 mac 則移除
        #  # duts_for_template = [dut for dut in duts_for_template if dut.get('sn') or dut.get('macs')]
        # duts_for_template = [
        #     dut for dut in duts_for_template 
        #     if dut.get('sn') or any(mac for mac in dut.get('macs',[]))
        #     ]

        report_data = {
            "report_title": "Test Report",
            "product_name": self.product_name,
            # --- Pass the list of DUTs ---
            'duts': filtered_duts,     
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
            created_files = []

            if filename is None:
                num_duts = min(self.script.pairing + 1, len(self.script.product))

                for i in range(num_duts):
                    # 確保產品資訊存在，並且有足夠的資料
                    if i >= len(self.script.product):
                        Log.warn(f"Product info for DUT {i+1} is not available.")
                        continue

                    station_str = self.station if self.station else "NoStation"
                    timestamp_str = self.start_time.strftime("%Y%m%d_%H%M%S")
                    mo_val = self.product_info.get(f"$mo{i+1}", '')

                    safe_mo = "".join(c if c.isalnum() else "_" for c in mo_val) if mo_val else "NoMO"
                    filename = f"{station_str}_{safe_mo}_{timestamp_str}"      
                    file_path = os.path.join(config.REPORT_FILE_PATH, f"{filename}.html")
                    # 寫入檔案
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(output_data)
                    created_files.append(file_path)
####################
                # for key, value in self.product_info.items():
                #     if '$mo' in key and value:
                #         station_str = self.station if self.station else "NoStation"
                #         timestamp_str = self.start_time.strftime("%Y%m%d_%H%M%S")

                #         safe_mo = "".join(c if c.isalnum() else "_" for c in value) if value else "NoMO"
                #         filename = f"{station_str}_{safe_mo}_{timestamp_str}"      
                #         file_path = os.path.join(config.REPORT_FILE_PATH, f"{filename}.html")
                #         # 寫入檔案
                #         with open(file_path, "w", encoding="utf-8") as f:
                #             f.write(output_data)
            else:
                file_path = os.path.join(config.REPORT_FILE_PATH, f"{filename}.html")
                # 寫入檔案
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(output_data)     
            
            # Log.info(f"HTML 報告已生成: {file_path}")           
            # return True
             # 記錄所有創建的檔案
            for path in created_files:
                Log.info(f"HTML 報告已生成: {path}")
                
            return bool(created_files)  # 如果創建了至少一個檔案，返回True
        except IOError as io_err:
            Log.error(f"File I/O error creating report file '{file_path}': {io_err}", exc_info=True)
            return False # Indicate failure
        except Exception as e:
            Log.error(f"生成報告時發生錯誤: '{file_path}': {e}", exc_info=True)
            return False # Indicate failure
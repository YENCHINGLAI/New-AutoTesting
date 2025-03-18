import hashlib
import os
import requests
from urllib.parse import urljoin  # 更方便的URL拼接
from dataclasses import dataclass # 導入 dataclass 簡化資料類別定義

# 定義 HTTP 請求類型，使用常數代替 Enum，更 Pythonic
HTTP_SELECT_POST_LOGIN = 0
HTTP_SELECT_GET_HASH = 1
HTTP_SELECT_GET_SEED = 2
HTTP_SELECT_POST_SET_POE = 3
HTTP_SELECT_GET_STATUS = 4

@dataclass
class HttpInfo:
    """儲存 HTTP 連線相關資訊的資料類別"""
    host: str
    password: str
    seed_value: str = None
    merge: str = None
    encode_password: str = None
    setting_hash: str = None
    cookie_token: str = None

    def __str__(self):
        return (f"Host: {self.host}\n"
                f"Password: {self.password}\n"
                f"SeedValue: {self.seed_value}\n"
                f"Merge: {self.merge}\n"
                f"Encode: {self.encode_password}\n"
                f"Token: {self.cookie_token}\n"
                f"Hash: {self.setting_hash}\n")

class PoeControl:
    """Netgear PoE 控制類別"""
    def __init__(self, host="192.168.100.2", password="@Cyp22232020@"):
        """建構子，初始化連線資訊並載入 Token"""
        self.http_info = HttpInfo(host=host, password=password)
        self.token_path = os.path.join(os.getcwd(), "PoeToken") # 使用 os.path.join 確保跨平台相容性
        self.http_info.cookie_token = self._load_token(self.token_path, f"Token-{host.replace('.', '')}.txt")
        self.is_login = False # 追蹤登入狀態 (雖然目前程式碼中未使用，但保留方便未來擴充)

    def get_info(self):
        """取得 HttpInfo 物件"""
        return self.http_info

    def get_is_login(self):
        """檢查是否已登入，透過 GET_STATUS 請求"""
        response_text = self._http_request(HTTP_SELECT_GET_STATUS)
        return False if response_text == "false" else True

    def connect(self):
        """連線到 Netgear 路由器並登入"""
        try:
            if self.get_is_login(): # 直接呼叫同步方法
                print("已登入") # 使用 print 取代 Trace.WriteLine
                return True

            self.http_info.seed_value = self._http_request(HTTP_SELECT_GET_SEED)
            self.http_info.encode_password = self._encrypt_password(self.http_info)
            self.http_info.cookie_token = self._http_request(HTTP_SELECT_POST_LOGIN)

            if not self.http_info.cookie_token:
                return False

            self._save_token(self.token_path)
            return True
        except Exception as e: # 更精確的錯誤處理
            print(f"連線錯誤: {e}") # 輸出更詳細的錯誤訊息
            return False

    def set_port(self, port, status):
        """設定 PoE 端口狀態 (On/Off)"""
        if not self.connect(): # 直接呼叫同步方法
            return False

        self.http_info.setting_hash = self._http_request(HTTP_SELECT_GET_HASH)
        if not self.http_info.setting_hash:
            return False

        result = self._http_request(HTTP_SELECT_POST_SET_POE, port=port, status=status)
        return result == "SUCCESS"

    def _http_request(self, order, port=1, status=True):
        """發送 HTTP 請求的底層方法"""
        result = ""
        base_url = f"http://{self.http_info.host}" # 定義 base_url 方便 URL 管理
        headers = {'Accept': 'application/x-www-form-urlencoded'} # 定義通用 headers
        session = requests.Session() # 使用 Session 物件保持 Cookie

        if self.http_info.cookie_token: # 如果有 token 則加入 cookie
             session.cookies.set('SID', self.http_info.cookie_token)

        try:
            if order == HTTP_SELECT_GET_STATUS:
                url = urljoin(base_url, "/PoEPortConfig.cgi") # 使用 urljoin
                response = session.get(url, headers=headers) # 使用 session 發送請求
                response.raise_for_status() # 檢查 HTTP 狀態碼
                response_text = response.text
                return "false" if self._check_is_login(response_text) else "true"

            elif order == HTTP_SELECT_GET_SEED:
                url = urljoin(base_url, "/login.cgi")
                response = session.get(url) # 使用 session 發送請求
                response.raise_for_status()
                text = response.text
                search_content = "id='rand' value="
                index = text.rfind(search_content) # 使用 rfind 更安全
                result = text[index + len(search_content) + 1:index + len(search_content) + 1 + 10].replace("'", "").replace(" ", "") # 更精確的字串切割

            elif order == HTTP_SELECT_POST_LOGIN:
                if not self.http_info.encode_password:
                    return ""
                url = urljoin(base_url, "/login.cgi")
                data = {'password': self.http_info.encode_password}
                response = session.post(url, headers=headers, data=data) # 使用 session 發送請求
                response.raise_for_status()
                if 'Set-Cookie' in response.headers: # 檢查 Set-Cookie header 是否存在
                    result = ""  # 初始化 result 為空字串，以防找不到 SID
                    token_value = response.headers.get('Set-Cookie')
                    if token_value:
                        for cookie_segment in token_value.split(','): # 處理可能有多個 Set-Cookie 項目 (以逗號分隔)
                            if "SID=" in cookie_segment:
                                start_index = cookie_segment.find("SID=") + len("SID=")
                                end_index = cookie_segment.find(";", start_index)
                                if end_index == -1: # 如果找不到分號，則取到字串結尾
                                    result = cookie_segment[start_index:]
                                else:
                                    result = cookie_segment[start_index:end_index]
                                break # 找到 SID 後即可跳出迴圈

            elif order == HTTP_SELECT_GET_HASH:
                url = urljoin(base_url, "/PoEPortConfig.cgi")
                response = session.get(url, headers=headers) # 使用 session 發送請求
                response.raise_for_status()
                text = response.text
                search_content = "id='hash' value="
                index = text.rfind(search_content) # 使用 rfind 更安全
                result = text[index + len(search_content) + 1:index + len(search_content) + 1 + 32].replace("'", "") # 更精確的字串切割

            elif order == HTTP_SELECT_POST_SET_POE:
                if not self.http_info.cookie_token or not self.http_info.setting_hash:
                    return ""

                url = urljoin(base_url, "/PoEPortConfig.cgi")
                data = {
                    "hash": self.http_info.setting_hash,
                    "ACTION": "Apply",
                    "portID": str(port - 1),  # 0~7 (1~8 port)
                    "ADMIN_MODE": "1" if status else "0",  # false=>Off,true=>On
                    "PORT_PRIO": "0",
                    "POW_MOD": "3",
                    "POW_LIMT_TYP": "2",
                    "POW_LIMT": "30.0",
                    "DETEC_TYP": "2",
                }
                response = session.post(url, headers=headers, data=data) # 使用 session 發送請求
                response.raise_for_status()
                result = response.text
            return result

        except requests.exceptions.RequestException as e: # 更精確地捕捉 requests 相關異常
            print(f"HTTP 請求錯誤: {e}") # 輸出更詳細的錯誤訊息
            return ""
        except Exception as e: # 捕捉其他未預期異常
            print(f"其他錯誤: {e}")
            return ""

    def _encrypt_password(self, http_info):
        """加密密碼"""
        http_info.merge = self._merge(http_info.password, http_info.seed_value)
        md5_hash = hashlib.md5() # 建立 md5 hash 物件
        md5_hash.update(http_info.merge.encode('utf-8')) # 更新 hash 物件內容，需 encode 為 bytes
        return md5_hash.hexdigest() # 取得 16 進位字串

    def _merge(self, password, seed_value):
        """合併密碼和 SeedValue 字串"""
        result = [] # 使用 list 效率更高
        max_len = max(len(password), len(seed_value))
        for i in range(max_len):
            if i < len(password):
                result.append(password[i])
            if i < len(seed_value):
                result.append(seed_value[i])
        return "".join(result) # 使用 join() 方法將 list 轉為 string

    def _check_is_login(self, http_response_body):
        """檢查 HTTP 回應內容判斷是否需要登入"""
        return len(http_response_body) < 10 or "/login.cgi" in http_response_body

    def _save_token(self, path):
        """儲存 Token 到檔案"""
        token_str = f"{self.http_info.host}\n{self.http_info.cookie_token}"
        log_filename = f"Token-{self.http_info.host.replace('.', '')}.txt"
        os.makedirs(path, exist_ok=True) # 確保目錄存在，makedirs 可以遞迴建立目錄
        try:
            with open(os.path.join(path, log_filename), "w") as f: # 使用 with 語句自動關閉檔案
                f.write(token_str)
            return True
        except Exception as e: # 更精確的錯誤處理
            print(f"儲存 Token 錯誤: {e}")
            return False

    def _load_token(self, path, filename):
        """從檔案載入 Token"""
        try:
            with open(os.path.join(path, filename), "r", encoding="utf-8") as f: # 指定編碼為 utf-8
                lines = f.readlines()
                if len(lines) >= 2: # 確保檔案內容至少有兩行
                    return lines[1].strip() # 移除換行符號
                else:
                    return "" # 檔案格式不正確
        except FileNotFoundError: # 精確捕捉 FileNotFoundError
            return ""
        except Exception as e: # 捕捉其他檔案讀取錯誤
            print(f"載入 Token 錯誤: {e}")
            return ""

# 範例使用
if __name__ == '__main__':
    poe_control = PoeControl(host="192.168.100.2", password="@Cyp22232020@") # 建立 PoeControl 物件
    if poe_control.connect():
        print("成功連線到 Netgear 路由器")
        port_number = 6 # 設定 Port 1
        poe_status_on = True # 開啟 PoE
        if poe_control.set_port(port_number, poe_status_on):
            print(f"Port {port_number} PoE 設定為 {'開啟' if poe_status_on else '關閉'} 成功")
        else:
            print(f"Port {port_number} PoE 設定失敗")

        poe_status_off = False # 關閉 PoE
        if poe_control.set_port(port_number, poe_status_off):
            print(f"Port {port_number} PoE 設定為 {'開啟' if poe_status_off else '關閉'} 成功")
        else:
            print(f"Port {port_number} PoE 設定失敗")

        print("\nHttpInfo 資訊:")
        print(poe_control.get_info()) # 印出 HttpInfo 資訊
    else:
        print("連線 Netgear 路由器失敗")
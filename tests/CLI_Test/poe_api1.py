import hashlib
import os
import time
import requests
from urllib.parse import urljoin
from dataclasses import dataclass
from typing import Optional, Dict, Tuple, Union, List  # 導入 Type Hints

# 自訂例外類別
class NetgearRouterError(Exception):
    """Netgear 路由器操作基底例外類別"""
    pass

class NetgearLoginError(NetgearRouterError):
    """登入 Netgear 路由器失敗例外"""
    pass

class NetgearRequestError(NetgearRouterError):
    """HTTP 請求 Netgear 路由器失敗例外"""
    pass

class NetgearTokenError(NetgearRouterError):
    """Token 處理相關例外"""
    pass

class NetgearPoeError(NetgearRouterError):
    """PoE 控制相關例外"""
    pass

# HTTP 請求類型常數
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
    seed_value: Optional[str] = None # 使用 Optional 表示可能為 None
    encode_password: Optional[str] = None
    cookie_token: Optional[str] = None
    setting_hash: Optional[str] = None


class NetgearRouter:
    """
    Netgear 路由器控制類別 (精簡版).

    負責與 Netgear 路由器進行 HTTP 通訊, 處理登入驗證, Token 管理,
    以及 PoE 端口控制等功能.
    """

    # 預設常數 (集中管理)
    DEFAULT_HOST = "192.168.100.2"
    TOKEN_FOLDER_NAME = "PoeToken"
    LOGIN_CGI_PATH = "/login.cgi"
    POE_CONFIG_CGI_PATH = "/PoEPortConfig.cgi"
    STATUS_CHECK_KEYWORDS = ["/login.cgi"] # 用於判斷登入狀態的關鍵字
    SEED_SEARCH_CONTENT = "id='rand' value="
    HASH_SEARCH_CONTENT = "id='hash' value="
    LOGIN_PASSWORD_KEY = "password"
    POE_ACTION_KEY = "ACTION"
    POE_ACTION_APPLY = "Apply"
    POE_PORT_ID_KEY = "portID"
    POE_ADMIN_MODE_KEY = "ADMIN_MODE"
    POE_PORT_PRIO_KEY = "PORT_PRIO"
    POE_POW_MOD_KEY = "POW_MOD"
    POE_POW_LIMT_TYP_KEY = "POW_LIMT_TYP"
    POE_POW_LIMT_KEY = "POW_LIMT"
    POE_DETEC_TYP_KEY = "DETEC_TYP"
    POE_DEFAULT_POWER_TYP = "2"
    POE_DEFAULT_POWER_LIMIT = "30.0"
    POE_DEFAULT_PRIORITY = "0"
    POE_DEFAULT_POWER_MODE = "3"
    POE_DEFAULT_DETECT_TYPE = "2"
    POE_ADMIN_MODE_ON_VALUE = "1"
    POE_ADMIN_MODE_OFF_VALUE = "0"
    TOKEN_COOKIE_NAME = "SID"
    TOKEN_FILE_PREFIX = "config"
    TOKEN_FILE_EXTENSION = ".ini"
    HTTP_ACCEPT_HEADER = "application/x-www-form-urlencoded"
    REQUESTS_SUCCESS = "SUCCESS"

    def __init__(self, host: str = DEFAULT_HOST, password: str = "@Cyp22232020@"):
        """
        建構子.

        初始化 NetgearRouter 物件, 設定路由器 IP 位址和密碼, 並嘗試載入已儲存的 Token.

        Args:
            host (str): Netgear 路由器 IP 位址 (預設: "192.168.100.2").
            password (str): 路由器登入密碼 (預設: "@Cyp22232020@").
        """
        self.http_info = HttpInfo(host=host, password=password)
        self.token_path = os.path.join(os.getcwd(), self.TOKEN_FOLDER_NAME)
        self.http_info.cookie_token = self._load_token_from_file() # 載入 Token
        self.is_login = False

    def connect(self) -> bool:
        """
        連線到 Netgear 路由器並登入.

        如果已登入則直接返回 True, 否則執行登入流程:
        1. 檢查是否已登入 (透過 `_check_login_status`).
        2. 取得 Seed Value (透過 `_get_seed_value`).
        3. 加密密碼 (透過 `_encrypt_password`).
        4. 使用加密後的密碼登入並取得 Token (透過 `_login_and_get_token`).
        5. 儲存 Token (透過 `_save_token_to_file`).

        Returns:
            bool: True 表示連線成功 (已登入), False 表示連線失敗.

        Raises:
            NetgearLoginError: 登入失敗時拋出.
            NetgearRequestError: HTTP 請求錯誤時拋出.
            NetgearTokenError: Token 處理錯誤時拋出.
        """
        try:
            if self._check_login_status():
                # print("已登入")
                return True

            self.http_info.seed_value = self._get_seed_value()
            self.http_info.encode_password = self._encrypt_password()
            self.http_info.cookie_token = self._login_and_get_token()

            if not self.http_info.cookie_token:
                raise NetgearLoginError("取得 Cookie Token 失敗") # 更精確的例外

            self._save_token_to_file()
            return True

        except NetgearRouterError as e: # 捕捉自訂例外
            print(f"連線錯誤: {e}")
            return False
        except Exception as e: # 捕捉其他未預期例外
            print(f"未預期錯誤: {e}")
            return False

    def set_poe_port(self, port: int, status: bool) -> bool:
        """
        設定指定 PoE 端口的狀態 (開啟/關閉).

        1. 確保已連線 (透過 `connect()`).
        2. 取得 Setting Hash (透過 `_get_setting_hash`).
        3. 發送 HTTP POST 請求設定 PoE 端口狀態 (透過 `_send_poe_set_request`).

        Args:
            port (int): PoE 端口號碼 (1-8).
            status (bool): True 表示開啟 PoE, False 表示關閉 PoE.

        Returns:
            bool: True 表示 PoE 設定成功, False 表示設定失敗.

        Raises:
            NetgearLoginError: 未登入時拋出.
            NetgearRequestError: HTTP 請求錯誤時拋出.
            NetgearPoeError: PoE 設定相關錯誤時拋出.
        """
        try:
            if not self.connect(): # 確保已連線
                raise NetgearLoginError("未連線到 Netgear 路由器")

            self.http_info.setting_hash = self._get_setting_hash()
            if not self.http_info.setting_hash:
                raise NetgearPoeError("取得 Setting Hash 失敗") # 更精確的例外

            result = self._send_poe_set_request(port, status)
            return result == self.REQUESTS_SUCCESS

        except NetgearRouterError as e: # 捕捉自訂例外
            print(f"PoE 設定錯誤: {e}")
            return False
        except Exception as e: # 捕捉其他未預期例外
            print(f"未預期錯誤: {e}")
            return False

    def get_info(self) -> HttpInfo:
        """
        取得 HttpInfo 物件.

        Returns:
            HttpInfo: 包含連線資訊的 HttpInfo 物件.
        """
        return self.http_info

    def _check_login_status(self) -> bool:
        """
        檢查目前是否已登入 Netgear 路由器.

        透過發送 GET_STATUS 請求並檢查回應內容判斷.

        Returns:
            bool: True 表示已登入, False 表示未登入.

        Raises:
            NetgearRequestError: HTTP 請求錯誤時拋出.
        """
        response_text = self._http_request(HTTP_SELECT_GET_STATUS).text
        return not self._is_login_page_response(response_text)

    def _is_login_page_response(self, http_response_body: str) -> bool:
        """
        判斷 HTTP 回應內容是否為登入頁面.

        檢查回應內容長度是否小於 10 或是否包含登入頁面關鍵字.

        Args:
            http_response_body (str): HTTP 回應內容.

        Returns:
            bool: True 表示是登入頁面回應, False 表示不是.
        """
        return len(http_response_body) < 10 or any(keyword in http_response_body for keyword in self.STATUS_CHECK_KEYWORDS)

    def _get_seed_value(self) -> str:
        """
        從 Netgear 路由器取得 Seed Value.

        發送 GET_SEED 請求並從回應內容中解析 Seed Value.

        Returns:
            str: Seed Value 字串.

        Raises:
            NetgearRequestError: HTTP 請求錯誤時拋出.
            NetgearLoginError: 無法解析 Seed Value 時拋出.
        """
        response_text = self._http_request(HTTP_SELECT_GET_SEED).text
        search_content = self.SEED_SEARCH_CONTENT
        index = response_text.rfind(search_content)
        if index == -1:
            raise NetgearLoginError("無法在登入頁面中找到 Seed Value") # 更精確的例外
        seed_value = response_text[index + len(search_content) + 1:index + len(search_content) + 1 + 10].replace("'", "").replace(" ", "")
        return seed_value

    def _encrypt_password(self) -> str:
        """
        加密密碼.

        使用 MD5 演算法加密合併後的密碼字串 (password + seed_value).

        Returns:
            str: 加密後的密碼字串 (Hex Digest).
        """
        merged_password = self._merge_password_and_seed()
        md5_hash = hashlib.md5()
        md5_hash.update(merged_password.encode('utf-8'))
        return md5_hash.hexdigest()

    def _merge_password_and_seed(self) -> str:
        """
        合併密碼和 Seed Value 字串.

        交錯合併 password 和 seed_value 字串.

        Returns:
            str: 合併後的字串.
        """
        password = self.http_info.password
        seed_value = self.http_info.seed_value or "" # 確保 seed_value 不為 None
        merged_chars: List[str] = [] # 使用 List 效率更高
        max_len = max(len(password), len(seed_value))
        for i in range(max_len):
            if i < len(password):
                merged_chars.append(password[i])
            if i < len(seed_value):
                merged_chars.append(seed_value[i])
        return "".join(merged_chars) # 使用 join() 方法

    def _login_and_get_token(self) -> str:
        """
        登入 Netgear 路由器並取得 Cookie Token.

        發送 POST_LOGIN 請求, 使用加密後的密碼登入, 並從回應標頭中解析 Set-Cookie 取得 Token.

        Returns:
            str: Cookie Token 字串 (SID 值).

        Raises:
            NetgearRequestError: HTTP 請求錯誤時拋出.
            NetgearLoginError: 登入失敗或無法取得 Token 時拋出.
        """
        response = self._http_request(HTTP_SELECT_POST_LOGIN, data={self.LOGIN_PASSWORD_KEY: self.http_info.encode_password})
        token_value = response.headers.get('Set-Cookie')
        result = ""
        if token_value:
            for cookie_segment in token_value.split(','):
                if "SID=" in cookie_segment:
                    start_index = cookie_segment.find("SID=") + len("SID=")
                    end_index = cookie_segment.find(";", start_index)
                    if end_index == -1:
                        result = cookie_segment[start_index:]
                    else:
                        result = cookie_segment[start_index:end_index]
                    break
        if not result:
            raise NetgearLoginError("登入成功, 但無法從 Set-Cookie 中取得 SID Token") # 更精確的例外
        return result

    def _get_setting_hash(self) -> str:
        """
        取得 PoE 設定頁面的 Hash 值.

        發送 GET_HASH 請求並從回應內容中解析 Hash 值.

        Returns:
            str: Setting Hash 字串.

        Raises:
            NetgearRequestError: HTTP 請求錯誤時拋出.
            NetgearPoeError: 無法解析 Setting Hash 時拋出.
        """
        response_text = self._http_request(HTTP_SELECT_GET_HASH).text
        search_content = self.HASH_SEARCH_CONTENT
        index = response_text.rfind(search_content)
        if index == -1:
            raise NetgearPoeError("無法在 PoE 設定頁面中找到 Setting Hash") # 更精確的例外
        setting_hash = response_text[index + len(search_content) + 1:index + len(search_content) + 1 + 32].replace("'", "")
        return setting_hash

    def _send_poe_set_request(self, port: int, status: bool) -> str:
        """
        發送 HTTP POST 請求設定 PoE 端口狀態.

        Args:
            port (int): PoE 端口號碼 (1-8).
            status (bool): True 表示開啟 PoE, False 表示關閉 PoE.

        Returns:
            str: HTTP 回應內容.

        Raises:
            NetgearRequestError: HTTP 請求錯誤時拋出.
        """
        data: Dict[str, str] = { # 使用 Type Hint
            self.HASH_SEARCH_CONTENT.replace("id='", "").replace("' value=", ""): self.http_info.setting_hash, # 從常數反向取得 key name，更安全
            self.POE_ACTION_KEY: self.POE_ACTION_APPLY,
            self.POE_PORT_ID_KEY: str(port - 1), # Port ID 從 0 開始
            self.POE_ADMIN_MODE_KEY: self.POE_ADMIN_MODE_ON_VALUE if status else self.POE_ADMIN_MODE_OFF_VALUE, # 使用常數
            self.POE_PORT_PRIO_KEY: self.POE_DEFAULT_PRIORITY,
            self.POE_POW_MOD_KEY: self.POE_DEFAULT_POWER_MODE,
            self.POE_POW_LIMT_TYP_KEY: self.POE_DEFAULT_POWER_TYP,
            self.POE_POW_LIMT_KEY: self.POE_DEFAULT_POWER_LIMIT,
            self.POE_DETEC_TYP_KEY: self.POE_DEFAULT_DETECT_TYPE,
        }
        response_text = self._http_request(HTTP_SELECT_POST_SET_POE, data=data).text
        return response_text

    def _http_request(self,
                      order: int,
                      data: Optional[Dict[str, str]] = None) -> requests.Response:
        """
        發送 HTTP 請求到 Netgear 路由器.

        底層 HTTP 請求處理方法, 封裝了 GET/POST 請求, Header 設定, Cookie 管理和錯誤處理.

        Args:
            order (int): HTTP 請求類型 (使用 HTTP_SELECT_ 常數).
            data (Optional[Dict[str, str]]): POST 請求的資料 (字典).  預設為 None (GET 請求).

        Returns:
            requests.Response: requests Response 物件.

        Raises:
            NetgearRequestError: HTTP 請求錯誤時拋出 (例如連線錯誤, HTTP 錯誤狀態碼).
        """
        base_url = f"http://{self.http_info.host}"
        headers = {'Accept': self.HTTP_ACCEPT_HEADER}
        session = requests.Session() # 使用 Session 保持 Cookie

        if self.http_info.cookie_token: # 如果有 token 則加入 cookie
            session.cookies.set(self.TOKEN_COOKIE_NAME, self.http_info.cookie_token)

        url = ""
        method = "GET" # 預設為 GET 請求
        if order == HTTP_SELECT_GET_STATUS:
            url = urljoin(base_url, self.POE_CONFIG_CGI_PATH)
        elif order == HTTP_SELECT_GET_SEED:
            url = urljoin(base_url, self.LOGIN_CGI_PATH)
        elif order == HTTP_SELECT_POST_LOGIN:
            method = "POST"
            url = urljoin(base_url, self.LOGIN_CGI_PATH)
        elif order == HTTP_SELECT_GET_HASH:
            url = urljoin(base_url, self.POE_CONFIG_CGI_PATH)
        elif order == HTTP_SELECT_POST_SET_POE:
            method = "POST"
            url = urljoin(base_url, self.POE_CONFIG_CGI_PATH)
        else:
            raise ValueError(f"未知的 HTTP 請求類型: {order}") # 程式碼錯誤, 拋出 ValueError

        try:
            if method == "GET":
                response = session.get(url, headers=headers, timeout=10) # 加入 timeout
            elif method == "POST":
                response = session.post(url, headers=headers, data=data, timeout=10) # 加入 timeout
            else: # 理論上不會執行到這裡，但為了完整性
                raise ValueError(f"未知的 HTTP 方法: {method}")

            response.raise_for_status() # 檢查 HTTP 狀態碼, 非 200 拋出異常
            return response # 成功返回 response 物件

        except requests.exceptions.RequestException as e: # 捕捉 requests 相關異常
            raise NetgearRequestError(f"HTTP 請求錯誤: {e}") from e # 拋出自訂例外, 並保留原始異常鏈

    def _save_token_to_file(self) -> bool:
        """
        儲存 Cookie Token 到檔案.

        Token 檔案名格式: Token-{router_host_no_dots}.txt, 儲存路徑: PoeToken 資料夾.

        Returns:
            bool: True 表示儲存成功, False 表示儲存失敗.

        Raises:
            NetgearTokenError: Token 儲存錯誤時拋出.
        """
        token_str = f"{self.http_info.host}\n{self.http_info.cookie_token}"
        log_filename = f"{self.TOKEN_FILE_PREFIX}{self.TOKEN_FILE_EXTENSION}" # 使用常數
        os.makedirs(self.token_path, exist_ok=True) # 確保目錄存在
        try:
            with open(os.path.join(self.token_path, log_filename), "w") as f: # 使用 with 語句
                f.write(token_str)
            return True
        except Exception as e:
            raise NetgearTokenError(f"儲存 Token 檔案錯誤: {e}") from e # 拋出自訂例外

    def _load_token_from_file(self) -> Optional[str]:
        """
        從檔案載入 Cookie Token.

        Token 檔案名格式: Token-{router_host_no_dots}.txt, 儲存路徑: PoeToken 資料夾.

        Returns:
            Optional[str]: Token 字串 (SID 值), 如果載入失敗或檔案不存在則返回 None.

        Raises:
            NetgearTokenError: Token 載入錯誤時拋出 (例如檔案格式錯誤).
        """
        log_filename = f"{self.TOKEN_FILE_PREFIX}{self.http_info.host.replace('.', '')}{self.TOKEN_FILE_EXTENSION}" # 使用常數
        try:
            with open(os.path.join(self.token_path, log_filename), "r", encoding="utf-8") as f: # 指定編碼
                lines = f.readlines()
                if len(lines) >= 2: # 檢查檔案格式
                    return lines[1].strip() # 返回 Token 字串
                else:
                    raise NetgearTokenError("Token 檔案格式錯誤: 內容不足兩行") # 檔案格式錯誤
        except FileNotFoundError:
            return None # 檔案不存在, 返回 None
        except Exception as e:
            raise NetgearTokenError(f"載入 Token 檔案錯誤: {e}") from e # 其他檔案讀取錯誤

# 範例使用
if __name__ == '__main__':
    try:
        start = time.time()

        netgear_router = NetgearRouter(host="192.168.100.2", password="@Cyp22232020@")

        if netgear_router.connect():
            # print("成功連線到 Netgear 路由器 (精簡版)")

            port_number = 6
            poe_status_off = False
            if netgear_router.set_poe_port(port_number, poe_status_off):
                # print(f"Port {port_number} PoE 設定為 {'開啟' if poe_status_off else '關閉'} 成功 (精簡版)")
                print(1)
            else:
                # print(f"Port {port_number} PoE 設定失敗 (精簡版)")
                print(0)


            # time.sleep(2) # 等待 2 秒

            # poe_status_on = True
            # if netgear_router.set_poe_port(port_number, poe_status_on):
            #     print(f"Port {port_number} PoE 設定為 {'開啟' if poe_status_on else '關閉'} 成功 (精簡版)")
            # else:
            #     print(f"Port {port_number} PoE 設定失敗 (精簡版)")

            # print("\nHttpInfo 資訊 (精簡版):")
            print(netgear_router.get_info())

        else:
            # print("連線 Netgear 路由器失敗 (精簡版)")
            print(0)
        
        end= time.time()
        print(f"執行時間: {end-start:.2f} 秒")

    except NetgearRouterError as e: # 捕捉自訂例外 (在主程式範例中也捕捉)
        # print(f"主程式錯誤: {e}")
        print(-1)
    except Exception as e: # 捕捉其他未預期例外
        # print(f"主程式未預期錯誤: {e}")
        print(-1)
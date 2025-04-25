#===================================================================================================
# Import the necessary modules
#===================================================================================================
import re
import platform

from PySide6.QtCore import QObject, Signal

#===================================================================================================
# Execute asdasd
#===================================================================================================
class ItemResult:
    def __init__(self, title, unit, min_val, max_val, value, result):
        self.title:str = title
        self.unit:str = unit
        self.min:str = min_val
        self.max:str = max_val
        self.value:str = value
        self.result:bool = result
        
class _Signals(QObject):
    """
    負責處理所有 UI 更新邏輯的類，將 UI 更新與商業邏輯分離
    """ 
    #===================================================================================================
    # Main window
    #===================================================================================================
    # Button
    startBtnChanged = Signal(str)

    # Progress Bar 更新
    scriptProgressChanged = Signal(int, int)
    """更新腳本進度條(當前值, 最大)"""
    itemProgressChanged = Signal(int, int)      
    """更新Item進度條(當前值, 最大)"""

    # Result Table 更新
    itemsTableInit = Signal()                 
    """測試結果表格初始化"""
    itemsTableChanged = Signal(int, str, bool)
    """測試結果表格更新(index, 項目名稱, 結果)"""

    # 即時訊息更新
    currentItemChanged = Signal(str)          
    """更新當前執行的測試項目名稱"""
    messageBoxDialog = Signal(str, str)             
    """顯示MessageBox訊息(標題, 顯示內容)"""

    passCountChanged = Signal(int)                    
    """Pass次數"""
    failCountChanged = Signal(int)                    
    """Fail次數"""

    # User訊息
    userNameChanged = Signal(str)
    """更新使用者名稱"""
    userLevelChanged = Signal(str)
    """更新使用者等級"""
    runcardChanged = Signal(str)
    """更新工單號碼"""
    
    #===================================================================================================
    # update dialog
    #===================================================================================================
    updateDialogShowed = Signal()               
    """顯示 Update 對話框"""
    updateTextChanged = Signal(str, str, str)   
    """Update 文字"""
    updateFinished = Signal(str)                
    """更新完成"""
    updateProgressChanged = Signal(int, int, int)
    """新進度條 (當前值,最小值,最大值)"""

    def __init__(self):
        super().__init__()
    
UiUpdater = _Signals()

#===================================================================================================
# Functions
#===================================================================================================
def is_mac(check_str: str) -> bool:
    """
    檢查是否為標準 MAC 地址格式 (XX:XX:XX:XX:XX:XX 或 XX-XX-XX-XX-XX-XX)。
    """
    if not isinstance(check_str, str): return False
    # Regex 匹配標準 MAC 格式，允許 : 或 - 作為分隔符
    pattern = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
    return bool(re.fullmatch(pattern, check_str))

def is_mac_nosign(check_str: str) -> bool:
    """
    檢查是否為無符號的 MAC 地址格式 (XXXXXXXXXXXX)。
    """
    if not isinstance(check_str, str): return False
    pattern = r"^[0-9A-Fa-f]{12}$"
    return bool(re.fullmatch(pattern, check_str))

def compare_macs(mac1_str: str, mac2_str: str) -> bool:
    """
    比較兩個 MAC 地址的大小 (數值上)。
    如果 mac2 > mac1 (數值上)，返回 True。
    如果格式錯誤或無法比較，返回 None。
    如果 mac2 <= mac1，返回 False。
    """
    # 先驗證兩個輸入是否是有效的 MAC 格式 (帶或不帶符號)
    valid_mac1 = is_mac(mac1_str) or is_mac_nosign(mac1_str)
    valid_mac2 = is_mac(mac2_str) or is_mac_nosign(mac2_str)

    if not (valid_mac1 and valid_mac2):
        return False # 格式不對，無法比較

    try:
        # 移除分隔符並轉換為數值進行比較
        num1 = int(re.sub(r'[:-]', '', mac1_str), 16)
        num2 = int(re.sub(r'[:-]', '', mac2_str), 16)
        return num2 > num1
    except (ValueError, TypeError):
        return False # 轉換錯誤

def is_mac_bci(check_str: str) -> bool:
    """
    檢查是否為 BCI MAC 地址格式 (00:19:XX:XX:XX:XX 或 00-19-XX-XX-XX-XX)。
    """
    if not isinstance(check_str, str): return False
    # Regex 匹配 00:19 或 00-19 開頭的 MAC
    # C# 的 ([0]{2}[:-])([1]{1})([9]{1}) 可以簡化
    pattern = r"^00[:-]19([:-][0-9A-Fa-f]{2}){4}$"
    return bool(re.fullmatch(pattern, check_str))

def is_mac_bci_nosign(check_str: str) -> bool:
    """
    檢查是否為無符號的 BCI MAC 地址格式 (0019XXXXXXXX)。
    """
    if not isinstance(check_str, str): return False
    pattern = r"^0019([0-9A-Fa-f]{2}){4}$"
    return bool(re.fullmatch(pattern, check_str))

def is_version(check_str: str) -> bool:
    """
    檢查版本格式，例如 1.23 或 1-23。
    """
    if not isinstance(check_str, str): return False
    # 匹配數字 + (.-) + 兩位數字
    pattern = r"^\d{1}[.-]\d{2}$"
    # C# 的 [0-9]{1} 等同於 \d{1} 或 \d
    # C# 的 [0-9]{2} 等同於 \d{2}
    return bool(re.fullmatch(pattern, check_str))

def is_sn_nosign(check_str: str, length: int = 11) -> bool:
    """
    檢查是否為指定長度的純數字 SN。
    """
    if not isinstance(check_str, str): return False
    # 匹配指定長度的數字
    pattern = fr"^\d{{{length}}}$" # 使用 f-string 插入長度
    return bool(re.fullmatch(pattern, check_str))

def is_mo(check_str: str) -> bool:
    """
    檢查是否為 MO 格式 (M 或 m 開頭，後跟 10 位數字)。
    """
    if not isinstance(check_str, str): return False
    pattern = r"^[Mm]\d{10}$"
    return bool(re.fullmatch(pattern, check_str))

def is_pcb(check_str: str) -> bool:
    """
    檢查是否為 PCB 格式 (M 或 m 開頭，後跟 21 個字母、數字或連字符)。
    注意：C# 的 [0-9A-Za-f-] 在 Python 中可以直接用，但如果允許所有字母，用 [0-9A-Za-z-]
    """
    if not isinstance(check_str, str): return False
    pattern = r"^[Mm][0-9A-Za-z-]{21}$" # 假設允許所有字母而不僅僅是 A-F
    return bool(re.fullmatch(pattern, check_str))

def is_testjig(check_str: str) -> bool:
    """
    檢查是否為 JIG 格式 (J 或 j 開頭，後跟 6 位數字)。
    """
    if not isinstance(check_str, str): return False
    pattern =  r"^TestJig.*$"
    return bool(re.fullmatch(pattern, check_str))

def is_ip(check_str: str) -> bool:
    """
    檢查是否為標準 IPv4 地址格式。
    """
    if not isinstance(check_str, str): return False
    # C# 的 IP Regex 可以直接用，但可以稍微簡化
    # (?:...) 表示非捕獲組
    octet = r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)" # 更精確的 octet 匹配
    pattern = fr"^{octet}\.{octet}\.{octet}\.{octet}$"
    return bool(re.fullmatch(pattern, check_str))

def is_local_ip(check_str: str) -> bool:
    """
    檢查是否為 192.168.100.xxx 格式的 IP。
    """
    if not isinstance(check_str, str): return False
    # C# 的實現略顯繁瑣，可以簡化
    octet_last = r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
    pattern = fr"^192\.168\.100\.{octet_last}$"
    return bool(re.fullmatch(pattern, check_str))

def is_valid_filename(check_str: str) -> bool:
    """
    檢查字串是否包含常見的非法檔名字符 (跨平台考慮)。
    注意：這比 C# 的 GetInvalidFileNameChars() 檢查更基本。
    """
    if not isinstance(check_str, str): return False
    # Windows 下常見非法字符: <>:"/\|?*，以及控制字符 (\x00-\x1f)
    # Linux/macOS 下主要是 / 和 NUL (\x00)
    # 取一個比較嚴格的集合
    # 不允許空字串或只包含點和空格
    if not check_str or check_str.strip() in ['', '.']:
        return False
    # 檢查非法字符
    invalid_chars = r'<>:"/\\|?*\x00-\x1f' # 合併 Windows 和 Linux/macOS
    if re.search(f'[{re.escape(invalid_chars)}]', check_str):
        return False
    # Windows 下檔名不能以點或空格結尾
    if platform.system() == "Windows" and check_str.endswith(('.', ' ')):
        return False
    # Windows 下的保留名稱（不區分大小寫，不含擴展名）
    reserved_names = {"CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4",
                      "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2",
                      "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"}
    if platform.system() == "Windows" and check_str.upper() in reserved_names:
        return False

    return True

# 可以添加一個通用的驗證函數入口，如果需要根據類型調用不同的驗證器
def validate_barcode(barcode_type: str, value: str, config: dict = None) -> bool:
    """
    根據條碼類型調用相應的驗證函數。
    config 可以包含額外參數，例如 SN 的預期長度。
    """
    if barcode_type == "MO":
        return is_mo(value)
    elif barcode_type == "SN":
        sn_length = config.get("sn_length", 11) if config else 11
        return is_sn_nosign(value, length=sn_length)
    elif barcode_type == "MAC":
        # 根據需要選擇驗證器，例如允許帶符號或不帶符號
        return is_mac(value) or is_mac_nosign(value)
    elif barcode_type == "MAC_BCI":
        return is_mac_bci(value) or is_mac_bci_nosign(value)
    # ... 添加其他類型
    else:
        # 如果沒有特定的驗證器，可以預設為 True 或 False
        return True # 或者 False，取決於你的策略
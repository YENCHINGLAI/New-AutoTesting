#===================================================================================================
# Import the necessary modules
#===================================================================================================
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
        self.result:str = result
        
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
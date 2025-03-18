#===================================================================================================
# Import the necessary modules
#===================================================================================================
from PySide6.QtCore import QObject,Signal

from src.utils.log import Log

#===================================================================================================
# Execute asdasd
#===================================================================================================
class UIUpdater(QObject):
    """
    負責處理所有 UI 更新邏輯的類，將 UI 更新與業務邏輯分離
    """
    # Progress Bar 更新
    items_bar_updated = Signal(int)             # 整個腳本的進度Bar
    max_items_bar_updated = Signal(int)         # 設定Bar最大值
    current_bar_updated = Signal(int)           # 單一測試項目的進度Bar
    max_current_bar_updated = Signal(int)       # 單一測試項目的進度Bar最大值(5/5)

    # Result Table 更新
    items_table_init = Signal()                 # 測試結果表格初始化
    items_table_updated = Signal(int, str, bool)# 測試結果表格更新

    # 即時訊息更新
    current_line_updated = Signal(str)          # 更新當前執行的測試項目名稱
    qbox_message = Signal(str, str)             # 顯示MessageBox訊息
    fail_count = Signal(int)                    # 失敗次數
    pass_count = Signal(int)                    # 通過次數

    def __init__(self):
        super().__init__()

    def update_bar(self, setting_bar: Signal, progress_percentage):
        """
        更新測試進度。 使用 signal 發射進度更新訊息，讓 UI 介面可以接收並更新進度條。

        Args:
            progress_percentage (int): 進度百分比 (0-100)。
        """
        setting_bar.emit(progress_percentage) # 發射 signal，傳遞進度百分比

    def set_max_bar(self, setting_bar: Signal, max_value):
        """
        設置進度條的最大值

        Args:
            max_value (int): Progressbar最大值
        """
        Log.debug(f"set {setting_bar} bar max: {max_value}")
        setting_bar.emit(max_value) # 發射 signal，傳遞進度百分比

    def update_current_line(self, line: Signal, current_line):
        """
        設置進度條的最大值

        Args:
            max_value (int): Progressbar最大值
        """
        Log.debug(f"Current item: {current_line}")
        line.emit(current_line)

    def update_result_table(self, index:int, check_value:int, check_result:bool):
        """
        更新Result Table
        """
        Log.debug(f"Update table index: {index}, result: {check_value}, check_result: {check_result}")
        self.items_table_updated.emit(index, check_value, check_result)

    def init_result_table(self):
        """
        初始化Result Table
        """
        Log.debug(f"Init result table.")
        self.items_table_init.emit()
       
    def show_message(self, title, message):
        """
        顯示測試完成訊息。
        """
        self.qbox_message.emit(title, message)

    def increment_fail_count(self, value):
        """
        失敗次數
        """
        self.fail_count.emit(value)

    def increment_pass_count(self, value):
        """
        通過次數
        """
        self.pass_count.emit(value)
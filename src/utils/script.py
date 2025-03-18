#===================================================================================================
# Import the necessary modules
#===================================================================================================
import os
import yaml # 導入 yaml 模組
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from src.utils.log import Log

#===================================================================================================
# Execute
#===================================================================================================
class ScriptValidationError(Exception):
    """自訂腳本驗證錯誤異常"""
    pass

@dataclass
class Product:
    model_name: str = ""        # 機種名
    mac_count: int = 0          # MAC數量
    serial_count: int = 0       # SN數量
    version: str = ""           # 產品版本
    mode: str = ""              # 配對或單側
    other_message: str = ""     # 備註

@dataclass
class ScriptItems:
    title: str = ""                   # 項目描述
    retry_message: str = ""           # Retry前的訊息
    valid_min: Optional[int] = None   # 測試最小值
    valid_max: Optional[int] = None   # 測試最大值
    unit: str = ""                    # 量測單位
    delay: float = 0.0                # 等待延遲
    execute: str = ""                 # 執行指令

@dataclass
class Script:
    version: str = ""                       # 版本號
    release_note: str = ""                  # 進版備註
    file_name: str = ""                     # 檔案名稱
    product: Product = field(default_factory=Product)
    items: List[ScriptItems] = field(default_factory=list)

class ScriptManager:
    def load_script(self, filename: str) -> Optional[Script]:
        """載入並解析腳本檔案

        Args:
            filename腳本檔案的路徑

        Returns:
            成功: Script
            失敗: None
        """
        if not os.path.exists(filename):
            Log.error("Script file not found: %s", filename)
            return None
        
        try:           
            with open(filename, 'r', encoding='utf-8') as file:
                script_data: Dict[str, Any] = yaml.safe_load(file)

            if script_data is None: # YAML 檔案為空或只有空白字元時 yaml.safe_load 會返回 None
                error_message = "驗證錯誤: YAML 檔案為空或僅包含空白字元"
                raise ScriptValidationError(error_message)
            
            # 驗證基本結構
            self._validate_script_structure(script_data)
            
            # 建立並填充 Script 物件
            script = Script(
                version=script_data.get("Version", ""),
                release_note=script_data.get("ReleaseNote", ""),
                file_name=filename
            )

            # 填充 Product 物件
            product_data = script_data.get("Product", {})
            script.product = self._parse_product(product_data)

            # 填充 Items 列表
            items_data = script_data.get("Items", [])
            script.items = self._parse_items(items_data)

            return script     
        except FileNotFoundError:
            Log.error(f"腳本檔案不存在: {filename}")
            return None
        except yaml.YAMLError as e: # 捕獲 yaml.YAMLError 異常
            Log.error(f"YAML 格式錯誤: {filename}. Error: {e}")
            return None    
        except ScriptValidationError as e:
            Log.error(f"Script validation error: {e}")
            return None
        except Exception as e:
            Log.error(f"Error loading script: {e}")
            return None

    def _validate_script_structure(self, script_data: Dict[str, Any]) -> None:
        """驗證腳本結構的有效性

        Args:
            script_data: 解析後的 YAML 資料

        Raises:
            ScriptValidationError: 如果結構無效則拋出異常
        """
        if not isinstance(script_data, dict):
            raise ScriptValidationError("Script data must be a YAML object (dictionary).")
        if "Product" not in script_data or not isinstance(script_data["Product"], dict):
            raise ScriptValidationError("Missing 'Product' section in script data.")
        if "Items" not in script_data or not isinstance(script_data["Items"], list):
            raise ScriptValidationError("Script data must contain an 'Items' list.")
    
    def _parse_product(self, product_data: Dict[str, Any]) -> Product:
        """解析產品資訊

        Args:
            product_data: 產品相關的 YAML 資料

        Returns:
            Product: 解析後的產品物件
        """
        return Product(
                model_name = str(product_data.get("Name", "")),
                mac_count = int(product_data.get("UseMac", 0)),
                serial_count = int(product_data.get("UseSn", 0)),
                version = str(product_data.get("Version", "")),
                mode = str(product_data.get("TestMode", "")),
                other_message = str(product_data.get("OtherMessage", ""))
            )

    def _parse_items(self, items_data: List[Dict[str, Any]]) -> List[ScriptItems]:
        """解析測試項目列表

        Args:
            items_data: 項目相關的 YAML 資料列表

        Returns:
            List[ScriptItems]: 解析後的項目物件列表

        Raises:
            ScriptValidationError: 如果項目格式無效則拋出異常
        """
        items = []
        for item_data in items_data:
            if not isinstance(item_data, dict):
                raise ScriptValidationError("Each item in 'items' list must be a YAML object (dictionary).")
            
            valid_range = str(item_data.get("Valid range", ""))
            min_val, max_val = self._valid_split(valid_range)
            items.append(ScriptItems(
                title = str(item_data.get("Title", "")),
                retry_message = str(item_data.get("Retry Message", "")),
                valid_min = int(min_val),
                valid_max = int(max_val),
                unit = str(item_data.get("Unit", "")),
                delay = float(item_data.get("Delay", 0)),
                execute = str(item_data.get("Execute", ""))
            ))

        return items

    def _valid_split(self, valid_range):
        try:
            min_val, max_val = map(int, valid_range.split(','))
        except Exception:
            return None, None
        return min_val, max_val

    def add_item(self, item):
        self.script.items.append(item)
    
    def remove_item(self, item):
        self.script.items.remove(item)

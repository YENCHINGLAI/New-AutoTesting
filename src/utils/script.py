import yaml # 導入 yaml 模組
import os
from src.utils.log import Log
from typing import List, Optional, Dict, Any

class Product:
    def __init__(self, model_name: str = "", mac_count: int = 0, serial_count: int = 0, version: str = "", 
                 mode: str = "", other_message: str = ""):
        self.model_name: str = model_name        #機種名
        self.mac_count:int = mac_count           #MAC數量
        self.serial_count:int = serial_count     #SN數量
        self.version:str = version               #產品版本
        self.mode:str = mode                     #配對或單側
        self.other_message:str = other_message   #備註

class ScriptItems:
    def __init__(self, title: str = "", retry_message: str = "", valid_min: int = None, valid_max: int = None, 
                 unit: str = "", delay: float = 0.0, execute: str = ""):
        self.title:str = title                   #項目描述
        self.retry_message:str = retry_message   #Retry前的訊息
        self.valid_min:int = valid_min           #測試最小值
        self.valid_max:int = valid_max           #測試最大值
        self.unit:str = unit                     #量測單位
        self.delay:float = delay                 #等待延遲
        self.execute:str = execute               #執行指令

class Script:
    def __init__(self):
        self.version: str = ""                   #版本號
        self.release_note: str = ""              #進版備註
        self.product: Product = Product()
        self.items: List[ScriptItems] = []       

class ScriptValidationError(Exception):
    """自訂腳本驗證錯誤異常"""
    pass

class ScriptManager:
    def __init__(self):
        self.script = Script()

    def load_script(self, filename: str) -> Optional[Script]:
        if not os.path.exists(filename):
            Log.error("Script file not found: %s", filename)
            return None
        
        try:
            self.script.file_name = filename
            
            with open(filename, 'r', encoding='utf-8') as file:
                script_data: Dict[str, Any] = yaml.safe_load(file)

            if script_data is None: # YAML 檔案為空或只有空白字元時 yaml.safe_load 會返回 None
                error_message = "驗證錯誤: YAML 檔案為空或僅包含空白字元。"
                raise ScriptValidationError(error_message)

             # --- 結構驗證 (Structure Validation) ---
            if not isinstance(script_data, dict):
                raise ScriptValidationError("Script data must be a YAML object (dictionary).")
            if "Product" not in script_data or not isinstance(script_data["Product"], dict):
                raise ScriptValidationError("Missing 'product' section in script data.")
            if "Items" not in script_data or not isinstance(script_data["Items"], list):
                raise ScriptValidationError("Script data must contain an 'items' list.")
            
            # 建立 Script 物件
            script = Script()    

            # 填充 Script 物件
            script.version = script_data.get("Version", "")
            script.release_note = script_data.get("Release note", "")

            # 填充 Product 物件
            product_data: Dict[str, Any] = script_data.get("Product", {})
            script.product = Product(
                model_name = str(product_data.get("Model Name", "")),
                mac_count = int(product_data.get("Mac Count", 0)),
                serial_count = int(product_data.get("Serial Count", 0)),
                version = str(product_data.get("Version", "")),
                mode = str(product_data.get("Mode", "")),
                other_message = str(product_data.get("Other Message", ""))
            )

            # 填充 Items 列表
            items_data: List[Dict[str, Any]] = script_data.get("Items", [])
            for item_data in items_data:
                if not isinstance(item_data, dict):
                    raise ScriptValidationError("Each item in 'items' list must be a YAML object (dictionary).")
                
                valid_range = str(item_data.get("Valid range", ""))
                min_val, max_val = self.valid_split(valid_range)
                script.items.append(ScriptItems(
                    title = str(item_data.get("Title", "")),
                    retry_message = str(item_data.get("Retry Message", "")),
                    valid_min = int(min_val),
                    valid_max = int(max_val),
                    unit = str(item_data.get("Unit", "")),
                    delay = float(item_data.get("Delay", 0)),
                    execute = str(item_data.get("Execute", ""))
                ))
            self.script = script
            return script
        
        except FileNotFoundError:
            Log.error(f"Script file not found: {filename}")
            return None
        except yaml.YAMLError as e: # 捕獲 yaml.YAMLError 異常
            Log.error(f"Invalid YAML format in script file: {filename}. Error: {e}")
            return None    
        except ScriptValidationError as e:
            Log.error(f"Script validation error: {e}")
            return None
        except Exception as e:
            Log.error(f"Error loading script: {e}")
            return None
               
    def valid_split(self, valid_range):
        min_val, max_val = map(int, valid_range.split(','))
        return min_val, max_val
    
    def save_script(self, filename):
        pass

    def add_item(self, item):
        self.script.items.append(item)
    
    def remove_item(self, item):
        self.script.items.remove(item)

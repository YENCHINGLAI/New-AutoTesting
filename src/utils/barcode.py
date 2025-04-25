from PySide6.QtWidgets import QWidget, QMessageBox, QInputDialog
from PySide6.QtCore import Qt

import src.utils.commonUtils as commonUtils
from src.utils.script import Script
from src.utils.log import Log

def _scan_with_input_dialog(parent_widget: QWidget, prompt: str, title: str ="掃描條碼") -> str:
    """
    使用 PySide6 的 QInputDialog 來模擬掃描條碼。

    Args:
        parent_widget (QWidget): 呼叫此對話方塊的父視窗元件。
        prompt (str): 顯示在輸入對話方塊中的提示文字。
        title (str): 輸入對話方塊的視窗標題。

    Returns:
        str: 使用者輸入的文字，如果取消或輸入為空，則返回 'N/A'。
    """
    if not isinstance(parent_widget, QWidget):
        Log.error("Invalid parent widget provided for QInputDialog.")
        # 或者可以引發 TypeError
        # raise TypeError("parent_widget must be a QWidget instance.")
        return 'N/A'
    
    try:
        # 顯示文字輸入對話方塊
        # 返回值是 (text, ok_pressed) 的元組
        text, ok = QInputDialog.getText(
            parent_widget, 
            title, 
            prompt, 
            inputMethodHints = Qt.InputMethodHint.ImhNoPredictiveText
            ) # 增加 ImhNoPredictiveText 避免干擾掃描槍

        if ok:
            # 使用者點擊了 OK
            cleaned_text = text.strip() if text else "" # 確保 text 不是 None 才 strip
            if cleaned_text:
                Log.info(f"Input dialog received: '{cleaned_text}' for prompt: '{prompt}'")
                return cleaned_text
            else:
                Log.warn(f"Input dialog received empty input for prompt: '{prompt}', treating as N/A.")
                # QMessageBox.warning(parent_widget, "輸入警告", "掃描輸入為空。")
                # return 'N/A'
                return cleaned_text
        else:
            # 使用者點擊了 Cancel
            Log.warn(f"Input dialog cancelled by user for prompt: '{prompt}'. Returning N/A.")
            return 'N/A'

    except Exception as e:
        Log.error(f"Error displaying input dialog: {e}", exc_info=True)
        # 顯示錯誤訊息給使用者
        QMessageBox.critical(parent_widget, "錯誤", f"顯示掃描對話方塊時發生錯誤:\n{e}")
        return 'N/A'   
    
def _maybe_allow_na(barcode_type: str) -> bool:
    """
    決定特定類型的條碼是否允許 'N/A' (未掃描/取消)。
    在這裡你可以根據實際需求自訂邏輯。
    例如，MO 和 SN 可能不允許 N/A，但 MAC 可以。
    """
    if barcode_type in ["MO"]:
        return False # 不允許 N/A
    else:
        return True # 允許 N/A
    
def collect_product_barcodes_old(parent_widget: QWidget, script_config: Script) -> dict | None:
    """
    根據腳本配置，使用 PySide6 InputDialog 收集條碼。

    Args:
        script_config (dict): 包含腳本設定的字典。

    Returns:
        dict: 包含掃描到的產品資訊的字典，或在出錯時返回 None。
    """
    product_info = {}
    active_device_id = 0 # 用於錯誤日誌
    
    try:
        pairing_mode = getattr(script_config, 'pairing', 0) # 取得 pairing 模式，預設為 0 (不配對)
        num_devices_to_scan = pairing_mode + 1
        Log.info(f"Starting barcode collection for {num_devices_to_scan} device(s).")

        for i in range(num_devices_to_scan):
            active_device_id = i + 1
            Log.info(f"--- Processing Device {active_device_id} ---")

            if i >= len(getattr(script_config, 'product', [])):
                Log.error(f"Script config 'product' list does not have an element at index {i}.")
                QMessageBox.critical(parent_widget, "配置錯誤", f"腳本配置缺少第 {i+1} 個產品的資訊。")
                return None
            
            product_config = script_config.product[i]
            use_sn = getattr(product_config[i],'sn_count', 0)
            use_mac = getattr(product_config[i], 'mac_count', 0)

            mo_key = f"$mo{active_device_id}"
            sn_key = f"$sn{active_device_id}"

            # --- 掃描 MO ---
            result = _scan_with_input_dialog(parent_widget,f"[{active_device_id}] 請掃描 MO 條碼:")
            if result == 'N/A' and not _maybe_allow_na("MO"): # 如果 MO 不允許 N/A
                Log.error(f"MO scan for device {active_device_id} failed or was cancelled.")
                # 可以在此處中止流程或提示重試
                QMessageBox.critical(parent_widget, "掃描失敗", f"設備 {active_device_id} 的 MO 條碼掃描失敗或被取消，流程中止。")
                return None # 中止流程
            product_info[mo_key] = result

            # --- 掃描 SN ---
            if use_sn:
                result = _scan_with_input_dialog(parent_widget, f"[{active_device_id}] 請掃描 SN 條碼:")
                if result == 'N/A' and not _maybe_allow_na("SN"): # 如果 SN 不允許 N/A
                    Log.error(f"SN scan for device {active_device_id} failed or was cancelled.")
                    QMessageBox.critical(parent_widget, "掃描失敗", f"設備 {active_device_id} 的 SN 條碼掃描失敗或被取消，流程中止。")
                    return None
                product_info[sn_key] = result
            else:
                Log.info(f"[{active_device_id}] 不需要掃描 SN.")
                product_info[sn_key] = 'N/A'

            # --- 掃描 MAC ---
            if use_sn and use_mac: # 只有需要 SN 且需要 MAC 時才掃描 MAC1
                for mac_index in range(1, use_mac + 1):
                    mac_key = f"$mac{active_device_id}{mac_index}"
                    result = _scan_with_input_dialog(parent_widget, f"[{active_device_id}] 請掃描 MAC-{mac_index} 條碼:")
                    if result == 'N/A' and not _maybe_allow_na(f"MAC-{mac_index}"): # 如果 MAC1 不允許 N/A
                        Log.error(f"MAC-1 scan for device {active_device_id} failed or was cancelled.")
                        QMessageBox.critical(parent_widget, "掃描失敗", f"設備 {active_device_id} 的 MAC-{mac_index} 條碼掃描失敗或被取消，流程中止。")
                        return None
                    product_info[mac_key] = result

            Log.info(f"--- Device {active_device_id} processing complete ---")

        Log.info("--- All barcode collection finished ---")
        Log.info(f"Collected Product Info: {product_info}")
        return product_info

    except Exception as e:
        Log.error(f"Unexpected error during barcode collection: {e}", exc_info=True)
        QMessageBox.critical(parent_widget, "嚴重錯誤", f"收集條碼過程中發生意外錯誤:\n{e}")
        return None # 返回 None 表示流程失敗     
    
def collect_product_barcodes(parent_widget: QWidget, script_config: Script) -> dict | None:
    """
    根據腳本配置，使用 PySide6 InputDialog 收集條碼。

    Args:
        script_config (dict): 包含腳本設定的字典。

    Returns:
        dict: 包含掃描到的產品資訊的字典，或在出錯時返回 None。
    """
    product_info = {}
    active_device_id = 0 # 用於錯誤日誌
    
    try:
        pairing_mode = getattr(script_config, 'pairing', 0) # 取得 pairing 模式，預設為 0 (不配對)
        num_devices_to_scan = pairing_mode + 1
        Log.info(f"Starting barcode collection for {num_devices_to_scan} device(s).")

        # --- 嵌套的掃描與驗證輔助函數 ---
        def _scan_and_validate(
            barcode_type: str,
            barcode_key: str,
            scan_prompt: str,
            validator, # 驗證函數，例如 validators.is_mo
            allow_na: bool,
            validation_args: dict = None # 傳遞給驗證函數的額外參數
        ) -> bool:
            """
            處理單個條碼的掃描、驗證、重試迴圈。

            Args:
                barcode_type: 條碼類型 (用於日誌和錯誤訊息, e.g., "MO", "SN").
                barcode_key: 儲存結果時使用的字典鍵 (e.g., "$mo1").
                scan_prompt: 顯示給使用者的掃描提示。
                validator: 用於驗證輸入的函數。
                allow_na: 是否允許此條碼為 'N/A' (使用者取消或空輸入)。
                validation_args: 傳遞給 validator 函數的關鍵字參數字典。

            Returns:
                True: 如果掃描和驗證成功 (或允許 N/A)。
                False: 如果掃描失敗且 *不* 允許 N/A，表示應中止流程。
            """
            nonlocal product_info, active_device_id # 允許修改外部的 product_info
            current_device_id = active_device_id # 捕獲當前設備ID用於錯誤消息

            while True: # 驗證失敗時的重試迴圈
                scanned_value = _scan_with_input_dialog(parent_widget, scan_prompt)

                if scanned_value == 'N/A':
                    if not allow_na:
                        msg = f"設備 {current_device_id} 的必要 {barcode_type} 條碼掃描失敗或被取消，流程中止。"
                        Log.error(msg)
                        QMessageBox.critical(parent_widget, "掃描失敗", msg)
                        return False # 中止信號
                    else:
                        Log.warn(f"Optional {barcode_type} scan for device {current_device_id} cancelled or empty.")
                        product_info[barcode_key] = 'N/A' # 記錄為 N/A
                        return True # 成功 (因為允許 N/A)

                # --- 執行驗證 ---
                validation_kwargs = validation_args if validation_args else {}
                try:
                    is_valid = validator(scanned_value, **validation_kwargs)
                except Exception as val_err:
                    Log.error(f"Validator function for {barcode_type} raised an error: {val_err}", exc_info=True)
                    QMessageBox.critical(parent_widget,"驗證錯誤",f"驗證 {barcode_type} 時發生內部錯誤。")
                    # 考慮是否中止流程
                    return False # 或者 True 如果允許跳過？取決於策略

                if is_valid:
                    Log.info(f"Validation successful for {barcode_type} (Device {current_device_id}): '{scanned_value}'")
                    product_info[barcode_key] = scanned_value # 儲存有效值
                    return True # 成功，跳出重試迴圈
                else:
                    # 驗證失敗，提示重試
                    Log.warn(f"Invalid format for {barcode_type} (Device {current_device_id}): '{scanned_value}'. Please rescan.")
                    QMessageBox.warning(parent_widget, "輸入格式錯誤",
                                        f"掃描的 {barcode_type} '{scanned_value}' 格式不正確。\n請重新掃描。")
                    # 迴圈繼續，再次呼叫 _scan_with_input_dialog

         # --- 主迴圈：處理每個設備 ---
        for i in range(num_devices_to_scan):
            active_device_id = i + 1
            Log.info(f"--- Processing Device {active_device_id} ---")

            if active_device_id > len(getattr(script_config, 'product', [])):
                msg = f"腳本配置錯誤：找不到第 {active_device_id} 個產品的配置信息。"
                Log.error(msg)
                QMessageBox.critical(parent_widget, "配置錯誤", msg)
                return None
            
            product_config = script_config.product[i]
            sn_count = getattr(product_config,'sn_count', 0)
            mac_count = getattr(product_config, 'mac_count', 0)

            # --- 掃描 MO ---
            mo_key = f"$mo{active_device_id}"
            mo_prompt = f"[{active_device_id}] 請掃描 MO 條碼:"
            mo_validator = lambda x: commonUtils.is_mo(x) or commonUtils.is_pcb(x) or commonUtils.is_testjig(x) # 允許 MO、PCB 或 TestJig
            if not _scan_and_validate("MO", mo_key, mo_prompt, mo_validator, allow_na=False):
                # 如果掃描失敗且不允許 N/A，則中止流程
                return None

            # --- 掃描 SN ---
            sn_key = f"$sn{active_device_id}"
            if sn_count > 0:
                sn_prompt = f"[{active_device_id}] 請掃描 SN 條碼:"
                if not _scan_and_validate("SN", sn_key, sn_prompt, commonUtils.is_sn_nosign, allow_na=False):
                    # 如果掃描失敗且不允許 N/A，則中止流程
                    return None
            else:    
                Log.info(f"[{active_device_id}] Skipping SN scan (sn_count={sn_count}).")
                product_info[sn_key] = 'N/A' # 確保有 SN 鍵，即使未掃描

            # --- 掃描 MAC ---
            if sn_count > 0 and mac_count > 0: # 只有需要 SN 且需要 MAC 時才掃描 MAC1
                Log.info(f"[{active_device_id}] Skipping MAC scan (mac_count={mac_count}).")
                for mac_index in range(1, mac_count + 1):
                    mac_key = f"$mac{active_device_id}{mac_index}"
                    mac_type = f"MAC-{mac_index}"
                    mac_prompt = f"[{active_device_id}] 請掃描 {mac_type} 條碼:"
                    mac_validator = lambda x: commonUtils.is_mac(x) or commonUtils.is_mac_nosign(x) # 允許帶符號或不帶符號的 MAC
                    if not _scan_and_validate(mac_type, mac_key, mac_prompt, mac_validator, allow_na=False):
                         # 即使 _scan_and_validate 返回 False (理論上在 allow_na=True 時不會)
                         # 但如果 validator 內部出錯可能返回 False，這裡決定是否中止
                         Log.error(f"Critical error during optional MAC scan for {mac_key}. Aborting.")
                         return None # 決定中止
                    # 如果返回 True, 值已存入 product_info (可能是有效 MAC 或 'N/A')
            else:
                # 確保即使不掃描 MAC，後續邏輯也不會因缺少鍵而出錯 (如果需要的話)
                # 目前做法：不掃描就不添加 MAC 鍵
                if sn_count > 0:
                    Log.info(f"[{active_device_id}] 不需要掃描 MAC (sn_count={sn_count}, mac_count={mac_count}).")
                   

            Log.info(f"--- Device {active_device_id} processing complete ---")

        Log.info("--- All barcode collection finished ---")
        Log.info(f"Collected Product Info: {product_info}")
        return product_info
    except AttributeError as ae:
        Log.error(f"Attribute error during barcode collection: {ae}", exc_info=True)
        QMessageBox.critical(parent_widget, "配置錯誤", f"腳本配置錯誤:\n{ae}")
        return None
    except Exception as e:
        Log.error(f"Unexpected error during barcode collection: {e}", exc_info=True)
        QMessageBox.critical(parent_widget, "嚴重錯誤", f"收集條碼過程中發生意外錯誤:\n{e}")
        return None # 返回 None 表示流程失敗     
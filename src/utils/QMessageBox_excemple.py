# QMessageBox 範例


def show_message_examples(self):
        """消息框示例"""
        # 信息提示框
        QMessageBox.information(
            self,
            "提示",
            "操作已完成",
            QMessageBox.StandardButton.Ok
        )

        # 警告框
        QMessageBox.warning(
            self,
            "警告",
            "檢測到異常情況",
            QMessageBox.StandardButton.Ok
        )

        # 錯誤框
        QMessageBox.critical(
            self,
            "錯誤",
            "操作失敗",
            QMessageBox.StandardButton.Ok
        )

        # 確認框（帶有是/否按鈕）
        reply = QMessageBox.question(
            self,
            "確認",
            "確定要執行此操作嗎？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No  # 默認按鈕
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            print("用戶選擇了是")
        else:
            print("用戶選擇了否")

        # 自定義按鈕
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("選擇")
        msg_box.setText("請選擇要執行的操作：")
        msg_box.addButton("保存", QMessageBox.ButtonRole.AcceptRole)
        msg_box.addButton("不保存", QMessageBox.ButtonRole.RejectRole)
        msg_box.addButton("取消", QMessageBox.ButtonRole.DestructiveRole)
        
        reply = msg_box.exec()
        button_text = msg_box.clickedButton().text()
        print(f"用戶點擊了：{button_text}")
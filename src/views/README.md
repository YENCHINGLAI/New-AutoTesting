# Agenda
1. 安裝Qt
2. Qt Designer
3. Ui 轉換
4. 主程式引用轉換後的py檔
5. signal與slot綁定

# 1. 安裝 Qt
## pyQt6
```python=
pip install pyqt6
pip install Pyqt6-tools
```
## pySide6
```
pip install pyside6
```

# 2. Qt Designer
## pyQt6
```
.\專案資料夾\venv\Lib\site-packages\qt6_applications\Qt\bin\designer.exe
```
## pySide6
```
.\專案資料夾\venv\Lib\site-packages\PySide6\designer.exe
```

# 3. Ui 轉換
## pyQt6
```
pyui6 -x <要轉換的.ui檔> -o <輸出.py檔>
pyuic6 -x ui_main.ui -o ui_main.py 
```

## pySide6
```
pyside6-uic <要轉換的.ui檔> -o <輸出.py檔>
pyside6-uic .\Ui_Main.ui -o .\Ui_Main.py
```

# 4. 主程式引用轉換後的py檔
```python=
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from ui_main_ui import Ui_MainWindow    # 使用者設計的樣板

if __name__ == "__main__":
        app = QApplication(sys.argv)    # 產生程式物件
        window = QMainWindow()          # 產生視窗物件
        ui = Ui_MainWindow()            # 產生import後的ui物件
        ui.setupUi(window)              # 將ui設計套用到視窗內
        window.show()                   # 顯示主程式
        sys.exit(app.exec())                      
```

# 4. signal與slot綁定
假設剛剛ui設計有兩個按鍵Btn_About, Btn_Start
```python=
self.ui.Btn_About.clicked.connect(self.show_about)
self.ui.Btn_Start.clicked.connect(self.start_test)

def start_test():
    """開始測試前的確認"""
    QMessageBox.question(
        self,
        "確認開始測試",
        "是否開始執行測試？",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No
    )
        
def show_about(self):
    """關於視窗"""
    ver = '1.0.0000'
    user='TEST01'
    text = "<center>" \
        "<h1>Auto Testing</h1>" \
        "&#8291;" \
        "</center>" \
        f"<p>User {user}<br/>" \
        f"<p>Version {ver}<br/>" \
        "Copyright &copy; Cypress Technologies Inc.</p>"
    
    QMessageBox.about(self, "About Auto Testing", text)
```
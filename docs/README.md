# 專案架構
# New_AutoTesting/
#   |-- __main__.py                     #專案主程式進入點
#   |-- src/                            #程式碼
#   |    |-- controllers/               #主程式
#   |    |    |-- main_controller.py
#   |    |-- models/                    #資料模型
#   |    |    |-- data_model.py
#   |    |-- views/                     #desigher產出之控件樣式
#   |    |    |-- ui_main_ui.py
#   |    |    |-- ui_main_ui.ui
#   |    |-- utils/                     #使用的Tool
#   |         |-- telnet
#   |         |-- serial
#   |         |-- ...
#   |-- res/                            #程式所需資源 Ex.圖片,樣式
#   |    |-- images/
#   |    |    |-- cyp.png               #Loding圖案
#   |    |-- styles/
#   |    |    |-- ui_main.qss           #介面樣式
#   |    |-- icons/
#   |         |-- cyp.ico               #EXE logo
#   |-- packege                         #部屬用打包檔案
#   |-- tools                           #API工具
#   |-- venv                            #虛擬環境
#   |-- requirements.txt                #專案套件訊息
#   |-- docs                            #專案相關文件
#   |    |-- README.md                  #專案架構說明
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#                       _oo0oo_
#                      o8888888o
#                      88" . "88
#                      (| -_- |)
#                      0\  =  /0
#                    ___/`---'\___
#                  .' \\|     |# '.
#                 / \\|||  :  |||# \
#                / _||||| -:- |||||- \
#               |   | \\\  -  #/ |   |
#               | \_|  ''\---/''  |_/ |
#               \  .-\__  '-'  ___/-. /
#             ___'. .'  /--.--\  `. .'___
#          ."" '<  `.___\_<|>_/___.' >' "".
#         | | :  `- \`.;`\ _ /`;.`/ - ` : | |
#         \  \ `_.   \_ __\ /__ _/   .-` /  /
#     =====`-.____`.___ \_____/___.-`___.-'=====
#                       `=---='
#
#     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#               佛祖保佑         永無BUG
#
#             Buddha bless      Never BUGG
#
#     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#===================================================================================================
# Splash screen
#===================================================================================================
import os
import tempfile
# 檢查是否在 Nuitka 打包的環境中
if "NUITKA_ONEFILE_PARENT" in os.environ:
   # 建立臨時文件路徑，用於通知關閉啟動畫面
   splash_filename = os.path.join(
      tempfile.gettempdir(),
      "onefile_%d_splash_feedback.tmp" % int(os.environ["NUITKA_ONEFILE_PARENT"]),
   )

   # 如果臨時文件存在，刪除它來觸發啟動畫面的關閉
   if os.path.exists(splash_filename):
      os.unlink(splash_filename)

#===================================================================================================
# Import the necessary modules
#===================================================================================================
import sys

# 切換到程式所在目錄
abs_pth = os.path.abspath(sys.argv[0])
working_dir = os.path.dirname(abs_pth)
os.chdir(working_dir)

from src.controllers.mainController import MainController
from src.utils.log import Log

#===================================================================================================
# Code
#===================================================================================================
if __name__ == "__main__":
    try:
        Log.init()
        MainController.main()
    except (RuntimeError, OSError) as e:  # 捕獲特定的異常
        Log.error(e)
        print(f"應用程序啟動錯誤: {e}")
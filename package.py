# Description: 打包程式
# Nuitka==2.4.8
# zstandard==0.23.0

import os
import subprocess
import shutil
from src.config import config

# 主程式資訊
APP_NAME = config.APP_NAME # "AutoTestingSystem" # 打包後的應用程式名稱
APP_VERSION = config.REAL_VERSION # "0.1.0"
DESCRIPTION = "New Auto Testing System"
COPYRIGHT = "Copyright 2025"
COMPANY_NAME = "Cypress Technology Co., Ltd"

# 專案根目錄
project_root = os.path.dirname(os.path.abspath(__file__))
print(project_root)

#===================================================================================================
# 打包參數
#===================================================================================================
def build(main, method):
    # 打包參數配置
    nuitka_cmd = [
        'nuitka',

        # 建立獨立環境
        '--standalone',     

        # 使用MinGW編譯器
        '--mingw64',   

        # 顯示包含的模組
        # '--show-modules',

        # Include模組
        '--follow-imports',
        '--enable-plugin=pyside6',

        # App icon
        f'--windows-icon-from-ico="{project_root}/res/icons/cyp.ico"',

        # 外觀樣式，會搬到打包後的專案內
        # '--include-data-dir=res=res',
        # '--include-data-dir=res/report=res/report',

        # API副程式 (將其他會用到的exe，複製到打包專案內)
        '--include-data-files=tools/*.exe=tools/',          # tools資料夾下所有exe檔
        # '--include-data-files=tools/*.dll=tools/',          # tools資料夾下所有dll檔

        # 清理中間編譯檔案
        '--remove-output',

        # 開啟中載入畫面 (單檔打包Only)
        # '--onefile',
        # f'--onefile-windows-splash-screen-image={project_root}/res/images/Loading.png',

        # 應用程式資訊
        f'--output-filename="{APP_NAME}"',
        f'--product-version="{APP_VERSION}"',
        f'--file-version="{APP_VERSION}"',
        f'--file-description="{DESCRIPTION}"',
        f'--company-name="{COMPANY_NAME}"',
        f'--copyright="{COPYRIGHT}"'
    ]

    # debug: 有console, api.exe都必須使用這個
    # release: 無console
    if method == "0":
        path = os.path.join(os.getcwd(), output_dir, 'debug')
        nuitka_cmd.append(f'--output-dir="{path}"')     # 指定最终文件的输出目录
    elif method == "1":
        path = os.path.join(os.getcwd(), output_dir, 'release')
        nuitka_cmd.append("--disable-console")          # 禁用控制台窗口
        nuitka_cmd.append(f'--output-dir="{path}"')     # 指定最终文件的输出目录
    else:
        raise ValueError
    
    # nuitka
    os.system(f"{' '.join(nuitka_cmd)} {main}.py")   
    print(f"{' '.join(nuitka_cmd)} {main}.py")
    return os.path.join(path, main + '.dist')

def execute_cmd(cmd):
    try:
        # 執行打包
        print("開始打包...")

        # 執行上面寫好的nuitka command
        process = subprocess.Popen(
            cmd,
            cwd=project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # 即時顯示編譯輸出
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())

        return_code = process.poll()
        
        if return_code == 0:
            print("\n打包成功！")
            return True
        else:
            print(f"\n打包失敗，錯誤代碼：{return_code}")
    except Exception as e:
        print(f"發生錯誤：{e}")

    return False

def movedir(src_path):
    dst_path = os.path.join(project_root, '.Update')
    os.makedirs(dst_path, exist_ok=True)
    shutil.copy(src_path, os.path.join(dst_path, os.path.basename(src_path)))

def zipdir(src_path):
    dst_path = os.path.join(project_root, '.Update', enter)
    shutil.make_archive(dst_path, 'zip', src_path)

    # 刪除原始資料夾
    # shutil.rmtree(src_path)

    print(f"打包完成，檔案位置：{dst_path}")

if __name__ == '__main__':
    try:
        # 要編譯的.PY檔案 (不需要寫.py)
        enter = 'AutoTesting'

        # # 輸出資料夾
        output_dir = os.path.join(project_root, 'package')
        os.makedirs(output_dir, exist_ok = True)

        # # 產生打包指令
        exe_path = build(enter, input("[Debug(0) / Release(1)]："))
        exe_path = r"C:\OneDrive-YC\OneDrive - CYPRESS TECHNOLOGY CO.,LTD\Python\New_AutoTesting\package\release\AutoTesting.dist"

        # 改名
        #os.rename(exe_path, enter)

        #壓縮
        zipdir(exe_path)

        # 搬到publish
        # movedir(exe_path)

    except Exception as e:
        print(f"發生錯誤：{e}")
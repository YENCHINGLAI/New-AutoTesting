import os
import subprocess
import sys

DEPLOY_FILE='subprocess_test.py'
APP_NAME="subprocess_test"
APP_VERSION="0.0.1"
DESCRIPTION='Auto Testing Application'
COPYRIGHT='Copyright 2025'
COMPANY_NAME="Cypress Technology Co., Ltd"

# 輸出資料夾
OUTPUT_DIR='package'

def build_executable():
    # 專案根目錄
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 打包參數配置
    nuitka_cmd = [
        sys.executable, '-m', 'nuitka',
        # 打包參數
        '--standalone',
        # Include模組
        '--follow-imports',
        # '--enable-plugin=anti-bloat',
        # '--enable-plugin=multiprocessing',
        # '--include-data-files=execute.txt=execute.txt',
        # App icon
        # f'--windows-icon-from-ico={project_root}\\res\\icons\\cyp.ico',
        # 外觀樣式
        # '--include-data-dir=res=res',
        # API副程式
        # '--include-data-dir=src\\utils=utils',
        # 輸出資料夾
        f'--output-dir={OUTPUT_DIR}',
        # 關閉命令提示畫面
        #'--disable-console',
        # 清理中間編譯檔案
        '--remove-output',
        # 單檔打包,載入畫面
        '--onefile',
        # f'--onefile-windows-splash-screen-image={project_root}\\res\\images\\Loading.png',
        # 應用程式資訊
        f'--output-filename={APP_NAME}',
        f'--product-version={APP_VERSION}',
        f'--file-version={APP_VERSION}',
        f'--file-description={DESCRIPTION}',
        f'--company-name={COMPANY_NAME}',
        f'--copyright={COPYRIGHT}',
        # 打包的主程式
        DEPLOY_FILE
    ]
    
    try:
        # 確保pakege目錄存在
        os.makedirs(os.path.join(project_root, OUTPUT_DIR), exist_ok=True)
        
        # 執行打包
        print("開始打包...")
#===================================================================================================
        # # '不'即時顯示編譯輸出
        # result = subprocess.run(nuitka_cmd, cwd=project_root, capture_output=True, text=True)
        
        # # 檢查打包結果
        # if result.returncode == 0:
        #     print("打包成功！")
        #     print(f"可執行文件位於 {OUTPUT_DIR} 目錄")
        # else:
        #     print("打包失敗：")
        #     print(result.stderr)

#===================================================================================================
        # 執行上面寫好的nuitka command
        process = subprocess.Popen(
            nuitka_cmd,
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
            print(f"可執行文件位於 {OUTPUT_DIR} 目錄")
        else:
            print(f"\n打包失敗，錯誤代碼：{return_code}")
    
    except Exception as e:
        print(f"發生錯誤：{e}")

if __name__ == '__main__':
    build_executable()
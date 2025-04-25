import os
import subprocess
import time
import sys

# 切換到程式所在目錄
abs_pth = os.path.abspath(sys.argv[0])
working_dir = os.path.dirname(abs_pth)
os.chdir(working_dir)

def read_file(filename):
    try:
        real_path = os.path.join(working_dir, filename)
        print(f"Real path: {real_path}")
    except NameError:
        real_path = os.path.join(os.path.dirname(sys.argv[0]), filename)
        print(f"Real path ex: {real_path}")

    try:
        with open(real_path, 'r', encoding='utf-8') as file:
            lines_array = list(file)
            lines_array = [line.strip() for line in lines_array]
        return lines_array
    except FileNotFoundError:
        print(f"找不到檔案: {real_path}")
        return []

def command_mac_sn_replace(command_template, mac_value, sn_value):
    # 替換命令中的 $mac 和 $sn 變數
    return command_template.replace('$mac', mac_value or '$mac')\
                           .replace('$sn', sn_value or '{$sn}')

def execute_with_run(command):
    try:       
        # 執行命令
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        
        if result.returncode == 0:
            print("命令執行成功")
            print("輸出:", result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"執行錯誤: {e}")
        print(f"錯誤輸出: {e.stderr}")
        return None

# 使用 Popen
def execute_with_popen(command):
    stdout = ''
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            text=True
            )

        stdout = process.communicate()
        if stdout:
            return stdout
        else:
            return None
    except subprocess.TimeoutExpired as e:
        print(f"執行超時: {e}")
        return None
    except subprocess.CalledProcessError as e:
        print(f"執行錯誤: {e}")
        print(f"錯誤輸出: {e.stderr}")
        return None

if __name__ == '__main__':
    print('Root: ', working_dir)
    print(f"Dir List: {os.listdir(working_dir)}")
        
    mac = 'COM13'
    sn = ""
    execute_list = read_file('execute.txt')

    for command in execute_list:
        new_command = command_mac_sn_replace(command, mac, sn)
        print(f"Command: {new_command}")

        #使用Popen
        time_start = time.time()
        result = execute_with_popen(new_command)
        print(f"Execute: {result}")
        print('Popen Time cost:', time.time() - time_start, 'seconds')

        # 使用Run
        time_start = time.time()
        result = execute_with_run(new_command)
        print(f"Execute: {result}")
        print('Run Time cost:', time.time() - time_start, 'seconds')
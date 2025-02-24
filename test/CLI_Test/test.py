import os
import subprocess
import time

def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        lines_array = list(file)
        lines_array = [line.strip() for line in lines_array]
    return lines_array

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
        process = subprocess.Popen(command, stdout=subprocess.PIPE, text=True)

        stdout = process.communicate(timeout=5.0)

        # 及時輸出測試
        # output=''

        # while True:
        #     output = process.stdout.readline()
        #     if output == '' and process.poll() is not None:
        #         break
        #     if '1' or '0' or '-1' in output:
        #         print("輸出:",output.strip())
        #         return output.strip()
        # return output

        # 單次輸出測試
        # if process.returncode == 0:
        #     print("輸出:", stdout)

        # return stdout

        # 時間量測
        # return ''
    except subprocess.TimeoutExpired as e:
        print(f"執行超時: {e}")
        if stdout:
            return stdout
        else:
            return None
    except subprocess.CalledProcessError as e:
        print(f"執行錯誤: {e}")
        print(f"錯誤輸出: {e.stderr}")
        return None

# 使用 Popen
def execute_with_call(command):
    try:
        result = subprocess.call(
            command,
            stdout=subprocess.PIPE,
            text=True,
        )

        return result
    except subprocess.CalledProcessError as e:
        print(f"執行錯誤: {e}")
        print(f"錯誤輸出: {e.stderr}")
        return None

if __name__ == '__main__':
    mac = 'COM13'
    sn = ""
    # 專案根目錄
    project_root = os.path.dirname(os.path.abspath(__file__))   
    execute_list = read_file('execute.txt')

    for command in execute_list:   
        new_command = command_mac_sn_replace(command, mac, sn)
        print(f"Command: {new_command}")

        # # 使用Run
        # time_start = time.time()
        # result = execute_with_call(new_command)
        # print(f"Execute: {result}")
        # print('Call Time cost:', time.time() - time_start, 'seconds')

        # 使用Popen
        time_start = time.time()
        result = execute_with_popen(new_command)
        print(f"Execute: {result}")
        print('Popen Time cost:', time.time() - time_start, 'seconds')

        # # 使用Run
        # time_start = time.time()
        # result = execute_with_run(new_command)
        # print(f"Execute: {result}")
        # print('Run Time cost:', time.time() - time_start, 'seconds')
import argparse
import py_netgear_plus 

ip_addr = '192.168.100.2' # replace with IP address of your switch
p = '@Cyp22232020@' # replace with your password

def run_poe_api(ip, pw, port, power):
    sw = py_netgear_plus.NetgearSwitchConnector(ip, pw)
    try:
        sw.autodetect_model()
        # 需在get_login_cookie前執行，注入之前登入過的cookie
        # sw.set_cookie('SID','boDRp_fZEOLIYOXDmv[oUep^ZSdDgPLPkgJfRuy^c\\gtSukt`TZCZNGrBZmEdBgjp^mVoweIJquKETnI')
        cookie_status = sw.get_login_cookie()
        cookie = sw.get_cookie()

        # data = sw.get_switch_infos()
        # print(sw.switch_model.MODEL_NAME)
        # print(data["port_5_poe_output_power"])
        # print(data["port_6_poe_output_power"])

        # if power == 0:
        #     sw.turn_off_poe_port(port) # Supported only on PoE capable models
        # else:
        #     sw.turn_on_poe_port(port)
        return 1
    except Exception as e:
        return -1
    finally:
        sw.delete_login_cookie()

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(prog='poe_api',description="Netgear POE API")    
    # parser.add_argument("ip",type=str, help="")
    # parser.add_argument("password",type=str, help="")
    # parser.add_argument("port",type=int, help="")
    # parser.add_argument("power",type=int, help="")
    # args = parser.parse_args()

    try:
        # run_poe_api(args.ip, args.password, args.port ,args.power)
        run_poe_api(ip_addr, p, 6 ,1)
    except Exception as e:
        print(e)
        print('-1')
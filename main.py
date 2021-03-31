# Created by Mahdi Parastesh, February and March 2021
# Github: https://github.com/fulcrum1378
# All rights reserved.

import MetaTrader5 as mt5
import simple_http_server.server as server
import webbrowser

import data

data.get_config()

import analyze, watch

print("SQLite:", data.do_connect())
print("Mofid:", data.init_mofid())
data.init_analyzer(analyze.Analyzer())
data.init_watcher(watch.Watcher())

try:
    from netifaces import ifaddresses

    my_ip = ifaddresses(ni.gateways()['default'][ni.AF_INET][1])[ni.AF_INET][0]['addr']
except:
    my_ip = input("Please enter your device's IP address:")
webbrowser.open("http://" + str(my_ip) + ":1399/")
try:
    server.scan("", r".*controller.*")
    server.start(host=my_ip, port=1399)
except Exception as e:
    if str(e) == "[WinError 10022] Windows Error 0x2726":
        print("ERROR STARTING SERVER: ", my_ip + " IS NOT YOUR DEVICE'S IP ADDRESS!")
    else:
        print("ERROR STARTING SERVER: ", e)

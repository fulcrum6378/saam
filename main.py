import MetaTrader5 as mt5
import simple_http_server.server as server

import data

print("Connecting to MofidTrader...")
if not mt5.initialize("C:/Program Files/MofidTrader/terminal64.exe",
                      login=2646769,
                      password="cngs5iov",
                      server="MofidSecurities-Server"):
    print("Could not connect to MofidTrader!!")
    quit()
print("DONE!")

print("Connecting to MySQL...")
data.get_config()
data.do_connect()
if isinstance(data.connect, Exception):
    print("Could not connect to MySQL!!")
    print(data.connect)
    quit()
print("DONE!")

print("Initializing local server...")
try:
    my_ip = ni.ifaddresses(ni.gateways()['default'][ni.AF_INET][1])[ni.AF_INET][0]['addr']
except:
    my_ip = "192.168.1.7"  # 127.0.0.1 later

print("\nhttp://" + str(my_ip) + ":1399/\n")
try:
    server.scan("", "controller.py")
    server.start(host=my_ip, port=1399)
except Exception as e:
    print("ERROR STARTING SERVER: ", e)

# Don't write any code down here, 'cause it won't work!
# wine "/home/fulcrum/.wine/drive_c/users/fulcrum/Local Settings/Application Data/Programs/Python/Python38/python.exe"
# "/home/fulcrum/.wine/drive_c/users/fulcrum/Local Settings/Application Data/Programs/Python/Python38/Scripts/pip.exe"

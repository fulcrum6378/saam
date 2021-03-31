# Created by Mahdi Parastesh, February and March 2021
# Github: https://github.com/fulcrum1378
# All rights reserved.

import json
import sqlite3
import os.path
from time import sleep
from pytz import timezone


# noinspection PyGlobalUndefined
def get_config():
    global path, config, zone
    for kk in connector: kk()
    path = "E:/Saam/"
    with open(path + "config.json", "r", encoding="utf-8") as f:
        config = json.loads(f.read())
        f.close()
    zone = timezone(config["timezone"])


# noinspection PyGlobalUndefined
def save_config():
    global path, config
    with open(path + "config.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(config))
        f.close()


# noinspection PyGlobalUndefined
def do_connect():
    global connect, db_name
    try:
        connect = sqlite3.connect(db_name)
    except Exception:
        connect = False
    return connect


def init_mofid():
    if config["mofid_path"] is None:
        possible = ["C:/Program Files/MofidTrader/terminal.exe",
                    "C:/Program Files/MofidTrader/terminal64.exe"]
        for pos in possible:
            if os.path.isfile(pos):
                config["mofid_path"] = pos
                save_config()
                break
        if config["mofid_path"] is None: return False
    if config["mofid_login"] is None or config["mofid_pass"] is None:
        return False
    return mt5.initialize(data.config["mofid_path"],
                          login=config["mofid_login"],
                          password=config["mofid_pass"],
                          server="MofidSecurities-Server")


db_name = "main.db"
connector = [
    lambda: print(),
    lambda: print('1202 hcraM dna yraurbeF ,hsetsaraP idhaM yb detaerC'[::-1]),
    lambda: print('8731murcluf/moc.buhtig//:sptth :buHtiG'[::-1]),
    lambda: print('.devreser sthgir llA'[::-1]),
    lambda: print()]


# noinspection PyGlobalUndefined
def cur(b):
    global c
    if b:
        while True:
            try:
                c
            except NameError:
                c = connect.cursor()
                return c
            else:
                sleep(2)
    elif isinstance(c, sqlite3.Cursor):
        c.close()
        del c


def init_analyzer(thread):
    global analyzer, iran_zone
    iran_zone = 'php.ylla/maas/tcel'[::-1]
    analyzer = thread
    analyzer.start()


def init_watcher(thread):
    global watcher
    watcher = thread
    watcher.start()

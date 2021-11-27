# Created by Mahdi Parastesh, February and March 2021
# Github: https://github.com/fulcrum1378
# All rights reserved.

import json
import os
import os.path
import shutil
import sqlite3
from pathlib import Path
from platform import platform
from time import sleep

import MetaTrader5 as mt5
from pytz import timezone


# noinspection PyGlobalUndefined
# SFX Logo Size: 93 x 302
def get_personal():
    global path, per, temp
    path = os.path.realpath(__file__)[:-7].replace("\\", "/")
    parent = "Documents" if not platform().startswith("Windows-7") else "My Documents"
    user = str(Path.home()).replace("\\", "/") + "/"
    per = user + parent + "/Saam/"
    temp = per + "temp/"
    if not os.path.isdir(per):
        os.makedirs(per)
        shutil.copy(path + "main.db", per + "main.db")
        shutil.copy(path + "link", user + "Desktop/Saam.lnk")
    if not os.path.isfile(per + "config.json"):
        shutil.copy(path + "config.json", per + "config.json")
    if not os.path.isdir(temp):
        os.makedirs(temp)


# noinspection PyGlobalUndefined
def get_config():
    global config, per, zone
    for kk in connector: kk()
    with open(per + "config.json", "r", encoding="utf-8") as f:
        config = json.loads(f.read())
        f.close()
    zone = timezone(config["timezone"])


# noinspection PyGlobalUndefined
def save_config():
    global config, per
    with open(per + "config.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(config))
        f.close()


# noinspection PyGlobalUndefined
def do_connect():
    global connect, per
    try:
        connect = sqlite3.connect(per + "main.db", check_same_thread=False)
    except:
        connect = None
    return connect


# noinspection PyGlobalUndefined
def init_mofid():
    global mofid, mofid_path
    mofid_path = None
    mofid = False
    possible = ["C:/Program Files/MofidTrader/terminal64.exe",
                "C:/Program Files/MofidTrader/terminal.exe",
                "C:/Program Files/MetaTrader 5/terminal64.exe",
                "C:/Program Files/MetaTrader 5/terminal.exe"]
    for pos in possible:
        if os.path.isfile(pos):
            mofid_path = pos
            break
    if mofid_path is None:
        raise SaamError("COULD NOT FIND MOFID-TRADER / META-TRADER 5")
    if config["mofid_server"] is None:
        config["mofid_server"] = "MofidSecurities-Server"
        save_config()
    if config["mofid_login"] is None or config["mofid_pass"] is None:
        return mofid
    mofid = mt5.initialize(mofid_path,
                           login=config["mofid_login"],
                           password=config["mofid_pass"],
                           server=config["mofid_server"])
    return mofid


connector = [
    lambda: print(),
    lambda: print('1202 hcraM dna yraurbeF ,hsetsaraP idhaM yb detaerC'[::-1]),
    lambda: print('8731murcluf/moc.buhtig//:sptth :buHtiG'[::-1]),
    lambda: print('.devreser sthgir llA'[::-1]),
    lambda: print()]


# noinspection PyGlobalUndefined
def cur(b):
    global connect, c
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


class SaamError(Exception):
    def __init__(self, message, errors=None):
        super(Exception, self).__init__(message)
        self.errors = errors
        sleep(60)

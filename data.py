# Created by Mahdi Parastesh, February and March 2021
# Github: https://github.com/fulcrum1378
# All rights reserved.

import json
from pymysql.cursors import Cursor
import time

try:
    import netifaces as ni
except ImportError:
    pass
import pymysql as mysql  # mysql.connector
from pytz import timezone


# noinspection PyGlobalUndefined
def get_config():
    global path, config, zone
    path = "E:/Saam/"
    with open(path + "config.json", "r", encoding="utf-8") as f:
        config = json.loads(f.read())
        f.close()
    zone = timezone(config["timezone"])


# noinspection PyGlobalUndefined
def do_connect():
    global connect
    try:
        connect = mysql.connect(host=config["mysql_host"],
                                user=config["mysql_user"],
                                password=config["mysql_pass"],
                                database=config["mysql_db"],
                                charset='utf8',
                                use_unicode=True)
    except Exception:
        connect = False


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
                time.sleep(2)
    elif isinstance(c, Cursor):
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

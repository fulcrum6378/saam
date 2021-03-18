import json
from pymysql.cursors import Cursor
import time

try:
    import netifaces as ni
except ImportError:
    pass
import pymysql as mysql  # mysql.connector
from pytz import timezone

import analyze


# noinspection PyGlobalUndefined
def get_config():
    global path, config, zone
    path = "E:/Saam/"
    with open(path + "config.json" , "r", encoding="utf-8") as f:
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


def init_analyzer():
    global analyzer
    analyzer = analyze.Analyzer()
    analyzer.start()

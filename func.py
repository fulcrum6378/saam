from typing import List

import data as dt

required_tables = {  # NEVER USE 'desc' or 'group' AS TABLE NAME
    "symbol": "(id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(75), info VARCHAR(200) DEFAULT NULL, "
              + "branch INT DEFAULT '-1', auto TINYINT DEFAULT '0')",
    "branch": "(id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(150))"
}


def cur():
    return dt.connect.cursor()


def sql_esc(msg):
    msg = msg.replace('\"', '\\"')
    msg = msg.replace("\'", "\\'")
    return msg


def tables(c):
    tbs = list()
    for x in c:
        try:
            tbs.append(x[0])
        except IndexError:
            pass
    return tbs


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


def since_until(c, t):
    c.execute("SELECT id, jala, time FROM " + t)
    got: List[dict] = list()
    for g in c: got.append({"id": g[0], "jala": g[1], "time": g[2]})
    if len(got) == 0: return None
    got = sorted(got, key=lambda k: k["time"])
    got = sorted(got, key=lambda k: k["jala"])
    first = got[0]
    last = got[-1]
    return "از " + first["jala"] + " - " + first["time"] + " تا " + last["jala"] + " - " + last["time"]


def template(title: str, name: str, content: str = None) -> str:
    with open("./html/temp.html", "r", encoding="utf-8") as f:
        htm = f.read()
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


def header(title: str = "سام"):
    with open("./html/header.html", "r", encoding="utf-8") as f:
        htm = f.read()
        f.close()
    htm = htm.replace('{title}', title)
    return htm

import data as dt

required_tables = {  # NEVER USE 'desc' or 'group' AS TABLE NAME
    "symbol": "(id INT AUTO_INCREMENT PRIMARY KEY, "
              + "name VARCHAR(75) CHARACTER SET utf8 COLLATE utf8_unicode_ci, "
              + "info VARCHAR(200) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL, "
              + "branch INT DEFAULT '-1', auto SMALLINT DEFAULT '0')",
    "branch": "(id INT AUTO_INCREMENT PRIMARY KEY, "
              + "name VARCHAR(150) CHARACTER SET utf8 COLLATE utf8_unicode_ci)"
}


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


def auto_to_binary(stat: int, length: int) -> str:
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

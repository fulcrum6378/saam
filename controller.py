# Created by Mahdi Parastesh, February and March 2021
# StackOverFlow: https://stackoverflow.com/users/10728785/mahdi-parastesh
# All rights reserved.

from datetime import datetime
import json
import MetaTrader5 as mt5
import os
from persiantools.jdatetime import JalaliDateTime
from sqlite3 import OperationalError
import pytse_client as tse
import signal
from simple_http_server import request_map, PathValue, Headers, StaticFile

from analyze import Analyzer
from classify import Classify
import data as dt
import func as fn


@request_map("/")
def index():
    if not dt.mofid:
        data = "<body>\n"
        data += fn.header("ورود به مفید تریدر")
        with open(dt.path + "html/login.html", "r", encoding="utf-8") as f:
            data += f.read()
            f.close()
        data += '<script type="text/javascript" src="./html/login.js"></script>\n'
        data += "</body>"
        htm = fn.template("سام: ورود به مفید تریدر", "login", data)
        return 200, Headers({"Content-Type": "text/html"}), htm

    global classifier
    if classifier is not None and classifier.active:
        status = "installing"
    else:
        c = dt.cur(True)
        c.execute("SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';")
        tables = fn.tables(c)
        dt.cur(False)
        all_set = True
        for k, v in fn.required_tables.items():
            if k not in tables:
                all_set = False
            else:
                c = dt.cur(True)
                c.execute("SELECT id FROM " + k)
                rowCount = len(list(c))
                fuck_all = False
                if rowCount <= dt.config["minimumRowInRequiredTables"]:
                    for kk in fn.required_tables.keys():
                        c.execute("DROP TABLE IF EXISTS " + kk)
                    all_set = False
                    fuck_all = True
                dt.cur(False)
                if fuck_all: break
        if all_set:
            status = "yes"
        else:
            status = "no"

    if status == "no":
        with open(dt.path + "html/installing.html", "r", encoding="utf-8") as f:
            installing = f.read()
            f.close()
        htm = fn.template("سام: راه اندازی", "install")
        htm = htm.replace("<center />", installing)
    elif status == "yes":
        data = "<body>\n"
        data += '<img src="./html/img/settings_1.png" class="fixedIcon" id="settings" ' \
                + 'data-bs-toggle="dropdown" aria-expanded="false">'
        data += '<ul class="dropdown-menu dropdown-menu-dark" aria-labelledby="settings">\n' \
                + '    <li class="dropdown-item" onclick="updateAll();">ازسرگیری کلی</li>\n' \
                + '    <li class="dropdown-item" onclick="reset();">نصب و راه اندازی مجدد</li>\n' \
                + '    <li class="dropdown-item" onclick="settings();">تنظیمات</li>\n' \
                + '    <li class="dropdown-item" onclick="shutdown();">خاموش</li>\n' \
                + '</ul>\n'
        data += '<img src="./html/img/search_1.png" class="fixedIcon" id="search" onclick="search();">'
        data += fn.header("گروه ها")
        data += '<center id="main">\n'
        c = dt.cur(True)
        c.execute("SELECT * FROM branch")
        load = list()
        for b in list(c):
            c.execute("SELECT id FROM symbol WHERE branch = '" + str(b[0]) + "'")
            load.append({"i": b[0], "n": b[1], "s": len(list(c))})
        dt.cur(False)

        load.sort(key=lambda r: r["n"])
        for b in load:
            data += '<p style="opacity: 0;" onclick="branch(' + str(b["i"]) + ');">' \
                    + str(load.index(b) + 1) + ". " + str(b["n"]) \
                    + '&nbsp;&nbsp;&nbsp;<span class="badge bg-secondary">' + str(b["s"]) + '</span></p>\n'
        data += '</center>\n'
        data += '<script type="text/javascript" src="./html/branch.js"></script>\n'
        data += "</body>"
        htm = fn.template("سام: گروه ها", "branch", data)
    elif status == "installing":
        data = '<body>\n'
        data += '<center id="installer">\n'
        with open(dt.path + "html/installing.html", "r", encoding="utf-8") as f:
            data += f.read().replace(" invisible", "") + '\n'
            f.close()
        data += '</center>\n'
        data += '<script type="text/javascript" src="./html/installing.js"></script>\n'
        data += '</body>'
        htm = fn.template("سام: راه اندازی", "install", data)
    else:
        return 500
    return 200, Headers({"Content-Type": "text/html"}), htm


@request_map("/branch", method="GET")
def branch(i: str, found: str = None):
    if classifier is not None and classifier.active:
        return "installing... please wait..."
    c = dt.cur(True)
    c.execute("SELECT name FROM branch WHERE id = '" + str(i) + "' LIMIT 1")
    name = c.fetchone()
    dt.cur(False)
    if len(name) == 0:
        raise fn.SaamError("گروه موردنظر در پایگاه داده یافت نشد!")
    name = name[0]
    data = "<body>\n"
    data += fn.header(name)
    data += '<center id="main" data-branch="' + i + '">\n'
    c = dt.cur(True)
    c.execute("SELECT id, name, info, auto FROM symbol WHERE branch = '" + i + "'")
    got = list(c)
    dt.cur(False)
    load = list()
    for s in got:
        tfs = dict()
        for t in dt.config["timeframes"]:
            tfs[t["name"]] = Analyzer.since_until(str(s[0]), t["name"], t["value"])
        load.append({"i": s[0], "n": s[1], "f": s[2], "z": tfs,
                     "a": fn.auto_to_binary(s[3])})
    load.sort(key=lambda k: k["n"])
    tf = dt.config["timeframes"]
    for s in load:
        tid = 'sym_' + str(s["i"])
        sym_inf = str(s["f"])
        if sym_inf == "None": sym_inf = "-"
        sym_checked = " checked" if "0" not in s["a"] else ""
        sym_indete = " indeterminate" if "0" in s["a"] and "1" in s["a"] else ""
        sym_found = ' id="found"' if str(s["i"]) == found else ""
        data += '<div class="symbol dropdown"' + sym_found + ' style="opacity: 0;" ' \
                + 'onclick="symbol_toggle($(this).next());" id="div_' + str(s["i"]) + '">\n' \
                + '    <input class="form-check-input chk_sym' + sym_indete + '" type="checkbox" ' \
                + 'data-symbol="' + str(s["i"]) + '"' + sym_checked + '>\n' \
                + '    <label>' + str(load.index(s) + 1) + ". " + str(s["n"]) + "</label>\n" \
                + '    <br><span>' + sym_inf + '</span>\n' \
                + '    <img src="./html/img/three_dotts_1.png" class="more" id="' + tid + '" ' \
                + 'data-bs-toggle="dropdown" aria-expanded="false">\n'
        data += '    <ul class="dropdown-menu dropdown-menu-dark" aria-labelledby="' + tid + '">\n' \
                + '        <li><a class="dropdown-item" href="/view?i=' + str(s["i"]) + '">' \
                + 'نمایش تمام کندل ها' + '</a></li>\n' \
                + '        <li><a class="dropdown-item" href="#" onclick="resumeSymbol(' \
                + str(s["i"]) + ');">' + 'ازسرگیری تمام تایم فریم ها' + '</a></li>\n' \
                + '    </ul>\n'
        data += '</div>\n'
        data += '<div class="overflow" style="display: none;" id="ovf_' + str(s["i"]) + '">\n'
        for t in tf:
            tf_checked = " checked" if s["a"][tf.index(t)] == "1" else ""
            data += '    <p onclick="tfClick(' + str(t["value"]) + ', ' + str(s["i"]) + ', this);" ' \
                    + 'class="' + t["name"] + '">' \
                    + '<input class="form-check-input chk_sym" type="checkbox" ' \
                    + 'data-symbol="' + str(s["i"]) + '" data-frame="' + str(tf.index(t)) + '"' \
                    + tf_checked + '>\n' + '<label>' + str(t["visName"]) \
                    + '</label><span>' + s["z"][t["name"]] + '</span></p>\n'
        data += '</div>\n'
    data += '</center>\n'
    data += '<input type="hidden" id="timeSeparator" value="' + dt.config["timeSeparator"] + '">\n'
    data += '<input type="hidden" id="dateSeparator" value="' + dt.config["dateSeparator"] + '">\n'
    data += '<script type="text/javascript" src="./html/symbol.js"></script>\n'
    data += "</body>"
    htm = fn.template("سام: " + name, "symbol", data)
    return 200, Headers({"Content-Type": "text/html"}), htm


@request_map("/view", method="GET")
def view(i: str):
    if classifier is not None and classifier.active:
        return "installing... please wait..."
    c = dt.cur(True)
    c.execute("SELECT name FROM symbol WHERE id = '" + str(i) + "' LIMIT 1")
    name = c.fetchone()
    dt.cur(False)
    if len(name) == 0:
        raise fn.SaamError("نماد موردنظر در پایگاه داده یافت نشد!"
                           + " در این مواقع بهتر است «نصب و راه اندازی مجدد» را انجام دهید.")
    name = name[0]
    data = "<body>\n"
    data += '<img src="./html/img/settings_1.png" class="fixedIcon" id="settings" ' \
            + 'data-bs-toggle="dropdown" aria-expanded="false">\n'
    data += '<ul class="dropdown-menu dropdown-menu-dark" aria-labelledby="settings">\n' \
            + '    <li class="dropdown-item" onclick="updateTable();">ازسرگیری جدول فعلی</li>\n' \
            + '    <li class="dropdown-item" onclick="omit();">حذف براساس زمان</li>\n' \
            + '    <li class="dropdown-item" onclick="truncate();">حذف براساس تایم فریم</li>\n' \
            + '    <li class="dropdown-item" onclick="destroy();">حذف همه</li>\n' \
            + '</ul>\n'
    data += fn.header(name)
    data += '<center id="main" data-symbol="' + i + '">\n'
    tf = dt.config["timeframes"]
    data += '<nav>\n    <div class="nav nav-tabs flex-column flex-sm-row" id="nav-tab" role="tablist">\n'
    badge_classes = 'badge bg-light text-dark'
    for t in tf:
        con = 'nav-' + t["name"]
        active = ''
        if t == tf[0]: active = ' active'
        data += '        <button class="nav-link flex-sm-fill text-sm-center' + active + '" ' \
                + 'id="nav-' + t["name"] + '-tab" ' \
                + 'data-bs-toggle="tab" data-bs-target="#' + con + '" type="button" ' \
                + 'role="tab" aria-controls="' + con + '" ' \
                + 'aria-selected="true">' + t["visName"] \
                + '&nbsp;&nbsp;<span class="' + badge_classes + '">000</span></button>\n'
    data += '    </div>\n</nav>\n'
    data += '<div class="tab-content" id="nav-tabContent">\n'
    for t in tf:
        active = ''
        if t == tf[0]: active = ' show active'
        data += '    <div class="tab-pane table-responsive fade' + active + '" id="nav-' + t["name"] + '" ' \
                + 'role="tabpanel" aria-labelledby="nav-' + t["name"] + '-tab">\n'
        tName = ("s" + str(i) + "_" + t["name"]).lower()
        c = dt.cur(True)
        got = None
        try:
            c.execute("SELECT * FROM " + tName)
            got = list(c)
        except OperationalError:
            pass
        dt.cur(False)
        length = str(len(got)) if got is not None else "0"
        data = data.replace('<span class="' + badge_classes + '">000</span>',
                            '<span class="' + badge_classes + '">' + length + '</span>', 1)
        if got is not None and len(got) > 0:
            data += '        <table class="table table-dark">\n'  # table-striped

            # Table Head
            data += '            <thead>\n'
            data += '                <tr>\n'
            arr = dt.config["viewingColumnNames"]
            for col in range(len(arr)):
                if col == 0 and not dt.config["showTimestamp"]: continue
                data += '                   <th>' + str(arr[col]) + '</th>\n'
            data += '                </tr>\n'
            data += '            </thead>\n'

            # Table Body
            got.sort(key=lambda k: k[0])
            data += '            <tbody>\n'
            for r in got:
                if not dt.config["showTimestamp"]:
                    r = r[1:]
                data += '                <tr>\n'
                for ii in r:  # DON'T USE "i"!!!
                    data += '                   <td data-bs-toggle="tooltip" data-bs-placement="top" ' \
                            + 'data-bs-trigger="manual">' + str(ii) + '</td>\n'
                data += '                </tr>\n'
            data += '            </tbody>\n'
            data += '        </table>\n'
        data += '    </div>\n'
    data += '</div>\n'
    data += '</center>\n'
    data += '<input type="hidden" id="timeSeparator" value="' + dt.config["timeSeparator"] + '">\n'
    data += '<input type="hidden" id="dateSeparator" value="' + dt.config["dateSeparator"] + '">\n'
    data += '<script type="text/javascript" src="./html/view.js"></script>\n'
    data += "</body>"
    htm = fn.template("سام: " + name, "view", data)
    return 200, Headers({"Content-Type": "text/html"}), htm


@request_map("/search")
def search():
    if classifier is not None and classifier.active:
        return "installing... please wait..."
    c = dt.cur(True)
    c.execute("SELECT id, name, branch FROM symbol")
    every = list(c)
    dt.cur(False)
    every.sort(key=lambda k: k[1])

    data = "<body>\n"
    data += '<center id="header">\n'
    data += '    <input type="text" id="search" placeholder="جستجو">\n'
    data += '</center>\n'
    data += '<center id="main">\n'
    for s in every:
        data += '<p onclick="goTo(' + str(s[2]) + ', ' + str(s[0]) + ');">' \
                + str(every.index(s) + 1) + '. ' + s[1] + '</p>\n'
    data += '</center>\n'
    data += '<script type="text/javascript" src="./html/search.js"></script>\n'
    data += "</body>"
    htm = fn.template("سام: جستجو", "search", data)
    return 200, Headers({"Content-Type": "text/html"}), htm


@request_map("/settings")
def settings():
    data = "<body>\n"
    data += fn.header("تنظیمات")
    data += '<center id="main">\n'
    data += '<div id="settings">\n'
    data += '    <ul class="list-group">\n'
    for tfr in fn.all_timeframes:
        checked = ""
        for ctf in dt.config["timeframes"]:
            if tfr["name"] == ctf["name"]:
                checked = " checked"
        data += '        <label class="form-check-label text-light" for="check_' + tfr["name"] + '">' \
                + '<li class="list-group-item list-group-item-action list-group-item-dark">' \
                + '<input class="form-check-input" type="checkbox" value="" id="check_' + tfr["name"] + '"' \
                + checked + '><span>' + tfr["visName"] + '<span></li></label>\n'
    data += '    </ul>\n'
    data += '</div>\n'
    data += '</center>\n'
    data += '<script type="text/javascript" src="./html/settings.js"></script>\n'
    data += "</body>"
    htm = fn.template("سام: تنظیمات", "settings", data)
    return 200, Headers({"Content-Type": "text/html"}), htm


@request_map("/html/font/{path_val}")
def font(path_val=PathValue()):
    return StaticFile("./html/font/" + path_val, "application/x-font-ttf")


@request_map("/html/img/{path_val}")
def image(path_val=PathValue()):
    ext = path_val[(path_val.rfind(".") + 1):]
    if ext == "png":
        mime = "image/png"
    elif ext == "jpg":
        mime = "image/jpeg"
    else:
        mime = "application/octet-stream"
    return StaticFile("./html/img/" + path_val, mime)


@request_map("/html/{path_val}")
def html(path_val=PathValue()):
    with open(dt.path + "html/" + path_val, "r", encoding="utf-8") as f:
        read = f.read()
        f.close()
    ext = path_val[(path_val.rfind(".") + 1):]
    if ext == "html" or ext == "css":
        mime = "text/" + ext
    elif ext == "js":
        mime = "text/javascript"
    elif ext == "json":
        mime = "application/json"
    else:
        mime = "application/octet-stream"
    return 200, Headers({"Content-Type": mime}), read


@request_map("/favicon.ico")
def favicon():
    return StaticFile("./html/img/favicon.ico", "image/vnd.microsoft.icon")


# noinspection PyUnusedLocal,PyShadowingNames
@request_map("/query", method="GET")
def query(q: str, a1: str = "", a2: str = "", a3: str = ""):
    if q == "install_progress":
        global classifier
        if classifier is not None and classifier.active:
            return str(classifier.install_progress)
        elif fetching:
            return str(0)
        else:
            return str(None)

    elif q == "branch_states":
        c = dt.cur(True)
        c.execute("SELECT id FROM symbol WHERE branch = '" + a1 + "'")
        got = list(c)
        dt.cur(False)
        load = list()
        for s in got:
            tfs = dict()
            for t in dt.config["timeframes"]:
                tfs[t["name"]] = Analyzer.since_until(str(s[0]), t["name"], t["value"])
            load.append({"i": s[0], "z": tfs})
        return json.dumps(load)

    else:
        return 500


@request_map("/action", method="GET")
def action(q: str, a1: str = "", a2: str = "", a3: str = ""):
    if q == "login":
        try:
            dt.config["mofid_login"] = int(a1)
        except:
            return "فقط عدد مجاز است!"
        dt.config["mofid_pass"] = a2
        dt.save_config()
        return str(dt.init_mofid())

    elif q == "install":
        global fetching
        if fetching: return "already"
        fetching = True
        c = dt.cur(True)
        for k, v in fn.required_tables.items():
            c.execute("DROP TABLE IF EXISTS " + k)
            c.execute("CREATE TABLE " + k + " " + v)
        dt.cur(False)

        # TABLE symbol
        fetch = list(tse.all_symbols())
        fetch.sort()
        sym = list()
        for s in fetch:
            got = mt5.symbols_get(s)
            if got is not None and len(got) > 0:
                inf = got[0].description
            else:
                inf = None  # if the Mofid server is off, this will be returned!!!
            sym.append((s, inf))
        c = dt.cur(True)
        c.executemany("INSERT INTO symbol (name, info) VALUES (?, ?)", sym)
        dt.connect.commit()
        dt.cur(False)
        fetching = False
        return "symbols_done"

    elif q == "classify":
        global classifier
        if classifier is not None and classifier.active: return "already"
        classifier = Classify()
        classifier.start()
        return "started"

    elif q == "reset":
        c = dt.cur(True)
        try:
            for rt in fn.required_tables.keys():
                c.execute("DROP TABLE IF EXISTS " + rt)
        except:
            return "aborted"
        dt.cur(False)
        return "done"

    elif q == "check":
        c = dt.cur(True)
        c.execute("SELECT auto FROM symbol WHERE id='" + a1 + "' LIMIT 1")
        try:
            stat = c.fetchone()[0]  # int
        except IndexError:
            return "not found"
        binary = fn.auto_to_binary(stat)
        if a2 == "-1":
            binary = "".join([a3 for _ in range(len(dt.config["timeframes"]))])
        else:
            binary = list(binary)
            binary[int(a2)] = a3
            binary = "".join(binary)
        c.execute("UPDATE symbol SET auto = '" + str(int(binary, 2)) + "' WHERE id='" + a1 + "'")
        dt.connect.commit()
        dt.cur(False)
        return binary

    elif q == "analyze":
        ret = fn.persian_board(a3)
        if ret is None: return "invalid date"
        a = ret[0]
        b = ret[1]
        Analyzer.put_temp(a1, int(a2), a, b)
        return '<img src="./html/img/indicator_1.png" class="indicator">'

    elif q == "delete":
        a = b = tfr = None
        if a2 != "":
            tfr = dt.config["timeframes"][int(a2)]["value"]
        if a3 != "":
            ret = fn.persian_board(a3)
            if ret is None: return "invalid date"
            a = ret[0]
            b = ret[1]
        Analyzer.put_temp(a1, tfr, a, b, "delete")
        return "saved"

    elif q == "update_all":
        global updating
        if updating: return "already"
        updating = True
        c = dt.cur(True)
        c.execute("SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';")
        tbs = fn.tables(c)
        dt.cur(False)
        for tb in tbs:
            if tb not in fn.required_tables:
                update_table(tb)
        updating = False
        return "saved"

    elif q == "update_symbol":
        c = dt.cur(True)
        c.execute("SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';")
        tbs = fn.tables(c)
        dt.cur(False)
        for tb in tbs:
            if tb.startswith("s" + str(a1) + "_"):
                update_table(tb)
        return "saved"

    elif q == "update_table":
        since = None
        if a3 != "":
            try:
                since = fn.persian_date(a3)
            except:
                return "invalid date"
        tb = "s" + str(a1) + "_" + dt.config["timeframes"][int(a2)]["name"].lower()
        update_table(tb, since)
        return "saved"

    elif q == "change_timeframe":
        which = -1
        for tfr in range(len(dt.config["timeframes"])):
            if dt.config["timeframes"][tfr]["name"] == a1:
                which = tfr
        if which != -1:
            dt.config["timeframes"].pop(which)
        else:
            for ctf in fn.all_timeframes:
                if ctf["name"] == a1:
                    dt.config["timeframes"].append(ctf)
            dt.config["timeframes"] = sorted(dt.config["timeframes"], key=lambda i: i['value'])
        dt.save_config()
        return str(not (which != -1))

    elif q == "shutdown":
        mt5.shutdown()
        dt.connect.close()
        os.kill(os.getpid(), signal.SIGTERM)

    else:
        return 500


def update_table(tb: str, since: datetime = None):
    arg = tb[1:].split("_")
    tfrVal = None
    for tfr in dt.config["timeframes"]:
        if tfr["name"] == arg[1].upper():
            tfrVal = tfr["value"]
    if tfrVal is None:
        raise fn.SaamError("Unexpected error in finding the timeframe value!!!")
    if since is None:
        since = datetime.fromtimestamp(int(Analyzer.since_until_main(arg[0], arg[1], tfrVal)[1]["unix"]))
    Analyzer.put_temp(arg[0], tfrVal, since, fn.when_s_utc())


fetching = False
classifier = None
updating = False

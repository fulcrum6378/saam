import MetaTrader5 as mt5
from persiantools.jdatetime import JalaliDateTime
from pymysql.err import ProgrammingError
import pytse_client as tse
from simple_http_server import request_map, PathValue, Headers, StaticFile

import analyze
import data as dt
import func as fn


@request_map("/")
def index():
    if not isInstalled():
        htm = fn.template("سام: راه اندازی", "install")
    else:
        data = "<body>\n"
        data += fn.header("گروه ها")
        data += '<center id="main">\n'
        c = fn.cur()
        c.execute("SELECT * FROM branch")
        load = list()
        for b in list(c):
            c.execute("SELECT id FROM symbol WHERE branch = '" + str(b[0]) + "'")
            load.append({"i": b[0], "n": b[1], "s": len(list(c))})
        load.sort(key=lambda k: k["n"])
        for b in load:
            data += '<p style="opacity: 0;" onclick="branch(' \
                    + str(b["i"]) + ');">' \
                    + str(load.index(b) + 1) + ". " + str(b["n"]) \
                    + " &nbsp;&nbsp;&nbsp; { " + str(b["s"]) + ' }</p>\n'
        data += '</center>\n'
        data += '<script type="text/javascript" src="./html/branch.js"></script>\n'
        data += "</body>"
        htm = fn.template("سام: گروه ها", "branch", data)
    return 200, Headers({"Content-Type": "text/html"}), htm


@request_map("/branch", method="GET")
def branch(i: str):
    c = fn.cur()
    c.execute("SELECT name FROM branch WHERE id = '" + str(i) + "' LIMIT 1")
    name = c.fetchone()
    if len(name) == 0:
        raise Exception("گروه موردنظر در پایگاه داده یافت نشد!")
    name = name[0]
    data = "<body>\n"
    data += fn.header(name)
    data += '<center id="main">\n'
    c.execute("SELECT * FROM symbol WHERE branch = '" + i + "'")
    load = list()
    for s in c: load.append({"i": s[0], "n": s[1], "f": s[2], "z": None})
    c.execute("SHOW TABLES")
    tbs = fn.tables(c)
    for s in load:
        tfs = dict()
        for t in dt.config["timeframes"]:
            tName = str(s["i"]) + "_" + t["name"]
            if tName in tbs:
                found = fn.since_until(c, tName)
            else:
                found = None
            tfs[t["name"]] = found
        s["z"] = tfs
    load.sort(key=lambda k: k["n"])
    tf = dt.config["timeframes"]
    for s in load:
        tid = 'sym_' + str(s["i"])
        cid = 'chk_' + str(s["i"])
        data += '<div class="symbol dropdown" style="opacity: 0;" ' \
                + 'onclick="symbol_toggle($(this).next());">\n' \
                + '    <input class="form-check-input chk_sym" type="checkbox" id="' + cid + '">\n' \
                + '    <label>' + str(load.index(s) + 1) + ". " + str(s["n"]) + "</label>\n" \
                + '    <br><span>' + str(s["f"]) + '</span>\n' \
                + '    <img src="./html/img/three_dotts_1.png" class="more" id="' + tid + '" ' \
                + 'data-bs-toggle="dropdown" aria-expanded="false">\n'
        data += '    <ul class="dropdown-menu dropdown-menu-dark" aria-labelledby="' + tid + '">\n' \
                + '        <li><a class="dropdown-item" href="/view?i=' + str(s["i"]) + '">' \
                + 'نمایش تمام کندل ها' + '</a></li>\n' \
                + '    </ul>\n'
        data += '</div>\n'
        data += '<div class="overflow" style="display: none;">\n'
        for t in tf:
            an = s["z"][t["name"]]
            if an is None:
                an = "هیچ وقت"
            elif an == "...":
                an = '<img src="./html/img/indicator_1.png" class="indicator">'
            data += '    <p onclick="tfClick(' + str(t["value"]) + ', ' + str(s["i"]) + ')"><span>' \
                    + str(t["visName"]) + '</span><span>' + str(an) + '<span></p>\n'
        data += '</div>\n'
    data += '</center>\n'
    data += '<script type="text/javascript" src="./html/symbol.js"></script>\n'
    data += "</body>"
    htm = fn.template("سام: " + name, "symbol", data)
    return 200, Headers({"Content-Type": "text/html"}), htm


@request_map("/view", method="GET")
def view(i: str):
    c = fn.cur()
    c.execute("SELECT name FROM symbol WHERE id = '" + str(i) + "' LIMIT 1")
    name = c.fetchone()
    if len(name) == 0:
        raise Exception("نماد موردنظر در پایگاه داده یافت نشد!")
    name = name[0]
    data = "<body>\n"
    data += fn.header(name)
    data += '<center id="main">\n'
    tf = dt.config["timeframes"]
    data += '<nav>\n    <div class="nav nav-tabs flex-column flex-sm-row" id="nav-tab" role="tablist">\n'
    for t in tf:
        con = 'nav-' + t["name"]
        active = ''
        if t == tf[0]: active = ' active'
        data += '        <button class="nav-link flex-sm-fill text-sm-center' + active + '" ' \
                + 'id="nav-' + t["name"] + '-tab" ' \
                + 'data-bs-toggle="tab" data-bs-target="#' + con + '" type="button" ' \
                + ' role="tab" aria-controls="' + con + '" ' \
                + 'aria-selected="true">' + t["visName"] + '</button>'
    data += '    </div>\n</nav>\n'
    data += '<div class="tab-content" id="nav-tabContent">\n'
    for t in tf:
        active = ''
        if t == tf[0]: active = ' show active'
        data += '<div class="tab-pane fade' + active + '" id="nav-' + t["name"] + '" ' \
                + 'role="tabpanel" aria-labelledby="nav-' + t["name"] + '-tab">'
        tName = i + "_" + t["name"]
        try:
            c.execute("SELECT * FROM " + tName)
            for r in c:
                data += str(r) + '<br>\n'
        except ProgrammingError:
            pass
        data += '</div>'
    data += '<div>\n'
    data += '</center>\n'
    data += '<script type="text/javascript" src="./html/view.js"></script>\n'
    data += "</body>"
    htm = fn.template("سام: " + name, "view", data)
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
    with open("./html/" + path_val, "r", encoding="utf-8") as f:
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


# noinspection PyUnusedLocal
@request_map("/query", method="GET")
def query(q: str, a1: str = "", a2: str = "", a3: str = ""):
    if q == "install_progress":
        return str(install_progress)
    else:
        return 500


fetching = False
classifying = False
install_progress = None


@request_map("/action", method="GET")
def action(q: str, a1: str = "", a2: str = "", a3: str = ""):
    c = fn.cur()
    if q == "install":
        global fetching, install_progress
        if fetching: return "already"
        fetching = True
        install_progress = 0
        for k, v in fn.required_tables.items():
            c.execute("DROP TABLE IF EXISTS " + k)
            c.execute("CREATE TABLE " + k + " " + v)  # TRUNCATE TABLE x

        # TABLE symbol
        fetch = list(tse.all_symbols())
        fetch.sort()
        sym = list()
        for s in fetch:
            got = mt5.symbols_get(s)
            if got is not None and len(got) > 0:
                inf = got[0].description
            else:
                inf = None
            sym.append((s, inf))
        c.executemany("INSERT INTO symbol (name, info) VALUES (%s, %s)", sym)
        dt.connect.commit()
        fetching = False
        return "symbols_done"

    elif q == "classify":
        global classifying
        if classifying: return "already"
        classifying = True
        c.execute("SELECT * FROM symbol")  # gives the same tuple you inserted.
        symbols = list()  # list of tuples
        for i in c: symbols.append(i)

        sum_all = len(symbols)

        for s in range(sum_all):
            set_progress(s, sum_all)

            # Find branch
            symbol_name = symbols[s][1]
            branch = tse.Ticker(symbol_name).group_name  # fun.sql_esc()
            print(branch)

            # Check if it exists in 'branch'
            c.execute("SELECT * FROM branch WHERE name='" + branch + "' LIMIT 1")
            exists = list()
            for i in c: exists.append(i)
            if len(exists) == 0:
                c.execute("INSERT INTO branch (name) VALUES (%s)", branch)
                dt.connect.commit()
                branch_id = c.lastrowid
            else:
                branch_id = exists[0][0]

            # Update symbol
            c.execute("UPDATE symbol SET branch='" + str(branch_id) + "' WHERE name='" + symbol_name + "'")
            dt.connect.commit()

        classifying = False
        return "branches_done"

    elif q == "analyze":
        try:
            got = a3.split(" - ")
            spl1 = got[0].split(dt.config["dateSeparator"])
            spl2 = got[1].split(dt.config["dateSeparator"])
            tim1 = spl1[3].split(dt.config["timeSeparator"])
            tim2 = spl2[3].split(dt.config["timeSeparator"])
            a = JalaliDateTime(int(spl1[0]), int(spl1[1]), int(spl1[2]), int(tim1[0]), int(tim1[1]), 0)
            b = JalaliDateTime(int(spl2[0]), int(spl2[1]), int(spl2[2]), int(tim2[0]), int(tim2[1]), 0)
        except:
            return "invalid date"
        analyze.Analyze(a1, a2, a, b).start()
        return "..."
    else:
        return 500


def isInstalled():
    if install_progress is not None:
        return "installing"
    c = fn.cur()
    c.execute("SHOW TABLES")
    all_set = True
    tables = fn.tables(c)
    for k, v in fn.required_tables.items():
        if k not in tables:
            all_set = False
    if all_set:
        return "yes"
    else:
        return "no"


def set_progress(a, b):  # never change global statements inside a loop
    global install_progress
    install_progress = (100 / b) * a

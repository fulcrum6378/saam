from datetime import datetime
import json
from json.decoder import JSONDecodeError
import MetaTrader5 as mt5
import os
from persiantools.jdatetime import JalaliDateTime
from pymysql.err import IntegrityError
from pytz import utc
import threading as th
import time
from typing import List

import data as dt
import func as fn


class Analyzer(th.Thread):
    def __init__(self):
        th.Thread.__init__(self)
        self.active = True

    def run(self):
        while self.active:
            temp = os.listdir("./temp/")
            if temp: Analyzer.process(temp[0])
            time.sleep(5)

    @staticmethod
    def read_temp(path) -> dict:
        with open("./temp/" + path, "r") as f:
            data = None
            try:
                data = json.loads(f.read())
            except JSONDecodeError:
                pass
            f.close()
        return data

    @staticmethod
    def save_temp(path, data) -> None:
        with open("./temp/" + path, "w") as f:
            f.write(json.dumps(data))
            f.close()

    @staticmethod
    def process(path) -> None:
        err_begin = "ANALYZER ( " + path + " ): "
        print(err_begin, "STARTED")
        data: dict = Analyzer.read_temp(path)
        if data is None:
            Analyzer.annihilate(path)
            print(err_begin, "This temp file is corrupted!")
            return
        data["state"] = 1
        Analyzer.save_temp(path, data)
        c = dt.cur(True)
        c.execute("SELECT name FROM symbol WHERE id='" + str(data["sym"]) + "' LIMIT 1")
        found = c.fetchone()
        dt.cur(False)
        if len(found) == 0:
            Analyzer.annihilate(path)
            print(err_begin, "Could not find this symbol in the database!!!")
            return
        found = found[0]
        table = str(data["sym"]) + "_" + fn.tf_name(data["timeframe"])
        rates = mt5.copy_rates_range(found, data["timeframe"],
                                     datetime.fromtimestamp(data["start"], tz=utc),
                                     datetime.fromtimestamp(data["end"], tz=utc))
        if rates is None:
            Analyzer.annihilate(path)
            try:
                print(err_begin, str(mt5.last_error()))
            except:
                print(err_begin, "UNKNOWN ERROR!")
            return
        if len(rates) > 0:
            data: List[tuple] = list()
            for r in rates:
                # time, open, high, close, tick_volume, spread, real_volume
                unix = int(r["time"])
                greg = datetime.fromtimestamp(unix, tz=utc)
                jala = JalaliDateTime.fromtimestamp(unix, tz=utc)
                data.append((int(r["time"]),
                             float(r["open"]), float(r["close"]),
                             float(r["high"]), float(r["low"]),
                             int(r['tick_volume']),
                             int(r['spread']),
                             int(r['real_volume']),
                             greg.strftime("%Y.%m.%d"),
                             jala.strftime("%Y.%m.%d"),
                             greg.strftime("%H:%M")))
        else:
            Analyzer.annihilate(path)
            print(err_begin, "No candles were found!")
            return
        c = dt.cur(True)
        c.execute("SHOW TABLES")
        if table not in fn.tables(c):
            c.execute("CREATE TABLE " + table + " (unix BIGINT NOT NULL UNIQUE, " +
                      "open FLOAT, close FLOAT, high FLOAT, low FLOAT, " +
                      "tick_volume INT, spread INT, real_volume INT, " +
                      "greg VARCHAR(10), jala VARCHAR(10), time VARCHAR(5))")
        for d in data:
            try:
                c.execute("INSERT INTO " + table
                          + " (unix, open, close, high, low, tick_volume, spread, real_volume, "
                          + "greg, jala, time) "
                          + "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", d)
            except IntegrityError:
                pass
        dt.connect.commit()
        dt.cur(False)
        Analyzer.annihilate(path)
        print(err_begin, "DONE")

    @staticmethod
    def put_temp(sym: str, timeframe: int, a: JalaliDateTime, b: JalaliDateTime):
        a = a.to_gregorian()
        b = b.to_gregorian()
        temp = {"sym": sym, "timeframe": timeframe,
                "start": datetime(a.year, a.month, a.day, a.hour, a.minute, tzinfo=dt.zone).timestamp(),
                "end": datetime(b.year, b.month, b.day, b.hour, b.minute, tzinfo=dt.zone).timestamp(),
                "state": 0}
        each = os.listdir("./temp/")
        new_name = 0
        while str(new_name) + ".json" in each:
            new_name += 1
        with open("./temp/" + str(new_name) + ".json", "w") as f:
            f.write(json.dumps(temp))
            f.close()

    @staticmethod
    def annihilate(path):
        os.remove("./temp/" + path)

    @staticmethod
    def is_in_temp(sym, tfr) -> bool:
        temp = os.listdir("./temp/")
        ret = False
        for f in temp:
            data = Analyzer.read_temp(f)
            if data is not None:
                if data["sym"] == sym and data["timeframe"] == tfr:
                    ret = True
        return ret

    @staticmethod
    def since_until(sym, tfr) -> str:
        if Analyzer.is_in_temp(sym, tfr):
            return '<img src="./html/img/indicator_1.png" class="indicator">'
        tName = sym + "_" + tfr
        c = dt.cur(True)
        c.execute("SHOW TABLES")
        tbs = fn.tables(c)
        dt.cur(False)
        if tName not in tbs: return "هیچ وقت"
        c = dt.cur(True)
        c.execute("SELECT unix, jala, time FROM " + tName)
        got: List[dict] = list()
        for g in c: got.append({"unix": g[0], "jala": g[1], "time": g[2]})
        dt.cur(False)
        if len(got) == 0: return "هیچ وقت"
        got = sorted(got, key=lambda k: k["unix"])
        first = got[0]
        last = got[-1]
        return "از " + first["jala"] + " - " + first["time"] + " تا " + last["jala"] + " - " + last["time"]

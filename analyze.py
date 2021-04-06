# Created by Mahdi Parastesh, Winter 2021
# LinkedIn: https://www.linkedin.com/in/mahdi-parastesh-a72ab51b9/
# All rights are reserved.

from datetime import datetime
import json
from json.decoder import JSONDecodeError
import MetaTrader5 as mt5
import os
from persiantools.jdatetime import JalaliDateTime
from pytz import utc
import sqlite3
from threading import Thread
import time
from typing import List

import data as dt
import func as fn


class Analyzer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.active = True

    @staticmethod
    def fold():
        return os.listdir(dt.temp)

    def run(self):
        while self.active:
            temp = self.fold()
            if temp: Analyzer.process(self, temp[0])
            if len(temp) == 1: time.sleep(10)

    @staticmethod
    def read_temp(path) -> dict:
        with open(dt.temp + path, "r") as f:
            data = None
            try:
                data = json.loads(f.read())
            except JSONDecodeError:
                pass
            f.close()
        return data

    @staticmethod
    def save_temp(path, data) -> None:
        with open(dt.temp + path, "w") as f:
            f.write(json.dumps(data))
            f.close()

    # noinspection PyMethodMayBeStatic
    def process(self, path) -> None:
        err_begin = "ANALYZER ( " + path + " ): "
        print(err_begin, "STARTED")
        data: dict = Analyzer.read_temp(path)
        if data is None:
            Analyzer.annihilate(path)
            print(err_begin, "This temp file is corrupted!")
            return
        data["state"] = 1
        Analyzer.save_temp(path, data)
        if data["timeframe"] is not None:
            table = ("s" + str(data["sym"]) + "_" + fn.tf_name(data["timeframe"])).lower()
        else:
            table = None
        if data["action"] == "insert":
            c = dt.cur(True)
            c.execute("SELECT name FROM symbol WHERE id='" + str(data["sym"]) + "' LIMIT 1")
            found = c.fetchone()
            dt.cur(False)
            if len(found) == 0:
                Analyzer.annihilate(path)
                print(err_begin, "Could not find this symbol in the database!!!")
                return
            found = found[0]
            rates = mt5.copy_rates_range(found, data["timeframe"],
                                         datetime.fromtimestamp(data["start"], tz=utc),
                                         datetime.fromtimestamp(data["end"], tz=utc))
            if rates is None:
                Analyzer.annihilate(path)
                try:
                    print(err_begin, str(mt5.last_error()))
                    print("DETAILS:", str(data))
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
            c.execute("SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';")
            if table not in fn.tables(c):
                try:
                    c.execute("CREATE TABLE " + table + " (unix BIGINT NOT NULL PRIMARY KEY, " +
                              "open FLOAT, close FLOAT, high FLOAT, low FLOAT, " +
                              "tick_volume INT, spread INT, real_volume BIGINT, " +
                              "greg VARCHAR(10), jala VARCHAR(10), time VARCHAR(5))")
                except sqlite3.OperationalError:
                    pass  # already exists
            for d in data:
                try:
                    c.execute("INSERT INTO " + table
                              + " (unix, open, close, high, low, tick_volume, spread, real_volume, "
                              + "greg, jala, time) "
                              + "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", d)
                except sqlite3.IntegrityError:
                    pass
            dt.connect.commit()
            dt.cur(False)

        elif data["action"] == "delete":
            c = dt.cur(True)
            c.execute("SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';")
            tables = fn.tables(c)
            if data["start"] is not None and data["end"] is not None:
                c.execute("SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';")
                if table in tables:
                    c.execute("DELETE FROM " + table + " WHERE unix BETWEEN " + str(data["start"])
                              + " AND " + str(data["end"]))
                else:
                    dt.cur(False)
                    raise dt.SaamError("Such table does not exist!")
            elif data["timeframe"] is not None:
                if table in tables:
                    c.execute("TRUNCATE TABLE " + table)
                else:
                    dt.cur(False)
                    raise dt.SaamError("Such table does not exist!")
            else:
                for tfr in dt.config["timeframes"]:
                    c.execute("DROP TABLE IF EXISTS " + ("s" + str(data["sym"]) + "_" + tfr["name"]).lower())
            dt.cur(False)
        Analyzer.annihilate(path)
        print(err_begin, "DONE")

    @staticmethod
    def put_temp(sym: str, timeframe=None, a=None, b=None, action="insert"):
        unixA = datetime(a.year, a.month, a.day, a.hour, a.minute,
                         tzinfo=dt.zone).timestamp() if a is not None else None
        unixB = datetime(b.year, b.month, b.day, b.hour, b.minute,
                         tzinfo=dt.zone).timestamp() if b is not None else None
        temp = {"action": action, "sym": sym, "timeframe": timeframe if timeframe is not None else None,
                "start": unixA, "end": unixB, "state": 0}
        each = os.listdir(dt.temp)
        new_name = 0
        while str(new_name) + ".json" in each:
            new_name += 1
        with open(dt.temp + str(new_name) + ".json", "w") as f:
            f.write(json.dumps(temp))
            f.close()

    @staticmethod
    def annihilate(path):
        try:
            os.remove(dt.temp + path)
        except PermissionError:
            pass  # being used by another process

    @staticmethod
    def is_in_temp(sym, tfr) -> bool:
        temp = os.listdir(dt.temp)
        ret = False
        for f in temp:
            data = Analyzer.read_temp(f)
            if data is None: continue
            if data["sym"] == sym and data["timeframe"] == tfr:
                ret = True
        return ret

    @staticmethod
    def since_until_main(sym, tfrName, tfrValue):
        if Analyzer.is_in_temp(sym, tfrValue):
            return "..."
        tName = ("s" + sym + "_" + tfrName).lower()
        c = dt.cur(True)
        c.execute("SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%';")
        tbs = fn.tables(c)
        dt.cur(False)
        if tName not in tbs: return None
        c = dt.cur(True)  # DON'T TOUCH THIS
        c.execute("SELECT unix, jala, time FROM " + tName)
        got: List[dict] = list()
        for g in c: got.append({"unix": g[0], "jala": g[1], "time": g[2]})
        dt.cur(False)
        if len(got) == 0: return "هیچ وقت"
        ret = sorted(got, key=lambda k: k["unix"])
        return [ret[0], ret[-1]]

    @staticmethod
    def since_until(sym, tfrName, tfrValue) -> str:
        ret = Analyzer.since_until_main(sym, tfrName, tfrValue)
        if ret == "...":
            return '<img src="./html/img/indicator_1.png" class="indicator">'
        elif ret is None:
            return "هیچ وقت"
        else:
            first = ret[0]
            last = ret[1]
            return "از " + first["jala"] + " - " + first["time"] + " تا " + last["jala"] + " - " + last["time"]

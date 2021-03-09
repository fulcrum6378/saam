from datetime import datetime
import json
import MetaTrader5 as mt5
import os
from persiantools.jdatetime import JalaliDateTime
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
    def process(path):
        with open(path, "r") as f:
            data: dict = json.loads(f.read())
            f.close()
        data["state"] = 1
        c = fn.cur()
        c.execute("SELECT name FROM symbol WHERE id='" + str(data["sym"]) + "' LIMIT 1")
        found = c.fetchone()
        if len(found) == 0:
            Analyzer.annihilate(path)
            # print("Could not find this symbol in the database!!!")
            return
        found = found[0]
        table = str(data["sym"]) + "_" + fn.tf_name(data["timeframe"])
        rates = mt5.copy_rates_range(found, data["timeframe"], data["start"], data["end"])
        if rates is None:
            Analyzer.annihilate(path)
            # try:
            #     return str(mt5.last_error())
            # except:
            #     return "خطای ناشناخته!"
            return
        if len(rates) > 0:
            data: List[tuple] = list()
            for r in rates:
                # time, open, high, close, tick_volume, spread, real_volume
                unix = int(r["time"])
                greg = datetime.fromtimestamp(unix, tz=utc)
                jala = JalaliDateTime.fromtimestamp(unix, tz=utc)
                data.append((float(r["open"]), float(r["close"]), float(r["high"]), float(r["low"]),
                             greg.strftime("%Y.%m.%d"), jala.strftime("%Y.%m.%d"), greg.strftime("%H:%M")))
        else:
            return "هیچ کندلی پیدا نشد!"
        c.execute("SHOW TABLES")
        if table not in fn.tables(c):
            c.execute("CREATE TABLE " + table + " (id BIGINT AUTO_INCREMENT PRIMARY KEY, " +
                      "open FLOAT, close FLOAT, high FLOAT, low FLOAT, " +
                      "greg VARCHAR(10), jala VARCHAR(10), time VARCHAR(5))")
        c.executemany("INSERT INTO " + table +
                      " (open, close, high, low, greg, jala, time) VALUES (%s, %s, %s, %s, %s, %s, %s)", data)
        dt.connect.commit()
        Analyzer.annihilate(path)

    @staticmethod
    def put_temp(sym: str, timeframe: int, a: JalaliDateTime, b: JalaliDateTime):
        a = a.to_gregorian()
        b = b.to_gregorian()
        temp = {"sym": sym, "timeframe": timeframe,
                "start": datetime(a.year, a.month, a.day, a.hour, a.minute, tzinfo=dt.zone),
                "end": datetime(b.year, b.month, b.day, b.hour, b.minute, tzinfo=dt.zone),
                "state": 0}  # start.strftime("%Y-%m-%d_%H-%M")
        with open("./temp/" + str(len(os.listdir("./temp/"))) + ".json", "w") as f:
            f.write(json.dumps(temp))
            f.close()

    @staticmethod
    def annihilate(path):
        os.remove(path)

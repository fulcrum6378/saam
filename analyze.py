from datetime import datetime
from enum import Enum
import MetaTrader5 as mt5
from persiantools.jdatetime import JalaliDateTime
from pytz import utc
import threading as th
from typing import List

import data as dt
import func as fn


class Board:
    def __init__(self, sym: str, timeframe: int, a: JalaliDateTime, b: JalaliDateTime):
        self.sym = sym
        self.timeframe = timeframe
        a = a.to_gregorian()
        self.start = datetime(a.year, a.month, a.day, a.hour, a.minute, tzinfo=dt.zone)
        b = b.to_gregorian()
        self.end = datetime(b.year, b.month, b.day, b.hour, b.minute, tzinfo=dt.zone)
        self.state = Board.State.PENDING

    def vis(self):
        return self.start.strftime("%Y-%m-%d_%H-%M")

    class State(Enum):
        PENDING = 0
        WORKING = 1
        DONE = 2


boards: List[Board] = list()


class Analyze(th.Thread):
    def __init__(self, a1, a2, a, b):
        th.Thread.__init__(self)
        self.b = Board(a1, int(a2), a, b)

    def run(self) -> None:
        if self.b in boards: return "already"
        self.b.state = Board.State.WORKING
        c = fn.cur()
        c.execute("SELECT name FROM symbol WHERE id='" + str(self.b.sym) + "' LIMIT 1")
        found = c.fetchone()
        if len(found) == 0:
            return "Could not find this symbol in the database!!!"  # Repair....
        found = found[0]
        table = str(self.b.sym) + "_" + fn.tf_name(self.b.timeframe)
        rates = mt5.copy_rates_range(found, self.b.timeframe, self.b.start, self.b.end)
        if rates is None:
            try:
                return str(mt5.last_error())
            except:
                return "خطای ناشناخته!"
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
        self.b.state = Board.State.DONE
        return "done"

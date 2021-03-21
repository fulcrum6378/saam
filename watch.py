from datetime import datetime, timedelta
import MetaTrader5 as mt5
from pytz import timezone, utc
from threading import Thread
from time import sleep
from typing import List

from analyze import Analyzer
import data as dt
import func as fn


class Watcher(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.active = True
        self.time = 0

        self.evMin = None
        self.ev2Min = None
        self.ev3Min = None
        self.ev4Min = None
        self.ev5Min = None
        self.ev6Min = None
        self.ev10Min = None
        self.ev12Min = None
        self.ev15Min = None
        self.ev20Min = None
        self.ev30Min = None
        self.evHour = None
        self.ev2Hour = None
        self.ev3Hour = None
        self.ev4Hour = None
        self.ev6Hour = None
        self.ev8Hour = None
        self.ev12Hour = None
        self.daily = None
        self.weekly = None
        self.monthly = None
        frames = dt.config["timeframes"]
        for tfr in range(len(frames)):
            v = frames[tfr]["value"]
            if v == mt5.TIMEFRAME_M1: self.evMin = tfr
            if v == mt5.TIMEFRAME_M2: self.ev2Min = tfr
            if v == mt5.TIMEFRAME_M3: self.ev3Min = tfr
            if v == mt5.TIMEFRAME_M4: self.ev4Min = tfr
            if v == mt5.TIMEFRAME_M5: self.ev5Min = tfr
            if v == mt5.TIMEFRAME_M6: self.ev6Min = tfr
            if v == mt5.TIMEFRAME_M10: self.ev10Min = tfr
            if v == mt5.TIMEFRAME_M12: self.ev12Min = tfr
            if v == mt5.TIMEFRAME_M15: self.ev15Min = tfr
            if v == mt5.TIMEFRAME_M20: self.ev20Min = tfr
            if v == mt5.TIMEFRAME_M30: self.ev30Min = tfr
            if v == mt5.TIMEFRAME_H1: self.evHour = tfr
            if v == mt5.TIMEFRAME_H2: self.ev2Hour = tfr
            if v == mt5.TIMEFRAME_H3: self.ev3Hour = tfr
            if v == mt5.TIMEFRAME_H4: self.ev4Hour = tfr
            if v == mt5.TIMEFRAME_H6: self.ev6Hour = tfr
            if v == mt5.TIMEFRAME_H8: self.ev8Hour = tfr
            if v == mt5.TIMEFRAME_H12: self.ev12Hour = tfr
            if v == mt5.TIMEFRAME_D1: self.daily = tfr
            if v == mt5.TIMEFRAME_W1: self.weekly = tfr
            if v == mt5.TIMEFRAME_MN1: self.monthly = tfr

    def run(self) -> None:
        if Watcher.stock_open(Watcher.when_s_now()):
            print("STOCK MARKET IS OPEN!!!")

        while self.active:
            self.time += 1
            now = Watcher.when_s_now()

            # When it is a holiday
            if now.weekday() == 4:
                print("IT IS FRIDAY!! SCHEDULING FOR SATURDAY... HAVE A GOOD DAY!")
                nex = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                sleep((nex - now).total_seconds())
                continue

            # Check if it's installed
            c = dt.cur(True)
            c.execute("SELECT id, auto FROM symbol WHERE auto > 0")
            auto = list(c)
            dt.cur(False)
            # print("ITEMS:", len(auto))

            # When the Stock Market is open
            if Watcher.stock_open(now):
                self.high_level_update(auto, now)
                now = Watcher.when_s_now()
                nex = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
                sleep((nex - now).total_seconds())  # DANGER: DON'T USE "60"!!!
                continue

            # Other times
            self.high_level_update(auto, now)
            now = Watcher.when_s_now()
            if now.hour < 9:
                nex = now.replace(hour=9, minute=0, second=0, microsecond=0)
            else:
                nex = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            print("STOCK MARKET IS CLOSED!!! SCHEDULING FOR", nex, ".....")
            sleep((nex - now).total_seconds())

    def high_level_update(self, auto: List, now: datetime):
        for a in auto:
            sta = fn.auto_to_binary(int(a[1]))
            moment = now.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)
            until = now.replace(hour=0, minute=10, second=0, microsecond=0, tzinfo=utc)
            if self.daily is not None and one(sta, self.daily):
                Analyzer.put_temp(a[0], 16408, moment, until)
            if self.weekly is not None and one(sta, self.weekly) and now.weekday() == 0:
                Analyzer.put_temp(a[0], 32769, moment, until)
            if self.monthly is not None and one(sta, self.monthly) and now.day == 1:
                Analyzer.put_temp(a[0], 49153, moment, until)

    def low_level_update(self, auto: List, now: datetime):
        for a in auto:
            sta = fn.auto_to_binary(int(a[1]))
            since = now - timedelta(minutes=1)
            # ATTENTION: MORE CONDITIONS NEEDED FOR THE ALGORITHM...
            if self.evMin is not None and one(sta, self.evMin):
                Analyzer.put_temp(a[0], 1, since, now)
            if self.ev2Min is not None and one(sta, self.ev2Min):
                Analyzer.put_temp(a[0], 2, since, now)
            if self.ev3Min is not None and one(sta, self.ev3Min):
                Analyzer.put_temp(a[0], 3, since, now)
            if self.ev4Min is not None and one(sta, self.ev4Min):
                Analyzer.put_temp(a[0], 4, since, now)
            if self.ev5Min is not None and one(sta, self.ev5Min):
                Analyzer.put_temp(a[0], 5, since, now)
            if self.ev6Min is not None and one(sta, self.ev6Min):
                Analyzer.put_temp(a[0], 6, since, now)
            if self.ev10Min is not None and one(sta, self.ev10Min):
                Analyzer.put_temp(a[0], 10, since, now)
            if self.ev12Min is not None and one(sta, self.ev12Min):
                Analyzer.put_temp(a[0], 12, since, now)
            if self.ev15Min is not None and one(sta, self.ev15Min):
                Analyzer.put_temp(a[0], 15, since, now)
            if self.ev20Min is not None and one(sta, self.ev20Min):
                Analyzer.put_temp(a[0], 20, since, now)
            if self.ev30Min is not None and one(sta, self.ev30Min):
                Analyzer.put_temp(a[0], 30, since, now)
            if self.evHour is not None and one(sta, self.evHour):
                Analyzer.put_temp(a[0], 16385, since, now)
            if self.ev2Hour is not None and one(sta, self.ev2Hour):
                Analyzer.put_temp(a[0], 16386, since, now)
            if self.ev3Hour is not None and one(sta, self.ev3Hour):
                Analyzer.put_temp(a[0], 16387, since, now)
            if self.ev4Hour is not None and one(sta, self.ev4Hour):
                Analyzer.put_temp(a[0], 16388, since, now)
            if self.ev6Hour is not None and one(sta, self.ev6Hour):
                Analyzer.put_temp(a[0], 16390, since, now)
            if self.ev8Hour is not None and one(sta, self.ev8Hour):
                Analyzer.put_temp(a[0], 16392, since, now)
            if self.ev12Hour is not None and one(sta, self.ev12Hour):
                Analyzer.put_temp(a[0], 16396, since, now)

    @staticmethod
    def when_s_now():
        return datetime.now(tz=timezone("Asia/Tehran"))

    @staticmethod
    def stock_open(now) -> bool:
        return now.hour >= 9 and (now.hour < 12 or now.minute <= 30)


def one(status, pos) -> bool:
    return status[pos] == "1"

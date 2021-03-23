# Written by Mahdi Parastesh, February and March 2021
# Twitter: https://twitter.com/fulcrum1378
# All rights reserved.

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
        if Watcher.stock_open(fn.when_s_now()):
            print("STOCK MARKET IS OPEN!!!")

        while self.active:
            self.time += 1
            now = fn.when_s_now()

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
                self.low_level_update(auto, now)
                now = fn.when_s_now()
                nex = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
                dist = (nex - now).total_seconds()
                if dist > 0: sleep(dist)  # DANGER: DON'T USE "60"!!!
                continue

            # Other times
            self.high_level_update(auto, now)
            now = fn.when_s_now()
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
            if able(sta, self.daily):
                Analyzer.put_temp(a[0], 16408, moment, until)
            if able(sta, self.weekly) and now.weekday() == 0:
                Analyzer.put_temp(a[0], 32769, moment, until)
            if able(sta, self.monthly) and now.day == 1:
                Analyzer.put_temp(a[0], 49153, moment, until)

    def low_level_update(self, auto: List, now: datetime):
        for a in auto:
            sta = fn.auto_to_binary(int(a[1]))
            cau = 30
            # Minutes
            if able(sta, self.evMin):
                Analyzer.put_temp(a[0], 1, now - timedelta(minutes=1, seconds=cau), now)
            if able(sta, self.ev2Min) and now.minute % 2 == 0:
                Analyzer.put_temp(a[0], 2, now - timedelta(minutes=2, seconds=cau), now)
            if able(sta, self.ev3Min) and now.minute % 3 == 0:
                Analyzer.put_temp(a[0], 3, now - timedelta(minutes=3, seconds=cau), now)
            if able(sta, self.ev4Min) and now.minute % 4 == 0:
                Analyzer.put_temp(a[0], 4, now - timedelta(minutes=4, seconds=cau), now)
            if able(sta, self.ev5Min) and now.minute % 5 == 0:
                Analyzer.put_temp(a[0], 5, now - timedelta(minutes=5, seconds=cau), now)
            if able(sta, self.ev6Min) and now.minute % 6 == 0:
                Analyzer.put_temp(a[0], 6, now - timedelta(minutes=6, seconds=cau), now)
            if able(sta, self.ev10Min) and now.minute % 10 == 0:
                Analyzer.put_temp(a[0], 10, now - timedelta(minutes=10, seconds=cau), now)
            if able(sta, self.ev12Min) and now.minute % 12 == 0:
                Analyzer.put_temp(a[0], 12, now - timedelta(minutes=12, seconds=cau), now)
            if able(sta, self.ev15Min) and now.minute % 15 == 0:
                Analyzer.put_temp(a[0], 15, now - timedelta(minutes=15, seconds=cau), now)
            if able(sta, self.ev20Min) and now.minute % 20 == 0:
                Analyzer.put_temp(a[0], 20, now - timedelta(minutes=20, seconds=cau), now)
            if able(sta, self.ev30Min) and now.minute % 30 == 0:
                Analyzer.put_temp(a[0], 30, now - timedelta(minutes=30, seconds=cau), now)
            # Hours
            if able(sta, self.evHour) and now.minute == 0:
                Analyzer.put_temp(a[0], 16385, now - timedelta(hours=1, minutes=5), now)
            if able(sta, self.ev2Hour) and now.minute == 0:
                Analyzer.put_temp(a[0], 16386, now - timedelta(hours=2, minutes=5), now)
            if able(sta, self.ev3Hour) and now.minute == 0:
                Analyzer.put_temp(a[0], 16387, now - timedelta(hours=3, minutes=5), now)
            if able(sta, self.ev4Hour) and now.minute == 0:
                Analyzer.put_temp(a[0], 16388, now - timedelta(hours=4, minutes=5), now)
            if able(sta, self.ev6Hour) and now.minute == 0:
                Analyzer.put_temp(a[0], 16390, now - timedelta(hours=6, minutes=5), now)
            if able(sta, self.ev8Hour) and now.minute == 0:
                Analyzer.put_temp(a[0], 16392, now - timedelta(hours=8, minutes=5), now)
            if able(sta, self.ev12Hour) and now.minute == 0:
                Analyzer.put_temp(a[0], 16396, now - timedelta(hours=12, minutes=5), now)
            # Since the hourly candles are unorganized, we won't tighten the above conditions

    @staticmethod
    def stock_open(now) -> bool:
        return (8 < now.hour < 12) or (now.hour == 12 and now.minute <= 30)


def able(status, pos) -> bool:
    return pos is not None and status[pos] == "1"

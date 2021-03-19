from datetime import datetime, timedelta
from pytz import timezone, utc
from threading import Thread
from time import sleep
from typing import List

from analyze import Analyzer
import data as dt


class Watcher(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.active = True

    def run(self) -> None:
        while self.active:
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
            print("ITEMS:", len(auto))

            # When Stock Market is open
            if now.hour >= 9 and (now.hour < 12 or now.minute <= 30):
                print("STOCK MARKET IS OPEN!!!")
                sleep(60)
                continue

            # Other times
            Watcher.high_level_update(auto, now)
            now = Watcher.when_s_now()
            if now.hour < 9:
                nex = now.replace(hour=9, minute=0, second=0, microsecond=0)
            else:
                nex = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            print("STOCK MARKET IS CLOSED!!! SCHEDULING FOR", nex, ".....")
            sleep((nex - now).total_seconds())

    @staticmethod
    def high_level_update(auto: List, now: datetime):
        # ATTENTION: ONLY IF IT IS DETERMINED IN a[1]
        for a in auto:
            moment = now.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)
            until = now.replace(hour=0, minute=10, second=0, microsecond=0, tzinfo=utc)
            Analyzer.put_temp(a[0], 16408, moment, until)
            if now.weekday() == 0: Analyzer.put_temp(a[0], 32769, moment, until)
            if now.day == 1: Analyzer.put_temp(a[0], 49153, moment, until)

    @staticmethod
    def low_level_update(auto: List, now: datetime):
        for a in auto:
            Analyzer.put_temp(a[0])

    @staticmethod
    def when_s_now():
        return datetime.now(tz=timezone("Asia/Tehran"))

from datetime import datetime, timedelta
from pytz import timezone
from threading import Thread
from time import sleep

import data as dt


class Watcher(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.active = True

    def run(self) -> None:
        while self.active:
            now = datetime.now(tz=timezone("Asia/Tehran"))
            if now.hour >= 9 and (now.hour < 12 or now.minute <= 30):
                print("STOCK MARKET IS OPEN!!!")
                sleep(60)
            else:
                if now.hour < 9:
                    nex = now.replace(hour=9, minute=0, second=0, microsecond=0)
                else:
                    nex = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                print("STOCK MARKET IS CLOSED!!! SCHEDULING FOR", nex, ".....")
                sleep((nex - now).total_seconds())

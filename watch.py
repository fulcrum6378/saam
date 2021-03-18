from datetime import datetime
from threading import Thread
from time import sleep

import data as dt


class Watcher(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.active = True

    def run(self) -> None:
        while self.active:
            now = datetime.now()
            print(now)
            sleep(5)

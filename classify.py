# Created by Mahdi Parastesh, February and March 2021
# Github: https://github.com/fulcrum1378
# All rights reversed.

import MetaTrader5 as mt5
import re
import requests
from requests.adapters import HTTPAdapter
from threading import Thread
from urllib3 import Retry

import data as dt
import func as fn


class Classify(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.active = True
        self.install_progress = 0
        self.indices = fn.indices()
        self.names = list(self.indices.keys())
        self.names.sort()

    def run(self):
        c = dt.cur(True)
        for k, v in fn.required_tables.items():
            c.execute("DROP TABLE IF EXISTS " + k)
            c.execute("CREATE TABLE " + k + " " + v)

        sum_all = len(self.names)
        for s in range(sum_all):  # never change global statements inside a loop
            self.install_progress = (100 / sum_all) * s
            symbol_name = self.names[s]
            index = self.indices[symbol_name]
            print("Classifying symbol", s, "of", sum_all)

            # Find branch
            page = Classify.requests_retry_session() \
                .get("http://tsetmc.com/Loader.aspx?ParTree=151311&i=" + index, timeout=10).text
            branch = re.findall(r"LSecVal='([\D]*)',", page)
            if len(branch) == 0:
                print("UNKNOWN SYMBOL!!!", s)
                continue
            branch = branch[0]

            # TABLE branch
            c.execute("SELECT * FROM branch WHERE name='" + branch + "' LIMIT 1")
            exists = list()
            for i in c: exists.append(i)
            if len(exists) == 0:
                c.execute("INSERT INTO branch (name) VALUES (?)", [branch])
                dt.connect.commit()
                branch_id = c.lastrowid
            else:
                branch_id = exists[0][0]

            # TABLE symbol
            got = mt5.symbols_get(symbol_name)
            if got is not None and len(got) > 0:
                inf = got[0].description
            else:
                inf = None  # if the Mofid server is off, this will be returned!!!
            c.execute("INSERT INTO symbol (id, name, info, branch) VALUES (?, ?, ?, ?)",
                      (index, symbol_name, inf, branch_id))
            dt.connect.commit()
        dt.cur(False)
        self.active = False

    @staticmethod
    def requests_retry_session(
            retries=10,
            backoff_factor=0.3,
            status_forcelist=(500, 502, 504, 503),
            session=None,
    ):
        session = session or requests.Session()
        adapter = HTTPAdapter(max_retries=Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        ))
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

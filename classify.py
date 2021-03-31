# Created by Mahdi Parastesh, February and March 2021
# Github: https://github.com/fulcrum1378
# All rights reversed.

import pytse_client as tse
from threading import Thread

import data as dt
from func import Connector


class Classify(Connector):
    def __init__(self):
        Connector.__init__(self)
        self.install_progress = 0

    def run(self):
        c = self.cur(True)
        c.execute("SELECT * FROM symbol")  # gives the same tuple you inserted.
        symbols = list()  # list of tuples
        for i in c: symbols.append(i)
        self.cur(False)

        sum_all = len(symbols)
        for s in range(len(symbols)):  # never change global statements inside a loop
            self.install_progress = (100 / sum_all) * s

            # Find branch
            symbol_name = symbols[s][1]
            branch = tse.Ticker(symbol_name).group_name  # fun.sql_esc()
            # print(branch)  # Persian not supported in Win7-CMD
            print("Classifying symbol", s, "of", sum_all)

            # Check if it exists in 'branch'
            c = self.cur(True)
            c.execute("SELECT * FROM branch WHERE name='" + branch + "' LIMIT 1")
            exists = list()
            for i in c: exists.append(i)
            if len(exists) == 0:
                c.execute("INSERT INTO branch (name) VALUES (%s)", branch)
                dt.connect.commit()
                branch_id = c.lastrowid
            else:
                branch_id = exists[0][0]

            # Update symbol
            c.execute("UPDATE symbol SET branch='" + str(branch_id) + "' WHERE name='" + symbol_name + "'")
            dt.connect.commit()
            self.cur(False)
        self.active = False

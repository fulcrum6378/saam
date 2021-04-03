# Created by Mahdi Parastesh, February and March 2021
# Github: https://github.com/fulcrum1378
# All rights reversed.

import pytse_client as tse
from threading import Thread

import data as dt


class Classify(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.active = True
        self.install_progress = 0

    def run(self):
        c = dt.cur(True)
        c.execute("SELECT * FROM symbol")  # gives the same tuple you inserted.
        symbols = list()  # list of tuples
        for i in c: symbols.append(i)
        dt.cur(False)

        sum_all = len(symbols)
        for s in range(len(symbols)):  # never change global statements inside a loop
            self.install_progress = (100 / sum_all) * s

            # Find branch
            symbol_name = symbols[s][1]
            branch = tse.Ticker(symbol_name).group_name  # fun.sql_esc()
            # print(branch)  # Persian not supported in Win7-CMD
            print("Classifying symbol", s, "of", sum_all)

            # Check if it exists in 'branch'
            c = dt.cur(True)
            c.execute("SELECT * FROM branch WHERE name='" + branch + "' LIMIT 1")
            exists = list()
            for i in c: exists.append(i)
            if len(exists) == 0:
                c.execute("INSERT INTO branch (name) VALUES (?)", [branch])
                dt.connect.commit()
                branch_id = c.lastrowid
            else:
                branch_id = exists[0][0]

            # Update symbol
            c.execute("UPDATE symbol SET branch='" + str(branch_id) + "' WHERE name='" + symbol_name + "'")
            dt.connect.commit()
            dt.cur(False)
        self.active = False

# coding: utf-8

import time

principal = 200
cash = 100
i = 0
encashment = 0

while True:
    time.sleep(1)
    i += 1
    bonus = principal * 0.3

    if bonus > 4 * cash:
        cash += 100
        bonus -= cash
        encashment += cash
    elif bonus > 2 * cash:
        bonus -= cash
        encashment += cash
    else:
        pass

    principal += bonus
    print "{0} day: bonus {1}, principal {2}, encashment {3}".format(
        i, bonus, principal, encashment)
    if cash > 2000:
        break

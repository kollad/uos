# -*- coding: mbcs -*-
from stealth import *
from time import sleep
from datetime import timedelta, datetime as dt

def CheckSave():
    ts = dt.now() - timedelta(seconds=30)
    if InJournalBetweenTimes('Saving World State', ts, dt.now()) > 0:
        sleep(30)
    return True

print("Loading: UO.CheckSave    [ok]")

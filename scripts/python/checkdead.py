# -*- coding: mbcs -*-
from stealth import *
from time import sleep

def CheckDead(res=1):
   if Dead():
      print("<<-- вот в это время чар умер")
      if res == 1:
         SetWarMode(True)
         WaitGump('1')
         while Dead():
            sleep(2)
         print("Чар снова жив!")
         UOSay("Danke Schoen!")
      elif res == 2:
         print("По желанию заказчика мы отказывается от резуректа и валим в логаут")
         SetARstatus(False)
         Disconnect()
      else:
         print("По желанию заказчика мы отказывается от резуректа, но остаемся висеть в онлайне")
         while Dead():
            sleep(10)
   return True

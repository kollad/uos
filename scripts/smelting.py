# -*- coding: mbcs -*-
from stealth import *
from checksave import CheckSave
from checkdead import CheckDead
import time

STORAGES = {
    'all': 0x4009DD1B,
    'high': 0x400A3E0A,
    'low': 0x4009EBEE,
}

ORE_TYPES = [0x19B7, 0x19B8, 0x19B9, 0x19BA]
INGOT_TYPES = [0x1BEF]

ORE_COLORS = {
    'high': [],
    'low': []
}

ORE_TO_SMELT = 750
WAIT_TIME = 1000
LAG_WAIT = 15000

def Smelting():
    CheckSave()
    CheckDead()
    for ore_type in ORE_TYPES:
        if FindType(ore_type,STORAGES['all']):  
            item = FindItem()
            MoveItem(item, ORE_TO_SMELT, Backpack(), 0, 0, 0)
            UseObject(item)
            Wait(WAIT_TIME)
            CheckLag(LAG_WAIT)
            return 1                
        DropIngots()            
                    
def DropIngots():
    CheckSave()        
    CheckDead()
    for ingot_type in INGOT_TYPES:
        if FindType(ingot_type, Backpack()):
            item = FindItem()
            storage = get_storage(item)    
            MoveItem(item, GetQuantity(item), storage, 0, 0, 0);
            Wait(WAIT_TIME)
            CheckLag(LAG_WAIT)
            return 1

def get_storage(item):
    color = GetColor(item)
    if color in ORE_COLORS['high']:
        return STORAGES['high']
    elif color in ORE_COLORS['low']:
        return STORAGES['low']
    else:
        return STORAGES['all']
        
    
while True:
    Smelting()
    time.sleep(0.2)                        

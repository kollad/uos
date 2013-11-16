from stealth import *
from checksave import CheckSave
from checkdead import CheckDead

from datetime import datetime

import time

STORAGES = {
    'all': 0x4009DD1B,  # Storage where all ore and probably ingots are
    'high': 0x400A3E0A, # Storage with High ores. Start from Black Steel and higher
    'low': 0x4009EBEE,  # Storage with low ores
    'crafted': 0x4006605F  # Storage where crafted items will be stored
}

ORE_TYPES = [0x19B7, 0x19B8, 0x19B9, 0x19BA]
INGOT_TYPES = [0x1BEF]  # Probably deprecated
INGOT_TYPE = 0x1BEF
HAMMER_TYPE = 0x13E3
SCIMITAR_TYPE = 0x13B5

ORE_COLORS = {
    'high': [], # Starting from Black Steel
    'low': []
}

INGOTS_COUNT = 500
WAIT_TIME = 1000
LAG_WAIT = 15000
REQUIRED_INGOTS = 25 # Minimum ingots required for craft (Scimitar)

FORGE_ID = 0x40006325

def _GetIngots():
    CheckSave()
    CheckDead()                      
    CheckLag(LAG_WAIT)
    FindType(INGOT_TYPE, Backpack())
    ingots = FindItem()
    quantity = GetQuantity(ingots)
    print 'Checking if we have minimum ingots, required to craft'
    if quantity < REQUIRED_INGOTS:
        CheckLag(LAG_WAIT)
        time.sleep(0.5)          
        print 'We have %s ingots in backpack left. Getting more' % quantity
        if FindType(INGOT_TYPE, STORAGES['low']):
            ingots = FindItem()
            MoveItem(ingots, INGOTS_COUNT - quantity, Backpack(), 0, 0, 0);
            Wait(WAIT_TIME);
            CheckLag(LAG_WAIT);
    if ingots:
        return ingots
    else:
        print 'Something is wrong, no ingots found anywhere'
        return False
                
def _CountIngots(ingots):
    CheckSave()
    CheckDead()
    if FindType(INGOT_TYPE, Backpack()):
        return GetQuantity(FindItem())
    return False


def _Craft(ingots):
    CheckSave()        
    CheckDead()
    hammer = False
    ingots_count = _CountIngots(ingots)   
    while ingots_count >= REQUIRED_INGOTS:
        time.sleep(0.5)
        CheckLag(LAG_WAIT)                       
        if ObjAtLayer(0x01):
            Disarm()      
        if FindType(HAMMER_TYPE, Backpack()):
            hammer = FindItem()       
            UseObject(hammer)
            WaitTargetObject(ingots)
            Wait(WAIT_TIME)
            CheckLag(LAG_WAIT)
            CancelTarget()
            _GumpSelect()          
        ingots_count = _CountIngots(ingots)   
        Wait(WAIT_TIME)
        CheckLag(LAG_WAIT)
        print 'Ingots left in backpack: %s' % ingots_count
        if not hammer:
            print 'You have no hammer in your inventory' 
    return True 
           
def _Crafting():
    _DropIngots()
    CheckLag(LAG_WAIT)
    ingots = _GetIngots()
    CheckLag(LAG_WAIT)    
    _Craft(ingots)    
    CheckLag(LAG_WAIT)
    # _DropCrafted()
    _SmeltCrafted()
    CheckLag(LAG_WAIT) 
    return True       
                    
def get_storage(item):
    color = GetColor(item)
    if color in ORE_COLORS['high']:
        return STORAGES['high']
    elif color in ORE_COLORS['low']:
        return STORAGES['low']
    else:
        return STORAGES['all']
                                          
def _GumpSelect():
    CheckSave()
    CheckDead()
    WaitGump('5') # First menu (select Swords)
    WaitGump('102') # Second menu (select Scimitar)
    WaitGump('1') # Third menu (select Make item)
    CheckLag(LAG_WAIT)      
    if WaitJournalLine(datetime.now(), 'You put the', 15000):
        CheckSave()
        CheckDead()
        CheckLag(LAG_WAIT)
    return True      
                       
def _DropCrafted():
    print 'Dropping crafted items'
    CheckSave()
    CheckDead()
    quantity = FindFullQuantity(FindType(SCIMITAR_TYPE, Backpack()))
    MoveItems(Backpack(), SCIMITAR_TYPE, 0xFFFF, STORAGES['crafted'], 0, 0, 0, 500);
    CheckLag(LAG_WAIT)                                                              
    print 'Dropped %s scimitars' % quantity 
    return True

def _SmeltCrafted():
    print 'Smelting crafted items'
    CheckSave()
    CheckDead()
    if FindType(SCIMITAR_TYPE, Backpack()):
        for scimitar in GetFindedList():
            UseObject(Forge)
            WaitTargetObject(scimitar)
            Wait(WAIT_TIME)
            CheckLag(LAG_WAIT)
    print 'Smelting finished'
    
def _DropIngots():
    print 'Dropping any ingots from backpack'
    CheckSave()
    CheckDead()
    MoveItems(Backpack(), INGOT_TYPE, 0xFFFF, STORAGES['all'], 0, 0, 0, 500);
    CheckLag(LAG_WAIT)
    return True
      
while True:
    CheckLag(LAG_WAIT)
    _Crafting()
                          

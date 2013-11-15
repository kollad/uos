from stealth import *
from checksave import CheckSave
from checkdead import CheckDead
from time import sleep
from datetime import timedelta, datetime as dt
import logging
import time

HOME_X = 2459
HOME_Y = 898

FORGE = 0x4006F085
STORAGE = 0x4009DD1B
INGOTS_STORAGE = 0x4003EC5A
INGOTS_TYPE = 0x1BF2

IRON_COLOR = 0x0000
IRON_COUNT = 0x20

WAIT_TIME = 1000
WAIT_CYCLES = 7
LAG_WAIT = 15000

MINING_TOOLS = [0x0E85, 0x0E86]
ORE_TYPES = [0x19B7, 0x19B8, 0x19B9, 0x19BA]
MINE_POINTS = [[2431, 903],
               [2434, 903],
               [2437, 903],
               [2440, 903],
               [2443, 903],
               [2446, 903],
               [2441, 907],
               [2439, 900],
               [2440, 896],
               [2443, 896],
               [2446, 896],
               [2448, 892],
               [2448, 886],
               [2448, 882],
               [2445, 882],
               [2442, 883],
               [2438, 883],
               [2435, 881],
               [2438, 878],
               [2441, 877],
               [2445, 878],
               [2436, 875],
               [2435, 872],
               [2432, 877],
               [2443, 885],
               [2443, 892],
               [2449, 894],
               [2448, 899],
               [2447, 903],
               [2443, 906]]

SESSION_DROP_COUNT = {}

ORE_COLORS = {
    0x0AAE: 'Elemental',
    0x043A: 'Lava',
    0x0AAF: 'Dark Crystal',
    0x0A9F: 'Platinum',
    0x0AA0: 'Meteor',
    0x0445: 'Gold',
    0x0AA3: 'Black Steel',
    0x042D: 'Silver',
    0x042C: 'Steel',
    0x0488: 'Bronze',
    0x0AB2: 'Copper',
    0x0000: 'Iron'
}

logging.basicConfig(filename='mining.log', level=logging.DEBUG)
log = logging.getLogger('mining')

mining_tool = None
       
def _check():
    CheckSave()
    CheckDead()
    CheckLag(LAG_WAIT)


def check_mining_tool():
    mining_tool = None
    _check()
    if ObjAtLayer(LhandLayer()):
        Disarm()
    for tool in MINING_TOOLS:
        FindType(tool, Backpack())
        if FindCount():
            mining_tool = FindItem()
            break
        else:
            mining_tool = None
            continue   
    return mining_tool


def drop_ore():
    global SESSION_DROP_COUNT
    print 'Dropping ORE...'
    for ore in ORE_TYPES:
        _check()
        if FindType(ore, Backpack()):
            for item in GetFindedList():
                quantity = GetQuantity(item)  
                if quantity > 0:
                    _check()
                    MoveItem(item, quantity, STORAGE, 0xFFFF, 0xFFFF, 0)
                    Wait(WAIT_TIME)
                    color = GetColor(item)  
                    SESSION_DROP_COUNT.setdefault(color, 0)
                    print 'Dropped {quantity} x {color_name}'.format(quantity=quantity, color_name=ORE_COLORS[color])
                    SESSION_DROP_COUNT[color] += quantity
        Wait(WAIT_TIME)
    print 'Dropped.'
    log.info('Total drops by session: %s' % ' | '.join(
        ['{o} {q}'.format(o=ORE_COLORS[color], q=quantity or 0) for color, quantity in SESSION_DROP_COUNT.items()])
    )


def go(x, y):
    in_place = False
    while not in_place:
        CheckDead()
        Wait(WAIT_TIME)
        MoveThroughNPC = 0
        in_place = NewMoveXY(x, y, True, 0, False)
    return True


def go_home():
    print 'Going home...'
    go(HOME_X, HOME_Y)
    print 'At home.'
    return True


def check_state():
    if 1100 < Weight() + 60:
        while True:
            CheckDead()
            if go_home():
                break

        drop_ore()
    while not check_mining_tool():
        CheckDead()


def mine(x, y, position_x, position_y):
    tile = None
    found = False
    static_data = ReadStaticsXY(x, y, WorldNum())  
    for t in static_data:
        if (GetTileFlags(2, t.Tile) and 0x200) == 0x200:
            z = t.Z  
            tile = t
            found = True
            break

    check_state()

    if tile:
        CheckDead()
        if TargetPresent():
            CancelTarget()
        while not check_mining_tool():
            CheckDead()
            Wait(WAIT_TIME)

        empty = False

        while not empty:
            Wait(WAIT_TIME)
            UseObject(check_mining_tool())
            CheckLag(LAG_WAIT)
            WaitForTarget(WAIT_TIME)
            if TargetPresent():
                if not position_x == GetX(Self()) or not position_y == GetY(Self()):
                    go(position_x, position_y)
                start_time = dt.now()
                TargetToTile(tile.Tile, x, y, z)
                found = False
                idle_count = 0
                
                while not found:
                    CheckLag(LAG_WAIT)
                    if idle_count >= 15:
                        found = True
                    now = dt.now()    
                    if InJournalBetweenTimes('Try mining elsewhere|You cannot mine|nothing here to mine|Iron Ore|Copper Ore|Bronze Ore',                       start_time, now) > 0: 
                        empty = True
                        found = True
                    elif InJournalBetweenTimes('You put|You loosen some rocks', start_time, now) > 0:
                        found = True
                    else: 
                        Wait(WAIT_TIME)
                        idle_count += 1
        check_state()
    return True


def mine_point(position_x, position_y):
    if not position_x == GetX(Self()) or not position_y == GetY(Self()):
        go(position_x, position_y)

    print 'At mining location. Starting mining...'

    x = GetX(Self())
    y = GetY(Self())
                         
    mine(x + 1, y, position_x, position_y)
    mine(x + 1, y + 1, position_x, position_y)
    mine(x, y + 1, position_x, position_y)
    mine(x - 1, y + 1, position_x, position_y)
    mine(x - 1, y, position_x, position_y)
    mine(x - 1, y - 1, position_x, position_y)
    mine(x, y - 1, position_x, position_y)
    mine(x + 1, y - 1, position_x, position_y)

    print 'Current spot finished.'


while True:
    terminated = False
    if not terminated:
        if Dead():
            terminated = True
        if not Connected():
            Connect()
            Wait(10000)

        for point in MINE_POINTS:
            mine_point(point[0], point[1])


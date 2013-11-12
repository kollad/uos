# -*- coding: mbcs -*-
from stealth import *
from checksave import CheckSave
from checkdead import CheckDead
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

ORE_NAMES = {}

logging.basicConfig(filename='mining.log', level=logging.DEBUG)
log = logging.getLogger('mining')

mining_tool = None


def _check():
    CheckSave()
    CheckDead()
    CheckLag(LAG_WAIT)


def check_mining_tool():
    _check()
    if ObjAtLayer(0x01):
        Disarm()
    for tool in MINING_TOOLS:
        FindType(tool, Backpack())
        if FindCount():
            global mining_tool
            mining_tool = FindItem()
            break
        else:
            continue


def drop_ore():
    print 'Dropping ORE...'
    for ore in ORE_TYPES:
        SESSION_DROP_COUNT.setdefault(ore, 0)
        _check()
        if FindType(ore, Backpack()):
            item = FindItem()
            quantity = GetQuantity(item)
            if quantity > 0:
                _check()
                MoveItem(item, quantity, INGOTS_STORAGE, 0xFFFF, 0xFFFF, 0)
                Wait(WAIT_TIME)
                print 'Dropped {quantity} x {color_name}'.format(quantity, ORE_NAMES[ore])
                global SESSION_DROP_COUNT
                SESSION_DROP_COUNT[ore] += quantity
    print 'Dropped.'
    log.info('Total drops by session: ' % '|'.join(
        ['{}:{}'.format(ore, quantity) for ORE_NAMES[ore], quantity in SESSION_DROP_COUNT.iteritems()])
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
    if 1300 < Weight() + 60:
        while True:
            CheckDead()
            if go_home():
                break

        drop_ore()
    while not check_mining_tool():
        CheckDead()


def mine(x, y, position_x, position_y):
    found = False
    iron = False
    static_data = ReadStaticsXY(x, y, WorldNum)
    for i in static_data.StaticCount():
        if i >= static_data.StaticCount():
            break
        if GetTileFlags(2, static_data.Statics[i].Tile() and 0x200) == 0x200:
            tile = static_data.Statics[i].Tile()
            z = static_data.Statics[i].Z()
            found = True
            break

    check_state()

    while found:
        CheckDead()
        if TargetPresent():
            CancelTarget()
        while not check_mining_tool():
            CheckDead()

        empty = False

        while not empty:
            Wait(WAIT_TIME)
            UseObject(mining_tool)
            CheckLag(LAG_WAIT)
            WaitForTarget(WAIT_TIME)
            if TargetPresent():
                if not position_x == GetX(Self()) or not position_y == GetY(Self()):
                    go(position_x, position_y)
                start_time = time.time()
                TargetToTile(tile, x, y, z)
                found = False

                idle_count = 0

                while not found:
                    CheckLag(LAG_WAIT)

                    if idle_count >= 15:
                        found = True

                    if InJournalBetweenTimes(
                            'Try mining elsewhere|You cannot mine|nothing here to mine|Iron Ore|Copper Ore|Bronze Ore',
                            start_time, time.time()) > 0:
                        empty = True
                        found = True

                    if InJournalBetweenTimes('You put|You loosen some rocks', start_time, time.time()) > 0:
                        found = True

                    if not found:
                        Wait(WAIT_TIME)

                    idle_count += 1

        check_state()


def mine_point(position_x, position_y):
    if not position_x == GetX(Self()) or not position_y == GetY(Self()):
        print 'Moving to target location'
        go(position_x, position_y)

    print 'At mining location. Starting mining...'

    x = GetX(Self())
    y = GetY(Self())

    for _x in xrange(-1, 1):
        for _y in xrange(-1, 1):
            mine(x + _x, position_x, position_y)

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



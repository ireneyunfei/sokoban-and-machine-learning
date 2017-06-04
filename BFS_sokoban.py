'''
This file provides tools to process the game.BaseException.
'''

from array import array
from collections import deque
# import psyco


def init(board, nrows=10):
    # 1 wall 0 empty 2 box 4 player 3 goal 5 box on the goal
    # "1" wall '0' empty "$" box "@" player . goal * box on the goal
    maps = {'0': '0', '3': '3', "4": '0', "1": "1", "2": '0'}
    mapd = {'0': '0', '3': '0', "4": "4", "1": '0', "2": "5"}
    sdata = ""
    ddata = ""

    for c, ch in enumerate(board):
        sdata += maps[ch]
        ddata += mapd[ch]
        if ch == '4':
            px = c % nrows
            py = c // nrows
    return (px, py, sdata, ddata)


def push(x, y, dx, dy, data, nrows, sdata):
    if sdata[(y + 2 * dy) * nrows + x + 2 * dx] == "1" or \
       data[(y + 2 * dy) * nrows + x + 2 * dx] != '0':
        return None
    data2 = [int(x) for x in data]
    data2[y * nrows + x] = 0
    data2[(y + dy) * nrows + x + dx] = 4
    data2[(y + 2 * dy) * nrows + x + 2 * dx] = 5
    return ''.join(str(x) for x in data2)
    # return data2


def is_solved(data, sdata):
    for i in range(len(data)):
        if (sdata[i] == '3') != (data[i] == "5"):
            return False
    return True


def solve(level, nrows=10):
    px, py, sdata, ddata = init(level, nrows)
    open = deque([(ddata, "", px, py)])
    visited = set([ddata])
    dirs = ((0, -1, 'u', 'U'), (1, 0, 'r', 'R'),
            (0,  1, 'd', 'D'), (-1, 0, 'l', 'L'))

    lnrows = nrows
    optstep = 999
    optpath = []
    while open:
        cur, csol, x, y = open.popleft()
        if len(csol) == optstep:
            break
        for di in dirs:
            temp = cur
            dx, dy = di[0], di[1]

            if temp[(y + dy) * lnrows + x + dx] == "5":
                temp = push(x, y, dx, dy, temp, lnrows, sdata)
                if temp and temp not in visited:
                    if is_solved(temp, sdata):
                        optpath.append(csol + di[3])
                        optstep = len(optpath[0])
                        continue
                    open.append((temp, csol + di[3], x + dx, y + dy))
                    visited.add(temp)
            else:
                if sdata[(y + dy) * lnrows + x + dx] == "1" or \
                   temp[(y + dy) * lnrows + x + dx] != '0':
                    continue
                temp = [int(x) for x in temp]
                data2 = temp
                data2[y * lnrows + x] = 0
                data2[(y + dy) * lnrows + x + dx] = 4
                temp = ''.join(str(x) for x in data2)
                # temp = data2

                if temp not in visited:
                    if is_solved(temp, sdata):
                        optpath.append(csol + di[2])
                        optstep = len(optpath[0])
                        continue
                    open.append((temp, csol + di[2], x + dx, y + dy))
                    visited.add(temp)
    return (optpath, optstep)


def visitedmap(level, path, nrows=10):
    '''
    level is the inital map of the game, inputted as a string in one line;
    path is also a string in one line using l r d u to denote the direction
     and upper case to denote pushing.

     This function returns a list of int.
     '''
    px, py, sdata, ddata = init(level, nrows)
    initmap = [int(x) for x in ddata]
    track = [initmap]
    dic_dir = {'l': (-1, 0), 'r': (1, 0), 'd': (0, 1), 'u': (0, -1)}
    for tempi,di in enumerate(path):
        # copy a new list rather than redirect to the old one
        curmap = list(track[-1])
        if di.islower():
            dx, dy = dic_dir[di]
            curmap[py * nrows + px] = 0
            curmap[(py + dy) * nrows + px + dx] = 4
            px += dx
            py += dy
        else:
            dx, dy = dic_dir[di.lower()]
            curmap[py * nrows + px] = 0
            curmap[(py + dy) * nrows + px + dx] = 4
            curmap[(py + 2 * dy) * nrows + px + 2 * dx] = 5
            px += dx
            py += dy
        track.append(curmap)
    return track


def printtrack(level, path, nrows=10):
    px, py, sdata, ddata = init(level, nrows)
    track = visitedmap(level, path, nrows)
    smap = [int(x) for x in sdata]
    dic_digit = {0: ' ', 1: '#', 2: '$', 3: '.', 4: '@', 5: '*', 6: '&'}
    for counter, eachmap in enumerate(track):
        curmap = ''
        print(counter)
        print('\n============================================\n')
        for x, y in zip(smap, eachmap):
            z = max(x, y)
            if z == 5 and x != 3:
                z = 2
            if z == 4 and x == 3:
                z = 6
            curmap = curmap+dic_digit[z]
        i = 0
        while i < len(curmap):
            print(curmap[i:i + 10])
            i = i + 10
    return None

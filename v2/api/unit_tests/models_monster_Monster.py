#!/usr/bin/python2.7

import unit_test

logger = unit_test.set_env()

from models import monster
import utils

def dump(M):
    print "Name: %s" % M.get("name")
    print "Expansion: %s" % M.get("expansion")
    print "Level: %s" % M.get("level")
    print "Type: %s" % M.get("__type__")
    print

W = monster.Monster(handle="white_lion")
print utils.asset_object_to_json(W)
dump(W)

G = monster.Monster(name="Gorm")
print utils.asset_object_to_json(G)
dump(G)

L = monster.Monster(name="Lonely Tree Lvl 1")
dump(L)

G2 = monster.Monster(name="Gorm 2")
dump(G2)

P = monster.Monster(name="phoenix")
dump(P)

P2 = monster.Monster(name="phoniex l 2")
dump(P2)

B = monster.Monster(name="butchee 2")
dump(B)

WATCHER = monster.Monster(name="the watcher")
print utils.asset_object_to_json(WATCHER)
dump(WATCHER)

K = monster.Monster(name="the king's man")
print utils.asset_object_to_json(K)
dump(K)

w = monster.Monster(name="White Lion (First Story)")
print utils.asset_object_to_json(w)
dump(w)

g = monster.Monster(name="Golden Eyed King of 1000 Years")
print utils.asset_object_to_json(g)
dump(g)

b = monster.Monster(name="Butcher Lvl 2")
print utils.asset_object_to_json(b)
dump(b)

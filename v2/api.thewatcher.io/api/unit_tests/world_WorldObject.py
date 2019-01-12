#!/usr/bin/python2.7

import unit_test

logger = unit_test.set_env()

import world

W = world.World()
print W.killboard()
print W.latest_kill()
print W.max_survival_limit()

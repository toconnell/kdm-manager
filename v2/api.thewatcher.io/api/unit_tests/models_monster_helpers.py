#!/usr/bin/python2.7

import unit_test

logger = unit_test.set_env()

from models import monster

A = monster.Assets()
handles = A.get_handles()
print handles

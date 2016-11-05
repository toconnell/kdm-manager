#!/usr/bin/python2.7

import unit_test

logger = unit_test.set_env()

import settings

S = settings.Settings()

print S.secret_keys

print settings.check_key("Yitk8ZRWl9Z3M6Zx.N29mnvCMs")

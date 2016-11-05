#!/usr/bin/python2.7

import unit_test

generic_logger = unit_test.set_env()

from models import survivors

S = survivors.Survivor(_id="581cb2d24af5ca76ebb4ee6f")
#S.logger.debug("here")


#!/usr/bin/env python

import os
import unittest
import sys

if __name__ == "__main__":
    cwd = os.getcwd().split("/")
    if not (cwd[-1] == 'v1' and cwd[-2] == 'kdm-manager'):
        print("Run this test harness from the 'v1' folder only!")
        sys.exit(1)

    loader = unittest.TestLoader()
    suite = loader.discover('unit_tests/')

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

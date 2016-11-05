#!/usr/bin/python2.7

import os
import sys


def set_env():
    """ Sets the cwd and other sys elements so that unit test can run. """

    sys.path.append(os.getcwd())

    import utils

    return utils.get_logger()


if __name__ == "__main__":
    pass

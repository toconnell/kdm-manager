#!/usr/bin/python2.7


# general imports
import daemon
from optparse import OptionParser

# local imports
import utils

class world:
    def __init__(self):
        self.utils = utils.Utilities()
        self.logger = self.utils.get_logger()
        self.logger.debug("success")

        self.test = "true"

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-d", dest="daemon_cmd", metavar="status|start|stop|restart", default=None)
    (options, args) = parser.parse_args()

    W = world()
    print W.test

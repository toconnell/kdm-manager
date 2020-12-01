"""

    Our generic utilities module.


"""

# standard lib
from datetime import datetime
import logging
import os
import sys

# second party
from bson.objectid import ObjectId

# application imports
from app import app

# CONSTANTS
YMD = "%Y-%m-%d"
YMDHMS = "%Y-%m-%d %H:%M:%S"


def convert_json_dict(ng_dict):
    """ Converts a dictionary with JSON keys into a normal dict. """

    logger = get_logger()
    for key, value in ng_dict.items():
        if isinstance(value, dict):
            if value.get('$oid', None) is not None:
                ng_dict[key] = ObjectId(value['$oid'])
            elif value.get('$date', None) is not None:
                ng_dict[key] = datetime.fromtimestamp(value['$date'] / 1000.0)

    return ng_dict


def get_logger(log_level=None, log_name=None):
    """ Initialize a logger. Defaults come from config.py. """

    # defaults
    log_root_dir = os.path.join(app.root_path, '..', 'logs')
    if log_level is None:
        if app.config['DEBUG']:
            log_level = 'DEBUG'
        else:
            log_level = 'INFO'
    if log_name is None:
        log_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if log_name == '':
        log_name = 'default'

    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    if len(logger.handlers):    # if we're initializing a log, kill other
        logger.handlers = []    # open handles, so the latest init wins

    if not len(logger.handlers):    # if it's not already open, open it

        # now check the logging root, create it if it's not there
        if not os.path.isdir(log_root_dir):
            os.mkdir(log_root_dir)

        # create the path and add it to the handler
        log_path = os.path.join(log_root_dir, log_name + ".log")
        logger_fh = logging.FileHandler(log_path)

        #   set the formatter and add it via addHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s:\t%(message)s', YMDHMS
        )
        logger_fh.setFormatter(formatter)
        logger.addHandler(logger_fh)

    return logger

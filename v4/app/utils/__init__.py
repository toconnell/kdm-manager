"""

    Our generic utilities module.


"""

# standard lib
from datetime import datetime
import functools
import logging
import os
import sys

# second party
from bson.objectid import ObjectId
import requests

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


#
#   misc.
#

def api_preflight():
    """ Pings the API; returns true if it's alive. """
    endpoint = app.config['API']['url'] + 'stat'
    try:
        requests.get(
            endpoint,
            verify = app.config['API']['verify_ssl']
        )
    except requests.exceptions.ConnectionError as e:
        return False
    return True


#
#   Custom exceptions
#

class Logout(Exception):

    def __init__(self, message=None, status_code=500):
        self.logger = get_logger(log_name='errors')
        self.logger.error(message)
        self.logger.warn('Forcing logout...')

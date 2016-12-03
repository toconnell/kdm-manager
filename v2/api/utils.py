#!/usr/bin/python2.7


# general imports
from bson import json_util
from datetime import datetime, timedelta
from flask import Response
import json
import logging
import os
import socket
import sys
from pymongo import MongoClient

# project-specific imports
import settings


# random, one-off helpers in the main namespace

mdb = MongoClient()[settings.get("api","mdb")]
ymd = "%Y-%m-%d"
hms = "%H:%M:%S"
ymdhms = "%Y-%m-%d %H:%M:%S"
thirty_days_ago = datetime.now() - timedelta(days=30)
recent_session_cutoff = datetime.now() - timedelta(hours=12)

# generic http responses
http_401 = Response(response="Valid API key required", status=401)
http_404 = Response(response=None, status=404)
http_422 = Response(response="Missing argument, parameter or value", status=422)
http_500 = Response(response="Server explosion! The server erupts in a shower of gore, killing your request instantly. All other servers are so disturbed that they lose 1 survival.", status=500)



# API response/request helpers

#
#   stub dictionary for creating the meta element of API returns
#

api_meta = {
    "meta": {
        "api": {
        "version": settings.get("api","version"),
        "hostname": socket.gethostname(),
        "mdb_name": settings.get("api","mdb"),
        },
        "object": {},
    },
}




# laziness and DRYness methods

def cli_dump(key, spacer, value):
    """ Returns a command line interface pretty string for use in admin scripts
    and other things that dump strings to CLI over STDOUT. """

    spaces = spacer - len(key)

    output = "%s:" % key
    output += " " * spaces
    output += "%s" % value

    print(output)

def seconds_to_hms(seconds):
    """ Converts seconds (expressed as int) to a h:m:s string. """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)

def get_percentage(part, whole):
    """ Input a part, then the whole. Returns percent as a float. """
    if whole == 0:
        return 0
    else:
        return 100 * round(float(part)/float(whole), 2)


# general usage methods

def get_logger(log_level=None, log_name=None):
    """ Initialize a logger, specifying a new file if necessary. """
    logger = logging.getLogger(__name__)

    if len(logger.handlers):    # if we're initializing a log, kill whatever other
        logger.handlers = []    # handlers are open, so that the latest init wins

    if not len(logger.handlers):    # if it's not already open, open it

        # set the file name or default to the script asking for the logger
        log_file_name = log_name
        if log_name is None:
            log_file_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        log_handler_level = log_level

        # do the same for log level, defaulting to the server's 'log_level'
        if log_handler_level is None:
            logger.setLevel(settings.get("server","log_level"))
        elif type(log_handler_level) == str:
            exec 'log_level_obj = logging.%s' % log_level
            logger.setLevel(log_level_obj)
        else:
            logger.setLevel(log_handler_level)

        # now check the logging root, just as a precaution
        log_root_dir = settings.get("api","log_dir")
        if not os.path.isdir(log_root_dir):
            e = Exception("Logging root dir '%s' does not exist!" % log_root_dir)
            raise e

        # create the path and add it to the handler
        log_path = os.path.join(log_root_dir, log_file_name + ".log")
        logger_fh = logging.FileHandler(log_path)

        #   set the formatter and add it via addHandler()
        formatter =  logging.Formatter('[%(asctime)s] %(levelname)s:\t%(message)s', ymdhms)
        logger_fh.setFormatter(formatter)
        logger.addHandler(logger_fh)

    return logger


class AssetDict(dict):
    """ Creates a dictionary with additional attributes. """

    def __init__(self, d={}, attribs={}):
        """ Initialize with any dictionary and then use the 'attribs' kwarg as a
        dictionary of arbitry key/value pairs that will become attribs of the
        dictionary. """

        self.meta_attribs = attribs

        for k, v in self.meta_attribs.iteritems():
            if type(v) == str:
                exec """self.%s = "%s" """ % (k,v)
            else:
                exec "self.%s = %s" % (k,v)

        self.update(d)
        self.add_vars_to_dict()

    def add_vars_to_dict(self):
        """ Adds the arbitrary attribs of the dictionary to each asset in the dict
        as an __whatever__ value. """

        for d in self.keys():
            self[d]["handle"] = d
            for k, v in self.meta_attribs.iteritems():
                key = "__%s__" % k
                self[d][key] = v


def asset_object_to_json(asset):
    """ Takes one of our asset objects and coerces it to json, stripping it of
    internal-use attributes, logger objects, etc. that is not serializeable or
    relevant to an object retrieval. """


    for banned_attrib in ["logger", "assets"]:
        if hasattr(asset, banned_attrib):
            delattr(asset, banned_attrib)

    return json.dumps(asset.__dict__, default=json_util.default)



# decorators for logging
def error_log(func):
    """ This is a decorator that should decorate all functions where we're
    attempting to update or modify a user asset on behalf of an API user.
    This will wrap any function in a try/except, log and return exceptions
    or simply return True if everything works out OK. """

    logger = get_logger(log_name="error")
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
            return True
        except Exception as e:
            logger.exception(e)
            return e
    return wrapper

def log_route_error(func):
    """ Use this decorator to decorate route methods (i.e. modules defined in
    the routes/ module dir) and capture exceptions to the server.log file."""
    logger = get_logger(log_name="server")
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            logger.exception(e)
    return wrapper


# private exception classes

class WorldQueryError(Exception):
    """ Handler for asset-based errors. """

    def __init__(self, query=None, message="World query produced zero results!"):
        self.logger = get_logger()
        self.logger.exception(message)
        self.logger.error(query)
        Exception.__init__(self, message)


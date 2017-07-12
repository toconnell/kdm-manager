#!/usr/bin/python2.7



# general imports
from bson import json_util
from datetime import datetime, timedelta
from flask import Response, make_response, request, current_app
from functools import update_wrapper
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
recent_session_cutoff = datetime.now() - timedelta(hours=settings.get("application","recent_session_horizon"))
active_user_cutoff = datetime.now() - timedelta(minutes=settings.get("application","active_user_horizon"))


# generic http responses
http_200 = Response(response="OK!", status=200)
http_400 = Response(response="Bad Request!", status=400)
http_401 = Response(response="Authorization required", status=401)
http_404 = Response(response="Resource not found", status=404)
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

def list_to_pretty_string(l):
    """ Takes a list of strings and makes it into a single, pretty string
    with commas, the word 'and' and that type of shit. """

    l = list(l)

    if len(l) == 1:
        return l[0]

    return " and ".join([", ".join(l[:-1]), l[-1]])


def sort_timeline(timeline):
    """ Returns a sorted timeline. """
    sorting_hat = {}
    for ly in timeline:
        sorting_hat[int(ly["year"])] = ly
    return [sorting_hat[ly_key] for ly_key in sorted(sorting_hat.keys())]


def get_timeline_index_and_object(timeline,lantern_year):
    """ Input a timeline and a target ly; get the index of that year and the
    year (as a JSON object i.e. list of dicts) back.

    If it can't find a year, it adds it. """

    def get_ly():
        for t in timeline:
            if t["year"] == int(lantern_year):
                return timeline.index(t), t

    if get_ly() is None:
        timeline.append({"year": lantern_year})
        timeline = sort_timeline(timeline)
        return get_ly()
    else:
        return get_ly()




# general usage methods

def basic_logging():
    """ Executes logging.basicConfig() to catch logging from imported modules,
    i.e. to make sure we don't lose any logging. """

    logging.basicConfig(
        filename = os.path.join(settings.get("application","log_root_dir"), "server.log"),
        format = '[%(asctime)s] %(levelname)s:\t%(message)s',
        level = settings.get("server","log_level"),
    )

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
        log_root_dir = settings.get("application","log_root_dir")
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
        """ Adds the arbitrary attribs of the dictionary to each asset in the
        dict. """

        for d in self.keys():
            self[d]["handle"] = d
            for k, v in self.meta_attribs.iteritems():
                key = "%s" % k
                self[d][key] = v




# decorators for API


def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()


    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


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
        self.logger.error("Query was: %s" % query)
        Exception.__init__(self, message)


class InvalidUsage(Exception):
    """ Raise this type of exception at any point to return an HTTP response to
    the requester. Syntax goes like this:

        raise utils.InvalidUsage("Message", status_code=400)

    Do this whenever the requester's param keys/values are not up to snuff, etc.
    """

    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
           self.status_code = status_code
           self.payload = payload

    def to_dict(self):
       rv = dict(self.payload or ())
       rv['message'] = self.message
       return rv

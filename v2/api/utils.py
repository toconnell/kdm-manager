#!/usr/bin/python2.7

# general imports
from bson import json_util
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import email
from email.header import Header as email_Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Response, make_response, request, current_app
from functools import update_wrapper
import json
import logging
import os
from pymongo import MongoClient
import smtplib
import socket
from string import Template
import sys
import time
import traceback

# project-specific imports
import settings


# random, one-off helpers in the main namespace

mdb = MongoClient()[settings.get("api","mdb")]

ymd = "%Y-%m-%d"
hms = "%H:%M:%S"
ymdhms = "%Y-%m-%d %H:%M:%S"
thirty_days_ago = datetime.now() - timedelta(days=30)


# generic http responses
http_200 = Response(response="OK!", status=200)
http_400 = Response(response="Bad Request!", status=400)
http_401 = Response(response="Authorization required", status=401)
http_404 = Response(response="Resource not found", status=404)
http_405 = Response(response="Method not allowed", status=405)
http_422 = Response(response="Missing argument, parameter or value", status=422)
http_500 = Response(response="Server explosion! The server erupts in a shower of gore, killing your request instantly. All other servers are so disturbed that they lose 1 survival.", status=500)
http_501 = Response(response="Not implemented in this release", status=501)




# laziness and DRYness methods

def cli_dump(key, spacer, value):
    """ Returns a command line interface pretty string for use in admin scripts
    and other things that dump strings to CLI over STDOUT. """

    spaces = spacer - len(key)

    output = "%s:" % key
    output += " " * spaces
    output += "%s" % value

    print(output)


def decompose_name_string(name):
    """ Accepts a name string and returns a list of possible versions of it. """

    output = []

    name_list = name.split(" ")
    for i in range(len(name_list) + 1) :
        output.append(" ".join(name_list[:i]))

    return output


def html_file_to_template(rel_path):
    """ Turns an HTML file into a string.Template object. """
    tmp_file = os.path.join(settings.get("api","cwd"), rel_path)
    return Template(file(tmp_file, "rb").read())


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


def get_time_elapsed_since(start_time, units=None, round_seconds=True):
    """ Use a datetime object as the first arg and a 'units' kwarg value of
    either 'minutes' or 'hours' to find out how long it has been since that
    time (in your preferred units).

    Use 'age' as the value for 'units' to get a human-readable string
    representing the elapsed time.
    """

    delta = (datetime.now() - start_time)
    days = delta.days
    years = relativedelta(datetime.now(), start_time).years
    offset = delta.total_seconds()

    offset_hours = offset / 3600.0

    if round_seconds:
        offset = int(offset)

    if units == "seconds":
        return offset
    elif units == "hours":
        return int(offset_hours)
    elif units == "minutes":
        return int(delta.seconds / 60)
    elif units == "days":
        return delta.days
    elif units == "years":
        return years
    elif units == "years_and_days":
        for y in range(years):
           days -= 365
        year_word = "year"
        if years >= 2:
           year_word = "years"
        return "%s %s and %s days" % (years, year_word, days)
    elif units == "age":
        if offset == 1:
            return 'one second'
        elif offset < 60:
           return '%s seconds' % offset
        elif offset == 60:
            return 'one minute'
        elif offset < 3600:
           return "%s minutes" % get_time_elapsed_since(start_time, "minutes")
        elif offset == 3600:
            return 'one hour'
        elif offset < 86400:
           return "%s hours" % get_time_elapsed_since(start_time, "hours")
        elif offset < 172800:
           return "one day"
        elif delta.days < 365:
           return "%s days" % get_time_elapsed_since(start_time, "days")
        elif delta.days == 365:
           return "one year"
        elif delta.days > 365:
           return get_time_elapsed_since(start_time, 'years_and_days')

    return delta


def list_to_pretty_string(l, quote_char=False):
    """ Takes a list of strings and makes it into a single, pretty string
    with commas, the word 'and' and that type of shit. """

    l = list(l)

    if len(l) == 0:
        return None
    elif len(l) == 1:
        if quote_char:
            return "%s%s%s" % (quote_char, l[0], quote_char)
        else:
            return l[0]

    if quote_char:
        l = [str("%s%s%s" % (quote_char,i,quote_char)) for i in l]
    else:
        l = [str(i) for i in l]

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





# API response/request helpers

class noUser:
    def __init__(self):
        self.login="admin@kdm-manager.com"
        self._id = "666"

#
#   performance monitoring
#

def record_response_time(r):
    """ Accepts a request object, uses it to log the request and its response
    time to mdb. Prunes old lines. """
    duration = request.stop_time - r.start_time

    url_list = request.url.split(request.url_root)[1].split("/")
    for i in url_list:
        try:
            ObjectId(i)
            url_list.remove(i)
        except:
            pass
    url = "/".join(url_list)

    mdb.api_response_times.insert({
       "created_on": datetime.now(),
       "url": url,
       "method": request.method,
       "time": duration.total_seconds()
    })

    if request.metering:
        request.logger = get_logger()
        request.logger.debug('[%s] %s response in %s ' % (request.method, request.url, duration))

    old_record_query = {"created_on": {"$lt": (datetime.now() - timedelta(days=7))}}
    removed_records = mdb.api_response_times.remove(old_record_query)


#
#   stub dictionary for creating the meta element of API returns
#

api_meta = {
    "meta": {
        "webapp": {
            "release": settings.get('application','webapp_release'),
            "age": get_time_elapsed_since(datetime.strptime('2015-11-29', '%Y-%m-%d'), units='age'),
        },
        "api": {
            "version": settings.get("api","version"),
            "hostname": socket.gethostname(),
            "mdb_name": settings.get("api","mdb"),
        },
        "admins": list(mdb.users.find({"admin": {"$exists": True}}).sort('login')),
        "object": {},
    },
}




# mail session object

class mailSession:
    """ Initialize one of these to authenticate via SMTP and send emails. This
    is a port from the legacy app."""

    def __init__(self):
        self.logger = get_logger()
        p_settings = settings.Settings('private')
        self.smtp_host = p_settings.get("smtp","host")
        self.smtp_user = p_settings.get("smtp","name")
        self.smtp_pass = p_settings.get("smtp","pass")
        self.sender_name = p_settings.get("smtp","name_pretty")
        self.no_reply = p_settings.get("smtp","no-reply")
        self.connect()

    def connect(self):
        self.server = smtplib.SMTP(self.smtp_host, 587)
        self.server.starttls()
        self.server.login(self.smtp_user, self.smtp_pass)
        self.logger.debug("SMTP Authentication successful for %s (%s)." % (self.smtp_user, self.smtp_host))
        time.sleep(0.75)


    def send(self, reply_to=None, recipients=["toconnell@tyrannybelle.com"], html_msg='This is a <b>test</b> message!', subject="KDM-Manager!"):
        """ Generic Emailer. Accepts a list of 'recipients', a 'msg' string and a
        sender name (leave undefinied to use admin@kdm-manager.com). """

        author = email.utils.formataddr((str(email_Header(self.sender_name, 'utf-8')), self.no_reply))
        msg = MIMEMultipart('alternative')
        msg['From'] = author
        msg['Subject'] = subject
        msg['To'] = recipients[0]

        if reply_to is not None:
            msg.add_header('reply-to', reply_to)

        msg.attach(MIMEText(html_msg,'html'))

        self.server.sendmail(self.no_reply, recipients, msg.as_string())
        self.server.quit()
        self.logger.debug("Email sent successfully!")



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


def get_local_ip():
    """ Uses the 8.8.8.8 trick to get the localhost IP address. """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def get_application_url(strip_http=False):
    """ Determines the URL to use for API operations based on some socket
    operations and settings from the settings.cfg. Defaults to using localhost
    on the default API port defined in settings.cfg. """

    fqdn = socket.getfqdn()
    if fqdn == settings.get("api","prod_fqdn"):
        output = 'http://kdm-manager.com'
    else:
        output = "http://%s" % (get_local_ip())

    if strip_http:
        return output[7:]
    else:
        return output


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



#
# exception auto-mailer
#

def email_exception(exception):
    """ This is called by the main Flask errorhandler() decorator in api.py
    when we have an unhandled exception at any point of responding to a request.

    This prevents user-facing (or Khoa-facing) failures from being silently
    swallowed. """

    # first, log it
    logger = get_logger(log_level='DEBUG', log_name='error')
    logger.exception(exception)

    if not hasattr(request, 'User'):
        request.User = noUser()

    # finally, prepare the message template and the traceback for emailing
#    tmp_file = os.path.join(settings.get("api","cwd"), "html/exception_alert.html")
#    msg = Template(file(tmp_file, "rb").read())
    msg = html_file_to_template("html/exception_alert.html")
    tb = traceback.format_exc().replace("    ","&ensp;").replace("\n","<br/>")

    # do it
    s = msg.safe_substitute(traceback=tb, user_login=request.User.login, user_oid=request.User._id, datetime=datetime.now(), r_method=request.method, r_url=request.url, r_json=request.json)
    e = mailSession()
    e.send(subject="API Error! [%s]" % socket.getfqdn(), recipients=['toconnell@tyrannybelle.com'], html_msg=s)



#
#   special exception classes
#

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

    def __init__(self, message, status_code=400, payload=None):
        Exception.__init__(self)
        self.logger = get_logger(log_name='error')
        self.message = message
        if status_code is not None:
           self.status_code = status_code
           self.payload = payload
        self.alert()

    def alert(self):
        """ Records the error and alerts the admins. TBD. """
        self.logger.error("%s - %s" % (self.status_code, self.message))
#        e = utils.mailSession()
#        e.send(recipients=[user_login]i, html_msg=self.message)

    def to_dict(self):
       rv = dict(self.payload or ())
       rv['message'] = self.message
       return Response(rv['message'], self.status_code)

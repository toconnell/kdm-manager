#!/usr/bin/env python

#   standard
import collections
from ConfigParser import SafeConfigParser
from datetime import datetime, timedelta
from dateutil.parser import parse as dateutil_parse
import email
from email.header import Header as email_Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import logging
import os
from pymongo import MongoClient
import smtplib
import sys
import time
from urllib import urlopen
from user_agents import parse as ua_parse


# function to get settings. This has to be up top.

def load_settings(settings_type=None):
    """ Creates a settings object from settings.cfg in the application root dir.
    This func has to be at the top of this module, since everything below here
    (basically) uses it. """

    config = SafeConfigParser()

    if settings_type == "private":
        filename = "settings_private.cfg"
    else:
        filename = "settings.cfg"

    config.readfp(open(filename))
    config.file_path = os.path.abspath(filename)
    return config


#
#   General purpose helpers and references
#

settings = load_settings()
mdb = MongoClient()[settings.get("application","mdb")]
ymd = "%Y-%m-%d"
hms = "%H:%M:%S"
ymdhms = "%Y-%m-%d %H:%M:%S"
thirty_days_ago = datetime.now() - timedelta(days=30)
recent_session_cutoff = datetime.now() - timedelta(hours=12)
admin_session = {"_id": 0, "login": "ADMINISTRATOR", "User": {"_id": 0}}
forbidden_names = ["test","Test","TEST","Unknown","UNKNOWN","Anonymous","anonymous"]

#
#  application helper functions
#

def u_to_str(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(u_to_str, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(u_to_str, data))
    else:
        return data

def to_handle(s):
    return s.lower().replace(" ","_")

def get_percentage(part, whole):
    if whole == 0:
        return 0
    else:
        return 100 * round(float(part)/float(whole), 2)

def days_hours_minutes(td):
    return abs(td.days), td.seconds//3600, (td.seconds//60)%60


def stack_list(raw_list):
    """ Takes a list and 'stacks' duplicative members of that list, returning a
    list of strings with counts. """

    count_dict = {}
    for i in raw_list:
        if not i in count_dict.keys():
             count_dict[i] = 1
        else:
             count_dict[i] += 1

    stacked_list = []
    for i in sorted(count_dict.keys()):
        if count_dict[i] == 1:
            stacked_list.append(i)
        else:
            stacked_list.append("%s (x%s)" % (i, count_dict[i]))

    return stacked_list


#  sysadmin helper functions



def get_user_agent():
    """ Returns a user-agents object if we can get a user agent. Otherwise,
    returns None. """

    if "HTTP_USER_AGENT" not in os.environ:
        return None
    else:
        return ua_parse(os.environ["HTTP_USER_AGENT"])


def get_logger(log_level="INFO", log_name=False):
    """ Creates a generic logger at the specified log level."""

    settings = load_settings()
    if settings.getboolean("application","DEBUG"):
        log_level="DEBUG"

    #   initialize a generic logger
    logger = logging.getLogger(__name__)

    if not len(logger.handlers):    # if it's not already open, open it
        exec 'log_level_obj = logging.%s' % log_level
        logger.setLevel(log_level_obj)

        #   set the logger's name and path
        log_file_name = log_name
        if not log_file_name:
            log_file_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]

        log_root_dir = settings.get("application","log_dir")
        if not os.path.isdir(log_root_dir):
            e = Exception("Logging root dir '%s' does not exist!" % log_root_dir)
            raise e

        log_path = os.path.join(log_root_dir, log_file_name + ".log")
        logger_fh = logging.FileHandler(log_path)

        #   set the formatter and add it via addHandler()
        formatter =  logging.Formatter('[%(asctime)s] %(levelname)s:\t%(message)s',"%Y-%m-%d %H:%M:%S")
        logger_fh.setFormatter(formatter)
        logger.addHandler(logger_fh)

    return logger


class mailSession:
    """ Initialize one of these to authenticate via SMTP and send emails. """

    def __init__(self):
        self.logger = get_logger()
        settings = load_settings("private")
        self.smtp_host = settings.get("smtp","host")
        self.smtp_user = settings.get("smtp","name")
        self.smtp_pass = settings.get("smtp","pass")
        self.sender_name = settings.get("smtp","name_pretty")
        self.no_reply = settings.get("smtp","no-reply")
        self.connect()


    def connect(self):
        self.server = smtplib.SMTP(self.smtp_host, 587)
        self.server.set_debuglevel(1)
        self.server.starttls()
        self.server.login(self.smtp_user, self.smtp_pass)
        self.logger.debug("SMTP Authentication successful for %s (%s)." % (self.smtp_user, self.smtp_host))
        time.sleep(0.75)


    def send(self, recipients=["toconnell@tyrannybelle.com"], html_msg='This is a <b>test</b> message!', subject="KDM-Manager!"):
        """ Generic Emailer. Accepts a list of 'recipients', a 'msg' string and a
        sender name (leave undefinied to use admin@kdm-manager.com). """

        author = email.utils.formataddr((str(email_Header(self.sender_name, 'utf-8')), self.no_reply))
        msg = MIMEMultipart('alternative')
        msg['From'] = author
        msg['Subject'] = subject
        msg['To'] = recipients[0]
        msg.attach(MIMEText(html_msg,'html'))

        self.server.sendmail(self.no_reply, recipients, msg.as_string())
        self.server.quit()
        self.logger.debug("Email sent successfully!")


def get_latest_posts():
    try:
        response = urlopen('https://www.googleapis.com/blogger/v3/blogs/3322385743551419703/posts?key=AIzaSyBAms6po9Dc82iTeRzDXMYI-bw81ufIu-0').read()
        return json.loads(response)
    except Exception as e:
        return {"exception": e}

def get_latest_change_log():
    """ Gets the latest post to the blog. """
    posts = get_latest_posts()
    if "items" in posts.keys():
        for post in posts["items"]:
            if "labels" in post.keys() and "Change Logs" in post["labels"] and "V1" in post["labels"]:
                return post
    else:
        return {
            'content': None,
            'kind': None,
            'labels': None,
            'title': None,
            'url': None,
            'author': None,
            'updated': None,
            'replies': None,
            'blog': None,
            'etag': None,
            'published': None,
            'id': None,
            'selfLink': None,
        }

def get_latest_update_string():
    """ Returns a summary string about the latest update. """
    posts = get_latest_posts()
    if "items" in posts.keys():
        try:
            for post in posts["items"]:
                if "labels" in post.keys() and "Change Logs" in post["labels"]:
                    d = dateutil_parse(post["published"])
                    return "Version %s released on %s, %s." % (settings.get("application","version"), d.strftime("%A"), d.strftime(ymd))
        except Exception as e:
            return e
    else:
        return None


if __name__ == "__main__":
    print("Starting unit tests...")
    settings = load_settings()
    if not settings:
        raise Exception("Settings file could not be loaded!")
    else:
        print(" Settings file '%s' loaded!" % settings.file_path)
    logger = get_logger()
    if not logger:
        raise Exception("Logger could not be initialized!")
    else:
        print(" Logger initialized!")

    logger.info("Unit tests passed!")

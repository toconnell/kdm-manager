#!/usr/bin/python2.7


# general imports
from flask import Flask, send_file, request
import logging
from logging.handlers import RotatingFileHandler
import os

# application-specific imports
import settings
import utils

# initialize settings and utils
S = settings.Settings()
U = utils.Utilities()

# create the flask app with settings/utils info
application = Flask(__name__)
application.config.update(
    DEBUG = S.get("server","DEBUG"),
    TESTING = S.get("server","DEBUG"),
)
application.logger.addHandler(U.get_logger(log_name="server"))



#
#   Routes start here! Settings object initialized above...
#

# default route - landing page, vanity URL stuff
@application.route("/")
def index():
    application.logger.debug("index view")
    return send_file("templates/index.html")


# file-spoofing example
@application.route("/settings.json")
def settings_json():
    return send_file(S.json_file(), attachment_filename="settings.json", as_attachment=True)



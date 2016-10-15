#!/usr/bin/python2.7


# general imports
from flask import Flask, send_file, request
import logging
from logging.handlers import RotatingFileHandler
import os

# application-specific imports
import settings


# initialize settings and pass critical params to the flask app
S = settings.Settings()
log_file_path = os.path.join(S.get("api","log_dir"), "server.log")

handler = RotatingFileHandler(log_file_path, maxBytes=10000, backupCount=1)
handler.setLevel(S.get("server","log_level"))
application = Flask(__name__)
application.config.update(
    DEBUG = S.get("server","DEBUG"),
    TESTING = S.get("server","DEBUG"),
)
application.logger.addHandler(handler)



#
#   Routes start here! Settings object initialized above...
#

# default route - landing page, vanity URL stuff
@application.route("/")
def index():
    application.logger.debug("success")
    return send_file("templates/index.html")


# file-spoofing example
@application.route("/settings.json")
def settings_json():
    return send_file(S.json_file(), attachment_filename="settings.json", as_attachment=True)



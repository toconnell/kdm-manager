#!/usr/bin/python2.7


# general imports
from bson import json_util
from flask import Flask, send_file, request, Response
import json
import logging
from logging.handlers import RotatingFileHandler
import os

# application-specific imports
import settings
import utils
import world


# create the flask app with settings/utils info
application = Flask(__name__)
application.config.update(
    DEBUG = settings.get("server","DEBUG"),
    TESTING = settings.get("server","DEBUG"),
)
application.logger.addHandler(utils.get_logger(log_name="server"))



#
#   Routes start here! Settings object initialized above...
#

# default route - landing page, vanity URL stuff
@application.route("/")
def index():
    return send_file("templates/index.html")

@application.route("/world")
def world_json():
    W = world.World()
    D = world.WorldDaemon()
    d = {"world_daemon": D.dump_status("dict")}
    d.update(W.list("dict"))
    j = json.dumps(d, default=json_util.default)
    response = Response(response=j, status=200, mimetype="application/json")
    return response

# file-spoofing example
@application.route("/settings.json")
def settings_json():
    return send_file(S.json_file(), attachment_filename="settings.json", as_attachment=True)



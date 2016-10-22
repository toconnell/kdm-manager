#!/usr/bin/python2.7


# general imports
from bson import json_util
from flask import Flask, send_file, request, Response
import json
import logging
from logging.handlers import RotatingFileHandler
import os

# application-specific imports
from models import monster
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

@application.route("/monster")
def monster_json():
    m_handle = request.args.get("handle", None)
    m_name = request.args.get("name", None)

    four_oh_four = Response(response=None, status=404, mimetype="application/json")
    try:
        if m_handle is not None:
            M = monster.Monster(handle=m_handle)
        elif m_name is not None:
            M = monster.Monster(name=m_name)
        else:
            return four_oh_four
    except:
        return four_oh_four

    r = utils.asset_object_to_json(M)
    return Response(response=r, status=2, mimetype="application/json")

# file-spoofing example
@application.route("/settings.json")
def settings_json():
    S = settings.Settings()
    return send_file(S.json_file(), attachment_filename="settings.json", as_attachment=True)



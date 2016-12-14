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
import world
import utils

# models
from models import settlements, survivors

# routes
from routes import monster, cursed_items

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

@application.route("/cursed_items", methods=["GET","POST"])
def cursed_items_json():
    if request.method == "GET":
        return cursed_items.GET_all()
    else:
        if not utils.authorize(request):
            return utils.http_401
        return cursed_items.POST_available()

@application.route("/settlement/get/<settlement_id>", methods=["POST","GET"])
@utils.crossdomain(origin='*')
def get_settlement(settlement_id):
    """ Dumps a serialized settlement, to include all assets, etc."""
    S = settlements.Settlement(_id=settlement_id)
    return S.http_response()

@application.route("/survivor/get/<survivor_id>", methods=["POST"])
def get_survivor(survivor_id):
    """ Dumps a survivor's MDB document. """
    S = survivors.Survivor(_id=survivor_id)
    return S.http_response()

#@application.route("/survivor/update/<survivor_id>", methods=["POST"])
#def update_survivor(survivor_id):
#    """ You need to be authorized to do this, i.e. post a key in the JSON. """
#
#    if not utils.authorize(request):
#        return utils.http_401
#    S = survivor.init_survivor(survivor_id)
#    if type(S) == Response:
#        return S
#    return survivor.POST_to_mdb(S)



@application.route("/monster")
def monster_json():
    return monster.GET_json()

# file-spoofing example
@application.route("/settings.json")
def settings_json():
    S = settings.Settings()
    return send_file(S.json_file(), attachment_filename="settings.json", as_attachment=True)

if __name__ == "__main__":
    application.run(port=8013, host="0.0.0.0")

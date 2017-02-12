#!/usr/bin/python2.7


# general imports
from bson.objectid import ObjectId
from bson import json_util

from flask import Flask, send_file, request, Response, send_from_directory
import flask_jwt
import flask_jwt_extended

import json
import os
from pprint import pprint

# application-specific imports
import request_broker
import settings
import world
import utils

# models
from models import users, settlements

utils.basic_logging()

# create the flask app with settings/utils info
application = Flask(__name__)
application.config.update(
    DEBUG = settings.get("server","DEBUG"),
    TESTING = settings.get("server","DEBUG"),
)
application.logger.addHandler(utils.get_logger(log_name="server"))
application.config['SECRET_KEY'] = settings.get("api","secret_key","private")

#   Javascript Web Token!
jwt = flask_jwt_extended.JWTManager(application)
#jwt = flask_jwt.JWT(application, users.authenticate, users.jwt_identity_handler)


#
#   Routes start here! Settings object initialized above...
#


# default route - landing page, vanity URL stuff
@application.route("/")
def index():
    return send_file("templates/index.html")

# static css and js routes
@application.route('/static/<sub_dir>/<path:path>')
def route_to_static(path, sub_dir):
    return send_from_directory('static/%s' % sub_dir, path)


#
#   public routes
#

@application.route("/monster", methods=["GET","POST"])
def monster_json():
    return request_broker.get_game_asset("monster")

@application.route("/campaign", methods=["POST"])
def campaign_json():
    return request_broker.get_game_asset("campaign")

@application.route("/settings.json")
def get_settings_json():
    S = settings.Settings()
    return send_file(S.json_file(), attachment_filename="settings.json", as_attachment=True)

@application.route("/settings")
def get_settings():
    S = settings.Settings()
    return Response(
        response=S.json_file(),
        status=200,
        mimetype="application/json",
    )

@application.route("/world")
@utils.crossdomain(origin=['*'],headers='Content-Type')
def world_json():
    W = world.World()
    D = world.WorldDaemon()
    d = {"world_daemon": D.dump_status("dict")}
    d.update(W.list("dict"))
    j = json.dumps(d, default=json_util.default)
    response = Response(response=j, status=200, mimetype="application/json")
    return response

@application.route("/new_settlement")
@utils.crossdomain(origin=['*'],headers='Content-Type')
def get_new_settlement_assets():
    S = settlements.Assets()
    return Response(
        response=json.dumps(S.serialize()),
        status=200,
        mimetype="application/json"
    )


#
#   /login (not to be confused with the built-in /auth route)
#
@application.route("/login", methods=["POST","OPTIONS"])
@utils.crossdomain(origin=['*'],headers=['Content-Type','Authorization'])
def get_token():
    """ Tries to get credentials from the request headers. Fails verbosely."""

    U = users.authenticate(request.json.get("username",None), request.json.get("password",None))
    if U is None:
        return utils.http_401
    tok = {'access_token': flask_jwt_extended.create_access_token(identity=U.serialize())}
    return Response(response=json.dumps(tok), status=200, mimetype="application/json")


#
#   private routes
#

@application.route('/protected',methods=["GET","POST","OPTIONS"])
@flask_jwt.jwt_required()
def protected():
    return Response(response=flask_jwt.current_identity, status=200, mimetype="application/json")


@application.route("/<collection>/<action>/<asset_id>", methods=["GET","POST","OPTIONS"])
@utils.crossdomain(origin=['*'],headers='Content-Type')
#@cross_origin(headers=['Content-Type','Authorization'])
#@flask_jwt.jwt_required()
def get_settlement(collection, action, asset_id):
    """ This is our major method for retrieving and updating settlements. """
    asset_object = request_broker.get_user_asset(collection, asset_id)
    if type(asset_object) == Response:
        return asset_object
    return asset_object.request_response(action)


if __name__ == "__main__":
    application.run(port=8013, host="0.0.0.0")

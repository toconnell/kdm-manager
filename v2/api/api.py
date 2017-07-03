#!/usr/bin/python2.7

# general imports
from bson.objectid import ObjectId
from bson import json_util

from flask import Flask, send_file, request, Response, send_from_directory, jsonify
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


# general logging
#utils.basic_logging()


# create the flask app with settings/utils info
application = Flask(__name__)
application.config.update(
    DEBUG = settings.get("server","DEBUG"),
    TESTING = settings.get("server","DEBUG"),
)
application.logger.addHandler(utils.get_logger(log_name="server"))
application.config['SECRET_KEY'] = settings.get("api","secret_key","private")


#   Javascript Web Token! DO NOT import jwt (i.e. pyjwt) here!
jwt = flask_jwt_extended.JWTManager(application)



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
def get_token(check_pw=True, user_id=False):
    """ Tries to get credentials from the request headers. Fails verbosely."""

    U = None
    if check_pw:
        U = users.authenticate(request.json.get("username",None), request.json.get("password",None))
    else:
        U = users.User(_id=user_id)

    if U is None:
        return utils.http_401

    tok = {
        'access_token': flask_jwt_extended.create_access_token(identity=U.jsonize()),
        "_id": str(U.user["_id"]),
    }
    return Response(response=json.dumps(tok), status=200, mimetype="application/json")


#
#   private routes
#

@application.route("/authorization/<action>", methods=["POST","GET"])
@utils.crossdomain(origin=['*'],headers=['Content-Type','Authorization'])
def refresh_auth(action):

    if not "Authorization" in request.headers:
        return utils.http_401
    else:
        auth = request.headers["Authorization"]

    if action == "refresh":
        user = users.refresh_authorization(auth)
        if user is not None:
            return get_token(check_pw=False, user_id=user["_id"])
        else:
            return utils.http_401
    elif action == "check":
        return users.check_authorization(auth)
    else:
        return utils.http_402


@application.route("/new/<asset_type>", methods=["POST"])
@utils.crossdomain(origin=['*'],headers='Content-Type')
def new_asset(asset_type):
    """ Uses the 'Authorization' block of the header and POSTed params to create
    a new settlement. """
    request.logger = utils.get_logger()
    request.User = users.token_to_object(request)
    if isinstance(request.User, users.User):
        return request_broker.new_user_asset(asset_type)
    else:
        return utils.http_401 #unauthorized


@application.route("/<collection>/<action>/<asset_id>", methods=["GET","POST","OPTIONS"])
@utils.crossdomain(origin=['*'],headers=['Content-Type','Authorization'])
#@flask_jwt.jwt_required()
def collection_action(collection, action, asset_id):
    """ This is our major method for retrieving and updating settlements. """


    #
    #   This is temporary! For the next few releases, auth is optional and will
    #   only truly bomb out the request if the password in the cookie's JWT is
    #   incorrect.
    #

    if not "Authorization" in request.headers:
        application.logger.warn("Performing '%s' on '%s' object '%s' without authorization!" % (action, collection, asset_id))
        application.logger.warn("Request URL -> %s" % request.url)
    else:
        u = users.refresh_authorization(request.headers["Authorization"])
        request.User = users.User(_id=u["_id"])
        if not isinstance(request.User, users.User):
            return utils.http_401 #unauthorized

    asset_object = request_broker.get_user_asset(collection, asset_id)
    if type(asset_object) == Response:
        return asset_object
    return asset_object.request_response(action)


#
#   special/bogus/meta routes
#

@application.errorhandler(utils.InvalidUsage)
@utils.crossdomain(origin=['*'])
def return_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response



if __name__ == "__main__":
    application.run(port=8013, host="0.0.0.0")

#!/usr/bin/python2.7

# general imports
from bson.objectid import ObjectId
from bson import json_util
from datetime import datetime

from flask import Flask, send_file, render_template, request, Response, send_from_directory, jsonify
from flask_httpauth import HTTPBasicAuth
basicAuth = HTTPBasicAuth()
import flask_jwt
import flask_jwt_extended

import json
import os
from pprint import pprint
import socket
import ssl

# application-specific imports
import request_broker
import settings
import world
import utils

# models
from models import users, settlements, names


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
    return send_file("html/index.html")

# static css and js routes
@application.route('/static/<sub_dir>/<path:path>')
def route_to_static(path, sub_dir):
    return send_from_directory('static/%s' % sub_dir, path)

@application.route("/favicon.ico")
def favicon():
    return send_file("static/media/images/the_watcher.png")


#
#   public routes
#

# asset lookups
@application.route("/game_asset/<asset_collection>", methods=["GET","POST","OPTIONS"])
@utils.crossdomain(origin=['*'],headers=['Authorization','Content-Type','Access-Control-Allow-Origin'])
def lookup_asset(asset_collection):
    """ Looks up game asset collection assets. Or, if you GET it, dumps the whole
    asset collection object """
    return request_broker.get_game_asset(asset_collection)

# deprecation warnings: maintain until 2018-03-10
@application.route("/monster", methods=["GET","POST"])
def lookup_monster():
    return Response(response="This endpoint is deprecated! Use /game_asset/monster instead.", status=410)

@application.route("/campaign", methods=["GET","POST"])
def lookup_campaign():
    return Response(response="This endpoint is deprecated! Use /game_asset/campaign instead.", status=410)

@application.route("/expansion", methods=["GET","POST"])
def lookup_expansion():
    return Response(response="This endpoint is deprecated! Use /game_asset/expansion instead.", status=410)

@application.route("/gear", methods=["GET","POST"])
def lookup_gear():
    return Response(response="This endpoint is deprecated! Use /game_asset/gear instead.", status=410)


# world
@application.route("/world")
@utils.crossdomain(origin=['*'],headers='Content-Type')
def world_json():
    W = world.World()
    D = world.WorldDaemon()
    d = {"world_daemon": D.dump_status(dict)}
    d.update(W.list(dict))
    j = json.dumps(d, default=json_util.default)
    response = Response(response=j, status=200, mimetype="application/json")
    return response

# application junk
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

# ui/ux helpers
@application.route("/new_settlement")
@utils.crossdomain(origin=['*'],headers='Content-Type')
def get_new_settlement_assets():
    S = settlements.Assets()
    return Response(
        response=json.dumps(S.serialize(), default=json_util.default),
        status=200,
        mimetype="application/json"
    )

@application.route("/get_random_names/<count>")
@utils.crossdomain(origin=['*'],headers='Content-Type')
def get_random_names(count):
    N = names.Assets()
    return Response(
        response=json.dumps(N.get_random_names(int(count)), default=json_util.default),
        status=200,
        mimetype="application/json"
    )


#
#   /login (not to be confused with the built-in /auth route)
#
@application.route("/login", methods=["POST","OPTIONS"])
@utils.crossdomain(origin=['*'],headers=['Content-Type','Authorization','Access-Control-Allow-Origin'])
def get_token(check_pw=True, user_id=False):
    """ Tries to get credentials from the request headers. Fails verbosely."""

    U = None
    if check_pw:
        if request.json is None:
            return Response(response="JSON payload missing from /login request!", status=422)
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

@application.route("/reset_password/<action>", methods=["POST","OPTIONS"])
@utils.crossdomain(origin=['*'],headers='Content-Type')
def reset_password(action):

    if action == 'request_code':
        return users.initiate_password_reset()
    elif action == 'reset':
        return users.reset_password()
    return Response(response="'%s' is not a valid action for this route." % action, status=422)



#
#   private routes - past here, you've got to authenticate
#

@application.route("/authorization/<action>", methods=["POST","GET","OPTIONS"])
@utils.crossdomain(origin=['*'],headers=['Content-Type','Authorization','Access-Control-Allow-Origin'])
def refresh_auth(action):

    if not "Authorization" in request.headers:
        return utils.http_401
    else:
        auth = request.headers["Authorization"]

    if action == "refresh":
        if request.method == "GET":
            return utils.http_402
        user = users.refresh_authorization(auth)
        if user is not None:
            return get_token(check_pw=False, user_id=user["_id"])
        else:
            return utils.http_401
    elif action == "check":
        return users.check_authorization(auth)
    else:
        return utils.http_402



@application.route("/new/<asset_type>", methods=["POST", "OPTIONS"])
@utils.crossdomain(origin=['*'],headers=['Authorization','Content-Type','Access-Control-Allow-Origin'])
def new_asset(asset_type):
    """ Uses the 'Authorization' block of the header and POSTed params to create
    a new settlement. """

    # first, check to see if this is a request to make a new user. If it is, we
    #   don't need to try to pull the user from the token b/c it doesn't exist
    #   yet, obvi. Instead, initialize a user obj w/ no _id to call User.new().
    if asset_type == 'user':
        U = users.User()
        output = U.serialize('create_new')
        output["Authorization"] = {
           'access_token': flask_jwt_extended.create_access_token(identity=U.jsonize()),
           "_id": str(U.user["_id"]),
        }
        return Response(response=json.dumps(output, default=json_util.default), status=200, mimetype="application/json")

    request.collection = asset_type
    request.User = users.token_to_object(request, strict=False)
    return request_broker.new_user_asset(asset_type)

@application.route("/<collection>/<action>/<asset_id>", methods=["GET","POST","OPTIONS"])
@utils.crossdomain(origin=['*'],headers=['Content-Type','Authorization','Access-Control-Allow-Origin'])
def collection_action(collection, action, asset_id):
    """ This is our major method for retrieving and updating settlements.

    This is also one of our so-called 'private' routes, so you can't do this
    stuff without an authenticated user.
    """

    if not ObjectId.is_valid(asset_id):
        return Response(response='The /%s/%s/ route requires a valid Object ID!' % (collection, action), status=400)

    # update the request object
    request.collection = collection
    request.action = action
    request.User = users.token_to_object(request, strict=False)     # temporarily non-strict

    asset_object = request_broker.get_user_asset(collection, asset_id)
    if type(asset_object) == Response:
        return asset_object
    return asset_object.request_response(action)




#                      
#      ADMIN PANEL     
#                      

@basicAuth.verify_password
def verify_password(username, password):
    request.User = users.authenticate(username, password)
    if request.User is None:
        return False
    elif request.User.user.get("admin", None) is None:
        msg = "Non-admin user %s attempted to access the admin panel!" % request.User.user["login"]
        application.logger.warn(msg)
        return False
    return True


@application.route("/admin")
@basicAuth.login_required
def panel():
    return send_file("html/admin/panel.html")


@application.route("/admin/get/<resource>", methods=["GET"])
#@basicAuth.login_required
def admin_view(resource):
    """ Retrieves admin panel resources as JSON. """
    return request_broker.get_admin_data(resource)


#
#   request logger (special route)
#

@application.before_request
def before_request():
    """ Updates the request with the 'start_time' attrib, which is used for
    performance monitoring. """
    request.start_time = datetime.now()
    request.metering = False
    if socket.getfqdn() != settings.get('api','prod_fqdn'):
        request.metering = True

@application.after_request
def after_request(response):
    """ Logs requests. """
    request.stop_time = datetime.now()
    utils.record_response_time(request)
    if response.status == 500:
        application.logger.error("fail")
    return response


#
#   special/bogus/meta routes
#
@application.errorhandler(Exception)
@utils.crossdomain(origin=['*'])
def general_exception(exception):
    utils.email_exception(exception)
    return Response(response=exception.message, status=500)


@application.errorhandler(utils.InvalidUsage)
@utils.crossdomain(origin=['*'])
def return_exception(error):
    return Response(response=error.message, status=error.status_code)



if __name__ == "__main__":
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(
        '/etc/letsencrypt/live/api.thewatcher.io/fullchain1.pem',
        '/etc/letsencrypt/live/api.thewatcher.io/privkey1.pem',
    )
    application.run(port=8013, host="0.0.0.0", debug = True, ssl_context=context)

"""

    No blueprints in this app! All the routes happen in this module.

    See also: request_broker.py for the rest of what goes on with dynamic
    request routing (becase we process endpoint components in certain types of
    requests.

"""


# stdlib
import json

# json/bson/oid
from bson.objectid import ObjectId
from bson import json_util

# flask!
from flask import send_file, request, Response, send_from_directory
import flask_jwt_extended

#
#   app imports
#
from api import application, docs, request_broker
from api.models import users, settlements, names

#   app module imports
import utils
import world



#
#   public API routes; these routes are not meant for use by applications or
#       users or anything like that. These are reference and index routes.
#

@application.route("/")
def index():
    """ The default return for accessing https://api.thewatcher.io (or
    equivalent endpoint), which gets you the API docs.

    This is NOT the same as the https://thewatcher.io return, which we handle
    in the webserver (nginx) config, because that's a webserver job for now.
    """
    return send_file("html/docs.html")


@application.route("/docs/<action>/<render_type>")
def render_documentation(action, render_type):
    """ These routes get you various representations of the contents of the
    docs module.

    For now, the supported 'action' list includes only the following::

        - get: this basically retrieves all extant documentation
        - get_sections: returns all sections defined in docs.sections

    The only supported 'render_type' is 'json' (case-insensitive).

    """

    response = utils.http_404           # default response

    render_type = render_type.upper()   # case-insensitive: json/JSON

    docs_object = docs.DocumentationObject()
    if action == 'get':
        if render_type == 'JSON':
            j = json.dumps(
                docs_object.render_as_json(),
                default=json_util.default
            )
            response = Response(
                response=j,
                status=200,
                mimetype="application/json"
            )
    elif action == 'get_documented_endpoints':
        output = docs_object.get_documented_endpoints()
        if render_type == 'JSON':
            response = Response(
                response=json.dumps(output),
                status=200,
                mimetype="application/json"
            )
        elif render_type == 'TEXT':
            response = Response(
                response="\n".join(output),
                status=200,
                mimetype="application/json"
            )
    elif action == 'get_sections':
        if render_type == 'JSON':
            j = json.dumps(
                docs_object.dump_sections(),
                default=json_util.default
            )
            response = Response(
                response=j,
                status=200,
                mimetype="application/json"
            )

    return response


@application.route("/settings.json")
def get_settings_json():
    """ Deprecated: 2019-01-13. """
    settings_object = utils.settings.Settings()
    return send_file(
        settings_object.json_file(),
        attachment_filename="settings.json",
        as_attachment=True
    )


@application.route("/settings")
def get_settings():
    """ Deprecated: 2019-01-13. """
    settings_object = utils.settings.Settings()
    return Response(
        response=settings_object.json_file(),
        status=200,
        mimetype="application/json",
    )



#
#   public routes for API users and webapps
#

@application.route("/stat", methods=["GET", "POST", "OPTIONS"])
@utils.crossdomain(origin=['*'])
def stat_api():
    """ Returns a dict of API information. """
    return Response(
        response=json.dumps(utils.api_meta, default=json_util.default),
        status=200,
        mimetype="application/json"
    )


@application.route(
    "/game_asset/<asset_collection>",
    methods=["GET", "POST", "OPTIONS"]
)
@utils.crossdomain(origin=['*'])
def lookup_asset(asset_collection):
    """ Looks up game asset collection assets. Or, if you GET it, dumps the whole
    asset collection object """
    return request_broker.get_game_asset(asset_collection)


@application.route("/new_settlement")
@utils.crossdomain(origin=['*'], headers='Content-Type')
def get_new_settlement_assets():
    """ Deprecated! This should be under /game_asset/settlement (or similar)."""
    settlement_assets = settlements.Assets()
    return Response(
        response=json.dumps(
            settlement_assets.serialize(),
            default=json_util.default
        ),
        status=299,
        mimetype="application/json"
    )


@application.route("/world")
@utils.crossdomain(origin=['*'], headers='Content-Type')
def world_json():
    """ Renders the world data (from the world module) in webapp-friendly JSON. """

    # 1.) initialize world/world daemon objects
    world_object = world.World()
    world_daemon = world.WorldDaemon()

    # 2.) create the output dictionary using both objects
    output = {"world_daemon": world_daemon.dump_status(dict)}
    output.update(world_object.list(dict))

    # 3.) render the response
    response = Response(
        response=json.dumps(output, default=json_util.default),
        status=200,
        mimetype="application/json"
    )
    return response


@application.route("/get_random_names/<count>")
@utils.crossdomain(origin=['*'], headers='Content-Type')
def get_random_names(count):
    """ Rapid-fire random name generator for FIRST names. """
    names_object = names.Assets()
    return Response(
        response=json.dumps(
            names_object.get_random_names(int(count)),
            default=json_util.default
        ),
        status=200,
        mimetype="application/json"
    )

@application.route("/get_random_surnames/<count>")
@utils.crossdomain(origin=['*'], headers='Content-Type')
def get_random_surnames(count):
    """ Rapid-fire random name generator for LAST names. """
    names_object = names.Assets()
    return Response(
        response=json.dumps(
            names_object.get_random_surnames(int(count)),
            default=json_util.default
        ),
        status=200,
        mimetype="application/json"
    )


#
#   /login (not to be confused with the built-in /auth route)
#
@application.route("/login", methods=["POST", "OPTIONS"])
@utils.crossdomain(origin=['*'])
def get_token(check_pw=True, user_id=False):
    """ Tries to get credentials from the request headers. Fails verbosely."""

    user_object = None

    if check_pw:
        if request.json is None:
            return Response(
                response="JSON payload missing from /login request!",
                status=422
            )
        user_object = users.authenticate(
            request.json.get("username", None),
            request.json.get("password", None)
        )
    else:
        user_object = users.User(_id=user_id)

    if user_object is None:
        return utils.http_401

    tok = {
        'access_token': flask_jwt_extended.create_access_token(identity=user_object.jsonize()),
        "_id": str(user_object.user["_id"]),
    }
    return Response(
        response=json.dumps(tok),
        status=200,
        mimetype="application/json"
    )


@application.route("/reset_password/<action>", methods=["POST", "OPTIONS"])
@utils.crossdomain(origin=['*'])
def reset_password(action):
    """ Routes for requesting and performing a password reset. """
    setattr(request, 'action', action)
    if action == 'request_code':
        return users.initiate_password_reset()
    elif action == 'reset':
        return users.reset_password()

    err_msg = "'%s' is not a valid action for this route." % action

    return Response(response=err_msg, status=422)



#
#   private routes - past here, you've got to authenticate
#

@application.route("/authorization/<action>", methods=["POST", "GET", "OPTIONS"])
@utils.crossdomain(origin=['*'])
def refresh_auth(action):
    """ Uses the 'Authorization' block in the request header to return a fresh
    token for a user. """

    # first, drop GETs trying to do a refresh: we don't play that shit
    if action == 'refresh' and request.method == 'GET':
        return utils.http_405

    setattr(request, 'action', action)

    if not "Authorization" in request.headers:
        return utils.http_401
    else:
        auth = request.headers["Authorization"]

    if action == "refresh":
        user = users.refresh_authorization(auth)
        if user is not None:
            return get_token(check_pw=False, user_id=user["_id"])
        return utils.http_401
    elif action == "check":
        return users.check_authorization(auth)

    # if we strike out, we're obviously not authorized:
    return utils.http_402


@application.route("/new/<asset_type>", methods=["POST", "OPTIONS"])
@utils.crossdomain(origin=['*'])
def new_asset(asset_type):
    """ Uses the 'Authorization' block of the header and POSTed params to create
    a new settlement. """

    setattr(request, 'action', 'new')

    # first, check to see if this is a request to make a new user. If it is, we
    #   don't need to try to pull the user from the token b/c it doesn't exist
    #   yet, obvi. Instead, initialize a user obj w/ no _id to call User.new().
    if asset_type == 'user':
        user_object = users.User()
        output = user_object.serialize('create_new')
        output["Authorization"] = {
            'access_token': flask_jwt_extended.create_access_token(identity=user_object.jsonize()),
            "_id": str(user_object.user["_id"]),
        }
        return Response(
            response=json.dumps(output, default=json_util.default),
            status=200,
            mimetype="application/json"
        )

    request.collection = asset_type
    request.User = users.token_to_object(request, strict=False)
    return request_broker.new_user_asset(asset_type)


@application.route(
    "/<collection>/<action>/<asset_id>",
    methods=["GET", "POST", "OPTIONS"]
)
@utils.crossdomain(origin=['*'])
def collection_action(collection, action, asset_id):
    """ This is our major method for retrieving and updating settlements.

    This is also one of our so-called 'private' routes, so you can't do this
    stuff without an authenticated user.
    """

    # fail anything without a valid OID right now, rather than spinning up a lot
    #   of machinery only to fail the request later
    if not ObjectId.is_valid(asset_id):
        err_msg = 'The /%s/%s/ route requires a valid Object ID!',
        return Response(
            response=err_msg % (collection, action),
            status=400
        )

    # update the request object
    request.collection = collection
    setattr(request, 'action', action)
    request.User = users.token_to_object(request, strict=False)     # temporarily non-strict

    asset_object = request_broker.get_user_asset(collection, asset_id)
    if isinstance(asset_object, Response):
        return asset_object

    return asset_object.request_response(action)


@application.route("/avatar/get/<image_oid>", methods=["GET"])
@utils.crossdomain(origin=['*'])
def serve_avatar_image(image_oid):
    """ Retrieves a survivor avatar from the GridFS system, sort of like a
    webserver would. Note to self: replace this with some kind of webserver
    functionality."""
    avatar = utils.GridfsImage(image_oid)
    return avatar.render_response()


#
#      ADMIN PANEL - these use the @basicAuth decorator found __init__.py
#

@application.route("/admin")
@application.basicAuth.login_required
def panel():
    """ Gets the admin panel."""
    return send_file("html/admin/panel.html")


@application.route("/admin/notifications/<method>", methods=["POST"])
@application.basicAuth.login_required
def admin_notifications(method):
    """ Creates a new admin type asset."""
    return request_broker.admin_notifications(method)


@application.route("/admin/get/<resource>", methods=["GET", "OPTIONS"])
@utils.crossdomain(origin=['*'])
def admin_view(resource):
    """ Retrieves admin panel resources as JSON."""
    return request_broker.get_admin_data(resource)


#
#   DEV SECTION! These routes are not used in production (because the webserver
#       does them). YHBW
#

@application.route('/static/<sub_dir>/<path:path>')
def route_to_static(path, sub_dir):
    """ Generic /static/* endpoints served here."""
    return send_from_directory('static/%s' % sub_dir, path)

@application.route("/favicon.ico")
def favicon():
    """ So you can see Logan's pretty logo in your dev environment."""
    return send_file("static/media/images/the_watcher.png")

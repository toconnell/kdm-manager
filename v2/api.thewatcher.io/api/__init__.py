"""
    Welcome to the extremely un-pythonic __init__.py for the 'api' module!

    DO NOT mess with the order of the import statements in this module.

    Also don't judge my life or the choices I have made.

"""

import flask
import flask_jwt_extended

# create the flask app with settings/utils info
application = flask.Flask(__name__)

import utils
from utils.route_decorators import crossdomain

#
#   do ALL application.config management here!
#
application.config.update(
    DEBUG = utils.settings.get("server","DEBUG"),
    TESTING = utils.settings.get("server","DEBUG"),
)
application.logger.addHandler(utils.get_logger(log_name="server"))
application.config['SECRET_KEY'] = utils.settings.get(
    "api",
    "secret_key",
    "private"
)

#   Javascript Web Token! DO NOT import jwt (i.e. pyjwt) here!
jwt = flask_jwt_extended.JWTManager(application)


#   HTTP basic auth, which we use for the admin panel:
from flask_httpauth import HTTPBasicAuth
application.basicAuth = HTTPBasicAuth()


#   additional methods for the main module

@application.before_request
def before_request():
    """ Updates the request with the 'start_time' attrib, which is used for
    performance monitoring. """
    request.start_time = datetime.now()
    request.metering = False

    # get the API key from the incoming request
    try:
        request.api_key = request.headers['API-Key']
    except:
        request.api_key = None

    if socket.getfqdn() != utils.settings.get('api','prod_fqdn'):
        request.metering = True


@application.after_request
def after_request(response):
    """ Logs the response times of all requests for metering purposes. """
    request.stop_time = datetime.now()
    utils.record_response_time(request)
    if response.status == 500:
        application.logger.error("fail")
    return response


@application.errorhandler(Exception)
@crossdomain(origin=['*'])
def general_exception(exception):
    """ This is how we do automatic email alerts on an API failure. """
    utils.email_exception(exception)
    return Response(response=exception.message, status=500)


@application.errorhandler(utils.InvalidUsage)
@crossdomain(origin=['*'])
def return_exception(error):
    """ This is how we fail an exception up (i.e. back) to the requester. """
    return Response(response=error.message, status=error.status_code)


@application.basicAuth.verify_password
def verify_password(username, password):
    """ cf. the methods in routes.py that use the @basicAuth decorator. This is
    what happens when those routes try to verify their user. """
    request.User = users.authenticate(username, password)
    if request.User is None:
        return False
    elif request.User.user.get("admin", None) is None:
        msg = "Non-admin user %s attempted to access the admin panel!" % request.User.user["login"]
        application.logger.warn(msg)
        return False
    return True


#   finally, import API routes and start the insanity!
from api import routes

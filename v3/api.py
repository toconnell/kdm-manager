"""

    This module (in its entirety) is deprecated in version 4!

    Transitional to the Flask app, the idea here is to start using deprecation
    warnings and, ultimately, killing off individual methods here until we
    get down to the bare minimum required for authentication.

    Then retire the whole thing.

"""


#
#   This is not the API! These are methods that the V1 webapp uses to access the
#   API via GET/POST of JSON.
#

from bson.objectid import ObjectId
from bson import json_util
import json
import requests
from retry import retry
import socket
from urlparse import urljoin

from utils import deprecated, get_logger, get_local_ip, load_settings

logger = get_logger(log_name="index")
settings = load_settings()
settings_private = load_settings("private")


def get_api_url(strip_http=False, trailing_slash=True):
    """ Determines the URL to use for API operations based on some socket
    operations and settings from the settings.cfg. Defaults to using localhost
    on the default API port defined in settings.cfg. """

    fqdn = socket.getfqdn()
    if fqdn == settings.get("api","prod_fqdn"):
        output = settings.get("api","prod_url")
    else:
        output = "https://%s:%s/" % (
            get_local_ip(),
            settings.get("api","localhost_port")
        )

    if not trailing_slash:
        output = output[:-1]

    if strip_http:
        return output[7:]

    return output


def route_to_url(r):
    """ Laziness method to turn a route snip/stub into a URL. """
    route = r
    if list(r)[-1] == "/":
        route = r[0:-1]
    return urljoin(get_api_url(), route)


@retry(tries=3,delay=1,jitter=1,logger=logger)
def get_jwt_token(username=None, password=None, Session=None):
    """ Gets a JWT token from /auth. Returns it (returns None if it fails for
    whatever reason, and tries to do some logging). """

    if not username or not password:
        err = "JWT token cannot be retrieved without a username and password!"
        raise Exception(err)

    req_url = route_to_url("/login")
    auth_dict = {"username": username, "password": password}
    response = post_JSON_to_route(req_url, auth_dict)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


@retry(tries=3,delay=1,jitter=1,logger=logger)
def check_token(Session):
    """ Checks the token on the sesh: returns True if it's still good, returns
    False if it's expired/whatever else. """

    req_url = route_to_url("/authorization/check")
    h = {
        'content-type':     'application/json',
        'API-Key':          settings_private.get('api', 'key'),
        'Authorization':    Session.session["access_token"],
    }
    r = requests.get(req_url, headers=h, verify=False)
    if r.status_code == 200:
        return True
    else:
        return False


@retry(tries=3,delay=1,jitter=1,logger=logger)
def refresh_jwt_token(Session):
    """ Refreshes the JWT token for the session so that we can use it to do API
    operations. """

    req_url = route_to_url("/authorization/refresh")
    h = {
        'content-type':     'application/json',
        'API-Key':          settings_private.get('api', 'key'),
        'Authorization':    Session.session["access_token"],
    }
    r = requests.post(req_url, headers=h, verify=False)

    if r.status_code == 200:
        Session.session["access_token"] = r.json()["access_token"]
        Session.save(verbose=False)
    else:
        logger.error(
            "[%s] JWT refresh response was %s - %s" % (
                Session.User,
                r.status_code,
                r.reason
            )
        )

    return r


@deprecated
@retry(tries=3,delay=1,jitter=1,logger=logger)
def post_JSON_to_route(route=None, payload={}, headers={}, Session=None):
    """ Blast some JSON at an API route. Return the response object. No fancy
    crap in this one, so you better know what you're doing here. """

    class customJSONencoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, ObjectId):
                return str(o)
            return json.JSONEncoder.default(self, o)

    req_url = route_to_url(route)
    endpoint = "/".join(req_url.split("/")[3:])

    # construct headers
    h = {'content-type': 'application/json'}

    if Session is not None:
        if not check_token(Session):
            refresh_jwt_token(Session)
        h['Authorization'] = Session.session["access_token"]
    else:
        if endpoint != 'login':
            logger.warn("API POST to JSON did not include a Session object!")

    if headers != {}:
        h.update(headers)

    try:
        return requests.post(
            req_url,
            data=json.dumps(payload, cls=customJSONencoder),
            headers=h,
            verify=False
        )
    except Exception as e:
        msg = (
            "api.post_JSON_to_Route() call failed! Exception caught "
            "while creating request object!"
        )
        logger.exception(e)
        raise Exception("\n".join([msg, str(payload)]))

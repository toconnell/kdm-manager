#!/usr/bin/python2.7


#
#   This is not the API! These are methods that the V1 webapp uses to access the
#   API via GET/POST of JSON.
#

from bson.objectid import ObjectId
from bson import json_util
import json
import flask
import requests
from retry import retry
import socket
from urlparse import urljoin

from utils import get_logger, load_settings

logger = get_logger(log_name="index")
settings = load_settings()
settings_private = load_settings("private")


def get_api_url():
    """ Determines the URL to use for API operations based on some socket
    operations and settings from the settings.cfg. Defaults to using localhost
    on the default API port defined in settings.cfg. """

    fqdn = socket.getfqdn()
    if fqdn == settings.get("api","prod_fqdn"):
        return settings.get("api","prod_url")
    else:
        logger.debug("[API] host FQDN is '%s'. Backing off to dev API settings." % (fqdn))
        return "http://%s:%s/" % (settings.get("api","localhost_addr"), settings.get("api","localhost_port"))


def route_to_url(r):
    """ Laziness method to turn a route snip/stub into a URL. """
    route = r
    if list(r)[-1] == "/":
        route = r[0:-1]
    return urljoin(get_api_url(), route)


def post_JSON_to_route(route=None, payload={}, headers={}, Session=None):
    """ Blast some JSON at an API route. Return the response object. No fancy
    crap in this one, so you better know what you're doing here. """

    class customJSONencoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, ObjectId):
                return str(o)
            return json.JSONEncoder.default(self, o)

    req_url = route_to_url(route)

    # construct headers
    h = {'content-type': 'application/json'}

    if Session is not None:
        h['Authorization'] = Session.session["access_token"]

    if headers != {}:
        h.update(headers)


    return requests.post(req_url, data=json.dumps(payload, cls=customJSONencoder), headers=h)


def get_jwt_token(username=None, password=None):
    """ Gets a JWT token from /auth. Returns it (returns None if it fails for
    whatever reason, and tries to do some logging). """

    if not username or not password:
        raise Exception("JWT token cannot be retrieved without a username and password!")

    req_url = route_to_url("/login")
    auth_dict = {"username": username, "password": password}
    response = post_JSON_to_route(req_url, auth_dict)
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


@retry(
    tries=3,delay=1,jitter=1,
    logger=logger,
)
def route_to_dict(route, params={}, return_as=dict, access_token=None):
    """ Retrieves data from a route. Returns a dict by default, which means that
    a 404 will come back as a {}. """

    req_url = route_to_url(route)

    # convert object IDs to strings: it's easier to just send a string and
    #   convert it back during API processing
    for k,v in params.iteritems():
        if type(v) == ObjectId:
            params[k] = str(v)

    j = json.dumps(params, default=json_util.default)

    h = {'content-type': 'application/json'}
    if access_token is not None:
        h["Authorization"] = "JWT %s" % access_token

    try:
        if params == {}:
            r = requests.get(req_url, data=j, headers=h)
        else:
            r = requests.post(req_url, data=j, headers=h)
    except Exception as e:
        logger.error("Could not retrieve data from API server!")
        logger.exception(e)
        return {}

    if r.status_code == 200:
        return dict(r.json())
    else:
        logger.error("%s - '%s' responded: %s - %s" % (r.request.method, r.url, r.status_code, r.reason))
        raise Exception("API Failure!")
        return {}



if __name__ == "__main__":
    print "\n localhost FQDN:\t%s" % socket.getfqdn()
    print " API URL:\t\t%s" % get_api_url()
    print " API version:\t\t%s\n" % (route_to_dict("settings.json")["api"]["version"])

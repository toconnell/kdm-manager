#!/usr/bin/python2.7


#
#   This is not the API! These are methods that the V1 webapp uses to access the
#   API via GET/POST of JSON.
#

from bson.objectid import ObjectId
from bson import json_util
import json
import requests
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


def route_to_dict(route, params={}, return_as=dict, authorize=False):
    """ Retrieves data from a route. Returns a dict by default, which means that
    a 404 will come back as a {}. """

    if list(route)[-1] == "/":
        route = route[0:-1]

    req_url = urljoin(get_api_url(), route)

    # convert object IDs to strings: it's easier to just send a string and
    #   convert it back during API processing
    for k,v in params.iteritems():
        if type(v) == ObjectId:
            params[k] = str(v)

    if authorize:
        params.update({"meta": {"api_key": settings_private.get("api","key")}})

    j = json.dumps(params, default=json_util.default)

    h = {'content-type': 'application/json'}

    try:
        if authorize:
            r = requests.post(req_url, data=j, headers=h)
        else:
            r = requests.get(req_url, data=j, headers=h)
    except Exception as e:
        logger.error("Could not retrieve data from API server!")
        logger.exception(e)
        return {}

    if r.status_code == 200:
        return dict(r.json())
    else:
        logger.error("API:GET -> '%s' returned a %s status!" % (r.url, r.status_code))
        return {}



if __name__ == "__main__":
    print "\n localhost FQDN:\t%s" % socket.getfqdn()
    print " API URL:\t\t%s" % get_api_url()
    print " API version:\t\t%s\n" % (route_to_dict("settings.json")["api"]["version"])

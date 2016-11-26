#!/usr/bin/python2.7


#
#   This is not the API! These are methods that the V1 webapp uses to access the
#   API via GET/POST of JSON.
#

from bson.objectid import ObjectId
from bson import json_util
import json
import requests
from urlparse import urljoin

from utils import get_logger, load_settings

logger = get_logger(log_name="index")
settings = load_settings()
settings_private = load_settings("private")

def route_to_dict(route, params={}, return_as=dict, authorize=False):
    """ Retrieves data from a route. Returns a dict by default, which means that
    a 404 will come back as a {}. """

    if list(route)[-1] == "/":
        route = route[0:-1]

    api_url = settings.get("application","api_url")
    req_url = urljoin(api_url, route)

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

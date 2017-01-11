#!/usr/bin/python2.7

import utils

from models import survivors, settlements, users
from Models import AssetLoadError

logger = utils.get_logger(log_name="errors")

#
#   routing.py is meant to centralize the "hand-off" operations between api.py
#   and the various modules in the routes/ module.
#
#   All methods in this module should return an HTTP response if they fail.
#

class badResponse():
    """ A little dummy/slug class for returning bad HTTP responses. """

    def __init__(self, http_response=utils.http_422, **kwargs):
        self.logger     = logger
        self.response   = http_response

    def request_response(self, action):
        self.logger.warn("Returning failure response to bad '%s' request." % action)
        return self.response


def get_asset(collection=None, asset_id=None):
    """ Tries to return an initialized asset from one of our collections.
    Returns a (bad) HTTP response if it cannot. """

    R = badResponse()

    try:
        if collection == "settlement":
            return settlements.Settlement(_id=asset_id)
        elif collection == "survivor":
            return survivors.Survivor(_id=asset_id)
        elif collection == "user":
            return users.User(_id=asset_id)
        else:
            return R

    except Exception as e:

        # return a 404 if we can't find the asset ID
        if isinstance(e, AssetLoadError):
            R.logger.warn("Requested %s asset _id %s could not be initialized!" % (collection, asset_id))
            R.response = utils.http_404
            return R

        R.response = utils.http_500
        R.logger.exception(e)
        return R






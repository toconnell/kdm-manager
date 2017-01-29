#!/usr/bin/python2.7

from flask import request, Response

import utils

from models import survivors, settlements, users, monsters, campaigns
from Models import AssetLoadError

logger = utils.get_logger(log_name="errors")

#
#   The point of this module is to get business logic re: request-handling
#   out of api.py, so that can stay focused on authenticaiton and request
#   routing.
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

    def send_bad_response(self, e):
        # return a 404 if we can't find the asset ID
        if isinstance(e, AssetLoadError):
            self.logger.warn("Requested asset _id could not be initialized!")
            return utils.http_404

        self.logger.exception(e)
        return utils.http_500


def get_user_asset(collection=None, asset_id=None):
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
        return R.send_bad_response(e)


def get_game_asset(collection):
    """ Simliar to get_user_asset(), except for game assets, such as monsters,
    gear, locations, etc. """

    R = badResponse()

    if request.json is None:
        return utils.http_422

    try:
        if collection == "monster":
            M = monsters.Assets()
            return M.request_response(request.json)
        elif collection == "campaign":
            C = campaigns.Assets()
            return C.request_response(request.json)
        else:
            return R

    except Exception as e:
        return R.send_bad_response(e)



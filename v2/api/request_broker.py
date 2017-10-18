#!/usr/bin/python2.7

from flask import request, Response

import panel
import utils

from models import survivors, settlements, users, monsters, campaigns
from Models import AssetLoadError

logger = utils.get_logger(log_name="server")

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
        """ We have a coupld of bad responses we can return when the broker
        fails. First, we if an AsseLoadError type exception, we do a generic
        404. Second, if we are being asked to return a utils.InvalidUsage
        type object, we just raise that as we normally would.

        Otherwise, we're sending the generic 500 server explosion back.
        """

        # return a 404 if we can't find the asset ID
        if isinstance(e, AssetLoadError):
            self.logger.warn("Requested asset _id could not be initialized!")
            return utils.http_404
        elif isinstance(e, utils.InvalidUsage):
            raise e

        self.logger.exception(e)
        return utils.http_500


def get_admin_data(resource=None):
    """ Retrieves admin panel data. """

    try:
        if resource == 'user_data':
            return panel.get_user_data()
        if resource == 'settlement_data':
            return panel.get_settlement_data()
        elif resource == 'logs':
            return panel.serialize_system_logs()
    except Exception as e:
        logger.error("Unable to return '%s' admin data!" % resource)
        logger.error(e)
        raise utils.InvalidUsage(e, status_code=500)

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


def new_user_asset(asset_type=None):
    """ Hands off a new asset creation request and returns the result of the
    request. Like all brokerage methods, this method always returns an HTTP
    response.

    The idea is to call this in request-processing workflow when you know that
    you've got an asset creation request.

    This brokerage method expects a few things:

        1.) you've added a logger to the request
        2.) you've also added a models.users.User object to the request
        3.) you're passing in JSON params that can be processed when
            fulfilling your request

    If you are NOT doing all of that, do NOT pass off a request to this method,
    unless you want to throw a 500 back at the user.

    """

    logger.debug("%s is requesting a new '%s' asset!" % (request.User, asset_type))

    if asset_type == "settlement":
        S = settlements.Settlement()
        return S.serialize()
    elif asset_type == "survivor":
        S = survivors.Survivor()
        return S.serialize()
    else:
        return Response(
            response="Creating '%s' user assets via request_broker() is not supported!" % asset_type,
            status=422,
            mimetype="text/plain",
        )

    return utils.http_400







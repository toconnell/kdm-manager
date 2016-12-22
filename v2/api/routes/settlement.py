#!/usr/bin/python2.7

from flask import request, Response

from Models import AssetLoadError
from models import settlements
import utils

logger = utils.get_logger(log_name="server")


def render_response(action, settlement_id):
    """ Returns a Response object based on request, action and settlement_id.
    Everything in and out of this module has to come through this method. """

    #
    #   First, try to initialize the incoming settlement. Return a big, bloody
    #   500 if we can't manage that for whatever reason.

    try:
        S = settlements.Settlement(_id=settlement_id)
    except Exception as e:
        logger.exception(e)

        # return a 404 if we can't find the settlement to load it
        if isinstance(e, AssetLoadError):
            return utils.http_404

        return utils.http_500

    #
    #   'action' cascade is here. Basically, if we have a known action, respond
    #   to it however we want to respond. If we have an unknown action, return
    #   a 422.
    #
    #   For 'action' values that request an operation, do the operation and exit
    #   the cascade, allowing this method to return a happy 200
    #

    if request.get_json() is not None:
        try:
            params = dict(request.get_json())
        except ValueError:
            params = request.get_json()

    if action == "get":
        return S.http_response()
    elif action == "set":
        S.update_sheet_from_dict(params)
    elif action == "add_expansions":
        S.add_expansions(params)
    elif action == "rm_expansions":
        S.rm_expansions(params)
    elif action == "add_note":
        S.add_settlement_note(params)
    elif action == "update_expansions":
        logger.debug(params)
    elif action == "rm_note":
        S.rm_settlement_note(params)
    elif action == "add_timeline_event":
        S.add_timeline_event(params)
    elif action == "rm_timeline_event":
        S.rm_timeline_event(params)
    elif action == "event_log":
        return Response(response=S.get_event_log("JSON"), status=200, mimetype="application/json")
    else:
        # unknown/unsupported action response
        logger.warn("Unsupported settlement route action: '%s' was received!" % action)
        return utils.http_422


    # finish successfully
    return utils.http_200



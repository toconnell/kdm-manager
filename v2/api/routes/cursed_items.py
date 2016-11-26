#!/usr/bin/python2.7

from bson import json_util
from flask import request, Response
import json

from models import cursed_items, settlements
import utils

logger = utils.get_logger(log_name="server")

def GET_all():
    """ Simple GET handling for monster assets. Supports lookup by handle or by
    name and returns a 200 if it can find one. Othewise, you get a 404. """

    all_items = cursed_items.Assets()
    r = json.dumps(all_items.assets, default=json_util.default)
    return Response(response=r, status=200, mimetype="application/json")

def POST_available():
    """ Requires a valid API key and a settlement ID. Returns only the cursed
    items that the settlement has access to, given campaigns, expansions, etc.
    Returns 500's if it doesn't like the input."""

    settlement_id = request.get_json()["settlement_id"]
    if settlement_id is None:
        return utils.http_422
    else:
        S = settlements.Settlement(_id=settlement_id["$oid"])
        if S.settlement is None:
            return utils.http_404
        else:
            r = json.dumps(S.get_cursed_items(), default=json_util.default)
            return Response(response=r, status=200, mimetype="application/json")

    return utils.http_500

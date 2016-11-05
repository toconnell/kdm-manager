#!/usr/bin/python2.7

from flask import Response, request

from models import survivors
import utils


def init_survivor(survivor_id):
    """ Checks a survivor _id and returns a survivor object if it's legit.
    Otherwise, if it's not legit, return a 404 Response object. """

    try:
        S = survivors.Survivor(_id=survivor_id)
        return S
    except:
        return utils.http_404


def GET_json(S):
    """ Simple GET handling for monster assets. Supports lookup by handle or by
    name and returns a 200 if it can find one. Othewise, you get a 404. """

    return Response(response=S.as_json(), status=200, mimetype="application/json")


def POST_to_mdb(S):
    """ Handles a POST containing updates for a survivor MDB document. """

    result = "No 'survivor' element present!"

    j = request.get_json()
    if "survivor" in j.keys():
        d = j["survivor"]
        result = S.update_from_dict(d)

    if result == True:
        S.logger.info("Survivor %s updated using API key %s: %s" % (S, j["meta"]["api_key"], d))
        return Response(response="Success! Updated %s keys." % len(d), status=200)
    else:
        return Response(response="Failed! Could not update survivor! Error: %s" % result, status=500)

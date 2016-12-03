#!/usr/bin/python2.7

from flask import Response, request

from models import survivors
import utils


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

#!/usr/bin/python2.7

from flask import request, Response

from models import monster
import utils

def GET_json():
    """ Simple GET handling for monster assets. Supports lookup by handle or by
    name and returns a 200 if it can find one. Othewise, you get a 404. """

    m_handle = request.args.get("handle", None)
    m_name = request.args.get("name", None)

    four_oh_four = Response(response=None, status=404, mimetype="application/json")

    try:
        if m_handle is not None:
            M = monster.Monster(handle=m_handle)
        elif m_name is not None:
            M = monster.Monster(name=m_name)
        else:
            return four_oh_four
    except:
        return four_oh_four

    r = utils.asset_object_to_json(M)
    return Response(response=r, status=200, mimetype="application/json")

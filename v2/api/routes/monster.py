#!/usr/bin/python2.7

from flask import request, Response

from models import monster
import utils

logger = utils.get_logger(log_name="server")

def GET_json():
    """ Simple GET handling for monster assets. Supports lookup by handle or by
    name and returns a 200 if it can find one. Othewise, you get a 404. """

    m_handle = None
    m_name = None
    if "name" in request.json:
        m_name = request.json["name"]
    if "handle" in request.json:
        m_name = request.json["handle"]

    try:
        if m_handle is not None:
            M = monster.Monster(handle=m_handle)
        elif m_name is not None:
            M = monster.Monster(name=m_name)
        else:
            return utils.http_404
    except:
        return utils.http_404

    r = utils.asset_object_to_json(M)
    return Response(response=r, status=200, mimetype="application/json")

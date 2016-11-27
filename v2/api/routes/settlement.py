#!/usr/bin/python2.7

from flask import Response, request

from models import settlements
import utils


def init_settlement(s_id):
    """ Checks a survivor _id and returns a survivor object if it's legit.
    Otherwise, if it's not legit, return a 404 Response object. """

    if not utils.authorize(request):
        return utils.http_401

    try:
        S = settlements.Settlement(_id=s_id)
        return S
    except:
        return utils.http_404


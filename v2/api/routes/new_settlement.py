#!/usr/bin/python2.7

from flask import request, Response

from models import campaigns, expansions, survivors
import utils

logger = utils.get_logger(log_name="server")


def serialize_assets():

    output = {}

    for mod in [campaigns, expansions, survivors]:

        mod_string = "%s" % str(mod.__name__).split(".")[1]
        output[mod_string] = []

        CA = mod.Assets()

        for c in sorted(CA.get_handles()):
            asset = CA.get_asset(c)
            asset_repr = {"handle": c, "name": asset["name"]}
            for optional_key in ["subtitle", "default"]:
                if optional_key in asset.keys():
                    asset_repr[optional_key] = asset[optional_key]
            output[mod_string].append(asset_repr)

    return output

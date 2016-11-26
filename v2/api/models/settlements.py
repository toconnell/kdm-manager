#!/usr/bin/python2.7

from bson import json_util
import json

import Models
from models import campaigns, expansions, cursed_items, survivors
import settings
import utils


class Settlement(Models.UserAsset):
    """ This is the base class for all expansions. Private methods exist for
    enabling and disabling expansions (within a campaign/settlement). """

    def __init__(self, *args, **kwargs):
        self.collection="settlements"
        self.object_version=0.1
        Models.UserAsset.__init__(self,  *args, **kwargs)


    def serialize(self, return_type="JSON"):
        """ Renders the settlement, including all methods and supplements, as
        a monster JSON object. This one is the gran-pappy. """

        output = self.get_serialize_meta()
        output.update({"settlement": self.settlement})
        output.update({"campaign": self.get_campaign()})
        output.update({"expansions": self.get_expansions()})
        output.update({"players": self.get_players()})
        output.update({"cursed_items": self.get_cursed_items()})
        output.update({"survivors": self.get_survivors()})
        return json.dumps(output, default=json_util.default)


    def get_players(self, return_type=None):
        """ Returns a set type object containing mdb.users documents if the
        'return_type' kwarg is left unspecified.

        Otherwise, use return_type="count" to get an int representation of the
        set of players. """

        player_set = set()
        survivors = utils.mdb.survivors.find({"settlement": self.settlement["_id"]})
        for s in survivors:
            player_set.add(s["email"])

        player_set = utils.mdb.users.find({"login": {"$in": list(player_set)}})

        if return_type == "count":
            return player_set.count()

        return [x for x in player_set]


    def get_survivors(self, return_type=None):
        """ Returns a dictionary of survivors where the keys are bson ObjectIDs
        and the values are serialized survivors. """

        output = []
        all_survivors = utils.mdb.survivors.find({"settlement": self.settlement["_id"]})
        for s in all_survivors:
            S = survivors.Survivor(_id=s["_id"])
            output.append(S.serialize())
        return output


    def get_campaign(self, return_type=None):
        """ Returns the campaign of the settlement as a string, if nothing is
        specified for kwarg 'return_type'.

        'return_type' can also be 'dict' or 'object'. Specifying 'dict' gets the
        raw campaign definition from assets/campaigns.py; specifying 'object'
        gets a campaign asset object. """

        if not "campaign" in self.settlement.keys():
            self.settlement["campaign"] = "People of the Lantern"

        if return_type == "dict":
            C = campaigns.Assets()
            return C.get_asset_from_name(name=self.settlement["campaign"])
        elif return_type == "object":
            C = campaigns.Campaign(name=self.settlement["campaign"])
            return C

        return self.settlement["campaign"]


    def get_expansions(self, return_type=None):
        """ Returns a list of expansions if the 'return_type' kwarg is left
        unspecified.

        Otherwise, 'return_type' can be either 'dict' or 'comma_delimited'.

        Setting return_type="dict" gets a dictionary where expansion 'name'
        attributes are the keys and asset dictionaries are the values. """

        if "expansions" in self.settlement.keys():
            expansions = list(set(self.settlement["expansions"]))
            self.settlement["expansions"] = expansions
        else:
            expansions = []

        if return_type == "dict":
            exp_dict = {}
            for exp_name in expansions:
                E = expansions.Assets()
                exp_dict[exp_name] = E.get_asset_from_name(exp_name)
            return exp_dict
        elif return_type == "comma-delimited":
            if expansions == []:
                return None
            else:
                return ", ".join(expansions)

        return expansions


    def get_cursed_items(self):
        """ Returns a dictionary of cursed items available to a settlement.
        Should probably be customizable to include campaign, but maybe later.
        """

        available = {}
        all_cursed_items = cursed_items.Assets()
        for k in all_cursed_items.assets.keys():
            item_dict = all_cursed_items.assets[k]
            if self.is_compatible(item_dict):
                available.update({item_dict["handle"]: item_dict})
        return available


    def is_compatible(self, asset_dict):
        """Evaluates an asset's dictionary to determine it is compatible for
        use with this settlement. Always returns a bool (no matter what). """

        # check to see if the asset excludes certian campaign types
        if "excluded_campaigns" in asset_dict.keys():
            if self.get_campaign() in asset_dict["excluded_campaigns"]:
                return False

        # check to see if the asset belongs to an expansion
        if "expansion" in asset_dict.keys():
            if asset_dict["expansion"] not in self.get_expansions():
                return False

        return True


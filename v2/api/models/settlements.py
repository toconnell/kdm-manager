#!/usr/bin/python2.7


import Models
from models import campaigns, expansions
import utils


class Settlement(Models.UserAsset):
    """ This is the base class for all expansions. Private methods exist for
    enabling and disabling expansions (within a campaign/settlement). """

    def __init__(self, *args, **kwargs):
        self.collection="settlements"
        Models.UserAsset.__init__(self,  *args, **kwargs)


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



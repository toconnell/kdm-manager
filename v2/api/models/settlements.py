#!/usr/bin/python2.7

from bson import json_util
import json

import Models
from models import cursed_items, survivors, weapon_specializations, weapon_masteries, causes_of_death, innovations, survival_actions
import settings
import utils


class Settlement(Models.UserAsset):
    """ This is the base class for all expansions. Private methods exist for
    enabling and disabling expansions (within a campaign/settlement). """

    def __init__(self, *args, **kwargs):
        self.collection="settlements"
        self.object_version=0.4
        Models.UserAsset.__init__(self,  *args, **kwargs)


    def serialize(self, return_type="JSON"):
        """ Renders the settlement, including all methods and supplements, as
        a monster JSON object. This one is the gran-pappy. """

        output = self.get_serialize_meta()

        # create the sheet
        output.update({"sheet": self.settlement})
        output["sheet"].update({"campaign": self.get_campaign()})
        output["sheet"].update({"expansions": self.get_expansions()})

        # create user_assets
        output.update({"user_assets": {}})
        output["user_assets"].update({"players": self.get_players()})
        self.survivor_weapon_masteries = []
        output["user_assets"].update({"survivors": self.get_survivors()})
        output["user_assets"].update({"survivor_weapon_masteries": self.survivor_weapon_masteries})

        # great game_assets
        output.update({"game_assets": {}})
        output["game_assets"].update(self.get_available_assets(weapon_specializations))
        output["game_assets"].update(self.get_available_assets(weapon_masteries))
        output["game_assets"].update(self.get_available_assets(cursed_items))
        output["game_assets"].update(self.get_available_assets(causes_of_death))
        output["game_assets"].update(self.get_available_assets(survival_actions))
        output["game_assets"]["survival_actions_available"] = self.get_available_survival_actions()

        return json.dumps(output, default=json_util.default)


    def get_innovations(self, return_type=None):
        """ Returns self.settlement["innovations"] by default; specify 'dict' as
        the 'return_type' to get a dictionary back instead. """

        s_innovations = self.settlement["innovations"]
        all_innovations = innovations.Assets()

        if return_type == dict:
            output = {}
            for i in s_innovations:
                if i in all_innovations.get_names():
                    i_dict = all_innovations.get_asset_from_name(i)
                    output[i_dict["handle"]] = i_dict
            return output

        return s_innovations


    def get_available_survival_actions(self):
        """ Returns a dictionary of survival actions available to the settlement
        and its survivors. """

        all_survival_actions = survival_actions.Assets()

        sa = {}
        for k,v in self.get_innovations(dict).iteritems():
            if "survival_action" in v.keys():
                sa_dict = all_survival_actions.get_asset_from_name(v["survival_action"])
                sa_dict["innovation"] = v["name"]
                sa[sa_dict["handle"]] = sa_dict
        return sa


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

        wm = weapon_masteries.Assets()

        output = []
        all_survivors = utils.mdb.survivors.find({"settlement": self.settlement["_id"]})
        for s in all_survivors:
            S = survivors.Survivor(_id=s["_id"])
            for ai in S.survivor["abilities_and_impairments"]:
                if ai in wm.get_names():
                    self.survivor_weapon_masteries.append(ai)
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


    def get_available_assets(self, asset_module=None):
        """ Generic function to return a dict of available game assets based on
        their family. The 'asset_module' should be something such as,
        'cursed_items' or 'weapon_proficiencies', etc. that has an Assets()
        method. """

        available = {}
        A = asset_module.Assets()
        for k in A.get_handles():
            item_dict = A.get_asset(k)
            if self.is_compatible(item_dict):
                available.update({item_dict["handle"]: item_dict})
        return {"%s" % (asset_module.__name__.split(".")[-1]): available}


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


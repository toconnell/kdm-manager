#!/usr/bin/python2.7

from bson import json_util
from bson.objectid import ObjectId
from copy import copy
from datetime import datetime, timedelta
import json

import Models
from models import campaigns, cursed_items, survivors, weapon_specializations, weapon_masteries, causes_of_death, innovations, survival_actions, events, abilities_and_impairments, monsters
import settings
import utils


class Settlement(Models.UserAsset):
    """ This is the base class for all expansions. Private methods exist for
    enabling and disabling expansions (within a campaign/settlement). """

    def __init__(self, *args, **kwargs):
        self.collection="settlements"
        self.object_version=0.13
        Models.UserAsset.__init__(self,  *args, **kwargs)
        self.normalize_data()


    def normalize_data(self):
        """ Makes sure that self.settlement is up to our current standards. """

        perform_save = False

        #
        #   timeline migrations
        #
        if not "timeline_version" in self.settlement.keys():
            self.convert_timeline_to_JSON()
            perform_save = True

        if self.settlement["timeline_version"] < 1.1:
            self.convert_timeline_quarry_events()
            perform_save = True

        #
        #   misc migrations
        #
        if not "monsters_version" in self.settlement.keys():
            self.convert_monsters_to_handles()
            perform_save = True

        #
        #   misc migrations/operations
        #
        if not "admins" in self.settlement.keys():
            self.logger.info("Creating 'admins' key for %s" % (self))
            creator = utils.mdb.users.find_one({"_id": self.settlement["created_by"]})
            self.settlement["admins"] = [creator["login"]]
            perform_save = True


        # finish
        if perform_save:
            self.save()


    def serialize(self, return_type="JSON"):
        """ Renders the settlement, including all methods and supplements, as
        a monster JSON object. This one is the gran-pappy. """

        output = self.get_serialize_meta()

        # create the sheet
        output.update({"sheet": self.settlement})
        output["sheet"].update({"campaign": self.get_campaign()})
        output["sheet"].update({"expansions": self.get_expansions()})
        output["sheet"]["settlement_notes"] = self.get_settlement_notes()

        # create user_assets
        output.update({"user_assets": {}})
        output["user_assets"].update({"players": self.get_players()})
        output["user_assets"].update({"survivors": self.get_survivors()})
        output["user_assets"].update({"survivor_weapon_masteries": self.survivor_weapon_masteries})

        # great game_assets
        output.update({"game_assets": {}})
        output["game_assets"].update(self.get_available_assets(innovations))
        output["game_assets"].update(self.get_available_assets(abilities_and_impairments))
        output["game_assets"].update(self.get_available_assets(weapon_specializations))
        output["game_assets"].update(self.get_available_assets(weapon_masteries))
        output["game_assets"].update(self.get_available_assets(cursed_items))
        output["game_assets"].update(self.get_available_assets(causes_of_death))
        output["game_assets"].update(self.get_available_assets(survival_actions))
        output["game_assets"].update(self.get_available_assets(events))
        output["game_assets"].update(self.get_available_assets(monsters))
        output["game_assets"]["showdown_options"] = self.get_defeated_monster_options()
        output["game_assets"]["eligible_parents"] = self.eligible_parents
        output["game_assets"]["campaign"] = self.get_campaign(dict)
        output["game_assets"]["survival_actions_available"] = self.get_available_survival_actions()

        return json.dumps(output, default=json_util.default)


    def get_settlement_notes(self):
        """ Returns a list of mdb.settlement_notes documents for the settlement.
        They're sorted in reverse chronological, because the idea is that you're
        goign to turn this list into JSON and then use it in the webapp. """

        notes = utils.mdb.settlement_notes.find({"settlement": self.settlement["_id"]}).sort("created_on",-1)
        if notes is None:
            return []
        return [n for n in notes]


    def add_settlement_note(self, n={}):
        """ Adds a settlement note to MDB. Expects a dict. """

        note_dict = {
            "note": n["note"].strip(),
            "created_by": ObjectId(n["author_id"]),
            "js_id": n["js_id"],
            "author": n["author"],
            "created_on": datetime.now(),
            "settlement": self.settlement["_id"],
            "lantern_year": n["lantern_year"],
        }

        utils.mdb.settlement_notes.insert(note_dict)
        self.logger.debug("[%s] added a settlement note to %s" % (n["author"], self))


    def rm_settlement_note(self, n={}):
        """ Removes a note from MDB. Expects a dict with one key. """

        utils.mdb.settlement_notes.remove({"settlement": self.settlement["_id"], "js_id": n["js_id"]})
        self.logger.debug("[%s] removed a settlement note from %s" % (n["user_login"], self))


    def get_defeated_monster_options(self, include_nemeses=False):
        """ Returns a sorted list of strings (they call it an 'array' in JS,
        because they fancy) representing the settlement's possible showdowns,
        given their quarries, nemeses, etc. """


        candidate_handles = copy(self.settlement["quarries"])
        if include_nemeses:
            candidate_handles.extend(self.settlement["nemesis_monsters"])

        output = []
        for m in candidate_handles:
            M = monsters.Monster(m)
            if M.is_unique():
                output.append(M.name)
            else:
                for l in range(M.get_levels()):
                    lvl = l+1
                    output.append("%s Lvl %s" % (M.name,lvl))


        return sorted(output)


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
        and the values are serialized survivors.

        Also sets some settlement object attributes such as "eligible_parents"
        and so on. This is the big survivor investigation method.

        """

        wm = weapon_masteries.Assets()
        self.survivor_weapon_masteries = []

        output = []
        all_survivors = utils.mdb.survivors.find({"settlement": self.settlement["_id"]})

        self.eligible_parents = {"male":[], "female":[]}

        for s in all_survivors:
            S = survivors.Survivor(_id=s["_id"])

            for ai in S.survivor["abilities_and_impairments"]:
                if ai in wm.get_names():
                    self.survivor_weapon_masteries.append(ai)

            if S.can_be_nominated_for_intimacy():
                i_dict = {"name": S.survivor["name"], "_id": S.survivor["_id"]}
                if S.get_sex() == "M":
                    self.eligible_parents["male"].append(i_dict)
                elif S.get_sex() == "F":
                    self.eligible_parents["female"].append(i_dict)

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

        C = campaigns.Assets()

        if self.settlement["campaign"] not in C.get_names():
            raise Models.AssetInitError("The name '%s' does not belong to any known campaign asset!" % self.settlement["campaign"])

        if return_type == dict:
            return C.get_asset_from_name(name=self.settlement["campaign"])
#        elif return_type == "object":
#            C = campaigns.Campaign(name=self.get_campaign())
#            return C

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


    def get_event_log(self, return_type=None):
        """ Returns the settlement's event log as a cursor object unless told to
        do otherwise."""

        event_log = utils.mdb.settlement_events.find(
            {
            "settlement_id": self.settlement["_id"]
            }
        ).sort("created_by",-1)

        if return_type=="JSON":
            return json.dumps(list(event_log),default=json_util.default)

        return event_log


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


    #
    #   conversion and migration functions
    #

    def convert_monsters_to_handles(self):
        """ Takes a legacy settlement object and swaps out its monster name
        lists for monster handles. """

        # create the v1.0 'nemesis_encounters' list and transcribe nemesis info
        self.settlement["nemesis_encounters"] = []
        for n in self.settlement["nemesis_monsters"]:
            M = monsters.Monster(name=n)
            self.settlement["nemesis_encounters"].append({M.handle: self.settlement["nemesis_monsters"][n]})

        for list_key in ["quarries","nemesis_monsters"]:
            new_list = []
            old_list = self.settlement[list_key]
            for m in old_list:
                M = monsters.Monster(name=m)
                new_list.append(M.handle)

            self.settlement[list_key] = new_list

        self.settlement["monsters_version"] = 1.0
        self.logger.debug("Migrated %s monster lists from legacy data model to 1.0." % self)


    def convert_timeline_to_JSON(self):
        """ Converts our old, pseudo-JSON timeline to the standard JSON one. """

        old_timeline = self.settlement["timeline"]
        new_timeline = []

        all_events = events.Assets()

        for old_ly in old_timeline:
            new_ly = {}
            for k in old_ly.keys():

                if type(old_ly[k]) == list:
                    event_type_list = []
                    for event in old_ly[k]:
                        event_dict = {"name": event}
                        if event in all_events.get_names():
                            event_dict.update(all_events.get_asset_from_name(event))
                        event_type_list.append(event_dict)
                    new_ly[k] = event_type_list
                else:
                    new_ly[k] = old_ly[k]
            new_timeline.append(new_ly)

        self.settlement["timeline"] = new_timeline
        self.settlement["timeline_version"] = 1.0
        self.logger.warn("Migrated %s timeline from legacy data model to version 1.0" % self)


    def convert_timeline_quarry_events(self):
        """ Takes a 1.0 timeline and converts its "quarry_events" to
        "showdown_events", making it 1.1. """

        new_timeline = []
        for y in self.settlement["timeline"]:
            for event_key in y.keys():
                if event_key == "quarry_event":
                    y["showdown_event"] = y[event_key]
                    del y[event_key]
            new_timeline.append(y)

        self.settlement["timeline"] = new_timeline
        self.settlement["timeline_version"] = 1.1
        self.logger.debug("Migrated %s timeline to version 1.1" % (self))





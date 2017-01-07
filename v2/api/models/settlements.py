#!/usr/bin/python2.7

from bson import json_util
from bson.objectid import ObjectId
from copy import copy
from datetime import datetime, timedelta
import json
import random
import time

import Models
from models import campaigns, cursed_items, expansions, survivors, weapon_specializations, weapon_masteries, causes_of_death, innovations, survival_actions, events, abilities_and_impairments, monsters, milestone_story_events, locations
import settings
import utils


class Settlement(Models.UserAsset):
    """ This is the base class for all expansions. Private methods exist for
    enabling and disabling expansions (within a campaign/settlement). """

    def __init__(self, *args, **kwargs):
        self.collection="settlements"
        self.object_version=0.24
        Models.UserAsset.__init__(self,  *args, **kwargs)
        self.normalize_data()


    def normalize_data(self):
        """ Makes sure that self.settlement is up to our current standards. """

        perform_save = False

        founder = utils.mdb.users.find_one({"_id": self.settlement["created_by"]})

        #
        #       1.) low-level/basic functionality
        #           misc migrations/operations
        #
        if not "admins" in self.settlement.keys():
            self.logger.info("Creating 'admins' key for %s" % (self))
            creator = utils.mdb.users.find_one({"_id": self.settlement["created_by"]})
            self.settlement["admins"] = [creator["login"]]
            perform_save = True
        if not founder["login"] in self.settlement["admins"]:
            self.settlement["admins"].append(founder["login"])
            self.logger.debug("Adding founder '%s' to %s admins list." % (founder["login"], self))
            perform_save = True
        if not "expansions" in self.settlement.keys():
            self.logger.info("Creating 'expansions' key for %s" % (self))
            self.settlement["expansions"] = []
            perform_save

        #       get legacy settlement_notes real quick
        if "settlement_notes" in self.settlement.keys():

            self.logger.debug("Converting legacy 'settlement_notes' to mdb.settlement_notes doc!")

            s = str(int(time.time())) + str(self.settlement["_id"])
            bogus_id = ''.join(random.sample(s,len(s)))

            note = {
                "note": self.settlement["settlement_notes"].strip(),
                "author": founder["login"],
                "author_id": self.settlement["created_by"],
                "js_id": bogus_id,
                "lantern_year": self.get_current_ly(),
            }
            self.add_settlement_note(note)
            del self.settlement["settlement_notes"]
            perform_save = True


        #
        #       2.) timeline migrations
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

        if not "expansions_version" in self.settlement.keys():
            self.convert_expansions_to_handles()
            perform_save = True


        # finish
        if perform_save:
            self.logger.debug("%s settlement modified! Saving changes..." % self)
            self.save()


    def serialize(self, return_type="JSON"):
        """ Renders the settlement, including all methods and supplements, as
        a monster JSON object. This one is the gran-pappy. """


        I = innovations.Assets()

        output = self.get_serialize_meta()

        # do some tidiness operations first
        for k in ["locations","innovations","defeated_monsters"]:
            self.settlement[k] = sorted(self.settlement[k])

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
        output["game_assets"].update(self.get_available_assets(locations))
        output["game_assets"].update(self.get_available_assets(abilities_and_impairments))
        output["game_assets"].update(self.get_available_assets(weapon_specializations))
        output["game_assets"].update(self.get_available_assets(weapon_masteries))
        output["game_assets"].update(self.get_available_assets(cursed_items))
        output["game_assets"].update(self.get_available_assets(causes_of_death))
        output["game_assets"].update(self.get_available_assets(survival_actions))
        output["game_assets"].update(self.get_available_assets(events))
        output["game_assets"].update(self.get_available_assets(monsters))

            # options (i.e. decks)
        output["game_assets"]["locations_options"] = self.get_locations_options()
        output["game_assets"]["principles_options"] = self.get_principles_options()
        output["game_assets"]["milestones_options"] = self.get_milestones_options()

            # monster game assets
        output["game_assets"]["nemesis_options"] = self.get_monster_options("nemesis_monsters")
        output["game_assets"]["quarry_options"] = self.get_monster_options("quarries")
        for c in [
            "showdown_options",
            "special_showdown_options",
            "nemesis_encounters",
            "defeated_monsters"
        ]:
            output["game_assets"][c] = self.get_timeline_monster_event_options(c)

            # meta/other game assets
        output["game_assets"]["campaign"] = self.get_campaign(dict)
        output["game_assets"]["expansions"] = self.get_expansions(dict)

            # misc helpers for front-end
        output["game_assets"]["eligible_parents"] = self.eligible_parents
        output["game_assets"]["survival_actions_available"] = self.get_available_survival_actions()


        # finally, return a JSON string of our object
        return json.dumps(output, default=json_util.default)


    def add_expansions(self, e_list=[]):
        """ Takes a list of expansion handles and then adds them to the
        settlement, applying Timeline updates, etc. as required by the expansion
        asset definitions. """

        E = expansions.Assets()

        # prune the list to reduce risk of downstream cock-ups
        for e_handle in e_list:
            if e_handle not in E.get_handles():
                e_list.remove(e_handle)
                self.logger.warn("Unknown expansion handle '%s' is being ignored!" % (e_handle))
            if e_handle in self.settlement["expansions"]:
                e_list.remove(e_handle)
                self.logger.warn("Expansion handle '%s' is already in %s" % (e_handle, self))

        #
        #   here is where we process the expansion dictionary
        #
        for e_handle in e_list:
            e_dict = E.get_asset(e_handle)
            self.log_event("Adding '%s' expansion content!" % e_dict["name"])

            self.settlement["expansions"].append(e_handle)

            if "timeline_add" in e_dict.keys():
               [self.add_timeline_event(e) for e in e_dict["timeline_add"] if e["ly"] >= self.get_current_ly()]
            if "timeline_rm" in e_dict.keys():
               [self.rm_timeline_event(e) for e in e_dict["timeline_rm"] if e["ly"] >= self.get_current_ly()]
            self.logger.info("Added '%s' expansion to %s" % (e_dict["name"], self))

        self.logger.info("Successfully added %s expansions to %s" % (len(e_list), self))
        self.save()


    def rm_expansions(self, e_list=[]):
        """ Takes a list of expansion handles and then removes them them from the
        settlement, undoing Timeline updates, etc. as required by the expansion
        asset definitions. """

        E = expansions.Assets()

        # prune the list to reduce risk of downstream cock-ups
        for e_handle in e_list:
            if e_handle not in E.get_handles():
                e_list.remove(e_handle)
                self.logger.warn("Unknown expansion handle '%s' is being ignored!" % (e_handle))
            if e_handle not in self.settlement["expansions"]:
                e_list.remove(e_handle)
                self.logger.warn("Expansion handle '%s' is not in %s" % (e_handle, self))

        #
        #   here is where we process the expansion dictionary
        #
        for e_handle in e_list:
            e_dict = E.get_asset(e_handle)
            self.log_event("Removing '%s' (%s) expansion content!" % (e_dict["name"], e_dict["handle"]))

            self.settlement["expansions"].remove(e_handle)

            try:
                if "timeline_add" in e_dict.keys():
                   [self.rm_timeline_event(e) for e in e_dict["timeline_add"] if e["ly"] >= self.get_current_ly()]
            except Exception as e:
                self.logger.error("Could not remove timeline events for %s expansion!" % e_dict["name"])
                self.logger.exception(e)
                raise
            try:
                if "timeline_rm" in e_dict.keys():
                   [self.add_timeline_event(e) for e in e_dict["timeline_rm"] if e["ly"] >= self.get_current_ly()]
            except Exception as e:
                self.logger.error("Could not add previously removed timeline events for %s expansion!" % e_dict["name"])
                self.logger.exception(e)
                raise

            self.logger.info("Removed '%s' expansion from %s" % (e_dict["name"], self))

        self.logger.info("Successfully removed %s expansions from %s" % (len(e_list), self))
        self.save()


    def add_timeline_event(self, e={}):
        """ Adds a timeline event to self.settlement["timeline"]. Expects a dict
        containing the whole event's data: no lookups here. """

        timeline = self.settlement["timeline"]
        t_index, t_object = utils.get_timeline_index_and_object(timeline, e["ly"]);

        timeline.remove(t_object)

        # try to improve the event if we've got a handle on it
        if "handle" in e.keys() and e["type"] in "story_event":
            E = events.Assets()
            e.update(E.get_asset(e["handle"]))

        if not e["type"] in t_object.keys():
            t_object[e["type"]] = []

        if not e in t_object[e["type"]]:
            t_object[e["type"]].append(e)
        else:
            self.logger.warn("Ignoring attempt to add duplicate event to %s timeline!" % (self))
            return False

        timeline.insert(t_index,t_object)

        self.settlement["timeline"] = timeline

        if "user_login" in e.keys():
            self.log_event("%s added '%s' to Lantern Year %s" % (e["user_login"], e["name"], e["ly"]))
        else:
            self.log_event("Automatically added '%s' to Lantern Year %s" % (e["name"], e["ly"]))

        # finish with a courtesy save
        self.save()



    def rm_timeline_event(self, e={}):
        """ Removes a timeline event from self.settlement["timeline"]. Expects a
        dict containing, at a minimum, an ly and a name for the event (so we can
        use this to remove custom events. """

        timeline = self.settlement["timeline"]
        t_index, t_object = utils.get_timeline_index_and_object(timeline, e["ly"]);

        timeline.remove(t_object)
        for i in t_object[e["type"]]:
            if "name" in i.keys() and e["name"] == i["name"]:
                t_object[e["type"]].remove(i)
                break
        timeline.insert(t_index, t_object)

        self.settlement["timeline"] = timeline

        if "user_login" in e.keys():
            self.log_event("%s removed '%s' from Lantern Year %s" % (e["user_login"], e["name"], e["ly"]))
        else:
            self.log_event("Automatically removed '%s' from Lantern Year %s" % (e["name"], e["ly"]))

        #finish with a courtesy save
        self.save()


    def update_nemesis_levels(self, params):
        """ Updates a settlement's 'nemesis_encounters' array/list for a nemesis
        monster handle. """

        handle = params["handle"]
        levels = params["levels"]

        if handle not in self.settlement["nemesis_monsters"]:
            self.logger.error("Cannot update nemesis levels for '%s' (nemesis is not in 'nemesis_monsters' list for %s)" % (handle, self))
        else:
            self.settlement["nemesis_encounters"][handle] = levels
            self.logger.debug("Updated 'nemesis_encounters' for %s" % self)
            self.save()


    def get_innovation_deck(self):
        """ Uses the settlement's current innovations to create an Innovation
        Deck, i.e. a list of innovation handle/name pairs. """

        I = innovations.Assets()
        self.logger.warn("NOT IMPLEMENTED!!!!!")


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
        self.logger.info("[%s] added a settlement note to %s" % (n["author"], self))


    def rm_settlement_note(self, n={}):
        """ Removes a note from MDB. Expects a dict with one key. """

        utils.mdb.settlement_notes.remove({"settlement": self.settlement["_id"], "js_id": n["js_id"]})
        self.logger.info("[%s] removed a settlement note from %s" % (n["user_login"], self))


    def get_locations_options(self):
        """ Returns a list of dictionaries where each dict is a location def-
        inition of a location that the settlement does not have, but could
        want to add. Think of it as a location deck. """

        #   first, get an asset collection and the always available locations from
        #   the campaign and the expansions

        L = locations.Assets()
        c_dict = self.get_campaign(dict)
        always_available = c_dict["always_available"]["location"]

        for e in self.get_expansions(dict).keys():
            e_dict = self.get_expansions(dict)[e]
            if "always_available" in e_dict.keys() and "location" in e_dict["always_available"].keys():
                e_loc_names = e_dict["always_available"]["location"]
                always_available.extend(e_loc_names)

        #   next, form a "base" options list by checking to see which of the
        #   always available locations are already present 
        base_options = []
        for l in always_available:
            if l not in self.settlement["locations"]:
                base_options.append(l)

        #   once we've got a "base", check the settlement's current locations,
        #   and, if present, use them to improve the base list by checking them
        #   for consequences

        for l in self.settlement["locations"]:
            l_dict = L.get_asset_from_name(l)
            if "consequences" in l_dict.keys():
                base_options.extend(l_dict["consequences"])

        #   remove dupes from base options
        base_options = set(base_options)

        #   next, do removes: anything that's already in locations gets removed
        #   and then anything that's forbidden by the campaign gets removed.

        for l in self.settlement["locations"]:
            if l in base_options:
                base_options.remove(l)
        if "forbidden" in c_dict.keys() and "location" in c_dict["forbidden"].keys():
            for f in c_dict["forbidden"]["location"]:
                if f in base_options:
                    base_options.remove(f)

        # finally, convert our list of names (soon to be handles) into a list of
        # dictionaries (i.e. JSON) that can be used to power the UI

        final_list = []
        base_options = set(base_options)
        for l in sorted(base_options):
            loc_asset = L.get_asset_from_name(l)
            if loc_asset is not None:
                final_list.append(loc_asset)
            else:
                self.logger.error("None type location asset retrieved for handle '%s'" % l)

        return final_list


    def get_milestones_options(self):
        """ Returns a list of dictionaries where each dict is a milestone def-
        inition. Useful for front-end stuff. """

        M = milestone_story_events.Assets()

        output = []
        for m_handle in self.get_campaign(dict)["milestones"]:
            output.append(M.get_asset(m_handle))

        return output


    def get_principles_options(self):
        """ Returns a dict (JSON) meant to be interated over in an ng-repeat on
        the Settlement Sheet. """

        I = innovations.Assets()

        p_handles = self.get_campaign(dict)["principles"]
        all_principles = {}
        for p_handle in p_handles:
            p_dict = I.get_principle(p_handle)
            all_principles[p_dict["name"]] = p_dict

        sorting_hat = {}
        for p in all_principles.keys():
            sorting_hat[all_principles[p]["sort_order"]] = all_principles[p]

        output = []
        for n in sorted(sorting_hat.keys()):

            p_dict = sorting_hat[n]
            p_dict["options"] = {}

            for o in p_dict["option_handles"]:
                o_dict = I.get_asset(o)

                selected=False
                if o_dict["name"] in self.settlement["principles"]:
                    selected=True

                o_dict.update({"input_id": "%s_%s_selector" % (p_dict["handle"],o), "checked": selected})
                p_dict["options"][o] = o_dict

            p_dict["form_handle"] = "set_principle_%s" % p_dict["name"]
            output.append(p_dict)

        return output


    def get_special_showdowns(self):
        """ Returns a list of monster handles representing the available special
        showdown monsters, given campaign and expansion assets. """

        output = []

        if "special_showdowns" in self.get_campaign(dict).keys():
            output.extend(self.get_campaign(dict)["special_showdowns"])

        for exp in self.get_expansions(dict).keys():
            e_dict = self.get_expansions(dict)[exp]
            if "special_showdowns" in e_dict.keys():
                output.extend(e_dict["special_showdowns"])

        return list(set(output))


    def get_monster_options(self, monster_type):
        """ Returns a list of available nemesis or quarry monster handles for
        use with the Settlement Sheet controls.

        The 'monster_type' kwarg should be something such as 'nemesis_monsters'
        that will be present in our campaign and expansion definitions.
        """

        options = []
        c_dict = self.get_campaign(dict)

        # first check our campaign and expansion assets, and get all options
        if monster_type in self.get_campaign(dict):
            c_monsters = self.get_campaign(dict)[monster_type]
            options.extend(c_monsters)

        for exp in self.get_expansions(dict):
            e_dict = self.get_expansions(dict)[exp]
            if monster_type in e_dict.keys():
                options.extend(e_dict[monster_type])

        # now convert our list into a set (just in case) and then go on to
        # remove anything we've already got present in the settlement
        option_set = set(options)
        for n in self.settlement[monster_type]:
            if n in option_set:
                option_set.remove(n)

        # check the remaining to see if they're selectable:
        option_set = list(option_set)
        final_set = []
        for m in option_set:
            M = monsters.Monster(m)
            if M.is_selectable():
                final_set.append(m)

        # remove anything that the campaign forbids
        forbidden = []
        if "forbidden" in c_dict.keys() and monster_type in c_dict["forbidden"].keys():
            forbidden.extend(c_dict["forbidden"][monster_type])
        for m_handle in forbidden:
            if m_handle in final_set:
                final_set.remove(m_handle)

        # now turn our set
        output = []
        for m in sorted(list(final_set)):
            M = monsters.Monster(m)
            output.append({
                "handle": M.handle,
                "name": M.name,
            })

        return output


    def get_timeline_monster_event_options(self, context=None):
        """ Returns a sorted list of strings (they call it an 'array' in JS,
        because they fancy) representing the settlement's possible showdowns,
        given their quarries, nemeses, etc.

        The idea here is that you specify a 'context' that has to do with user
        needs, e.g. 'showdown_options', to get back an appropriate list.
        """

        # use context to get a list of candidate handles

        candidate_handles = []
        if context == "showdown_options":
            candidate_handles.extend(self.settlement["quarries"])
        elif context == "nemesis_encounters":
            candidate_handles.extend(self.settlement["nemesis_monsters"])
            for n in self.get_campaign(dict)["nemesis_monsters"]:
                M = monsters.Monster(n)
                if M.is_final_boss():
                    candidate_handles.append(M.handle)
        elif context == "defeated_monsters":
            candidate_handles.extend(self.settlement["quarries"])
            candidate_handles.extend(self.settlement["nemesis_monsters"])
            candidate_handles.extend(self.get_special_showdowns())
        elif context == "special_showdown_options":
            candidate_handles.extend(self.get_special_showdowns())
        else:
            self.logger.warn("Unknown 'context' for get_monster_options() method!")

        # now create the output list based on our candidates
        output = []

        # this context wants handles back
        if context == "nemesis_encounters":
            for m in candidate_handles:
                M = monsters.Monster(m)
                if not M.is_selectable():
                    candidate_handles.remove(m)

        for m in candidate_handles:
            M = monsters.Monster(m)

            # hack the prologue White Lion in
            if M.handle == "white_lion":
                output.append("White Lion (First Story)")

            if M.is_unique():
                output.append(M.name)
            else:
                for l in range(M.levels):
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

        s_expansions = list(set(self.settlement["expansions"]))

        if return_type == dict:
            E = expansions.Assets()
            exp_dict = {}
            for exp_handle in s_expansions:
                exp_dict[exp_handle] = E.get_asset(exp_handle)
            return exp_dict

        elif return_type == "comma-delimited":
            if s_expansions == []:
                return None
            else:
                return ", ".join(s_expansions)

        return s_expansions


    def get_event_log(self, return_type=None):
        """ Returns the settlement's event log as a cursor object unless told to
        do otherwise."""

        event_log = utils.mdb.settlement_events.find(
            {
            "settlement_id": self.settlement["_id"]
            }
        ).sort("created_on",1)

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

        # check to see if the campaign forbids the asset
        if "forbidden" in self.get_campaign(dict):
            c_dict = self.get_campaign(dict)
            for f_key in c_dict["forbidden"]:
                if "type" in asset_dict.keys() and asset_dict["type"] == f_key:
                    if asset_dict["handle"] in c_dict["forbidden"][f_key]:
                        return False
                    elif asset_dict["name"] in c_dict["forbidden"][f_key]:
                        return False

        return True


    #
    #   update methods here
    #

    def update_sheet_from_dict(self, d):
        """ Accepts dict input and uses it to update the settlement sheet. Saves
        at the end. This is equivalent to the V1 modify() methods, as it only
        cares about certain keys (and ignores the ones it doesn't care about).
        """
        for sheet_k in d.keys():

            new_value = d[sheet_k]
            if new_value == "None":
                new_value = None

            if sheet_k == "current_quarry":
                self.settlement[sheet_k] = new_value
                self.log_event("Set current quarry to %s" % new_value)
            else:
                self.logger.warn("Unhandled update key: '%s' is being ignored!" % (sheet_k))

        # finally, save all changes
        self.logger.debug("%s settlement has been modified. Saving changes..." % self)
        self.save()





    #
    #   conversion and migration functions
    #

    def convert_expansions_to_handles(self):
        """ Takes a legacy settlement object and swaps out its expansion name
        key values for handles. """

        E = expansions.Assets()

        new_expansions = []
        for e in self.get_expansions():
            if e in E.get_handles():
                new_expansions.append(e)
            elif E.get_asset_from_name(e) is None:
                self.logger.warn("Expansion '%s' is being removed from %s" % (e, self))
            elif E.get_asset_from_name(e) is not None:
                new_expansions.append(E.get_asset_from_name(e)["handle"])
            else:
                msg = "The expansion asset '%s' from %s cannot be migrated!" % (e, self)
                self.logger.error(msg)
                Models.AssetMigrationError(msg)

        self.settlement["expansions"] = new_expansions
        self.settlement["expansions_version"] = 1.0
        self.logger.info("Migrated %s expansions to version 1.0. %s expansions were migrated!" % (self, len(new_expansions)))



    def convert_monsters_to_handles(self):
        """ Takes a legacy settlement object and swaps out its monster name
        lists for monster handles. """

        # create the v1.0 'nemesis_encounters' list and transcribe nemesis info
        self.settlement["nemesis_encounters"] = {}
        for n in self.settlement["nemesis_monsters"]:
            M = monsters.Monster(name=n)
            self.settlement["nemesis_encounters"][M.handle] = []
            n_levels = self.settlement["nemesis_monsters"][n]
            for l in n_levels:
                self.settlement["nemesis_encounters"][M.handle].append(int(l[-1]))

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
        """ Converts our old, pseudo-JSON timeline to the standard JSON one.

        The original/oldest legacy data model LY dictionaries look like this:

            {
                u'custom': [],
                u'story_event': u'Returning Survivors',
                u'year': 1
            }

        So, as we read individual LY dictionaries, bear in mind that each key
        within the dict might have a string as a value, rather than a list.

        Slightly less-fucked-up-looking LY dictionaries look like this:

            {
                u'quarry_event': [u'White Lion (First Story)'],
                u'settlement_event': [u'First Day'],
                u'year': 0
            }

        These are closer to what we want to have in the v1.0 timeline data
        model, i.e. the LY dict keys have lists as their values. The lists
        themselves aren't optimal, but they're closer to what we want.

        """

        old_timeline = self.settlement["timeline"]
        new_timeline = []

        all_events = events.Assets()

        for old_ly in old_timeline:         # this is an ly dict
            new_ly = {}
            for k in old_ly.keys():
                # k here is an event type key, such as 'quarry_event' or
                # 'settlement_event' or whatever. In the JSON timeline model,
                # each of these wants to be a key that points to a list, so
                # we initialize an empty list to hold the key's events

                event_type_list = []
                if type(old_ly[k]) == int:
                    new_ly[k] = old_ly[k]

                # handling for newer legacy timeline events
                elif type(old_ly[k]) == list:
                    for event in old_ly[k]:
                        if type(event) == dict:
                            event_type_list.append(event)
                        else:
                            event_dict = {"name": event}
                            if event in all_events.get_names():
                                event_dict.update(all_events.get_asset_from_name(event))
                            event_type_list.append(event_dict)
                    new_ly[k] = event_type_list

                # this is original data model (see doc string note)
                else:

                    err_msg = "Error converting legacy timeline! '%s' is an unknown event type!" % k

                    if k in ["settlement_event","story_event"]:
                        e = all_events.get_asset_from_name(old_ly[k])
                        if e is not None:
                            event_type_list.append(e)
                        else:
                            try:
                                event_root, event_parens = old_ly[k].split("(")
                                e = all_events.get_asset_from_name(event_root)
                                if e is not None:
                                    event_type_list.append(e)
                            except:
                                self.logger.error("Could not convert all '%s' events! for %s" % (k,self))
                                self.logger.error("Event value '%s' could not be converted!" % (old_ly[k]))
                                raise Exception("Fatal legacy timeline event conversion error!")

                    elif k in ["nemesis_encounter","quarry_event"]:
                        event_dict = {"name": old_ly[k]}
                        event_type_list.append(event_dict)

                    else:
                        self.logger.error(err_msg)
                        raise Exception(err_msg)

                    new_ly[k] = event_type_list

            new_timeline.append(new_ly)

        # finally, make sure that LYs are sorted: order is significant here
        sorting_hat = {}
        for ly in new_timeline:
            sorting_hat[int(ly["year"])] = ly
        new_timeline = [sorting_hat[ly_key] for ly_key in sorted(sorting_hat.keys())]


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





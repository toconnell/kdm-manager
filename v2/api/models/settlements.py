#!/usr/bin/python2.7

from bson import json_util
from bson.objectid import ObjectId
import collections
from copy import copy
from datetime import datetime, timedelta
from flask import Response, request
import json
import random
import time

import Models
import assets
from models import campaigns, cursed_items, epithets, expansions, survivors, weapon_specializations, weapon_masteries, causes_of_death, innovations, survival_actions, events, abilities_and_impairments, monsters, milestone_story_events, locations, causes_of_death, names
import settings
import utils


class Assets(Models.AssetCollection):
    """ This is a weird one, because the "Assets" that go into creating a
    settlement or working with a settlement are kind of...the whole manager.
    Nevertheless, this odd-ball Assets() class is used to represent options
    for new settlements. """


    def __init__(self, *args, **kwargs):
        self.assets = {}
        self.type = "new_settlement_assets"
        Models.AssetCollection.__init__(self,  *args, **kwargs)


    def serialize(self):
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

        output["special"] = survivors.Assets().get_specials().keys()

        return output



class Settlement(Models.UserAsset):
    """ This is the base class for all expansions. Private methods exist for
    enabling and disabling expansions (within a campaign/settlement). """

    def __init__(self, *args, **kwargs):
        self.collection="settlements"
        self.object_version=0.41
        Models.UserAsset.__init__(self,  *args, **kwargs)
        self.normalize_data()


    def new(self):
        """ Creates a new settlement. Expects a fully-loaded request, i.e. with
        an initialized User object, json() params, etc.

        Think of this method as an alternate form of Models.UserAsset.load()
        where, instead of getting a document from MDB and setting attribs from
        that, we have to create the document (and touch it up) to complete
        the load() request.

        The basic order-of-operations logic here is that we do a bunch of stuff
        to create what ammounts to the settlement 'sheet' and then save it to
        the MDB.

        Once it's saved, we call the base class load() method to initialize the
        object.

        Finally, once its initialized, we can use normal methods to apply what-
        ever other changes we need to apply (based on user params, etc.).

        """

        self.logger.info("%s creating a new settlement..." % request.User)
        self.logger.debug("%s new settlement params: %s" % (request.User, request.json))

        settlement = {
            # meta / admin
            "created_on": datetime.now(),
            "created_by": request.User._id,
            "admins": [request.User.login],
            "meta": {
                "timeline_version":     1.1,
                "campaign_version":     1.0,
                "monsters_version":     1.0,
                "expansions_version":   1.0,
                "innovations_version":  1.0,
            },

            # sheet
            "name": request.json.get("name", None),
            "campaign": request.json.get("campaign", "people_of_the_lantern"),
            "lantern_year":             0,
            "population":               0,
            "death_count":              0,
            "survival_limit":           1,
            "lost_settlements":         0,
            "expansions":               [],
            "milestone_story_events":   [],
            "innovations":              [],
            "locations":                [],
            "defeated_monsters":        [],
            "principles":               [],
            "storage":                  [],
            "custom_epithets":          [],
        }


        # set the settlement name before we save to MDB
        if settlement["name"] is None and request.User.get_preference("random_names_for_unnamed_assets"):
            N = names.Assets()
            settlement["name"] = N.get_random_settlement_name()
            self.logger.info("%s selected random settlement name due to user preference!" % request.User)
        elif settlement["name"] is None and not request.User.get_preference("random_names_for_unnamed_assets"):
            settlement["name"] = "Unknown"
            self.logger.info("%s set settlement name to 'Unknown' due to user preference!" % request.User)


        #
        #   This is where we save and load(); use self.settlement from here
        #

        self._id = utils.mdb.settlements.insert(settlement)
        self.logger.debug("%s new settlement _id=%s" % (request.User, self._id))
        self.load() # uses self._id

        # initialize methods

        self.initialize_sheet()
        self.initialize_timeline()

        # check params for additional expansions
        req_expansions = request.json.get("expansions", [])
        for e in req_expansions:
            if e not in self.settlement["expansions"]:
                self.settlement["expansions"].append(e)

        # add all expansions
        all_expansions = self.settlement["expansions"]
        self.settlement["expansions"] = []
        self.add_expansions(all_expansions)

        # process 'special' params here
        #   COMING SOON

        # finally, add pre-fab survivors
        #   COMING SOON

        # log settlement creation and save/exit
#        self.logger.debug(self.settlement)

        self.logger.info("%s created new %s and applied all user params successfully!" % (request.User, self))
        self.save()


    def normalize_data(self):
        """ Makes sure that self.settlement is up to our current standards. """

        self.perform_save = False

        self.bug_fixes()
        self.baseline_data_model()
        self.migrate_settlement_notes()

        #
        #       timeline migrations
        #
        if self.settlement["meta"].get("timeline_version", None) is None:
            self.convert_timeline_to_JSON()
            self.perform_save = True

        if self.settlement["meta"]["timeline_version"] < 1.1:
            self.convert_timeline_quarry_events()
            self.perform_save = True

        #
        #       other migrations
        #
        if self.settlement["meta"].get("campaign_version", None) is None:
            self.convert_campaign_to_handle()
            self.perform_save = True

        if self.settlement["meta"].get("monsters_version", None) is None:
            self.convert_monsters_to_handles()
            self.perform_save = True

        if self.settlement["meta"].get("expansions_version", None) is None:
            self.convert_expansions_to_handles()
            self.perform_save = True

        if self.settlement["meta"].get("innovations_version", None) is None:
            self.convert_innovations_to_handles()
            self.perform_save = True

        # finish
        if self.perform_save:
            self.logger.info("%s settlement modified! Saving changes..." % self)
            self.save()


    def serialize(self):
        """ Renders the settlement, including all methods and supplements, as
        a monster JSON object. This is where all views come from."""

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

        # create game_assets
        output.update({"game_assets": {}})
        output["game_assets"].update(self.get_available_assets(innovations))
        output["game_assets"].update(self.get_available_assets(locations))
        output["game_assets"].update(self.get_available_assets(abilities_and_impairments))
        output["game_assets"].update(self.get_available_assets(weapon_specializations))
        output["game_assets"].update(self.get_available_assets(weapon_masteries))
        output["game_assets"].update(self.get_available_assets(cursed_items))
        output["game_assets"].update(self.get_available_assets(survival_actions))
        output["game_assets"].update(self.get_available_assets(events))
        output["game_assets"].update(self.get_available_assets(monsters))
        output["game_assets"].update(self.get_available_assets(causes_of_death, handles=False))
        output["game_assets"].update(self.get_available_assets(epithets))

            # options (i.e. decks)
        output["game_assets"]["locations_options"] = self.get_locations_options()
        output["game_assets"]["principles_options"] = self.get_principles_options()
        output["game_assets"]["milestones_options"] = self.get_milestones_options()
        output["game_assets"]["milestones_dictionary"] = self.get_milestones_options(dict)

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
        output["game_assets"]["available_survival_actions"] = self.get_available_survival_actions()


        # finally, return a JSON string of our object
        return json.dumps(output, default=json_util.default)



    #
    #   meta/check/query methods here
    #

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
    #   Initialization methods. Be careful with these because every single one
    #   of them does massive overwrites and doesn't ask for permission, if you
    #   know what I mean.
    #

    def initialize_sheet(self):
        """ Initializes the settlement sheet according to the campaign
        definition's 'settlement_sheet_init' attribute. Meant to be used when
        creating new settlements. """

#        self.logger.debug("%s is initializing the sheet for %s" % (request.User, self))
        c_dict = self.get_campaign(dict)
        for init_key in c_dict["settlement_sheet_init"].keys():
            self.settlement[init_key] = copy(c_dict["settlement_sheet_init"][init_key])
        self.logger.info("%s initialized settlement sheet for '%s'" % (request.User, self))


    def initialize_timeline(self):
        """ Meant to be called during settlement creation, this method
        completely overwrites the settlement's timeline with the timeline
        'template' from the settlement's campaign.

        DO NOT call this method on an active/live settlement, unless you really
        know what you're doing.

        """

#        self.logger.debug("%s is initializing the timeline for %s" % (request.User, self))

        template = self.get_campaign(dict)["timeline"]
        E = events.Assets()

        self.settlement["timeline"] = []
        for year_dict in template:
            new_year = {}
            for k in year_dict.keys():
                if k == "year":
                    new_year[k] = year_dict[k]
                else:
                    new_year[k] = []
                    for event_dict in year_dict[k]:
                        try:
                            if "handle" in event_dict.keys():
                                event_dict.update(E.get_asset(event_dict["handle"]))
                        except TypeError:
                            self.logger.error("%s failed to initialize timeline for %s" % (request.User, self))
                            self.logger.error("%s event handle '%s' does not exist!" % (request.User, event_dict))
                            raise
                    new_year[k].append(event_dict)
            self.settlement["timeline"].append(new_year)

        self.logger.info("%s initialized timeline for %s!" % (request.User, self))



    #
    #   add/rm methods start here!
    #

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
               [self.add_timeline_event(e, save=False) for e in e_dict["timeline_add"] if e["ly"] >= self.get_current_ly()]
            if "timeline_rm" in e_dict.keys():
               [self.rm_timeline_event(e, save=False) for e in e_dict["timeline_rm"] if e["ly"] >= self.get_current_ly()]
            if "rm_nemesis_monsters" in e_dict.keys():
                for m in e_dict["rm_nemesis_monsters"]:
                    if m in self.settlement["nemesis_monsters"]:
                        self.settlement["nemesis_monsters"].remove(m)
                        self.logger.info("Removed '%s' from %s nemesis monsters." % (m, self))

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
                   [self.rm_timeline_event(e, save=False) for e in e_dict["timeline_add"] if e["ly"] >= self.get_current_ly()]
            except Exception as e:
                self.logger.error("Could not remove timeline events for %s expansion!" % e_dict["name"])
                self.logger.exception(e)
            try:
                if "timeline_rm" in e_dict.keys():
                   [self.add_timeline_event(e, save=False) for e in e_dict["timeline_rm"] if e["ly"] >= self.get_current_ly()]
            except Exception as e:
                self.logger.error("Could not add previously removed timeline events for %s expansion!" % e_dict["name"])
                self.logger.exception(e)

            if "rm_nemesis_monsters" in e_dict.keys():
                for m in e_dict["rm_nemesis_monsters"]:
                    if m not in self.settlement["nemesis_monsters"]:
                        self.settlement["nemesis_monsters"].append(m)
                        self.logger.info("Added '%s' to %s nemesis monsters." % (m, self))

            self.logger.info("Removed '%s' expansion from %s" % (e_dict["name"], self))

        self.logger.info("Successfully removed %s expansions from %s" % (len(e_list), self))
        self.save()


    def add_innovation(self):
        """ Adds an innovation to the settlement. Does business logic. """

        # first, try to initialize an innovations.Innovation object
        try:
            I = innovations.Innovation(self.params["handle"])
        except:
            self.logger.error("Could not initialize innovation asset from dict: %s" % self.params["handle"])
            self.logger.error("Unable to add '%s' to %s innovations!" % (self.params["handle"], self))
            self.logger.error("Bad params were: %s" % self.params)
            raise Exception

        if I.name in self.settlement["innovations"]:
            self.logger.warn("Ignoring attempt to add duplicate %s to %s" % (I, self))
            return False


        # finally, do it

        self.settlement["innovations"].append(I.handle)

        if hasattr(I, "levels") and not self.settlement.get("innovation_levels", False):
            self.settlement["innovation_levels"] = {}
        if hasattr(I, "levels"):
            self.settlement["innovation_levels"][I.handle] = 1

        self.log_event("Added '%s' to settlement innovations." % (I.name), event_type="add_innovation")

        self.save()


    def rm_innovation(self):
        """ Removes an innovation from the settlement. """

        # first, try to initialize an innovations.Innovation object
        try:
            I = innovations.Innovation(self.params["handle"])
        except:
            self.logger.error("Could not initialize innovation asset from dict: %s" % self.params["handle"])
            self.logger.error("Unable to remove '%s' from %s innovations!" % (self.params["handle"], self))
            self.logger.error("Bad params were: %s" % self.params)
            raise Exception

        if I.handle not in self.settlement["innovations"]:
            self.logger.warn("Ignoring attempt to remove %s to %s innovations (because it is not there)." % (I, self))
            return False

        self.settlement["innovations"].remove(I.handle)
        self.log_event("Removed '%s' from settlement innovations." % (I.name), event_type="rm_innovation")
        self.save()


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


    def add_timeline_event(self, e={}, save=True):
        """ Adds a timeline event to self.settlement["timeline"]. Expects a dict
        containing the whole event's data: no lookups here. """

        if e.get("excluded_campaign", None) == self.settlement["campaign"]:
            self.logger.warn("Ignoring attempt to add event to excluded campaign: %s" % e)
            return False

        timeline = self.settlement["timeline"]
        try:
            t_index, t_object = utils.get_timeline_index_and_object(timeline, e["ly"]);
        except Exception as excep:
            self.logger.error("Timeline event cannot be processed: %s" % e)
            self.logger.exception(excep)
            return False


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
        if save:
            self.save()


    def rm_timeline_event(self, e={}, save=True):
        """ Removes a timeline event from self.settlement["timeline"]. Expects a
        dict containing, at a minimum, an ly and a name for the event (so we can
        use this to remove custom events. """

        if e.get("excluded_campaign", None) == self.settlement["campaign"]:
            self.logger.warn("Ignoring attempt to add event to excluded campaign: %s" % e)
            return False

        timeline = self.settlement["timeline"]
        try:
            t_index, t_object = utils.get_timeline_index_and_object(timeline, e["ly"]);
        except Exception as excep:
            self.logger.debug(timeline)
            self.logger.error("Timeline event cannot be processed: %s" % e)
            self.logger.exception(excep)
            return False


        success = False

        timeline.remove(t_object)

        for i in t_object[e["type"]]:
            if "name" in i.keys() and "name" in e.keys() and e["name"] == i["name"]:
                t_object[e["type"]].remove(i)
                success = True
                break
            elif "handle" in i.keys() and "handle" in e.keys() and e["handle"] == i["handle"]:
                t_object[e["type"]].remove(i)
                success = True
                break
            else:
                self.logger.warn("Key errors encountered when comparing events %s and %s" % (e, i) )

        timeline.insert(t_index, t_object)

        if success:
            self.settlement["timeline"] = timeline
            self.logger.debug("Removed %s from %s timeline!" % (e, self))

            try:
                if "user_login" in e.keys():
                    self.log_event("%s removed '%s' from Lantern Year %s" % (e["user_login"], e["name"], e["ly"]))
                else:
                    self.log_event("Automatically removed '%s' from Lantern Year %s" % (e["name"], e["ly"]))
            except Exception as excep:
                self.logger.error("Could not create settlement event log message for %s" % self)
                self.logger.exception(excep)
        else:
            self.logger.error("Event could not be removed from %s timeline! %s" % (self, e))

        if save:
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



    #
    #   get/set methods start here!
    #

    def set_current_quarry(self):
        """ Sets the self.settlement["current_quarry"] attrib. """

        new_value = self.params["current_quarry"]
        self.settlement["hunt_started"] = datetime.now()
        self.settlement["current_quarry"] = new_value
        self.log_event("Set target monster to %s" % new_value)
        self.save()


    def set_innovation_level(self):
        """ Sets self.settlement["innovation_levels"][innovation] to an int. """

        try:
            handle = self.params["handle"]
            level = self.params["level"]
        except Exception as e:
            self.logger.error("Could not set settlement innovation level from JSON request: %s" % self.params)
            raise

        if handle not in self.settlement["innovations"]:
            self.logger.error("Could not set settlement innovation level for '%s', because that innovation is not included in the %s innovations list: %s" % (handle, self, self.settlement["innovations"]))
        else:
            self.settlement["innovation_levels"][handle] = int(level)

        self.log_event("Set '%s' innovation level to %s." % (handle, level), event_type="set_innovation_level")

        self.save()


    def get_founder(self):
        """ Helper method to rapidly get the mdb document of the settlement's
        creator/founder. """
        return utils.mdb.users.find_one({"_id": self.settlement["created_by"]})


    def get_innovation_deck(self, return_type=False):
        """ Uses the settlement's current innovations to create an Innovation
        Deck, which, since it's a pure game asset, is returned as a list of
        names, rather than as an object or as handles, etc."""

        #
        #   This is a port of the legacy method, but this method combines every-
        #   thing that the legacy app did in like, three different places to be
        #   the ultimately, single/central source of truth
        #
        #   The general logic of this method is that we start with a huge list
        #   of all possible options and then filter it down to a baseline.
        #
        #   Once we've got that baseline, we check the individual innovations
        #   we've got left to see if we keep them in the deck. 

        time.sleep(1)   # hack city! makes it feel more like something is
                        # happening; slows the users down

        I = innovations.Assets()
        available = dict(self.get_available_assets(innovations)["innovations"])

        # remove principles and innovations from expansions we don't use
        for a in available.keys():
            if available[a].get("type",None) == "principle":
                del available[a]

        # remove ones we've already got and make a list of consequences
        consequences = []
        for i_handle in self.settlement["innovations"]:
            if available[i_handle].get("consequences",None) is not None:
                consequences.extend(available[i_handle]["consequences"])
            if i_handle in available.keys():
                del available[i_handle]
        consequences = list(set(consequences))


        # now, we use the baseline and the consequences list to build a deck
        deck_dict = {}

        for c in consequences:
            if c not in self.settlement["innovations"]:
                if c in available.keys():
                    del available[c]
                deck_dict[c] = I.get_asset(c)


        # we've got a good list, but we still need to check available inno-
        # vations for some attribs that might force them into the list.
        for i in available:
            available_if = available[i].get("available_if",None)
            if available_if is not None:
                for tup in available_if:
                    asset,collection = tup
                    if asset in self.settlement[collection]:
                        deck_dict[i] = I.get_asset(i)

        # finally, create a new list and use the deck dict to 
        deck_list = []
        for k in deck_dict.keys():
            deck_list.append(deck_dict[k]["name"])

        if return_type == "JSON":
            return json.dumps(sorted(deck_list))
        else:
            return deck_dict


    def get_settlement_notes(self):
        """ Returns a list of mdb.settlement_notes documents for the settlement.
        They're sorted in reverse chronological, because the idea is that you're
        goign to turn this list into JSON and then use it in the webapp. """

        notes = utils.mdb.settlement_notes.find({"settlement": self.settlement["_id"]}).sort("created_on",-1)
        if notes is None:
            return []
        return [n for n in notes]


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


    def get_milestones_options(self, return_type=list):
        """ Returns a list of dictionaries where each dict is a milestone def-
        inition. Useful for front-end stuff. """

        M = milestone_story_events.Assets()


        if return_type==dict:
            output = {}
            for m_handle in self.get_campaign(dict)["milestones"]:
                output[m_handle] = M.get_asset(m_handle)
            return output
        elif return_type==list:
            output = []
            for m_handle in self.get_campaign(dict)["milestones"]:
                output.append(M.get_asset(m_handle))
            return output
        else:
            self.logger.error("get_milestones_options() does not support return_type=%s" % return_type)
            raise AttributeError


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
                if i in all_innovations.get_handles():
                    i_dict = all_innovations.get_asset(i)
                    output[i_dict["handle"]] = i_dict
            return output

        return s_innovations


    def get_available_survival_actions(self):
        """ Returns a dictionary of survival actions available to the settlement
        and its survivors. """

        all_survival_actions = survival_actions.Assets()

        sa = {"dodge": all_survival_actions.get_asset("dodge")}
        for k,v in self.get_innovations(dict).iteritems():
            if "survival_action" in v.keys():
                sa_dict = all_survival_actions.get_asset_from_name(v["survival_action"])
                sa_dict["innovation"] = v["name"]
                sa[sa_dict["handle"]] = sa_dict
        return sa


    def get_players(self, return_type=None):
        """ Returns a list of dictionaries where each dict is a short summary of
        the significant attributes of the player, as far as the settlement is
        concerned.

        This is NOT the place to get full user information and these dicts are
        intentionally sparse for exactly that reason.

        Otherwise, use return_type="count" to get an int representation of the
        set of players. """

        player_set = set()
        survivors = utils.mdb.survivors.find({"settlement": self.settlement["_id"]})
        for s in survivors:
            player_set.add(s["email"])

        player_set = utils.mdb.users.find({"login": {"$in": list(player_set)}})

        if return_type == "count":
            return player_set.count()

        player_list = []
        for p in player_set:
            p_dict = {"login": p["login"], "_id": p["_id"]}
            if p["login"] in self.settlement["admins"]:
                p_dict["settlement_admin"] = True
            if p["_id"] == self.settlement["created_by"]:
                p_dict["settlement_founder"] = True

            player_list.append(p_dict)

        return player_list


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

            output.append(json.loads(S.serialize()))

        return output


    def get_campaign(self, return_type=None):
        """ Returns the campaign handle of the settlement as a string, if
        nothing is specified for kwarg 'return_type'.

        Use 'name' to return the campaign's name (from its definition).

        'return_type' can also be dict. Specifying dict gets the
        raw campaign definition from assets/campaigns.py. """

        C = campaigns.Assets()

        # sanity check; fail big if we can't pass this
        if self.settlement["campaign"] not in C.get_handles():
            err = "The handle '%s' does not reference any known campaign definition!" % self.settlement["campaign"]
            raise Models.AssetInitError(err)

        if return_type == 'name':
            return C.get_asset(self.settlement["campaign"])["name"]

        # handle return_type requests
        if return_type == dict:
            return C.get_asset(self.settlement["campaign"])

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


    def get_available_assets(self, asset_module=None, handles=True):
        """ Generic function to return a dict of available game assets based on
        their family. The 'asset_module' should be something such as,
        'cursed_items' or 'weapon_proficiencies', etc. that has an Assets()
        method.


        Use the 'handles' kwarg (boolean) to determine whether to return a list
        of asset dictionaries, or a dictionary of dictionaries (where asset
        handles are the keys.
        """

        if handles:
            available = {}
        else:
            available = []

        A = asset_module.Assets()

        if handles:
            for k in A.get_handles():
                item_dict = A.get_asset(k)
                if self.is_compatible(item_dict):
                    available.update({item_dict["handle"]: item_dict})
        else:
            for n in A.get_names():
                item_dict = A.get_asset_from_name(n)
                if self.is_compatible(item_dict):
                    available.append(item_dict)

        final = []
        if type(available) == list:
            final = sorted(available)
        else:
            final = collections.OrderedDict(sorted(available.items()))

        return {"%s" % (asset_module.__name__.split(".")[-1]): final}



    #
    #   bug fix, conversion and migration functions start here!
    #

    def bug_fixes(self):
        """ In which we burn CPU cycles to fix our mistakes. """

        # 2016-02-02 - Weapon Masteries bug
        I = innovations.Assets()
        for i in self.settlement["innovations"]:
            if len(i.split(" ")) > 1 and "-" in i.split(" "):
                self.logger.warn("Removing name '%s' from innovations for %s" % (i, self))
                self.settlement["innovations"].remove(i)
                replacement = I.get_asset_from_name(i)
                if replacement is not None:
                    self.settlement["innovations"].append(replacement["handle"])
                    self.logger.warn("Replaced '%s' with '%s'" % (i, replacement["handle"]))
                else:
                    self.logger.error("Could not find an asset with the name '%s' for %s. Failing..." % (i, self))
                self.perform_save = True


    def baseline_data_model(self):
        """ This checks the mdb document to make sure that it has basic aux-
        iliary and supplemental attribute keys. If it doesn't have them, they
        get added and we set self.perform_save = True. """

        if not "meta" in self.settlement.keys():
            self.logger.info("Creating 'meta' key for %s" % self)
            self.settlement["meta"] = {}
            for meta_key in ["timeline_version", "monsters_version","expansions_version"]:
                if meta_key in self.settlement:
                    self.settlement["meta"][meta_key] = self.settlement[meta_key]
                    del self.settlement[meta_key]
                    self.logger.info("Moved meta key '%s' to settlement 'meta' dict for %s" % (meta_key,self))
            self.perform_save = True

        if not "admins" in self.settlement.keys():
            self.logger.info("Creating 'admins' key for %s" % (self))
            creator = utils.mdb.users.find_one({"_id": self.settlement["created_by"]})
            self.settlement["admins"] = [creator["login"]]
            self.perform_save = True

        if not "custom_epithets" in self.settlement.keys():
            self.logger.info("Creating 'custom_epithets' key for %s" %(self))
            self.settlement["custom_epithets"] = []
            self.perform_save = True

        founder = self.get_founder()
        if not founder["login"] in self.settlement["admins"]:
            self.settlement["admins"].append(founder["login"])
            self.logger.debug("Adding founder '%s' to %s admins list." % (founder["login"], self))
            self.perform_save = True

        if not "expansions" in self.settlement.keys():
            self.logger.info("Creating 'expansions' key for %s" % (self))
            self.settlement["expansions"] = []
            self.perform_save = True


    def migrate_settlement_notes(self):
        """ In the legacy data model, settlement notes were a single string that
        got saved to MDB on the settlement (yikes!). If the settlement has the
        'settlement_notes' key, this method removes it and creates that string
        as a proper settlement_note document in mdb. """

        if self.settlement.get("settlement_notes", None) is None:
            return True
        else:
            self.logger.debug("Converting legacy 'settlement_notes' to mdb.settlement_notes doc!")

            s = str(int(time.time())) + str(self.settlement["_id"])
            bogus_id = ''.join(random.sample(s,len(s)))

            founder = self.get_founder()
            note = {
                "note": self.settlement["settlement_notes"].strip(),
                "author": founder["login"],
                "author_id": self.settlement["created_by"],
                "js_id": bogus_id,
                "lantern_year": self.get_current_ly(),
            }
            self.add_settlement_note(note)
            del self.settlement["settlement_notes"]
            self.perform_save = True


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
        self.settlement["meta"]["expansions_version"] = 1.0
        self.logger.info("Migrated %s expansions to version 1.0. %s expansions were migrated!" % (self, len(new_expansions)))


    def convert_innovations_to_handles(self):
        """ Swaps out expansion name key values for handles. """

        I = innovations.Assets()

        new_innovations = []
        conversions = 0
        for i in self.settlement["innovations"]:
            i_dict = I.get_asset_from_name(i)
            if i_dict is None:
                self.logger.warn("Could not migrate innovation '%s'!" % i)
            else:
                new_innovations.append(i_dict["handle"])
                self.logger.debug("Converted '%s' to '%s'" % (i, i_dict["handle"]))
                conversions += 1

        if "innovation_levels" in self.settlement.keys():
            for i_name in self.settlement["innovation_levels"].keys():
                i_dict = I.get_asset_from_name(i_name)
                if i_dict is None:
                    self.logger.warn("Could not convert location level for '%s'!" % i_name)
                else:
                    self.settlement["innovation_levels"][i_dict["handle"]] = self.settlement["innovation_levels"][i_name]
                    del self.settlement["innovation_levels"][i_name]
            self.logger.debug(self.settlement["innovation_levels"])

        self.settlement["innovations"] = new_innovations
        self.settlement["meta"]["innovations_version"] = 1.0
        self.logger.info("Converted %s innovations from names (legacy) to handles for %s" % (conversions, self))



    def convert_monsters_to_handles(self):
        """ Takes a legacy settlement object and swaps out its monster name
        lists for monster handles. """

        # create the v1.0 'nemesis_encounters' list and transcribe nemesis info
        self.settlement["nemesis_encounters"] = {}
        for n in self.settlement["nemesis_monsters"]:
            try:
                M = monsters.Monster(name=n)
                self.settlement["nemesis_encounters"][M.handle] = []
                n_levels = self.settlement["nemesis_monsters"][n]
                for l in n_levels:
                    self.settlement["nemesis_encounters"][M.handle].append(int(l[-1]))
            except Exception as e:
                self.logger.exception(e)
                self.logger.critical("%s nemesis encounter w/ '%s' cannot be migrated to 1.0 data model!" % (self,n))

        for list_key in ["quarries","nemesis_monsters"]:
            new_list = []
            old_list = self.settlement[list_key]
            for m in old_list:
                try:
                    M = monsters.Monster(name=m)
                    new_list.append(M.handle)
                except:
                    self.logger.exception(e)
                    self.logger.critical("%s monster '%s' will cannot be migrated to 1.0 data model!" % (self,m))

            self.settlement[list_key] = new_list

        self.settlement["meta"]["monsters_version"] = 1.0
        self.logger.debug("Migrated %s monster lists from legacy data model to 1.0." % self)


    def convert_campaign_to_handle(self):
        """ Takes a name string 'campaign' attribute from self.settlement and
        swaps it out for the handle for that campaign. Fails big if it can't."""

        # first, some basic defaulting for the oldest legacy settlements
        if not "campaign" in self.settlement.keys():
            self.settlement["campaign"] = "people_of_the_lantern"
            self.logger.warn("Defaulted %s 'campaign' attrib to %s" % (self, self.settlement["campaign"]))
            self.settlement["meta"]["campaign_version"] = 1.0
            return True

        incoming_name = self.settlement["campaign"]

        C = campaigns.Assets()

        sorting_hat = {}
        for handle in C.get_handles():
            c_dict = C.get_asset(handle)
            sorting_hat[c_dict["name"]] = handle

        try:
            self.settlement["campaign"] = sorting_hat[incoming_name]
        except Exception as e:
            self.logger.error("Coult not convert %s campaign attrib!" % self)
            self.logger.exception(e)
            raise

        self.settlement["meta"]["campaign_version"] = 1.0
        self.logger.debug("Migrated %s campaign attrib from '%s' to '%s'." % (self, incoming_name, self.settlement["campaign"]))


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
        new_timeline = utils.sort_timeline(new_timeline)

        self.settlement["timeline"] = new_timeline
        self.settlement["meta"]["timeline_version"] = 1.0
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
        self.settlement["meta"]["timeline_version"] = 1.1
        self.logger.debug("Migrated %s timeline to version 1.1" % (self))



    #
    #   finally, the request response router and biz logic. Don't write model
    #   methods below this one.
    #

    def request_response(self, action=None):
        """ Initializes params from the request and then response to the
        'action' kwarg appropriately. This is the ancestor of the legacy app
        assets.Settlement.modify() method. """

        if request.method != "GET":
            self.get_request_params()

        #
        #   simple GET type methods
        #
        if action == "get":
            return self.return_json()
        elif action == "event_log":
            return Response(response=self.get_event_log("JSON"), status=200, mimetype="application/json")
        elif action == "get_innovation_deck":
            return Response(response=self.get_innovation_deck("JSON"), status=200, mimetype="application/json")

        #
        #   misc. controllers and actions (most actions go here)
        #
        elif action == "add_expansions":
            self.add_expansions(self.params)
        elif action == "rm_expansions":
            self.rm_expansions(self.params)

        elif action == "set_current_quarry":
            self.set_current_quarry()

        elif action == "update_nemesis_levels":
            self.update_nemesis_levels(self.params)

        elif action == "add_timeline_event":
            self.add_timeline_event(self.params)
        elif action == "rm_timeline_event":
            self.rm_timeline_event(self.params)

        elif action == "add_innovation":
            self.add_innovation()
        elif action == "rm_innovation":
            self.rm_innovation()
        elif action == "set_innovation_level":
            self.set_innovation_level()

        #
        #   campaign notes controllers
        #
        elif action == "add_note":
            self.add_settlement_note(self.params)
        elif action == "rm_note":
            self.rm_settlement_note(self.params)


        #
        #   finally, the catch-all/exception-catcher
        #
        else:
            # unknown/unsupported action response
            self.logger.warn("Unsupported settlement action '%s' received!" % action)
            return utils.http_400


        # finish successfully
        return utils.http_200





# ~fin

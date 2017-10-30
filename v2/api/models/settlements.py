#!/usr/bin/python2.7

from bson import json_util
from bson.objectid import ObjectId
import collections
from copy import copy
from datetime import datetime, timedelta
from flask import Response, request
import inspect
import json
import random
import socket
import time

import Models
import assets
from models import survivors, campaigns, cursed_items, disorders, gear, endeavors, epithets, expansions, fighting_arts, weapon_specializations, weapon_masteries, causes_of_death, innovations, survival_actions, events, abilities_and_impairments, monsters, milestone_story_events, locations, causes_of_death, names, resources, storage, survivor_special_attributes, weapon_proficiency
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
        """ This is primarily used by the '/new_settlement' public route to
        indicate what options are available (in terms of asset handles) when
        creating a new settlement.

        Keep in mind that we DO NOT return all attributes of every campaign,
        expansion, survivor, etc. asset that we serialize here: that would a.)
        make the '/new_settlement' output really heavy/big, potentially
        hurting page load times, and b.) return mostly irrelevant stuff, e.g.
        back-end and meta data, timelines, etc.
        """
        output = {}

        for mod in [campaigns, expansions, survivors]:

            mod_string = "%s" % str(mod.__name__).split(".")[1]
            output[mod_string] = []

            CA = mod.Assets()

            for c in sorted(CA.get_handles()):
                asset = CA.get_asset(c)
                asset_repr = {"handle": c, "name": asset["name"]}
                for optional_key in ["subtitle", "default",'ui']:
                    if optional_key in asset.keys():
                        asset_repr[optional_key] = asset[optional_key]
                output[mod_string].append(asset_repr)

        S = survivors.Assets()
        output["specials"] = S.get_specials("JSON")

        return output



#
#   Settlement class object ground rules:
#
#       1. do not initialize a survivor here.
#       2. serialize() calls should be as 'light', i.e. specific, as possible
#       3. use self.Innovations (for example) instead of initializing a new
#           AssetCollection object
#

class Settlement(Models.UserAsset):
    """ This is the base class for all expansions. Private methods exist for
    enabling and disabling expansions (within a campaign/settlement). """

    def __init__(self, *args, **kwargs):
        self.collection="settlements"
        self.object_version=0.72
        Models.UserAsset.__init__(self,  *args, **kwargs)

        self.init_asset_collections()
        # now normalize
        if self.normalize_on_init:
            self.normalize()

#        if request.User.get_preference("update_timeline"):
#            self.update_timeline_with_story_events()

        # performance metering; active in dev
        self.metering = False
        if socket.getfqdn() != settings.get('api','prod_fqdn'):
            self.metering = True


    def init_asset_collections(self):
        """ Generally you want Models.UserAsset.load() to call this method. """

        self.Endeavors = endeavors.Assets()
        self.Events = events.Assets()
        self.Expansions = expansions.Assets()
        self.FightingArts = fighting_arts.Assets()
        self.Gear = gear.Assets()
        self.Innovations = innovations.Assets()
        self.Locations = locations.Assets()
        self.Milestones = milestone_story_events.Assets()
        self.Monsters = monsters.Assets()
        self.Names = names.Assets()
        self.Resources = resources.Assets()
#        self.Storage = storage.Assets()
        self.SpecialAttributes = survivor_special_attributes.Assets()
        self.SurvivalActions = survival_actions.Assets()
        self.Survivors = survivors.Assets()
        self.WeaponMasteries = weapon_masteries.Assets()


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
#        self.logger.debug("%s new settlement params: %s" % (request.User, self.params))

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
                "locations_version":    1.0,
                "principles_version":   1.0,
                'storage_version':      1.0,
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




        #
        #   This is where we save and load(); use self.settlement from here
        #

        self._id = utils.mdb.settlements.insert(settlement)
        self.load() # uses self._id

        # set the settlement name before we save to MDB
        s_name = settlement['name']
        if s_name is None and request.User.get_preference("random_names_for_unnamed_assets"):
            s_name = self.Names.get_random_settlement_name()
        elif s_name is None and not request.User.get_preference("random_names_for_unnamed_assets"):
            s_name = "Unknown"

        self.settlement['name'] = None
        self.set_name(s_name)


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
        if all_expansions != []:
            self.add_expansions(all_expansions)

        # handle specials, i.e. first story, seven swordsmen, etc.
        if self.params.get("specials", None) is not None:
            for special_handle in self.params["specials"]:
                self.new_settlement_special(special_handle)

        # prefab survivors go here
        if self.params.get("survivors", None) is not None:
            for s in self.params["survivors"]:
                s_dict = copy(self.Survivors.get_asset(s))
                attribs = s_dict["attribs"]
                attribs.update({"settlement": self._id})
                survivors.Survivor(new_asset_attribs=attribs, Settlement=self)
                if s_dict.get("storage", None) is not None:
                    self.settlement["storage"].extend(s_dict["storage"])

        # log settlement creation and save/exit
        self.save()


    def new_settlement_special(self, special_handle):
        """ Think of these as macros. Basically, you feed this a handle, it
        checks out the handle and then takes action based on it. """

        specials = self.Survivors.get_specials()
        script = copy(specials.get(special_handle, None))

        if script is None:
            return True

        # do random survivors
        if script.get("random_survivors", None) is not None:
            for s in script["random_survivors"]:
                n = copy(s)
                n.update({"settlement": self._id})
                N = survivors.Survivor(new_asset_attribs=n, Settlement=self)

        # then storage
        if script.get("storage", None) is not None:
            for d in script["storage"]:
                for i in range(d["quantity"]):
                    self.settlement["storage"].append(d["name"])

        # quarry
        if script.get("current_quarry", None) is not None:
            self.set_current_quarry(script["current_quarry"])

        # events
        if script.get("timeline_events", None) is not None:
            for event in script["timeline_events"]:
                self.add_timeline_event(event)

        self.log_event("Automatically applied '%s' parameters." % (script["name"]))


    def normalize(self):
        """ Makes sure that self.settlement is up to our current standards. """

        self.perform_save = False

        self.bug_fixes()
        self.baseline()
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

        if self.settlement["meta"].get("expansions_version", None) is None:
            self.convert_expansions_to_handles()
            self.perform_save = True

        if self.settlement["meta"].get("innovations_version", None) is None:
            self.convert_innovations_to_handles()
            self.perform_save = True

        if self.settlement["meta"].get("locations_version", None) is None:
            self.convert_locations_to_handles()
            self.perform_save = True

        if self.settlement["meta"].get("monsters_version", None) is None:
            self.convert_monsters_to_handles()
            self.perform_save = True

        if self.settlement["meta"].get("principles_version", None) is None:
            self.convert_principles_to_handles()
            self.perform_save = True

        if self.settlement["meta"].get("storage_version", None) is None:
            self.convert_storage()
            self.perform_save = True


        # enforce minimums
        self.enforce_minimums()

        # finish
        if self.perform_save:
            self.logger.info("%s settlement modified during normalization! Saving changes..." % self)
            self.save()


    def serialize(self, return_type=None):
        """ Renders the settlement, including all methods and supplements, as
        a monster JSON object. This is where all views come from."""

        # performance metering: activate in dev
        total_start = datetime.now()

        # do some tidiness operations first

        for k in ["locations","innovations","defeated_monsters"]:
            self.settlement[k] = sorted(self.settlement[k])

        # now start
        output = self.get_serialize_meta()
        output["meta"].update({
            'creator_email': utils.mdb.users.find_one({'_id': self.settlement["created_by"]})['login'],
            'age': utils.get_time_elapsed_since(self.settlement["created_on"], units='age'),
            'player_email_list': self.get_players('email'),
        })

        # retrieve user assets
        if return_type in [None, "sheet",'campaign','survivors']:
            output.update({"user_assets": {}})
            output["user_assets"].update({"players": self.get_players()})
            output["user_assets"].update({"survivors": self.get_survivors()})


        # create the sheet
        if return_type in [None, 'sheet', 'dashboard', 'campaign']:
            output.update({"sheet": self.settlement})
            output["sheet"].update({"campaign": self.campaign.handle})
            output["sheet"].update({"campaign_pretty": self.campaign.name})
            output["sheet"].update({"expansions": self.get_expansions()})
            output["sheet"].update({"expansions_pretty": self.get_expansions(str)})
            output["sheet"]["settlement_notes"] = self.get_settlement_notes()
            output["sheet"]["enforce_survival_limit"] = self.get_survival_limit(bool)
            output["sheet"]["minimum_survival_limit"] = self.get_survival_limit("min")
            output["sheet"]["minimum_death_count"] = self.get_death_count("min")
            output["sheet"]["minimum_population"] = self.get_population("min")
            output['sheet']['population_by_sex'] = self.get_population('sex')
            output['sheet']['monster_volumes'] = self.get_monster_volumes()
            output['sheet']['lantern_research_level'] = self.get_lantern_research_level()

        # create game_assets
        if return_type in [None, 'game_assets','campaign']:
            start = datetime.now()
            output.update({"game_assets": {}})
            output["game_assets"].update(self.get_available_assets(innovations))
            output["game_assets"].update(self.get_available_assets(locations, exclude_types=["resources","gear"]))
            output["game_assets"].update(self.get_available_assets(abilities_and_impairments))
            output["game_assets"].update(self.get_available_assets(weapon_specializations))
            output["game_assets"].update(self.get_available_assets(weapon_masteries))
            output["game_assets"].update(self.get_available_assets(weapon_proficiency, handles=False))
            output["game_assets"].update(self.get_available_assets(cursed_items))
            output["game_assets"].update(self.get_available_assets(survival_actions))
            output["game_assets"].update(self.get_available_assets(events))
            output["game_assets"].update(self.get_available_assets(monsters))
            output["game_assets"].update(self.get_available_assets(causes_of_death, handles=False))
            output["game_assets"].update(self.get_available_assets(epithets))
            output["game_assets"].update(self.get_available_assets(fighting_arts))
            output["game_assets"].update(self.get_available_assets(disorders))
            output['game_assets'].update(self.get_available_assets(endeavors))

            # options (i.e. decks)
            output["game_assets"]["pulse_discoveries"] = self.get_pulse_discoveries()
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
            output["game_assets"]["campaign"] = self.campaign.serialize(dict)
            output["game_assets"]["expansions"] = self.get_expansions(dict)

            # misc helpers for front-end
            output['game_assets']['survivor_special_attributes'] = self.get_survivor_special_attributes()
            output["game_assets"]["survival_actions"] = self.get_survival_actions("JSON")
            output['game_assets']['inspirational_statue_options'] = self.get_available_fighting_arts()
            output['game_assets']['monster_volumes_options'] = self.get_available_monster_volumes()

            stop = datetime.now()
            duration = stop - start
            if self.metering:
                self.logger.debug("%s serialize(%s) -> Game Assets element in %s" % (self, return_type, duration))

        # additional top-level elements for more API "flatness"
        if return_type in ['storage']:
            output['settlement_storage'] = self.get_settlement_storage()

        if return_type in [None, 'campaign']:
            output["survivor_bonuses"] = self.get_bonuses("JSON")
            output["survivor_attribute_milestones"] = self.get_survivor_attribute_milestones()
            output["eligible_parents"] = self.get_eligible_parents()

        # campaign summary specific
        if return_type in ['campaign']:
            start = datetime.now()
            output.update({'campaign':{}})
            output['campaign'].update({'last_five_log_lines': self.get_event_log(lines=5)})
            output['campaign'].update({'latest_death': self.get_latest_survivor('dead')})
            output['campaign'].update({'latest_birth': self.get_latest_survivor('born')})
            output['campaign'].update({'endeavors': self.get_available_endeavors()})
            output['campaign'].update({'special_rules': self.get_special_rules()})
            output["user_assets"].update({'survivor_groups': self.get_survivors('groups')})

            stop = datetime.now()
            duration = stop - start
            if self.metering:
                self.logger.debug("%s serialize(%s) -> Campaign element in %s" % (self, return_type, duration))

        # finally, return a JSON string of our object
        total_stop = datetime.now()
        duration = total_stop - total_start
        if self.metering:
            self.logger.debug("%s serialize(%s) -> request done in %s" % (self, return_type, duration))
        return json.dumps(output, default=json_util.default)



    #
    #   meta/check/query methods here
    #

    def is_compatible(self, asset_dict={}):
        """Evaluates an asset's dictionary to determine it is compatible for
        use with this settlement. Always returns a bool (no matter what). """

        if type(asset_dict) != dict:
            asset_dict = asset_dict.__dict__

        # check to see if the asset excludes certian campaign types
        if "excluded_campaigns" in asset_dict.keys():
            if self.campaign.handle in asset_dict["excluded_campaigns"]:
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

        for init_key in self.campaign.settlement_sheet_init.keys():
            self.settlement[init_key] = copy(self.campaign.settlement_sheet_init[init_key])
        self.logger.info("%s initialized settlement sheet for '%s'" % (request.User, self))


    def initialize_timeline(self):
        """ Meant to be called during settlement creation, this method
        completely overwrites the settlement's timeline with the timeline
        'template' from the settlement's campaign.

        DO NOT call this method on an active/live settlement, unless you really
        know what you're doing.

        """

        template = self.campaign.timeline

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
                                event_dict.update(self.Events.get_asset(event_dict["handle"]))
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

    def add_defeated_monster(self, monster_string=None):
        """ Adds a monster to the settlement's defeated monsters. Updates the
        killboard. """

        if monster_string is None:
            self.check_request_params(['monster'])
            monster_string = self.params["monster"]

        M = monsters.Monster(name=monster_string)

        # do the killboard update
        killboard_dict = {
            'settlement_id': self.settlement['_id'],
            'settlement_name': self.settlement['name'],
            'kill_ly': self.get_current_ly(),
            'created_by': request.User._id,
            'created_on': datetime.now(),
            'handle': M.handle,
            'name': M.name,
            'type': M.type,
            'raw_name': monster_string,
        }
        for a in ['comment','level']:
            if hasattr(M, a):
                killboard_dict[a] = M.get(a)

        utils.mdb.killboard.insert(killboard_dict)
        self.logger.info("%s Updated the application killboard to include '%s' (%s) in LY %s" % (request.User, monster_string, M.type, self.get_current_ly()))

        # add it and save
        self.settlement["defeated_monsters"].append(monster_string)
        self.log_event("%s added '%s' to the settlement's defeated monsters list!" % (request.User.login, monster_string), event_type="defeated_monster")
        self.save()


    def rm_defeated_monster(self, monster_string=None):
        """ Removes a monster string from the settlement's list, i.e. the
        self.settlement["defeated_monsters"] list of strings, if that monster
        string is present. """

        if monster_string is None:
            self.check_request_params(['monster'])
            monster_string = self.params['monster']

        if monster_string not in self.settlement["defeated_monsters"]:
            msg = "The string '%s' was not found in the settlement's list of defeated monsters!" % monster_string
            self.logger.error(msg)
            raise utils.InvalidUsage(msg)

        self.settlement["defeated_monsters"].remove(monster_string)
        self.log_event("%s removed '%s' from the settlement's defeated monsters." % (request.User.login, monster_string))
        self.save()


    def add_monster(self, monster_handle=None):
        """ Adds quarry and nemesis type monsters to the appropriate settlement
        list, e.g. self.settlemnt["nemesis_monsters"], etc.

        If the 'monster_handle' kwargs is None, this method, list most others,
        will assume that this is a request, and will get request params. """

        if monster_handle is None:
            self.check_request_params(["handle"])
            monster_handle = self.params["handle"]

        # sanity check the handle; load an asset dict for it
        m_dict = self.Monsters.get_asset(monster_handle)

        # get the type from the asset dict
        if m_dict["type"] == 'quarry':
            target_list = self.settlement["quarries"]
        elif m_dict["type"] == 'nemesis':
            target_list = self.settlement["nemesis_monsters"]

        # finally, add, log and save
        if monster_handle not in target_list:
            target_list.append(monster_handle)
            if m_dict["type"] == 'nemesis':
                self.settlement["nemesis_encounters"][monster_handle] = []
        self.log_event("%s added '%s' to the settlement %s list." % (request.User.login, m_dict["name"], m_dict["type"]))
        self.save()


    def rm_monster(self, monster_handle=None):
        """ Removes a monster from the settlement's list of quarry or nemesis
        monsters. Basically the inverse of the add_monster() method (above)."""

        if monster_handle is None:
            self.check_request_params(["handle"])
            monster_handle = self.params["handle"]

        # sanity check the handle; load an asset dict for it
        m_dict = self.Monsters.get_asset(monster_handle)

        # get the type from the asset dict
        if m_dict["type"] == 'quarry':
            target_list = self.settlement["quarries"]
        elif m_dict["type"] == 'nemesis':
            target_list = self.settlement["nemesis_monsters"]

        # finally, add, log and save
        if monster_handle in target_list:
            target_list.remove(monster_handle)
            if m_dict["type"] == 'nemesis':
                del self.settlement["nemesis_encounters"][monster_handle]
        else:
            self.logger.error("%s Ignoring attempt to remove non-existing item '%s' from %s" % (request.User, monster_handle, target_list))
        self.log_event("%s removed '%s' from the settlement %s list." % (request.User.login, m_dict["name"], m_dict["type"]))
        self.logger.debug(target_list)
        self.save()


    def add_monster_volume(self):
        """ Adds a Monster Volume string. Forces the self.settlement['monster_volumes']
        to be unique. Expects a request context."""

        # initialize and validate
        self.check_request_params(['name'])
        vol_string = self.params['name']

        if vol_string in self.get_monster_volumes():
            self.logger.warn("%s Monster volume string '%s' has already been added! Ignoring bogus request..." % (self, vol_string))
            return True

        # add the list if it's not present
        if not 'monster_volumes' in self.settlement.keys():
            self.settlement['monster_volumes'] = []
        self.settlement['monster_volumes'].append(vol_string)

        self.log_event("%s added '%s' to settlement Monster Volumes" % (request.User.login, vol_string), event_type='add_monster_volume')
        self.save()


    def rm_monster_volume(self):
        """ Removes a Monster Volume string. Fails gracefully if asked to remove
        a non-existent string. Assumes a request context. """

        # initialize
        self.check_request_params(['name'])
        vol_string=self.params['name']

        if vol_string not in self.get_monster_volumes():
            self.logger.warn("%s Monster volume string '%s' is not recorded! Ignoring bogus request..." % (self, vol_string))
            return True

        # add the list if it's not present
        self.settlement['monster_volumes'].remove(vol_string)

        self.log_event("%s removed '%s' from settlement Monster Volumes" % (request.User.login, vol_string), event_type='add_monster_volume')
        self.save()


    def add_expansions(self, e_list=[]):
        """ Takes a list of expansion handles and then adds them to the
        settlement, applying Timeline updates, etc. as required by the expansion
        asset definitions. """

        if e_list == []:
            self.check_request_params(['expansions'])
            e_list = self.params['expansions']

        # prune the list to reduce risk of downstream cock-ups
        for e_handle in e_list:
            if e_handle not in self.Expansions.get_handles():
                e_list.remove(e_handle)
                self.logger.warn("Unknown expansion handle '%s' is being ignored!" % (e_handle))
            if e_handle in self.settlement["expansions"]:
                e_list.remove(e_handle)
                self.logger.warn("Expansion handle '%s' is already in %s" % (e_handle, self))

        #
        #   here is where we process the expansion dictionary
        #
        for e_handle in e_list:
            e_dict = self.Expansions.get_asset(e_handle)
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

        # initialize
        if e_list == []:
            self.check_request_params(['expansions'])
            e_list = self.params['expansions']

        # prune the list to reduce risk of downstream cock-ups
        for e_handle in e_list:
            if e_handle not in self.Expansions.get_handles():
                e_list.remove(e_handle)
                self.logger.warn("Unknown expansion handle '%s' is being ignored!" % (e_handle))
            if e_handle not in self.settlement["expansions"]:
                e_list.remove(e_handle)
                self.logger.warn("Expansion handle '%s' is not in %s" % (e_handle, self))

        #
        #   here is where we process the expansion dictionary
        #
        for e_handle in e_list:
            e_dict = self.Expansions.get_asset(e_handle)
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


    def add_location(self):
        "Adds a location to the settlement. """

        loc_handle = self.params["handle"]

        # first, verify that the incoming handle is legit
        loc_dict = self.Locations.get_asset(loc_handle)

        # next, make sure it's not a dupe
        if loc_handle in self.settlement["locations"]:
            self.logger.error("Ignoring request to add duplicate location handle '%s' to settlement." % loc_handle)
            return False

        # now add it
        self.settlement["locations"].append(loc_handle)

        if "levels" in loc_dict.keys():
            self.settlement["location_levels"][loc_handle] = 1

        self.log_event("%s added '%s' to settlement locations." % (request.User.login, loc_dict["name"]), event_type="add_location")

        self.save()


    def rm_location(self):
        """ Removes a location from the settlement. Requires a request.User
        object, i.e. should not be called unless it is part of a request.  """

        # spin everything up
        loc_handle = self.params["handle"]
        loc_dict = self.Locations.get_asset(loc_handle)

        # first, see if it's a real handle
        if loc_handle not in self.Locations.get_handles():
            self.logger.error("Location asset handle '%s' does not exist!" % loc_handle)
            return False

        # now check to see if it's there to remove in the first place
        if loc_handle not in self.settlement["locations"]:
            self.logger.warn("Ignoring attempt to remove %s from %s locations  (because it is not there)." % (loc_handle, self))
            return False

        # now do it
        self.settlement["locations"].remove(loc_handle)
        self.log_event("%s removed '%s' from settlement locations." % (request.User.login, loc_dict["name"]), event_type="rm_location")
        self.save()


    def add_innovation(self, i_handle=None):
        """ Adds an innovation to the settlement. Does business logic. """

        if i_handle is None:
            self.check_request_params(["handle"])
            i_handle = self.params["handle"]

        # first, pass/ignore if we're trying to add an innovation twice:
        if i_handle in self.get_innovations():
            self.logger.warn("%s Attempted to add duplicate innovation handle, '%s'" % (request.User, i_handle))
            return False

        # now try to get the dict; bail if it's bogus
        i_dict = self.Innovations.get_asset(i_handle)

        # finally, do it and log it
        self.settlement["innovations"].append(i_handle)

        if i_dict.get("levels", None) is not None:
            self.settlement["innovation_levels"][i_handle] = 1

        self.log_event("%s added '%s' to settlement innovations." % (request.User.login, i_dict["name"]), event_type="add_innovation")

        self.save()

        # now do survivor post-processing
        if i_dict.get("current_survivor", None) is not None:
            self.update_all_survivors("increment", i_dict["current_survivor"])


    def rm_innovation(self):
        """ Removes an innovation from the settlement. Requires request.User
        object, i.e. should not be called unless it is part of a request.  """

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
        self.log_event("%s removed '%s' from settlement innovations." % (request.User.login, I.name), event_type="rm_innovation")
        self.save()

        # now do survivor post-processing
#        if i_dict.get("current_survivor", None) is not None:
#            self.update_all_survivors("decrement", i_dict["current_survivor"])


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


        # warn about deprecated params
        if "user_login" in e.keys():
            self.logger.warn("add_timeline_event() -> the 'user_login' parameter is deprecated!")

        # try to improve the event if we've got a handle on it
        if "handle" in e.keys() and e["type"] in "story_event":
            e.update(self.Events.get_asset(e["handle"]))

        if not e["type"] in t_object.keys():
            t_object[e["type"]] = []

        if not e in t_object[e["type"]]:
            t_object[e["type"]].append(e)
        else:
            self.logger.warn("Ignoring attempt to add duplicate event to %s timeline!" % (self))
            return False

        timeline.insert(t_index,t_object)

        self.settlement["timeline"] = timeline

        self.log_event("%s added '%s' to Lantern Year %s" % (request.User.login, e["name"], e["ly"]))

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


    #
    #   misc. methods
    #

    def return_survivors(self, aftermath=None):
        """ Returns all survivors with departing=True (i.e. initializes the
        survivor and calls Survivor.return_survivor() on it and then processes
        showdown/hunt attributes.
        
        Assumes a request context (because why else would you be doing this?)
        """

        # determine (or default) the showdown type
        showdown_type = self.settlement.get('showdown_type', 'normal')

        # initialize!
        if aftermath is None:
            self.check_request_params(['aftermath'])
            aftermath = self.params['aftermath']
        if aftermath not in ['victory','defeat']:
            raise Exception("The 'aftermath' value of '%s' is not allowed!" % (aftermath))

        # 1.) handle the current quarry/showdown monst 
        if aftermath == 'victory' and self.settlement.get('current_quarry', None) is not None:
            self.add_defeated_monster(self.settlement['current_quarry'])
            del self.settlement['current_quarry']

        # 2.) remove misc meta data
        for tmp_key in ['hunt_started','showdown_type']:
            if tmp_key in self.settlement.keys():
                self.logger.debug("%s Removed tmp attribute: '%s'." % (self, tmp_key))
                del self.settlement[tmp_key]

        # 3.) process survivors, keeping a list of IDs for later
        returned = []
        for s in self.survivors:
            if s.is_departing():
                s.return_survivor(showdown_type)
                returned.append(s)

        # 4.) remove 'skip_next_hunt' from anyone who sat this one out
        if showdown_type == 'normal':
            for s in self.get_survivors(list, excluded=[s._id for s in returned], exclude_dead=True):
                if 'skip_next_hunt' in s.keys():
                    S = survivors.Survivor(_id=s['_id'], Settlement=self)
                    S.toggle_boolean('skip_next_hunt')

        # 5.) log the return
        live_returns = []
        for s in returned:
            if not s.is_dead():
                live_returns.append(s.survivor['name'])
                
        if live_returns != []:
            returners = utils.list_to_pretty_string(live_returns)
            if showdown_type == 'normal':
                msg = "%s returned to the settlement in %s." % (returners, aftermath)
            elif showdown_type == 'special':
                msg = "%s healed %s." % (request.User.login, returners)
        else:
            if showdown_type == 'normal':
                msg = "No survivors returned to the settlement."
            elif showdown_type == 'special':
                msg = 'No survivors were healed after the Special Showdown.'
        self.log_event(msg, event_type="survivors_return_%s" % aftermath)


        # 6.) increment endeavors
        if showdown_type == 'normal' and live_returns != []:
            self.update_endeavor_tokens(len(live_returns), save=False)

        self.save()


    #
    #   set methods
    #

    def set_abandoned(self):
        """ Abandons the settlement by setting self.settlement['abandoned'] to
        datetime.now(). Logs it. Expects a request context. """

        self.settlement['abandoned'] = datetime.now()
        self.log_event('%s abandoned the settlement!' % (request.User.login))
        self.save()


    def set_inspirational_statue(self):
        """ Set the self.settlement['inspirational_statue'] to a fighting art
        handle. Assumes a request context. """

        self.check_request_params(['handle'])
        fa_handle = self.params['handle']

        try:
            fa_dict = self.FightingArts.get_asset(fa_handle)
        except:
            raise utils.InvalidUsage("Fighting Art handle '%s' is not a known asset handle!" % (fa_handle))

        self.settlement['inspirational_statue'] = fa_handle
        self.log_event("%s set the settlement's Inspirational Statue to '%s'" % (request.User.login, fa_dict['name']))
        self.save()


    def set_lantern_research_level(self):
        """ Sets the self.settlement['lantern_research_level'] to incoming 'value'
        param. Requires a request context."""

        self.check_request_params(['value'])
        level = self.params['value']

        # create the attrib if it doesn't exist
        self.settlement['lantern_research_level'] = level
        self.log_event("%s set the settlement Lantern Research Level to %s" % (request.User.login, level))
        self.save()



    def set_last_accessed(self, access_time=None):
        """ Set 'access_time' to a valid datetime object to set the settlement's
        'last_accessed' value or leave it set to None to set the 'last_accessed'
        time to now. """

        if access_time is not None:
            self.settlement['last_accessed'] = access_time
        else:
            self.settlement['last_accessed'] = datetime.now()
        self.save(False)


    def set_lost_settlements(self, new_value=None):
        """ Updates settlement["lost_settlements"] to be int('new_value'). """

        if self.check_request_params(["value"], True):
            new_value = self.params["value"]
        else:
            self.logger.error("Incomplete params for updating lost settlements!")
            raise Exception

        try:
            new_value = int(new_value)
        except Exception as e:
            self.logger.error("Unable to set 'lost_settlements' to non-integer '%s'!" % new_value)
            self.logger.exception(e)
            raise Exception(e)

        if new_value <= 0:
            self.settlement["lost_settlements"] = 0
        else:
            self.settlement["lost_settlements"] = new_value

        self.log_event("%s set Lost Settlements count to %s" % (request.User.login, new_value))
        self.save()


    def set_name(self, new_name=None):
        """ Looks for the param key 'name' and then changes the Settlement's
        self.settlement["name"] to be that value. Works with or without a
        request context. """

        if new_name is None:
            self.check_request_params(['name'])
            new_name = self.params["name"].strip()

        if new_name == "":
            new_name = "UNKNOWN"

        old_name = self.settlement["name"]
        self.settlement["name"] = new_name

        if old_name is None:
            msg = "%s named the settlement '%s'." % (request.User.login, new_name)
        else:
            msg = "%s changed settlement name from '%s' to '%s'" % (request.User.login, old_name, new_name)

        self.log_event(msg)
        self.save()


    def set_principle(self):
        """ Basically, we're looking for incoming JSON to include a 'principle'
        key and an 'election' key.

        The 'principle' should be something such as,
        'new_life', 'conviction', 'new_life_potsun', etc. The 'election' should
        be an Innovation (principle) handle such as, 'barbaric', 'romantic, etc.

        Alternately, the 'principle' can be a boolean False. If this is the case
        we 'unset' the principle from the settlement.
        """

        # initialize
        self.check_request_params(["principle", "election"])
        principle = self.params["principle"]
        election = self.params["election"]

        # validate the principle first
        principles = self.Innovations.get_principles()

        if principle in principles.keys():
            p_dict = principles[principle]
        else:
            msg = "The principle handle '%s' is not recognized!" % principle
            self.logger.error(msg)
            raise utils.InvalidUsage(msg, status_code=400)

        # now validate the election
        unset = False
        if election in self.Innovations.get_handles():
            e_dict = self.Innovations.get_asset(election)
        elif type(election) == bool:
            unset = True
        else:
            msg = "The '%s' principle election handle '%s' is not recognized!" % (p_dict["name"], election)


        def remove_principle(principle_handle):
            """ private, internal fun for removing a principle. """
            principle_dict = self.Innovations.get_asset(principle_handle)
            self.settlement["principles"].remove(principle_handle)
            self.logger.debug("%s removed '%s' from %s principles" % (request.User, principle_handle, self))
            if principle_dict.get("current_survivor", None) is not None:
                self.update_all_survivors("decrement", principle_dict["current_survivor"])


        # do unset logic
        if unset:
            removed = 0
            for option in p_dict["option_handles"]:
                if option in self.settlement["principles"]:
                    remove_principle(option)
                    removed += 1
            if removed >= 1:
                self.log_event("%s unset settlement %s principle." % (request.User.login, p_dict['name']))
                self.save()
            else:
                self.logger.debug("%s Ignoring bogus 'unset princple' request." % (self))
            return True
        else:
            # ignore re-clicks
            if e_dict["handle"] in self.settlement["principles"]:
                self.logger.warn("%s Ignoring addition of duplicate principle handle '%s' to %s" % (request.User, e_dict["handle"], self))
                return True

        # remove the opposite principle
        for option in p_dict["option_handles"]:
            if option in self.settlement["principles"]:
                remove_principle(option)

        # finally, add the little fucker
        self.settlement["principles"].append(e_dict["handle"])
        self.log_event("%s set settlement %s principle to %s" % (request.User.login, p_dict["name"], e_dict["name"]), event_type="set_principle")

        # if we're still here, go ahead and save since we probably updated
        self.save()

        # post-processing: add 'current_survivor' effects
        if e_dict.get("current_survivor", None) is not None:
            self.update_all_survivors("increment", e_dict["current_survivor"])


    def set_showdown_type(self):
        """ Expects a request context and looks for key named 'type'. Uses the
        value of that key as self.settlement['showdown_type']. """

        self.check_request_params(['showdown_type'])
        showdown_type = self.params['showdown_type']
        self.settlement['showdown_type'] = showdown_type
        self.logger.debug("%s Set showdown type to '%s' for %s" % (request.User, showdown_type, self.Settlement))
        self.save()


    def set_storage(self):
        """ Takes in a list of JSON dictionaries from a request and updates the
        self.settlement['storage'] list. """

        self.check_request_params(['storage'])
        dict_list = self.params['storage']

        for d in dict_list:
            handle = d['handle']
            a_obj = self.storage_handle_to_obj(d['handle'])
            value = int(d['value'])

            # remove all occurrences of handle from storage
            self.settlement['storage'] = filter(lambda a: a != handle, self.settlement['storage'])
            for i in range(value):
                self.settlement['storage'].append(handle)
            self.log_event("%s updated settlement storage: %s x %s" % (request.User.login, a_obj.name, value))

        self.save()


    def update_all_survivors(self, operation=None, attrib_dict={}):
        """ Performs bulk operations on all survivors. Use 'operation' kwarg to
        either 'increment' or 'decrement' all attributes in 'attrib_dict'.

        'attrib_dict' should look like this:

        {
            'Strength': 1,
            'Courage': 1,
        }

        The 'increment' or 'decrement' values call the corresponding methods
        on the survivors.
        """

        if operation not in ['increment','decrement']:
            self.logger.exception("update_all_survivors() methods does not support '%s' operations!" % operation)
            raise Exception

        for s in self.survivors:
            for attribute, modifier in attrib_dict.iteritems():
                if operation == 'increment':
                    if attribute == 'abilities_and_impairments':
                        for ai_handle in modifier:  # 'modifier' is a list here
                            s.add_game_asset('abilities_and_impairments', ai_handle)
                    else:
                        s.update_attribute(attribute, modifier)
                elif operation == 'decrement':
                    if attribute == 'abilities_and_impairments':
                        for ai_handle in modifier:  # 'modifier' is a list here
                            s.rm_game_asset('abilities_and_impairments', ai_handle)
                    else:
                        s.update_attribute(attribute, -modifier)

    def update_attribute(self):
        """ Assumes a request context and looks for 'attribute' and 'modifier'
        keys in self.params. Uses them to increment (literally adds) the current
        self.settlement[attribute] value. """

        self.check_request_params(['attribute','modifier'])
        attribute = self.params["attribute"]
        modifier = self.params["modifier"]

        self.settlement[attribute] = self.settlement[attribute] + modifier
        attribute_pretty = attribute.title().replace('_',' ')
        self.log_event("%s updated settlement %s to %s" % (request.User.login, attribute_pretty, self.settlement[attribute]))
        self.save()


    def update_endeavor_tokens(self, modifier=0, save=True):
        """ Updates settlement["endeavor_tokens"] by taking the current value,
        which is normalized (above) to zero, if it is not defined or set, and
        adding 'modifier' to it.

        To increment ETs, do 'modifier=1'; to decrement, do 'modifier=-1'.
        """

        if "modifier" in self.params:
            modifier = self.params["modifier"]

        new_val = self.get_endeavor_tokens() + int(modifier)
        if new_val < 0:
            new_val = 0
        self.settlement["endeavor_tokens"] = new_val
        self.log_event("%s set endeavor tokens to %s" % (request.User.login, new_val))

        if save:
            self.save()


    def update_nemesis_levels(self):
        """ Updates a settlement's 'nemesis_encounters' array/list for a nemesis
        monster handle. Assumes that this is a request. """

        self.check_request_params(["handle","levels"])
        handle = self.params["handle"]
        levels = list(self.params["levels"])

        m_dict = self.Monsters.get_asset(handle)

        if handle not in self.settlement["nemesis_monsters"]:
            self.logger.error("Cannot update nemesis levels for '%s' (nemesis is not in 'nemesis_monsters' list for %s)" % (handle, self))
        else:
            self.settlement["nemesis_encounters"][handle] = levels
            self.log_event('%s updated %s encounters to include %s' % (request.User.login, m_dict["name"], utils.list_to_pretty_string(levels)))
            self.save()


    def update_population(self, modifier=None):
        """ Updates settlement["population"] by adding 'modifier' to it. Will
        never go below zero."""

        if modifier is None:
            self.check_request_params["modifier"]
            modifier = self.params["modifier"]

        current = self.settlement["population"]
        new = current + modifier

        if new < 0:
            new = 0

        self.settlement["population"] = new

        self.log_event("%s updated settlement population to %s" % (request.User.login, self.settlement["population"]))
        self.save()


    def update_survivors(self, include=None, attribute=None, modifier=None):
        """ This method assumes a request context and should not be called from
        outside of a request.

        Use this to modify a single attribute for one of the following groups of
        survivors:

            'departing': All survivors with 'departing': True

        NB: this is a waaaaaaay different method from update_all_survivors(), so
        make sure you know the difference between the two. """

        # initialize; assume a request context
        if include is None:
            self.check_request_params(['include', 'attribute', 'modifier'])
            include = self.params['include']
            attribute = self.params['attribute']
            modifier = self.params['modifier']

        # now check the include and get our targets
        target_group = []
        if include == 'departing':
            target_group = utils.mdb.survivors.find({'settlement': self.settlement['_id'], 'departing': True, 'dead': {'$exists': False}})
        else:
            raise InvalidUsage("update_survivors() cannot process the 'include' value '%s'" % (include))

        # now initialize survivors and update them with update_attribute()
        for s in target_group:
            S = survivors.Survivor(_id=s['_id'], Settlement=self)
            S.update_attribute(attribute, modifier)


    def update_timeline_with_story_events(self):
        """ LEGACYWEBAPP PORT
	This runs during Settlement normalization to automatically add story
        events to the Settlement timeline when the threshold for adding the
        event has been reached. """

        pass
#        updates_made = False

#        milestones_dict = self.get_api_asset("game_assets", "milestones_dictionary")

#        for m_key in self.get_campaign("dict")["milestones"]:

#            m_dict = milestones_dict[m_key]

#            event = self.get_event(m_dict["story_event"])

            # first, if the milestone has an 'add_to_timeline' key, create a
            # string from that key to determine whether we've met the criteria
            # for adding the story event to the timeline. The string gets an
            # eval below
#            add_to_timeline = False
#            if "add_to_timeline" in milestones_dict[m_key].keys():
#                add_to_timeline = eval(milestones_dict[m_key]["add_to_timeline"])

            # now, here's our real logic
#            condition_met = False
#            if m_key in self.settlement["milestone_story_events"]:
#                condition_met = True
#            elif add_to_timeline:
#                condition_met = True


            # final evaluation:
#            if condition_met and event["handle"] not in self.get_story_events("handles"):
#                self.logger.debug("[%s] automatically adding %s story event to LY %s" % (self.User, event["name"], se
#lf.get_ly()))
#                event.update({"ly": self.get_ly(),})
#                self.add_timeline_event(event)
#                self.log_event('Automatically added <b><font class="kdm_font">g</font> %s</b> to LY %s.' % (event["na
#me"], self.get_ly()))
#                updates_made = True

#        return updates_made



    #
    #   set methods
    #

    def set_attribute(self):
        """ Assumes a request context and looks for 'attribute' and 'modifier'
        keys in self.params. Uses them to increment (literally adds) the current
        self.settlement[attribute] value. """

        self.check_request_params(['attribute','value'])
        attribute = self.params["attribute"]
        value = self.params["value"]

        self.settlement[attribute] = value
        pretty_attribute = attribute.title().replace('_',' ')
        self.log_event("%s set settlement %s to %s" % (request.User.login, pretty_attribute, self.settlement[attribute]))
        self.save()


    def set_current_quarry(self, new_quarry=None):
        """ Sets the self.settlement["current_quarry"] attrib. """

        if new_quarry is None:
            new_quarry = self.params["current_quarry"]

        self.settlement["hunt_started"] = datetime.now()
        self.settlement["current_quarry"] = new_quarry
        self.log_event("%s set target monster to %s" % (request.User.login, new_quarry), event_type="set_quarry")
        self.save()



    def set_location_level(self):
        """ Sets self.settlement["location_levels"][handle] to an int. """

        if self.check_request_params(["handle","level"], True):
            handle = self.params["handle"]
            level = self.params["level"]
        else:
            self.logger.error("Could not set settlement location level!")
            raise Exception

        L = locations.Assets()
        loc_dict = L.get_asset(handle)

        if handle not in self.settlement["locations"]:
            self.logger.error("Could not set settlement location level for '%s', which is not in %s locations: %s" % (handle, self, self.settlement["locations"]))
        else:
            self.settlement["location_levels"][handle] = int(level)

        self.log_event("%s set '%s' location level to %s." % (request.User.login, loc_dict["name"], level), event_type="set_location_level")

        self.save()


    def set_innovation_level(self):
        """ Sets self.settlement["innovation_levels"][handle] to an int. """

        if self.check_request_params(["handle","level"], True):
            handle = self.params["handle"]
            level = self.params["level"]
        else:
            self.logger.error("Could not set settlement innovation level!")
            raise Exception

        i_dict = self.Innovations.get_asset(handle)

        if handle not in self.settlement["innovations"]:
            self.logger.error("Could not set settlement innovation level for '%s', because that innovation is not included in the %s innovations list: %s" % (handle, self, self.settlement["innovations"]))
        else:
            self.settlement["innovation_levels"][handle] = int(level)

        self.log_event("%s set '%s' innovation level to %s." % (request.User.login, i_dict["name"], level), event_type="set_innovation_level")

        self.save()



    #
    #   get methods
    #


    def get_available_assets(self, asset_module=None, handles=True, exclude_types=[]):
        """ Generic function to return a dict of available game assets based on
        their family. The 'asset_module' should be something such as,
        'cursed_items' or 'weapon_proficiencies', etc. that has an Assets()
        method.

        Use the 'handles' kwarg (boolean) to determine whether to return a list
        of asset dictionaries, or a dictionary of dictionaries (where asset
        handles are the keys.

        Use the 'ignore_types' kwarg (list) to filter/exclude assets whose
        'type' should NOT be returned.
        """
        if handles:
            available = collections.OrderedDict()   # NOT A REGULAR DICT!!!
        else:
            available = []

        A = copy(asset_module.Assets())

        # remove excluded types
        if exclude_types != []:
            A.filter("type", exclude_types)

        # update available
        for n in A.get_handles():
            asset_dict = A.get_asset(n)
            if self.is_compatible(asset_dict):
                if handles: # return a dict
                    available.update({asset_dict["handle"]: asset_dict})
                else:       # return a list of dicts
                    available.append(asset_dict)

        # REMOVE THIS
        if type(available) == list: #list of dicts; needs sorting
            available = sorted(available, key=lambda k: k['name'])

        return {"%s" % (asset_module.__name__.split(".")[-1]): available}


    def get_available_endeavors(self):
        """ Returns a list of endeavor handles based on campaign, innovations,
        locations, survivors and settlement events. """

        available = {
            'campaign': [],
            'innovations': [],
            'locations': [],
            'survivors': [],
            'settlement_events': [],
            'storage': [],
        }

        #
        #   Private method to check if an endeavor is possible
        #

        def get_eligible_endeavors(e_list):
            """ Returns a bool if the settlement can endeavor here. """

            eligible_endeavor_handles = []
            for e_handle in e_list:
                e_dict = self.Endeavors.get_asset(e_handle)
                eligible = True
                if e_dict.get('hide_if_location_exists', None) in self.settlement['locations']:
                    eligible = False
                elif e_dict.get('hide_if_innovation_exists',None) in self.settlement['innovations']:
                    eligible = False
                if e_dict.get('hide_if_settlement_attribute_exists', None) in self.settlement.keys():
                    eligible = False
                for req_inno in e_dict.get('requires_innovations', []):
                    if req_inno not in self.settlement['innovations']:
                        eligible = False
                if eligible:
                    eligible_endeavor_handles.append(e_handle)
            return eligible_endeavor_handles

        #
        #   all of these must be a list of dictionaries!
        #

        # campaign-specific
        c_dict = self.get_campaign(dict)
        if c_dict.get('endeavors', None) is not None:
            for e_handle in c_dict['endeavors']:
                available['campaign'].append(self.Endeavors.get_asset(e_handle))

        # innovations and locations
        for a_list in ['innovations','locations']:
            for a_dict in self.list_assets(a_list):
                if a_dict.get('endeavors',None) is not None:
                    eligible_endeavor_handles = get_eligible_endeavors(a_dict['endeavors'])
                    if len(eligible_endeavor_handles) >= 1:
                        a_dict['endeavors'] = eligible_endeavor_handles
                        available[a_list].append(a_dict)

        # storage
        for i_handle in self.settlement['storage']:
            i_obj = self.storage_handle_to_obj(i_handle)
            if hasattr(i_obj, 'endeavors'):
                eligible_endeavor_handles = get_eligible_endeavors(i_obj.endeavors)
                if len(eligible_endeavor_handles) >= 1:
                    i_obj.endeavors = eligible_endeavor_handles
                    available['storage'].append(i_obj.serialize(dict))

        # check survivors
        survivor_endeavors = []
        for s in self.survivors:
            available_e = s.get_available_endeavors()
            if available_e != []:
                s_dict = s.serialize(dict, False)
                s_dict['sheet']['endeavors'] = available_e
                survivor_endeavors.append(s_dict)
        available['survivors'] = survivor_endeavors

        return available


    def get_available_fighting_arts(self):
        """ Returns a uniqified list of farting art handles based on LIVING
        survivors. """

        output = set()

        fa_handles = set()
        for s in self.survivors:
            if not s.is_dead():
                fa_handles = fa_handles.union(s.survivor['fighting_arts'])

        for fa_handle in fa_handles:
            fa_dict = self.FightingArts.get_asset(fa_handle)
            if fa_dict['type'] == 'fighting_art':
                output.add(fa_handle)

        output = sorted(list(output))
        return output


    def get_available_monster_volumes(self):
        """ Returns a list of strings that are eligible for addition to the
        settlement's self.settlement['monster_volumes'] list. """

        options = set()

        for m in self.settlement['defeated_monsters']:
            M = monsters.Monster(name=m)
            if hasattr(M, 'level'):
                options.add('%s Vol. %s' % (M.name, M.level))

        for vol_string in self.get_monster_volumes():
            if vol_string in options:
                options.remove(vol_string)

        return sorted(list(options))


    def get_bonuses(self, return_type=None):
        """ Returns settlement and survivor bonuses according to 'return_type'.
        Supported types are:

            - dict (same as None/unspecified)
            - "JSON"

        The JSON type return is especially designed for front-end developers,
        and includes a pseudo-buff group called "all" that includes all buffs.
        Also, the JSON type return sorts by innovation name, which is nice.
        """

        output = {
            "settlement_buff": {},
            "survivor_buff": {},
            "departure_buff": {},
        }

        if return_type == "JSON":
            output = {
                "settlement_buff": [],
                "survivor_buff": [],
                "departure_buff": [],
                "all": [],
            }

        for handle,d in self.get_innovations(return_type=dict, include_principles=True).iteritems():
            for k in d.keys():
                if k in output.keys():
                    if return_type == "JSON":
                        dict_repr = {"name": d["name"], "desc": d[k]}
                        output[k].append(dict_repr)
                        output["all"].append(dict_repr)
                    else:
                        output[k][handle] = d[k]


        # sort, if we're doing JSON, and save the UI guys the trouble
        if return_type == "JSON":
            for buff_group in output:
                output[buff_group] = sorted(output[buff_group], key=lambda k: k['name'])

        return output


    def get_death_count(self, return_type=int):
        """ By default this returns the settlement's total number of deaths as
        an int.

        This method can accept the following values for 'return_type':

            - int
            - "min"

        Setting return_type='min' will return the settlement's minimum death
        count, i.e. the number of survivors in the settlement with
        survivor["dead"] = True. """

        if return_type == "min":
            min_death_count = 0
            for s in self.get_survivors(list):
                if s.get("dead", False):
                    min_death_count += 1
            return min_death_count

        return self.settlement["death_count"]


    def get_endeavor_tokens(self):
        """ Returns settlement Endeavor Tokens as an int. Does some aggressive
        duck-typing to prevent legacy data model issues from fucking everything
        up and causing us to throw a 500. """

        try:
            return int(self.settlement["endeavor_tokens"])
        except:
            return 0


    def get_expansions(self, return_type=None):
        """ Returns a list of expansions if the 'return_type' kwarg is left
        unspecified.

        Otherwise, 'return_type' can be either 'dict' or 'comma_delimited'.

        Setting return_type="dict" gets a dictionary where expansion 'name'
        attributes are the keys and asset dictionaries are the values. """

        if return_type is None:
            return self.settlement.get('expansions',[]) #bullshit legacy

        s_expansions = self.settlement['expansions']

        if return_type == dict:
            exp_dict = {}
            for exp_handle in s_expansions:
                exp_dict[exp_handle] = self.Expansions.get_asset(exp_handle)
            return exp_dict
        elif return_type == "comma-delimited":
            if s_expansions == []:
                return None
            else:
                return ", ".join(s_expansions)
        elif return_type in ['pretty', str]:
            output = []
            for e in s_expansions:
                output.append(self.Expansions.get_asset(e, backoff_to_name=True)["name"])
            return utils.list_to_pretty_string(output)

        return s_expansions


    def get_event_log(self, return_type=None, lines=None):
        """ Returns the settlement's event log as a cursor object unless told to
        do otherwise."""

        event_log = utils.mdb.settlement_events.find(
            {
            "settlement_id": self.settlement["_id"]
            }
        ).sort("created_on",-1)

        if lines is not None:
            event_log = list(event_log)[-lines:]

        if return_type=="JSON":
            return json.dumps(list(event_log),default=json_util.default)

        return event_log


    def get_eligible_parents(self):
        """ Returns a dictionary with two lists of survivors who are able to do
        the mommy-daddy dance: one for male survivors and one for female
        survivors.

        This method uses methods of the Survivor class to assess preparedness to
        do the deed. Check those methods for more info on how survivors are
        assessed.

        Important! The lists only contain survivor names and OIDs (i.e. you do
        NOT get a fully serialized survivor back in this list. """

        eligible_parents = {"male":[], "female":[]}

        for S in self.survivors:
            if S.can_be_nominated_for_intimacy():
                s_dict = {
                    "name": S.survivor["name"],
                    "_id": S.survivor["_id"],
                    "oid_string": str(S.survivor["_id"]),
                }

                if S.get_sex() == "M":
                    eligible_parents["male"].append(s_dict)
                elif S.get_sex() == "F":
                    eligible_parents["female"].append(s_dict)

        return eligible_parents


    def get_final_boss(self, return_type=None):
        """ Returns the settlement's final boss monster (according to the
        campaign asset. Returns a handle by default. """

        B = monsters.Monster(self.campaign.final_boss)

        if return_type == 'name':
            return B.name
        elif return_type == object:
            return B

        return B.handle


    def get_founder(self):
        """ Helper method to rapidly get the mdb document of the settlement's
        creator/founder. """

        return utils.mdb.users.find_one({"_id": self.settlement["created_by"]})


    def get_innovations(self, return_type=None, include_principles=False):
        """ Returns self.settlement["innovations"] by default; specify 'dict' as
        the 'return_type' to get a dictionary back instead. """

        s_innovations = copy(self.settlement["innovations"])
        if include_principles:
            s_innovations.extend(self.settlement["principles"])

        if return_type == dict:
            output = {}
            for i_handle in s_innovations:
                i_dict = self.Innovations.get_asset(i_handle, backoff_to_name=True)
                if i_dict is not None:
                    output[i_handle] = i_dict
                else:
                    self.logger.error("Ignoring unknown Innovation handle '%s'!" % i_handle)
            return output

        return s_innovations


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

        available = dict(self.get_available_assets(innovations)["innovations"])

        # remove principles and innovations from expansions we don't use
        for a in available.keys():
            if available[a].get("type", None) == "principle":
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
                asset_dict = self.Innovations.get_asset(c)
                if self.is_compatible(asset_dict):
                    deck_dict[c] = asset_dict


        # we've got a good list, but we still need to check available inno-
        # vations for some attribs that might force them into the list.
        for i in available:
            available_if = available[i].get("available_if",None)
            if available_if is not None:
                for tup in available_if:
                    asset,collection = tup
                    if asset in self.settlement[collection]:
                        deck_dict[i] = self.Innovations.get_asset(i)

        # finally, create a new list and use the deck dict to 
        deck_list = []
        for k in deck_dict.keys():
            deck_list.append(deck_dict[k]["name"])

        if return_type == "JSON":
            return json.dumps(sorted(deck_list))
        else:
            return deck_dict


    def get_lantern_research_level(self):
        """ Returns self.settlement['lantern_resarch_level']. Always an int."""

        return self.settlement.get('lantern_research_level', 0)


    def get_latest_survivor(self, category='dead'):
        """ Gets the latest survivor, based on the 'category' kwarg value. """

        if category == 'dead':
            s = utils.mdb.survivors.find({'dead': True}).sort('died_on')
            if s.count() >= 1:
                return s[0]
        elif category == 'born':
            s = utils.mdb.survivors.find({'born_in_ly': {'$exists': True}}).sort('created_on')
            if s.count() >= 1:
                return s[0]

        return None


    def get_monster_volumes(self):
        """ Returns the settlement's self.settlement['monster_volumes'] list,
        which is a list of unique strings. """

        return self.settlement.get('monster_volumes', [])



    def get_parents(self):
        """ Returns a list of survivor couplings, based on the 'father'/'mother'
        attributes of all survivors in the settlement. """

        couples = {}
        for s in self.get_survivors(list):
            if 'father' in s.keys() and 'mother' in s.keys():
                couple_id = "%s+%s" %(str(s['father']), str(s['mother']))
                couple = {'father': s['father'], 'mother': s['mother']}
                if couples.get(couple_id, None) is None:
                    couples[couple_id] = {'father': s['father'], 'mother': s['mother'], 'children': []}
                couples[couple_id]['children'].append(s['_id'])

        output = []
        for c in couples.keys():
            output.append(couples[c])

        return output


    def get_population(self, return_type=int):
        """ By default, this returns settlement["population"] as an int. Use the
        'return_type' kwarg to get different returns:

            - "min" -> returns the minimum population based on living survivors
            - "sex" -> returns a dictionary of M/F survivor counts

        """

        if return_type == "min":
            min_pop = 0
            for s in self.survivors:
                if not s.is_dead():
                    min_pop += 1
            return min_pop
        elif return_type == 'sex':
            output = {'M':0, 'F':0}
            for s in self.survivors:
                if not s.is_dead():
                    output[s.get_sex()] += 1
            return output

        return int(self.settlement["population"])


    def get_pulse_discoveries(self):
        """ Returns JSON representing Pulse Discoveries. Hardcoded for now. Hack
        City, bruh. """

        return [
            {"level": 1, "bgcolor": "#D4D8E1", "name": "Aggression Overload", "subtitle": "Add an attack roll to an attack.", "desc": "During your attack, after making your attack rolls but before drawing hit locations, you may roll the Death Die as an additional attack roll."},
            {"level": 2, "bgcolor": "#C6CED9", "name": "Acceleration", "subtitle": "Add +1d10 movement to a move action.", "desc": "Before moving, you may roll the Death Die and add the result to your movement for one move action this round."},
            {"level": 3, "bgcolor": "#B9CAD4", "name": "Uninhibited Rage", "subtitle": "Add +1d10 strength to a wound attempt.", "desc": "After a wound attempt is rolled you may roll the Death Die and add the result to the strength of your wound attempt."},
            {"level": 4, "bgcolor": "#AEC0CE", "name": "Legs Locked", "desc": "When you gian the Death Die, you you stand. While you have the Death Die, you cannot be knocked down for any reason."},
            {"level": 5, "bgcolor": "#9DB2C3", "name": "Metabolic Surrender", "desc": "Any time during the showdown,  you may roll the Death Die. Gain twice that much survival. This round, ignore the negative effects of permanent injuries, impairments, disorders and negative attributes (including tokens). At the end of the round, you die."},
        ]



    def get_settlement_notes(self):
        """ Returns a list of mdb.settlement_notes documents for the settlement.
        They're sorted in reverse chronological, because the idea is that you're
        goign to turn this list into JSON and then use it in the webapp. """

        notes = utils.mdb.settlement_notes.find({"settlement": self.settlement["_id"]}).sort("created_on",-1)
        if notes is None:
            return []
        return [n for n in notes]


    def get_settlement_storage(self):
        """ Returns a JSON-ish representation of settlement storage, meant to
        facilitate front-end design.

        We're basically constructing a data structure/schema here, so it gets a
        little messy.
        """

        gear_total = 0
        resources_total = 0


        # get available storage locations into a dictionary of dicts
        storage_repr = self.get_available_assets(storage)['storage']

        # now update the dictionaries in the big dict to have a new key
        # called 'inventory' where we will park note handles
        for k in storage_repr.keys():
            storage_repr[k]['inventory'] = []
            storage_repr[k]['digest'] = collections.OrderedDict()
            storage_repr[k]['collection'] = []
            S = storage.Storage(k)
            for handle in S.get_collection():
                if S.sub_type == 'gear':
                    item_obj = gear.Gear(handle)
                elif S.sub_type == 'resources':
                    item_obj = resources.Resource(handle)
                if self.is_compatible(item_obj):
                    item_obj.quantity = self.settlement['storage'].count(item_obj.handle)
                    if S.sub_type == 'gear':
                        gear_total += item_obj.quantity
                    elif S.sub_type == 'resources':
                        resources_total += item_obj.quantity
                    storage_repr[k]['collection'].append(item_obj.serialize(dict))

            # use expansion flair colors for gear locations from expansions
            if storage_repr[k]['sub_type'] == 'gear' and 'expansion' in storage_repr[k].keys():
                exp_dict = self.Expansions.get_asset(storage_repr[k]['expansion'])
                storage_repr[k]['bgcolor'] = exp_dict['flair']['bgcolor']
                storage_repr[k]['color'] = exp_dict['flair']['color']

        # first thing we do is sort all handles from settlement storage into our
        # 'inventory' lists
        for item_handle in sorted(self.settlement['storage']):
            item_obj = self.storage_handle_to_obj(item_handle)
            item_type = item_obj.sub_type # this will be a key in storage_repr
            if item_type in storage_repr.keys():
                storage_repr[item_type]['inventory'].append(item_handle)
                if item_handle in storage_repr[item_type]['digest'].keys():
                   storage_repr[item_type]['digest'][item_handle]['count'] += 1
                else:
                    storage_repr[item_type]['digest'][item_handle] = {'count': 1, 'name': item_obj.name, 'handle': item_handle, 'desc': item_obj.desc, 'keywords': item_obj.keywords, 'rules': item_obj.rules}


        # now turn the digest dict into a list of dicts for easy iteration
        for k in storage_repr.keys():
            orig_digest = copy(storage_repr[k]['digest'])
            storage_repr[k]['digest'] = []
            for key, value in orig_digest.iteritems():
                storage_repr[k]['digest'].append(value)

        #finally, package up our main dicts for export as JSON
        gear_dict = {'storage_type': 'gear', 'name': 'Gear', 'locations': [], 'total': gear_total}
        reso_dict = {'storage_type': 'resources', 'name': 'Resource', 'locations': [], 'total': resources_total}
        for k in storage_repr.keys():
            if storage_repr[k]['sub_type'] == 'gear':
                gear_dict['locations'].append(storage_repr[k])
            elif storage_repr[k]['sub_type'] == 'resources':
                reso_dict['locations'].append(storage_repr[k])

        return json.dumps([reso_dict, gear_dict])


    def get_survivor_special_attributes(self):
        """ Special Attributes are ones that are unique to a campaign or to an
        expansion (so far). The assets live in the assets/survivor_sheet_options.py
        file. """

        output = []
        for h in self.campaign.survivor_special_attributes:
            output.append(self.SpecialAttributes.get_asset(h))
        return output


    def get_survivors(self, return_type=None, excluded=[], exclude_dead=False):
        """ This method is the ONE AND ONLY exception to the Settlement Object
        rule about never initializing survivors. This is the ONE AND ONLY place
        that suvivors are ever initialized by this class/object.

        Use the following 'return_type' kwargs to control output:

            - 'initialize' -> sets self.survivors to be a list of initialized
                survivor objects and then RETURNS A BOOL
            - 'departing' -> returns a list of survivor dictionaries where all
                the survivors have self.is_departing==True
            - 'groups' -> this should only be used by Campaign Summary type
                views. It returns a specialized dictionary of survivor info that
                is JSON-ish and meant to be used by front-end.

        The default output (i.e. no 'return_type') is a list of survivior
        dictionaries.

        Use the 'excluded' and 'exclude_dead' kwargs to control default output.
        """

        #
        #   This is the only place this entire class should ever initialize a 
        #   survivor. I'm not fucking joking.
        #

        if return_type == 'initialize':
            self.survivors = []
            query = {"settlement": self.settlement["_id"]}

            # query mods
            if excluded != []:
                query.update({'_id': {"$nin": excluded}})
            if exclude_dead:
                query.update({'dead': {'$exists': False}})

            all_survivors = utils.mdb.survivors.find(query).sort('name')
            for s in all_survivors:
                # init the survivor
                S = survivors.Survivor(_id=s["_id"], Settlement=self, normalize_on_init=False)
                S.bug_fixes(force_save=True)
                self.survivors.append(S)
#            self.logger.debug("%s Initialized %s survivors!" % (self, len(self.survivors)))
            return True

        # now make a copy of self.survivors and work it to fulfill the request
        output_list = copy(self.survivors)

        # do filters
        for s in output_list:
            if exclude_dead and s.is_dead() and s in output_list:
                output_list.remove(s)
            if excluded != [] and s._id in excluded and s in output_list:
                output_list.remove(s)

        # early returns
        if return_type == 'departing':
            return [s.serialize(dict, False) for s in output_list if s.is_departing()]

        #
        # late/fancy returns start here
        #

        if return_type == 'groups':
            # This is where we do the whole dance of organizing survivors for
            # the Campaign Summary. This is a LOOSE port of the legacy app
            # version of this method, and skips...a lot of its BS.

            groups = {
                'departing': {
                    'name': 'Departing',
                    'bgcolor': '#FFF',
                    'color': '#000',
                    'title_tip': 'Survivors in this group are currently <b>Departing</b> for a Showdown.',
                    'sort_order': '0',
                    'survivors': [],
                },
                'favorite':  {
                    'name': 'Favorite',
                    'title_tip': 'Survivors in this group are your favorite survivors.',
                    'sort_order': '1',
                    'survivors': []
                },
                'available': {
                    'name': 'Available',
                    'bgcolor': '#FFF',
                    'color': '#000',
                    'title_tip': 'Survivors in this group are currently in the Settlement and available to <b>Depart</b> or to participate in <b>Endeavors</b>.',
                    'sort_order': '2',
                    'survivors': [],
                },
                'skip_next': {'name': 'Skipping Next Hunt', 'sort_order': '3', 'survivors': []},
                'retired':   {'name': 'Retired', 'sort_order': '4', 'survivors': []},
                'the_dead':  {
                    'name': 'The Dead',
                    'bgcolor': '#FFF',
                    'color': '#000',
                    'title_tip': 'Dead survivors are memorialized here.',
                    'sort_order': '5',
                    'survivors': [],
                },
            }

            for s in output_list:
                if s.survivor.get('departing', None) == True:
                    groups['departing']['survivors'].append(s.serialize(dict, False))
                elif s.survivor.get('dead', None) == True:
                    groups['the_dead']['survivors'].append(s.serialize(dict, False))
                elif s.survivor.get('retired', None) == True:
                    groups['retired']['survivors'].append(s.serialize(dict, False))
                elif s.survivor.get('skip_next_hunt', None) == True:
                    groups['skip_next']['survivors'].append(s.serialize(dict, False))
                elif 'favorite' in s.survivor.keys() and request.User.login in s.survivor['favorite']:
                    groups['favorite']['survivors'].append(s.serialize(dict, False))
                else:
                    groups['available']['survivors'].append(s.serialize(dict, False))

            # make it JSON-ish
            output = []
            for k in sorted(groups.keys(), key=lambda k: groups[k]['sort_order']):
                groups[k]['handle'] = k
                output.append(groups[k])
            return output

        # default return; assumes that we want a list of dictionaries
        return [s.serialize(dict, False) for s in output_list]


    def get_survival_actions(self, return_type=dict):
        """ Returns a dictionary of survival actions available to the survivor
        based on campaign type. Individual SAs are either 'available' or not,
        depending on whether they're unlocked. """


        # first, build the master dict based on the campaign def
        sa_dict = {}
        sa_handles = self.campaign.survival_actions
        for handle in sa_handles:
            sa_dict[handle] = self.SurvivalActions.get_asset(handle)

        # set innovations to unavailable if their availablility is not defined
        # already within their definition:
        for k in sa_dict.keys():
            if not "available" in sa_dict[k]:
                sa_dict[k]["available"] = False
                sa_dict[k]["title_tip"] = "'%s' has not been unlocked yet." % sa_dict[k]["name"]

        # second, udpate the master list to say which are available
        for k,v in self.get_innovations(dict).iteritems():
            innovation_sa = v.get("survival_action", None)
            if innovation_sa in sa_dict.keys():
                sa_dict[innovation_sa]["available"] = True
                sa_dict[innovation_sa]["title_tip"] = "Settlement innovation '%s' unlocks this ability." % v["name"]

        # support a JSON return type:
        if return_type=="JSON":
            j_out = []
            for sa_key in sa_dict.keys():
                j_out.append(sa_dict[sa_key])
            return sorted(j_out, key=lambda k: k['sort_order'])

        # dict return
        return sa_dict


    def get_survivor_attribute_milestones(self):
        """ Returns a dictionary of the settlement's survivor attribute
        milestones. """

        return self.campaign.survivor_attribute_milestones


    def get_survival_limit(self, return_type=int):
        """ By default, this returns the settlement's Survival Limit as an
        integer.

        This method accepts the following values for 'return_type':
            - int (default)
            - bool
            - 'min'

        Setting the 'return_type' kwarg to bool when calling this method will
        return a boolean representing whether the settlement is enforcing the
        survival limit (based on expansions, etc.).

        Setting 'return_type' to "min" will return the minimum possible value
        that the settlement's Survival Limit may be set to.
        """

        if return_type == bool:
            for e_dict in self.list_assets("expansions"):
                if not e_dict.get("enforce_survival_limit", True):
                    return False
            return True
        elif return_type == 'min':

            minimum = 0

            # process innovations
            for i_dict in self.list_assets("innovations"):
                minimum += i_dict.get("survival_limit", 0)

            # process principles (separately)
            for p in self.settlement["principles"]:
                p_dict = self.Innovations.get_asset(p, backoff_to_name=True)
                minimum += p_dict.get("survival_limit", 0)

            return minimum

        return int(self.settlement["survival_limit"])


    def get_survivor_weapon_masteries(self):
        """ Returns a list of weapon mastery handles representing the weapon
        masteries that have been acquired by the settlement's survivors. """

        survivor_weapon_masteries = set()

        for S in self.survivors:
            for ai in S.list_assets("abilities_and_impairments"):
                if ai["handle"] in self.WeaponMasteries.get_handles():
                    survivor_weapon_masteries.add(ai["handle"])

        return sorted(list(survivor_weapon_masteries))




    def get_milestones_options(self, return_type=list):
        """ Returns a list of dictionaries where each dict is a milestone def-
        inition. Useful for front-end stuff. """



        if return_type==dict:
            output = {}
            for m_handle in self.campaign.milestones:
                output[m_handle] = self.Milestones.get_asset(m_handle)
            return output
        elif return_type==list:
            output = []
            for m_handle in self.campaign.milestones:
                output.append(self.Milestones.get_asset(m_handle))
            return output
        else:
            self.logger.error("get_milestones_options() does not support return_type=%s" % return_type)
            raise AttributeError


    def get_principles_options(self):
        """ Returns a dict (JSON) meant to be interated over in an ng-repeat on
        the Settlement Sheet. """

        p_handles = self.campaign.principles
        all_principles = {}
        for p_handle in p_handles:
            p_dict = self.Innovations.get_principle(p_handle)
            all_principles[p_dict["name"]] = p_dict

        sorting_hat = {}
        for p in all_principles.keys():
            sorting_hat[all_principles[p]["sort_order"]] = all_principles[p]

        output = []
        for n in sorted(sorting_hat.keys()):

            p_dict = sorting_hat[n]
            p_dict["options"] = {}

            for o in p_dict["option_handles"]:
                o_dict = self.Innovations.get_asset(o)

                selected=False
                if o_dict["handle"] in self.settlement["principles"]:
                    selected=True

                o_dict.update({"input_id": "%s_%s_selector" % (p_dict["handle"],o), "checked": selected})
                p_dict["options"][o] = o_dict

            p_dict["form_handle"] = "set_principle_%s" % p_dict["name"]
            output.append(p_dict)

        return output


    def get_special_rules(self):
        """ Assets that can have special rules (so far) are these:

            - Campaign
            - Expansions
            - Locations

        This method checks all assets belonging to the settlement and returns a
        set of special rules dictionaries.
        """

        output = []

        # campaign
        c_dict = self.get_campaign(dict)
        if c_dict.get('special_rules', None) is not None:
            for r in c_dict['special_rules']:
                output.append(r)

        # expansions and locations
        for a_list in ['expansions','locations']:
            for a_dict in self.list_assets(a_list):
                if a_dict.get('special_rules', None) is not None:
                    for r in a_dict['special_rules']:
                        output.append(r)

        return list(output)


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
            candidate_handles.append(self.campaign.final_boss)
        elif context == "defeated_monsters":
            candidate_handles.extend(self.settlement["quarries"])
            candidate_handles.extend(self.settlement["nemesis_monsters"])
            candidate_handles.extend(self.get_special_showdowns())
            candidate_handles.append(self.campaign.final_boss)
        elif context == "special_showdown_options":
            candidate_handles.extend(self.get_special_showdowns())
        else:
            self.logger.warn("Unknown 'context' for get_monster_options() method!")

        # now create the output list based on our candidates
        output = []

        # uniquify candidate handles just in case
        candidate_handles = list(set(candidate_handles))

        # this context wants handles back
#        if context == "nemesis_encounters":
#            for m in candidate_handles:
#                M = monsters.Monster(m)
#                if not M.is_selectable():
#                    candidate_handles.remove(m)

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
        output = sorted(output)
        return output


    def get_players(self, return_type=None):
        """ Returns a list of dictionaries where each dict is a short summary of
        the significant attributes of the player, as far as the settlement is
        concerned.

        This is NOT the place to get full user information and these dicts are
        intentionally sparse for exactly that reason.

        Otherwise, use return_type="count" to get an int representation of the
        set of players. """

        player_set = set()
        for s in self.survivors:
            player_set.add(s.survivor["email"])

        player_set = utils.mdb.users.find({"login": {"$in": list(player_set)}})

        if return_type == "count":
            return player_set.count()
        elif return_type == "email":
            return [p["login"] for p in player_set]

        player_list = []
        for p in player_set:
            p_dict = {"login": p["login"], "_id": p["_id"]}
            if p["login"] in self.settlement["admins"]:
                p_dict["settlement_admin"] = True
            if p["_id"] == self.settlement["created_by"]:
                p_dict["settlement_founder"] = True

            player_list.append(p_dict)

        return player_list




    #
    #   bug fix, conversion and migration functions start here!
    #

    def baseline(self):
        """ This checks the mdb document to make sure that it has basic aux-
        iliary and supplemental attribute keys. If it doesn't have them, they
        get added and we set self.perform_save = True. """


        #
        #   general data model 
        #

        if not "endeavor_tokens" in self.settlement.keys():
            self.settlement["endeavor_tokens"] = 0
            self.perform_save = True

        if not "location_levels" in self.settlement.keys():
            self.settlement["location_levels"] = {}
            self.perform_save = True
        if not "innovation_levels" in self.settlement.keys():
            self.settlement["innovation_levels"] = {}
            self.perform_save = True


        #
        #   This is where we add the 'meta' element; note that we actually
        #   convert from the old/initial implementation of 'meta' in this code
        #

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


        # Duck Typing!

        for attrib in ['survival_limit', 'population', 'death_count']:
            self.settlement[attrib] = int(self.settlement[attrib])


    def bug_fixes(self):
        """ In which we burn CPU cycles to fix our mistakes. """

        # 2017-10-05 legacy data bug
        if self.settlement.get("expansions", None) is None:
            self.settlement["expansions"] = []
            self.perform_save = True

        # 2017-10-05 - missing settlement attrib
        if self.settlement.get("expansions", None) is None:
            self.settlement["expansions"] = []
            self.perform_save = True

        # 2016-02-02 - Weapon Masteries bug
        for i in self.settlement["innovations"]:
            if len(i.split(" ")) > 1 and "-" in i.split(" "):
                self.logger.warn("Removing name '%s' from innovations for %s" % (i, self))
                self.settlement["innovations"].remove(i)
                replacement = self.Innovations.get_asset_from_name(i)
                if replacement is not None:
                    self.settlement["innovations"].append(replacement["handle"])
                    self.logger.warn("Replaced '%s' with '%s'" % (i, replacement["handle"]))
                else:
                    self.logger.error("Could not find an asset with the name '%s' for %s. Failing..." % (i, self))
                self.perform_save = True


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


    def convert_expansions_to_handles(self):
        """ Takes a legacy settlement object and swaps out its expansion name
        key values for handles. """

        new_expansions = []
        for e in self.get_expansions():
            if e in self.Expansions.get_handles():
                new_expansions.append(e)
            elif self.Expansions.get_asset_from_name(e) is None:
                self.logger.warn("Expansion '%s' is being removed from %s" % (e, self))
            elif self.Expansions.get_asset_from_name(e) is not None:
                new_expansions.append(self.Expansions.get_asset_from_name(e)["handle"])
            else:
                msg = "The expansion asset '%s' from %s cannot be migrated!" % (e, self)
                self.logger.error(msg)
                Models.AssetMigrationError(msg)

        self.settlement["expansions"] = new_expansions
        self.settlement["meta"]["expansions_version"] = 1.0
        self.logger.info("Migrated %s expansions to version 1.0. %s expansions were migrated!" % (self, len(new_expansions)))


    def convert_innovations_to_handles(self):
        """ Swaps out innovation 'name' key values for handles. """

        new_innovations = []
        for i in self.settlement["innovations"]:
            i_dict = self.Innovations.get_asset_from_name(i)
            if i_dict is None:
                self.log_event("Unknown innovation '%s' removed from settlement!" % i)
                self.logger.warn("Could not migrate innovation '%s'!" % i)
            else:
                new_innovations.append(i_dict["handle"])
                self.logger.debug("Converted '%s' to '%s'" % (i, i_dict["handle"]))

        if "innovation_levels" in self.settlement.keys():
            for i_name in self.settlement["innovation_levels"].keys():
                i_dict = self.Innovations.get_asset_from_name(i_name)
                if i_dict is None:
                    self.logger.warn("Could not convert innovation level for '%s'!" % i_name)
                else:
                    self.settlement["innovation_levels"][i_dict["handle"]] = self.settlement["innovation_levels"][i_name]
                    del self.settlement["innovation_levels"][i_name]

        self.settlement["innovations"] = new_innovations
        self.settlement["meta"]["innovations_version"] = 1.0
        self.logger.info("Converted innovations from names (legacy) to handles for %s" % (self))


    def convert_locations_to_handles(self):
        """ Swaps out location 'name' key values for handles. """

        L = locations.Assets()

        # first, swap all keys for handles, dropping any that we can't look up
        new_locations = []
        for loc in self.settlement["locations"]:
            loc_dict = L.get_asset_from_name(loc)
            if loc_dict is None:
                self.log_event("Unknown location '%s' removed from settlement!" % loc)
                self.logger.warn("Could not migrate location '%s'!" % loc)
            else:
                new_locations.append(loc_dict["handle"])
                self.logger.debug("Converted '%s' to '%s'" % (loc, loc_dict["handle"]))

        # next, migrate any location levels
        if "location_levels" in self.settlement.keys():
            for loc_name in self.settlement["location_levels"].keys():
                loc_dict = L.get_asset_from_name(loc_name)
                if loc_dict is None:
                    self.logger.warn("Could not convert location level for '%s'!" % loc_name)
                else:
                    self.settlement["location_levels"][loc_dict["handle"]] = self.settlement["location_levels"][loc_name]
                    del self.settlement["location_levels"][loc_name]

        self.settlement["locations"] = new_locations
        self.settlement["meta"]["locations_version"] = 1.0
        self.logger.info("Converted locations from names (legacy) to handles for %s" % (self))


    def convert_principles_to_handles(self):
        """ Swaps out principle 'name' keys for handles. """

        new_principles = []

        for p in self.settlement["principles"]:
            p_dict = self.Innovations.get_asset_from_name(p)

            if p_dict is None:
                self.logger.error("%s Ignoring unknown principle '%s'! Unable to convert!" % (self,p))
            else:
                new_principles.append(p_dict["handle"])
                self.logger.info("%s Migrated principle '%s' to '%s'" % (self, p, p_dict["handle"]))

        self.settlement["principles"] = new_principles
        self.settlement["meta"]["principles_version"] = 1.0
        self.logger.info("Converted principles from names (legacy) to handles for %s" % (self))


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


    def convert_storage(self):
        """ Converts settlement storage from legacy (list of names) to current
        (list of handles).

        Dumps old, custom, legacy free-text entries (they have no place in the
        glorious future).
        """

        old_storage = self.settlement['storage']
        new_storage = []

        for name in old_storage:
            a_dict = self.Gear.get_asset_from_name(name)
            if a_dict is None:
                a_dict = self.Resources.get_asset_from_name(name)
            if a_dict is None:
                self.logger.warn("%s Cannot convert storage name '%s' to a handle!" % (self, name))
            else:
                new_storage.append(a_dict['handle'])

        self.logger.info('%s Converted %s settlement storage items from names to handles!' % (self, len(new_storage)))
        if len(old_storage) < len(new_storage):
            self.logger.warn('%s %s settlement storage items could not be converted!' % (self, len(old_storage)-len(new_storage)))

        self.settlement['storage'] = sorted(new_storage)
        self.settlement["meta"]["storage_version"] = 1.0
        self.logger.debug("Migrated %s storage list from legacy data model to 1.0." % self)


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
                            if event in self.Events.get_names():
                                event_dict.update(self.Events.get_asset_from_name(event))
                            event_type_list.append(event_dict)
                    new_ly[k] = event_type_list

                # this is original data model (see doc string note)
                else:

                    err_msg = "Error converting legacy timeline! '%s' is an unknown event type!" % k

                    if k in ["settlement_event","story_event"]:
                        e = self.Events.get_asset_from_name(old_ly[k])
                        if e is not None:
                            event_type_list.append(e)
                        else:
                            try:
                                event_root, event_parens = old_ly[k].split("(")
                                e = self.Events.get_asset_from_name(event_root)
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


    def enforce_minimums(self):
        """ Enforces settlement minimums for Survival Limit, Death Count, etc.
        """

        # TK this isn't very DRY; could probably use some optimization

        min_sl = self.get_survival_limit("min")
        if self.settlement["survival_limit"] < min_sl:
            self.settlement["survival_limit"] = min_sl
            self.log_event("Survival Limit automatically increased to %s" % min_sl)
            self.perform_save = True

        min_pop = self.get_population("min")
        if self.settlement["population"] < min_pop:
            self.settlement["population"] = min_pop
            self.log_event("Settlement Population automatically increased to %s" % min_pop)
            self.perform_save = True

        min_death_count = self.get_death_count("min")
        if self.settlement["death_count"] < min_death_count:
            self.settlement["death_count"] = min_death_count
            self.log_event("Settlement Death Count automatically increased to %s" % min_death_count)
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


    #
    #   ???
    #

    def storage_handle_to_obj(self, handle):
        """ private method that turns any storage handle into an object."""
        asset_dict = self.Gear.get_asset(handle, raise_exception_if_not_found=False)
        if asset_dict is None:
            asset_dict = self.Resources.get_asset(handle)

        if asset_dict['type'] == 'gear':
            return gear.Gear(handle)
        else:
            return resources.Resource(handle)




    #
    #   finally, the request response router and biz logic. Don't write model
    #   methods below this one.
    #

    def request_response(self, action=None):
        """ Initializes params from the request and then response to the
        'action' kwarg appropriately. This is the ancestor of the legacy app
        assets.Settlement.modify() method. """

        self.get_request_params(verbose=False)

        #
        #   simple GET type methods
        #

        if action == "get":
            return Response(response=self.serialize(), status=200, mimetype="application/json")
        elif action == 'get_sheet':
            return Response(response=self.serialize('sheet'), status=200, mimetype="application/json")
        elif action == 'get_survivors':
            return Response(response=self.serialize('survivors'), status=200, mimetype="application/json")
        elif action == 'get_game_assets':
            return Response(response=self.serialize('game_assets'), status=200, mimetype="application/json")
        elif action == 'get_campaign':
            return Response(response=self.serialize('campaign'), status=200, mimetype="application/json")
        elif action == 'get_storage':
            return Response(response=self.get_settlement_storage(), status=200, mimetype="application/json")
        elif action == "get_event_log":
            return Response(response=self.get_event_log("JSON"), status=200, mimetype="application/json")
        elif action == "get_innovation_deck":
            return Response(response=self.get_innovation_deck("JSON"), status=200, mimetype="application/json")


        #
        #   set / update, etc. methods
        #
        elif action == 'set_last_accessed':
            self.set_last_accessed()
        elif action == "add_expansions":
            self.add_expansions()
        elif action == "rm_expansions":
            self.rm_expansions()

        # monster methods
        elif action == "set_current_quarry":
            self.set_current_quarry()
        elif action == "add_defeated_monster":
            self.add_defeated_monster()
        elif action == "rm_defeated_monster":
            self.rm_defeated_monster()

        elif action == "add_monster":
            self.add_monster()
        elif action == "rm_monster":
            self.rm_monster()
        elif action == "update_nemesis_levels":
            self.update_nemesis_levels()


        # misc sheet controllers
        elif action == "set_name":
            self.set_name()
        elif action == "set_attribute":
            self.set_attribute()
        elif action == "update_attribute":
            self.update_attribute()
        elif action == "update_endeavor_tokens":
            self.update_endeavor_tokens()
        elif action == "set_lost_settlements":
            self.set_lost_settlements()

        # survivor methods
        elif action == 'update_survivors':
            self.update_survivors()


        # timeline 
        elif action == "add_timeline_event":
            self.add_timeline_event(self.params)
        elif action == "rm_timeline_event":
            self.rm_timeline_event(self.params)

        # innovations, locations, etc.
        elif action == "add_location":
            self.add_location()
        elif action == "rm_location":
            self.rm_location()
        elif action == "set_location_level":
            self.set_location_level()

        elif action == "add_innovation":
            self.add_innovation()
        elif action == "rm_innovation":
            self.rm_innovation()
        elif action == "set_innovation_level":
            self.set_innovation_level()
        elif action == "set_principle":
            self.set_principle()

        elif action == 'set_storage':
            self.set_storage()
        elif action == 'set_showdown_type':
            self.set_showdown_type()

        elif action == 'add_monster_volume':
            self.add_monster_volume()
        elif action == 'rm_monster_volume':
            self.rm_monster_volume()

        elif action == 'set_inspirational_statue':
            self.set_inspirational_statue()
        elif action == 'set_lantern_research_level':
            self.set_lantern_research_level()


        elif action == 'abandon':
            self.set_abandoned()


        #
        #   campaign notes controllers
        #
        elif action == "add_note":
            self.add_settlement_note(self.params)
        elif action == "rm_note":
            self.rm_settlement_note(self.params)


        elif action == "return_survivors":
            self.return_survivors()

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

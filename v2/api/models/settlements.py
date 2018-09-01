#!/usr/bin/python2.7

from bson import json_util
from bson.objectid import ObjectId
import collections
from copy import copy, deepcopy
from datetime import datetime, timedelta
from flask import Response, request
import inspect
import json
import random
import time

import Models
import assets
from models import survivors, campaigns, cursed_items, disorders, gear, endeavors, epithets, expansions, fighting_arts, weapon_specializations, weapon_masteries, causes_of_death, innovations, survival_actions, events, abilities_and_impairments, monsters, milestone_story_events, locations, causes_of_death, names, resources, storage, survivor_special_attributes, weapon_proficiency, survivor_color_schemes, strain_milestones
import settings
import utils


class Assets(Models.AssetCollection):
    """ This is a weird one, because the "Assets" that go into creating a
    settlement or working with a settlement are kind of...the whole manager.
    Nevertheless, this odd-ball Assets() class is used to represent options
    for new settlements. """


    def __init__(self, *args, **kwargs):
        self.assets = {}
        self.type_override = "new_settlement_assets"
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
#       4. NEVER SORT THE settlement['milestone_story_events'] list
#

class Settlement(Models.UserAsset):
    """ This is the base class for all expansions. Private methods exist for
    enabling and disabling expansions (within a campaign/settlement). """

    def __init__(self, *args, **kwargs):
        self.collection="settlements"
        self.object_version=0.81
        Models.UserAsset.__init__(self,  *args, **kwargs)

        self.init_asset_collections()
        # now normalize
        if self.normalize_on_init:
            self.normalize()

#        if request.User.get_preference("update_timeline"):
#            self.update_timeline_with_story_events()
        if request and request.metering:
            stop = datetime.now()
            duration = stop - request.start_time
            self.logger.debug("%s initialize() -> in %s" % (self, duration))

        self.campaign_dict = self.get_campaign(dict)


    def init_asset_collections(self):
        """ Generally you want Models.UserAsset.load() to call this method. """

        self.Campaigns = campaigns.Assets()
        self.Endeavors = endeavors.Assets()
        self.Events = events.Assets()
        self.Expansions = expansions.Assets()
        self.FightingArts = fighting_arts.Assets()
        self.Gear = gear.Assets()
        self.Resources = resources.Assets()
        self.Innovations = innovations.Assets()
        self.Locations = locations.Assets()
        self.Milestones = milestone_story_events.Assets()
        self.Monsters = monsters.Assets()
        self.Names = names.Assets()
#        self.Storage = storage.Assets()
        self.SpecialAttributes = survivor_special_attributes.Assets()
        self.SurvivalActions = survival_actions.Assets()
        self.Survivors = survivors.Assets()
        self.SurvivorColorSchemes = survivor_color_schemes.Assets()
        self.WeaponMasteries = weapon_masteries.Assets()
        self.StrainMilestones = strain_milestones.Assets()


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

        patron_attribs = request.User.get_patron_attributes()
        if request.User.get_settlements(return_type=int) >= 3 and patron_attribs['level'] < 1:
            raise utils.InvalidUsage('Non-supporters may only create three settlements!', status_code=405)

        self.logger.info("%s is creating a new settlement..." % request.User)
#        self.logger.debug("%s new settlement params: %s" % (request.User, self.params))

        settlement = {
            # meta / admin
            "created_on": datetime.now(),
            "created_by": request.User._id,
            "admins": [request.User.login],
            "meta": {
                "timeline_version":     1.2,
                "campaign_version":     1.0,
                "monsters_version":     1.0,
                "expansions_version":   1.0,
                "innovations_version":  1.0,
                "locations_version":    1.0,
                "milestones_version":   1.0,
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
            "strain_milestones":        [],
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
        self.campaign_dict = self.get_campaign(dict)
        self.initialize_sheet()
        self.initialize_timeline(save=False)

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
                if s_dict.get('expansion', None) is not None:
                    self.add_expansions([s_dict['expansion']])

        # log settlement creation and save/exit
        self.save()


    def new_settlement_special(self, special_handle):
        """ Think of these as macros. Basically, you feed this a handle, it
        checks out the handle and then takes action based on it.

        This method DOES NOT look at the request for input. It...probably
        never will (i.e. this will always be a child of the new() method.
        """

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
        if script.get('showdown_type', None) is not None:
            self.set_showdown_type(script['showdown_type'])

        # events
        if script.get("timeline_events", None) is not None:
            for event in script["timeline_events"]:
                self.add_timeline_event(event)

        self.log_event(action="apply", key="settlement", value=script["name"], event_type='sysadmin')


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

        if self.settlement["meta"]["timeline_version"] == 1.0:
            self.convert_timeline_quarry_events()
            self.perform_save = True

        if self.settlement["meta"]["timeline_version"] == 1.1:
            self.flatten_timeline_events()
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

        if self.settlement["meta"].get("milestones_version", None) is None:
            self.convert_milestones_to_handles()
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


    def remove(self):
        """ Marks the settlement as removed. """
        self.settlement['removed'] = datetime.now()
        self.log_event('%s marked the settlement as removed!' % request.User.user['login'])
        self.save()


    def serialize(self, return_type=None):
        """ Renders the settlement, including all methods and supplements, as
        a monster JSON object. This is where all views come from."""

        output = self.get_serialize_meta()

        # do some tidiness operations first
        for k in ["locations","innovations"]:
            self.settlement[k] = sorted(self.settlement[k])

        # now start
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

            if request.metering:
                stop = datetime.now()
                duration = stop - request.start_time
                self.logger.debug("%s serialize(%s) -> Sheet element in %s" % (self, return_type, duration))

        # create game_assets
        if return_type in [None, 'game_assets','campaign']:
            start = datetime.now()
            output.update({"game_assets": {}})
            output["game_assets"].update(self.get_available_assets(innovations))
            output["game_assets"].update(self.get_available_assets(gear))
            output["game_assets"].update(self.get_available_assets(resources))
            output["game_assets"].update(self.get_available_assets(locations, only_include_selectable=True))
            output["game_assets"].update(self.get_available_assets(abilities_and_impairments))
            output["game_assets"].update(self.get_available_assets(weapon_specializations))
            output["game_assets"].update(self.get_available_assets(weapon_masteries))
            output["game_assets"]['weapon_proficiency_types'] = self.get_available_assets(weapon_proficiency)['weapon_proficiency']
            output["game_assets"].update(self.get_available_assets(cursed_items))
            output["game_assets"].update(self.get_available_assets(survival_actions))
            output["game_assets"].update(self.get_available_assets(events))
            output["game_assets"].update(self.get_available_assets(monsters))
            output["game_assets"].update(self.get_available_assets(causes_of_death, handles=False))
            output["game_assets"].update(self.get_available_assets(epithets))
            output["game_assets"].update(self.get_available_assets(fighting_arts))
            output["game_assets"].update(self.get_available_assets(disorders))
            output['game_assets'].update(self.get_available_assets(endeavors))
            output['game_assets'].update(self.get_available_assets(strain_milestones))

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
            output['game_assets']['inspirational_statue_options'] = self.get_available_fighting_arts(exclude_dead_survivors=False, return_type='JSON')
            output['game_assets']['monster_volumes_options'] = self.get_available_monster_volumes()

            if request.metering:
                stop = datetime.now()
                duration = stop - request.start_time
                self.logger.debug("%s serialize(%s) -> Game Assets element in %s" % (self, return_type, duration))

        # additional top-level elements for more API "flatness"
        if return_type in ['storage']:
            output['settlement_storage'] = self.get_settlement_storage()

        if return_type in [None, 'campaign']:
            output['survivor_color_schemes'] = self.SurvivorColorSchemes.get_sorted_assets()
            output["survivor_bonuses"] = self.get_bonuses("JSON")
            output["survivor_attribute_milestones"] = self.get_survivor_attribute_milestones()
            output["eligible_parents"] = self.get_eligible_parents()
            flags = assets.survivor_sheet_options.survivor_status_flags
            output['survivor_status_flags'] = [{'handle': k, 'name': flags[k]['name']} for k in flags.keys()]


        # campaign summary specific
        if return_type in ['campaign']:
            start = datetime.now()
            output.update({'campaign':{}})
            output['campaign'].update({'last_five_log_lines': self.get_event_log(lines=5)})
            output['campaign'].update({'most_recent_milestone': self.get_latest_milestone()})
            output['campaign'].update({'most_recent_hunt': self.get_latest_defeated_monster()})
            output['campaign'].update({'latest_death': self.get_latest_survivor('dead')})
            output['campaign'].update({'latest_birth': self.get_latest_survivor('born')})
            output['campaign'].update({'special_rules': self.get_special_rules()})
            output["user_assets"].update({'survivor_groups': self.get_survivors('groups')})

            # endeavors
            available_endeavors, available_endeavor_count = self.get_available_endeavors()
            output['campaign'].update({'endeavors': available_endeavors})
            output['campaign'].update({'endeavor_count': available_endeavor_count})

            if request.metering:
                stop = datetime.now()
                duration = stop - request.start_time
                self.logger.debug("%s serialize(%s) -> Campaign element in %s" % (self, return_type, duration))

        return json.dumps(output, default=json_util.default)


    def unremove(self, unremove_survivors=True):
        """ Deletes the 'removed' attribute from the settlement and, if the
        'unremove_survivors' kwarg is True, all surviors as well.

        Not sure whether this should be exposed via API yet, so for now, it's
        only available via admin.py.
        """

        if not self.settlement.get('removed', False):
            self.logger.warn('%s Ignoring bogus request to unremove settlement...' % self)
            return False

        del self.settlement['removed']
        self.log_event(action="unset", value="removed", event_type="sysadmin")
        if unremove_survivors:
            self.logger.debug("Unremoving survivors...")
            for s in utils.mdb.survivors.find({'settlement': self.settlement['_id']}):
                if s.get('removed',False):
                    S = survivors.Survivor(_id=s['_id'])
                    S.unremove()
        self.save()


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

            #
            # special handling for KD Collection pseudo expansions
            #

            # farts/disorders pseudo
            if asset_dict['type'] in ['fighting_arts','disorders'] and asset_dict['sub_type'] != 'secret_fighting_art':
                if 'kd_collection_fighting_arts_and_disorders' in self.settlement['expansions']:
                    if asset_dict['expansion'] in request.User.user['collection']['expansions']:
                        return True

            # se pseudo
            if asset_dict.get('sub_type', None) == 'settlement_event':
                if 'kd_collection_settlement_events' in self.settlement['expansions']:
                    if asset_dict['expansion'] in request.User.user['collection']['expansions']:
                        return True

            # normal test
            if asset_dict["expansion"] not in self.get_expansions():
                return False

        # check to see if the campaign forbids the asset
        if "forbidden" in self.get_campaign(dict):
            for f_key in self.campaign_dict["forbidden"]:
                if asset_dict.get("type", None) == f_key:
                    if asset_dict["handle"] in self.campaign_dict["forbidden"][f_key]:
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


    def initialize_timeline(self, save=True):
        """ Meant to be called during settlement creation, this method
        completely overwrites the settlement's timeline with the timeline
        'template' from the settlement's campaign.

        DO NOT call this method on an active/live settlement, unless you really
        know what you're doing.

        """

        self.settlement['timeline'] = copy(self.campaign.timeline)
        if request:
            self.logger.warn("%s initialized timeline for %s!" % (request.User, self))
        else:
            self.logger.warn("%s Timeline initialized from CLI!" % self)

        if save:
            self.save()


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
        self.log_event(action="add", key="Defeated Monsters list", value=monster_string, event_type="add_defeated_monster")
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
        self.log_event(action="rm", key="Defeated Monsters list", value=monster_string, event_type="rm_defeated_monster")
        self.save()


    def add_lantern_years(self, years=None):
        """ Adds 'years' lantern years to the timeline. Works with a request
        context. """

        if years is None:
            self.check_request_params(['years'])
            years = self.params['years']
        years = int(years)

        last_year_in_tl = self.settlement['timeline'][-1]['year']
        if last_year_in_tl >= 50:
            self.logger.error("%s Attempt to add more than 50 LYs to Timeline." % (request.User))
            raise utils.InvalidUsage("Max Lantern Years is 50!")

        for y in range(years):
            ly = last_year_in_tl + 1 + y
            self.settlement['timeline'].append({'year': ly})

        self.log_event(action="add", key="Timeline", value="%s Lantern Years" % years)
        self.save()


    def rm_lantern_years(self, years=None):
        """ Removes 'years' lantern years from the timeline. Works with a request
        context. Will NOT remove an LY with events in it. """

        if years is None:
            self.check_request_params(['years'])
            years = self.params['years']
        years = int(years)

        lys_removed = 0

        for y in range(years):
            if len(self.settlement['timeline'][-1]) < 2:
                removed_year = self.settlement['timeline'].pop()
                self.logger.warn("%s Removed Lantern Year: %s" % (request.User, removed_year))
                lys_removed +=1
            else:
                self.logger.warn("Refusing to remove LY %s (which has events)." % (self.settlement['timeline'][-1]['year']))

        self.log_event(action="rm", key="Timeline", value="%s Lantern Years" % lys_removed)
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
        self.log_event(action="add", key="%s monsters" % m_dict['type'], value=m_dict["name"], event_type="add_monster")
        self.save()


    def rm_monster(self, monster_handle=None):
        """ Removes a monster from the settlement's list of quarry or nemesis
        monsters. Basically the inverse of the add_monster() method (above)."""

        if monster_handle is None:
            self.check_request_params(["handle"])
            monster_handle = self.params["handle"]

        # sanity check the handle; load an asset dict for it
        m_dict = self.Monsters.get_asset(monster_handle)

        # figure out what type it is or die trying
        m_type = m_dict['type']
        if m_type == 'quarry':
            target_list = self.settlement['quarries']
        elif m_type == 'nemesis':
            target_list = self.settlement['nemesis_monsters']
        else:
            raise utils.InvalidUsage("%s Unable to process 'rm_monster' operation on asset: %s" % (self, m_dict))

        # general handling for both types
        if monster_handle in target_list:
            target_list.remove(monster_handle)
#            self.logger.debug("%s Removed '%s' handle from settlement %s monsters list." % (self, monster_handle, m_type))
        else:
            self.logger.error("%s Ignoring attempt to remove non-existing item '%s' from %s" % (self, monster_handle, m_type))

        # additional handling for nemeses
        if m_type == 'nemesis' and monster_handle in self.settlement['nemesis_encounters'].keys():
            del self.settlement["nemesis_encounters"][monster_handle]
#            self.logger.debug("%s Removed '%s' handle from settlement 'nemesis_encounters' dict..." % (self, monster_handle))

        self.log_event(action="rm", key="%s monsters" % m_dict['type'], value=m_dict["name"], event_type="rm_monster")
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

        self.log_event(action="add", key="Monster Volumes", value=vol_string, event_type='add_monster_volume')
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

        self.log_event(action="rm", key="Monster Volumes", value=vol_string, event_type='rm_monster_volume')
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
            self.log_event(action="adding", key="expansions", value=e_dict['name'])

            self.settlement["expansions"].append(e_handle)

            if "timeline_rm" in e_dict.keys():
               [self.rm_timeline_event(e, save=False) for e in e_dict["timeline_rm"] if e["ly"] >= self.get_current_ly()]
            if "timeline_add" in e_dict.keys():
               [self.add_timeline_event(e, save=False) for e in e_dict["timeline_add"] if e["ly"] >= self.get_current_ly()]
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
            self.log_event(action="removing", key="expansions", value=e_dict['name'])

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


    def add_location(self, loc_handle=None, save=True):
        "Adds a location to the settlement. Expects a request context"""

        if loc_handle is None:
            self.check_request_params(['handle'])
            loc_handle = self.params["handle"]

        #
        #   SANITY CHECK
        #

        # verify that the incoming handle is legit
        loc_dict = self.Locations.get_asset(loc_handle)

        # make sure it's not a dupe
        if loc_handle in self.settlement["locations"]:
            self.logger.error("Ignoring request to add duplicate location handle '%s' to settlement." % loc_handle)
            return False

        # check whether the loc is selectable; if not, refuse it
        if not loc_dict.get('selectable', True):
            raise utils.InvalidUsage("Refusing to add non-selectable '%s' location to settlement!" % loc_dict['name'])


        #
        #   UPDATE
        #

        # append it (do not sort)
        self.settlement["locations"].append(loc_handle)

        # do levels
        if "levels" in loc_dict.keys():
            self.settlement["location_levels"][loc_handle] = 1

        # log and (optional) save
        self.log_event(action="add", key="Locations", value=loc_dict['name'], event_type="add_location")
        if save:
            self.save()


    def rm_location(self, loc_handle=None, save=True):
        """ Removes a location from the settlement. Requires a request.User
        object, i.e. should not be called unless it is part of a request.  """

        if loc_handle is None:
            self.check_request_params(['handle'])
            loc_handle = self.params["handle"]

        #
        #   SANITY CHECK
        #

        # verify that the incoming handle is legit
        loc_dict = self.Locations.get_asset(loc_handle)

        # check to see if it's there to remove in the first place
        if loc_handle not in self.settlement["locations"]:
            self.logger.warn("Ignoring attempt to remove %s from %s locations  (because it is not there)." % (loc_handle, self))
            return False

        #
        #   UPDATE
        #

        # now do it
        self.settlement["locations"].remove(loc_handle)

        # log and (optional) save
        self.log_event(action="rm", key="Locations", value=loc_dict['name'], event_type="rm_location")
        if save:
            self.save()


    def add_milestone(self, handle=None):
        """ Adds a Milestone Story Event. Wants a request context. """

        if handle is None:
            self.check_request_params(['handle'])
            handle = self.params['handle']

        M = milestone_story_events.Milestone(handle)
        if M.handle in self.settlement['milestone_story_events']:
            self.logger.info("%s Attempting to add Milestone that is already present. Ignoring bogus request..." % self)
            return True

        self.settlement['milestone_story_events'].append(M.handle)
        self.log_event(action="add", key="Milestone Story Events", value=M.name, event_type="add_milestone_story_event")
        self.save()


    def rm_milestone(self, handle=None):
        """ Removes a Milestone Story Event. Wants a request context. """

        if handle is None:
            self.check_request_params(['handle'])
            handle = self.params['handle']

        M = milestone_story_events.Milestone(handle)
        if M.handle not in self.settlement['milestone_story_events']:
            self.logger.info("%s Attempting to remove Milestone that is not present. Ignoring bogus request..." % self)
            return True

        self.settlement['milestone_story_events'].remove(M.handle)
        self.log_event(action="rm", key="Milestone Story Events", value=M.name, event_type="rm_milestone_story_event")
        self.save()


    def add_innovation(self, i_handle=None, save=True):
        """ Adds an innovation to the settlement. Request context optional.

        NB: this method (and rm_innovations(), which basically is its inverse)
        does NOT process current survivors.

        Which, to put that another way, means that you SHOULD NOT be using this
        method to add principle-type innovations to the settlement!
        """

        if i_handle is None:
            self.check_request_params(["handle"])
            i_handle = self.params["handle"]

        #
        #   SANITY CHECK
        #

        # verify the handle by initializing it
        i_dict = self.Innovations.get_asset(i_handle)

        # pass/ignore if we're trying to add an innovation twice:
        if i_handle in self.settlement['innovations']:
            self.logger.warn("%s Attempt to add duplicate innovation handle, '%s'. Ignoring... " % (request.User, i_handle))
            return False

        # refuse to add principles
        if i_dict.get('sub_type', None) == 'principle':
            raise utils.InvalidUsage("'Principle-type innovations such as '%s' may not be added this way. Use the set_principle route instead." % (i_dict['name']))

        #
        #   UPDATE
        #

        # append (do not sort)
        self.settlement["innovations"].append(i_handle)

        # levels
        if i_dict.get("levels", None) is not None:
            self.settlement["innovation_levels"][i_handle] = 1

        # log here, before checking for 'current_survivor' attrib
        self.log_event(action="add", key="innovations", value=i_dict['name'], event_type="add_innovation")

        # check for 'current_survivor' attrib
        if i_dict.get('current_survivor', None) is not None:
            self.update_all_survivors('increment', i_dict['current_survivor'], exclude_dead=True)

        # (optional) save
        if save:
            self.save()



    def rm_innovation(self, i_handle=None, save=True):
        """ Removes an innovation from the settlement. Request context is
        optional.

        This method DOES NOT do anything to innovation levels, which stay saved
        on the settlement. If the user re-adds the innovation, it automatically
        sets the level back to one.

        Otherwise, this is just a mirror of add_innovation (above), so
        if you haven't read that doc string yet, I don't know what you're
        waiting for. """

        if i_handle is None:
            self.check_request_params(["handle"])
            i_handle = self.params["handle"]

        #
        #   SANITY CHECK
        #

        # verify the handle by initializing it
        i_dict = self.Innovations.get_asset(i_handle)

        # ignore bogus requests
        if i_handle not in self.settlement["innovations"]:
            self.logger.warn("%s Bogus attempt to remove non-existent innovation '%s'. Ignoring..." % (request.User, i_dict['name']))
            return False

        # refuse to add principles
        if i_dict.get('sub_type', None) == 'principle':
            raise utils.InvalidUsage("'Principle-type innovations such as '%s' may not be removed this way. Use the set_principle route instead." % (i_dict['name']))

        #
        #   UPDATE
        #

        # remove
        self.settlement["innovations"].remove(i_handle)

        # check for 'current_survivor' attrib
        if i_dict.get('current_survivor', None) is not None:
            self.update_all_survivors('decrement', i_dict['current_survivor'], exclude_dead=True)

        # log and (optional) save
        self.log_event(action="rm", key="innovations", value=i_dict['name'], event_type="rm_innovation")
        if save:
            self.save()



    def add_settlement_admin(self, user_login=None):
        """ Adds a user login (i.e. email address) to the self.settlement['admins']
        list. Fails gracefully if the user is already there. Expects a request
        context. """

        if user_login is None:
            self.check_request_params(['login'])
            user_login = self.params['login']

        if user_login in self.settlement['admins']:
            self.logger.warn("%s User '%s' is already a settlement admin! Ignoring bogus request..." % (self, user_login))
            return True

        if utils.mdb.users.find_one({'login': user_login}) is None:
            raise utils.InvalidUsage("The email address '%s' does not belong to a registered user!" % user_login, status_code=400)

        self.settlement['admins'].append(user_login)
        self.log_event(action="add", key="administrators", value=user_login)
        self.save()


    def rm_settlement_admin(self, user_login=None):
        """ Removes a user login (i.e. email address) from the
        self.settlement['admins'] list. Fails gracefully if the user is already
        there. Expects a request context. """

        if user_login is None:
            self.check_request_params(['login'])
            user_login = self.params['login']

        if user_login not in self.settlement['admins']:
            self.logger.warn("%s User '%s' is not a settlement admin! Ignoring bogus request..." % (self, user_login))
            return True

        if utils.mdb.users.find_one({'login': user_login}) is None:
            raise utils.InvalidUsage("The email address '%s' does not belong to a registered user!" % user_login, status_code=400)

        self.settlement['admins'].remove(user_login)
        self.log_event(action="rm", key="administrators", value=user_login)
        self.save()


    def add_settlement_note(self, n={}):
        """ Adds a settlement note to MDB. Expects a dict. """

        author = utils.mdb.users.find_one({'_id': ObjectId(n['author_id'])})

        ly = n.get('lantern_year', self.get_current_ly())
        author_email = n.get('author', author['login'])

        note_dict = {
            "note": n["note"].strip(),
            "created_by": author['_id'],
            "author": author_email,
            "created_on": datetime.now(),
            "settlement": self.settlement["_id"],
            "lantern_year": ly,
        }

        note_oid = utils.mdb.settlement_notes.insert(note_dict)
#        self.logger.debug("[%s] added a settlement note to %s" % (author_email, self))
        return Response(response=json.dumps({'note_oid': note_oid}, default=json_util.default), status=200)


    def rm_settlement_note(self, n_id=None):
        """ Removes a note from MDB. Expects a dict with one key. """

        if n_id is None:
            self.check_request_params(['_id'])
            n_id = self.params['_id']

        n_id = ObjectId(n_id)

        n = utils.mdb.settlement_notes.remove({"settlement": self.settlement["_id"], "_id": n_id})
#        self.logger.debug(n)
        self.logger.info("%s User '%s' removed a settlement note" % (self, request.User.login))


    def add_timeline_event(self, e={}, save=True):
        """ Adds a timeline event to self.settlement["timeline"]. Expects a dict
        containing the whole event's data: no lookups here. """

        #
        #   Initialize and Sanity Check
        #

        # ensure that the incoming event specifies the target LY
        t_index = e.get('ly', None)
        if t_index is None:
            raise utils.InvalidUsage("To add an event to the Timeline, the incoming event dict must specify a Lantern Year, e.g. {'ly': 3}")

#        del e['ly'] # we don't need this any more; remove it

        # if we can, "enhance" the incoming dict with additional asset info
        if e.get('handle', None) is not None:
            e.update(self.Events.get_asset(e['handle']))

        # if we don't know the event's sub_type, we have to bail
        if e.get('sub_type', None) is None:
            utils.InvalidUsage("To add an event to the Timeline, the incoming event dict must specify the 'sub_type' of the event, e.g. {'sub_type': 'nemesis_encounter'}")
            return False

        # compatibility check!
        if not self.is_compatible(e):
            self.logger.warn("Event '%s' is not compatible with this campaign! Ignoring reuqest to add..." % e['name'])
            return False


        #
        #   Add it!
        #

        # remove the target LY (we're going to update it and insert it back in
        target_ly = self.settlement["timeline"][t_index]
        self.settlement['timeline'].remove(target_ly)

        # update the target LY list to include a dict for our incomign sub_type
        #    if it doesn't already have one
        if target_ly.get(e['sub_type'], None) is None:
            target_ly[e['sub_type']] = []

        target_ly[e['sub_type']].append(e)

        # re-insert and save if successful
        self.settlement['timeline'].insert(t_index, target_ly)

        self.log_event(action='add', key="timeline (LY %s)" % t_index, value=e["name"], event_type="sysadmin")

        # finish with a courtesy save
        if save:
            self.save()


    def rm_timeline_event(self, e={}, save=True):
        """ This method supports the removal of an event from the settlement's
        Timeline.

        At a bare minimum, the 'e' kwarg must be an event dict that includes the
        'ly' key (which should be an int representing the target LY) and the
        'handle' key, which will be used to determine other values.

        If you want to remove an event WITHOUT using the 'handle' key, you must
        then include the following keys (at a minimum):
            - 'ly'
            - 'name'
            - 'sub_type'

        Finally, this method was revised to support Timeline version 1.2, so
        Timelines later/earlier than that may not work correctly with it.
        """

        #
        #   Initialization and Sanity Checks!
        #

        # ensure that the incoming event specifies the target LY to remove it
        #   from. The LY of the incoming event is also the index of the year
        #   dict we want to with (since Timelines start with LY 0)
        t_index = e.get('ly', None)
        if t_index is None:
            raise utils.InvalidUsage("To remove an event from the Timeline, the incoming event dict must specify a Lantern Year, e.g. {'ly': 3}")

        # if we can, "enhance" the incoming dict with additional asset info
        if e.get('handle', None) is not None:
            e.update(self.Events.get_asset(e['handle']))

        # if we don't know the event's sub_type, we have to bail
        if e.get('sub_type', None) is None:
            utils.InvalidUsage("To remove an event from the Timeline, the incoming event dict must specify the 'sub_type' of the event, e.g. {'sub_type': 'story_event'}")
            return False

        # finally, get the target LY from the timeline; fail gracefully if there
        #   are no events of our target sub_type
        target_ly = self.settlement['timeline'][t_index]
        if target_ly.get(e['sub_type'], None) is None:
            self.logger.error("Lantern Year %s does not include any '%s' events! Ignoring attempt to remove..." % (t_index, e['sub_type']))
            return False


        #
        #   Timeline Update
        #

        # initialize a generic success toke
        success = False

        # get the timeline and remove the target year, since we're going to
        # update it and then re-insert it when we're done
        timeline = self.settlement["timeline"]
        timeline.remove(target_ly)

        # figure out if we're removing by name or handle
        rm_attrib = 'handle'
        if e.get('handle', None) is None:
            rm_attrib = 'name'

        # now iterate through all events of our target sub_type in our target LY
        #   and kill them, if they match our handle/name
        for e_dict in target_ly[e['sub_type']]:
            if e_dict.get(rm_attrib, None) == e[rm_attrib]:
                target_ly[e['sub_type']].remove(e_dict)
                self.log_event(action='rm', key="timeline (LY %s)" % t_index, value=e["name"], event_type="sysadmin")
                success = True

        # insert our updated year back into the TL and save
        timeline.insert(t_index, target_ly)

        # check our success flag and, if we were successful, save. Otherwise, we
        #   freak the fuck out and panic (j/k: fail gracefully, but log/email
        #   the error back to home base
        if success:
            self.settlement["timeline"] = timeline
            if save:
                self.save()
        else:
            utils.InvalidUsage("Event could not be removed from timeline! %s" % (e))



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

        msg = "Departing Survivors returend to the settlement in %s." % (aftermath)
        if live_returns != []:
            returners = utils.list_to_pretty_string(live_returns)
            if showdown_type == 'special':
                msg = "%s healed %s." % (request.User.login, returners)
            else:
                msg = "%s returned to the settlement in %s." % (returners, aftermath)
        else:
            if showdown_type == 'special':
                msg = 'No survivors were healed after the Special Showdown.'
            else:
                msg = "No survivors returned to the settlement."
        self.log_event(msg, event_type="survivors_return_%s" % aftermath)


        # 6.) increment endeavors
        if showdown_type == 'normal' and live_returns != [] and aftermath == "victory":
            self.update_endeavor_tokens(len(live_returns), save=False)

        self.save()


    #
    #   set methods
    #

    def set_abandoned(self):
        """ Abandons the settlement by setting self.settlement['abandoned'] to
        datetime.now(). Logs it. Expects a request context. """

        self.settlement['abandoned'] = datetime.now()
        self.log_event(action='abandon', event_type='abandon_settlement')
        self.save()


    def set_current_ly(self, ly=None):
        """ Sets the current Lantern Year. Supports a request context, but does
        not require it. """

        if ly is None:
            self.check_request_params(['ly'])
            ly = self.params['ly']
        ly = int(ly)

        self.settlement['lantern_year'] = ly

        self.log_event(action='set', key="current Lantern Year", value=ly)
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
        self.log_event(action="set", key="Inspirational Statue", value=fa_dict['name'])
        self.save()


    def set_lantern_research_level(self):
        """ Sets the self.settlement['lantern_research_level'] to incoming 'value'
        param. Requires a request context."""

        self.check_request_params(['value'])
        level = self.params['value']

        # create the attrib if it doesn't exist
        self.settlement['lantern_research_level'] = level
        self.log_event(action="set", key="Lantern Research level", value=level)
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
            self.settlement["lost_settlements"] = int(new_value)

        self.log_event(action="set", key="Lost Settlements count", value=new_value)
        self.save()


    def set_name(self, new_name=None):
        """ Looks for the param key 'name' and then changes the Settlement's
        self.settlement["name"] to be that value. Works with or without a
        request context. """

        if new_name is None:
            self.check_request_params(['name'])
            new_name = self.params["name"]

        if new_name == "":
            new_name = "UNKNOWN"
        new_name = utils.html_stripper(new_name.strip())

        old_name = self.settlement["name"]
        self.settlement["name"] = new_name

        if old_name is None:
            msg = "%s named the settlement '%s'." % (request.User.login, new_name)
        else:
            msg = "%s changed settlement name from '%s' to '%s'" % (request.User.login, old_name, new_name)

        self.log_event(action="set", key="name", value=new_name)
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
                self.update_all_survivors("decrement", principle_dict["current_survivor"], exclude_dead=True)


        # do unset logic
        if unset:
            removed = 0
            for option in p_dict["option_handles"]:
                if option in self.settlement["principles"]:
                    remove_principle(option)
                    removed += 1
            if removed >= 1:
                self.log_event(action="unset", key="'%s' principle" % p_dict['name'], event_type="set_principle")
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
        self.log_event(action="set", key="'%s' principle" % p_dict['name'], value=e_dict['name'])

        # if we're still here, go ahead and save since we probably updated
        self.save()

        # post-processing: add 'current_survivor' effects
        if e_dict.get("current_survivor", None) is not None:
            self.update_all_survivors("increment", e_dict["current_survivor"], exclude_dead=True)


    def set_showdown_type(self, showdown_type=None):
        """ Expects a request context and looks for key named 'type'. Uses the
        value of that key as self.settlement['showdown_type']. """

        if showdown_type is None:
            self.check_request_params(['showdown_type'])
            showdown_type = self.params['showdown_type']

        self.settlement['showdown_type'] = showdown_type
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


    def update_all_survivors(self, operation=None, attrib_dict={}, exclude_dead=False):
        """ Performs bulk operations on all survivors. Use 'operation' kwarg to
        either 'increment' or 'decrement' all attributes in 'attrib_dict'.

        'attrib_dict' should look like this:

        {
            'Strength': 1,
            'Courage': 1,
            'abilities_and_impairments': ['sword_specialization', 'ageless'],
        }

        The 'increment' or 'decrement' values call the corresponding methods
        on the survivors.
        """

        if operation not in ['increment','decrement']:
            self.logger.exception("update_all_survivors() methods does not support '%s' operations!" % operation)
            raise Exception

        for s in self.survivors:
            if exclude_dead and s.is_dead():
                pass
            else:
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
    #   Replace Methods! These are Watcher-style methods for updating multiple
    #   data elements at once. 
    #

    def replace_game_assets(self):
        """ Works just like the method of the same name in the survivor class,
        but for settlements.

        This one REQUIRES A REQUEST CONTEXT and cannot be called without one. It
        also does not accept any arguments, because, again, it should only be
        called when there's a POST body to parse for arguments.

        Must like the Survivor version, this creates two lists: handles to add
        and handles to remove, and then does them one by one. If it fails at any
        point, the whole thing is a wash and we don't save any changes.
        """

        self.check_request_params(['type','handles'])
        asset_class = self.params['type']
        asset_handles = self.params['handles']

        if asset_class not in self.settlement.keys():
            raise utils.InvalidUsage("The settlement objects does not have an '%s' attribute!" % asset_class)
        elif type(self.settlement[asset_class]) != list:
            raise utils.InvalidUsage("The settlement object '%s' attribute is not a list type and cannot be updated with this method!" % asset_class)
        elif type(asset_handles) != list:
            raise utils.InvalidUsage("'handles' value must be a list/array type!")

        # special check (transitional) for supported attribs
        supported_attribs = ['innovations','locations']
        if asset_class not in supported_attribs:
            raise utils.InvalidUsage("This route currently only supports updates to the following attribute keys: %s!" % utils.list_to_pretty_string(supported_attribs, quote_char="'"))

        # 0.) force incoming asset_handles to be a set
        asset_handles = set(asset_handles)

        # 1.) initialize holder sets
        handles_to_add = [h for h in asset_handles if h not in self.settlement[asset_class]]
        handles_to_rm = [h for h in self.settlement[asset_class] if h not in asset_handles]

        # 1.a) bail if we've got no changes to make
        if handles_to_add == [] and handles_to_rm == []:
            self.logger.warn("%s Incoming replace_game_assets() request makes no changes! Ignoring..." % self)
            return True

        # 2.) if we're still here, iterate over the lists
        if asset_class == 'innovations':
            for r in handles_to_rm:
                self.rm_innovation(r, save=False)
            for a in handles_to_add:
                self.add_innovation(a, save=False)
        elif asset_class == 'locations':
            for r in handles_to_rm:
                self.rm_location(r, save=False)
            for a in handles_to_add:
                self.add_location(a, save=False)


        self.save()


    def replace_lantern_year(self):
        """ Sets a lantern year. Requires a request context. """

        self.check_request_params(['ly'])
        new_ly = self.params['ly']

        # thanks to LY zero, Lantern Years correspond to Timtline list indexes.
        del self.settlement['timeline'][new_ly['year']]
        self.settlement['timeline'].insert(new_ly['year'], new_ly)

        self.log_event("%s updated Timeline events for Lantern Year %s." % (request.User.login, new_ly['year']))
        self.save()



    def toggle_strain_milestone(self):
        """ toggles a strain milestone on or off, i.e. adds/rms it from the list. """

        # get the handle or die
        self.check_request_params(['handle'])
        handle = self.params['handle']

        # find the asset or die
        strain_milestone_asset = self.StrainMilestones.get_asset(handle)
        if strain_milestone_asset is None:
            raise utils.InvalidUsage("'%s' is not a valid Strain Milestone handle!" % handle)

        # now do the toggle
        action = 'add'
        if handle not in self.settlement['strain_milestones']:
            self.settlement['strain_milestones'].append(handle)
        else:
            self.settlement['strain_milestones'].remove(handle)
            action = 'rm'

        self.logger.debug(self.settlement['strain_milestones'])
        self.log_event(action=action, key="Strain Milestones", value=strain_milestone_asset['name'])
        self.save()





    #
    #   get methods
    #


    def get_available_assets(self, asset_module=None, handles=True, exclude_types=[], only_include_selectable=False):
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

        # remove excluded type/sub_types
        if exclude_types != []:
            A.filter("type", exclude_types)
            A.filter("sub_type", exclude_types)

        if only_include_selectable:
            A.filter('selectable', [False])

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


    def get_available_endeavors(self, return_total=True):
        """ Returns a list of endeavor handles based on campaign, innovations,
        locations, survivors and settlement events. """
        total = 0
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
#                    if req_inno not in self.settlement['innovations']:
                    if req_inno not in self.get_innovations(include_principles=True):
                        eligible = False
                if eligible:
                    eligible_endeavor_handles.append(e_handle)
            return eligible_endeavor_handles

        #
        #   all of these must be a list of dictionaries!
        #

        # campaign-specific
        if self.campaign_dict.get('endeavors', None) is not None:
            bogus_dict = {'name': self.campaign_dict['name'], 'endeavors': []}
            for e_handle in self.campaign_dict['endeavors']:
                bogus_dict['endeavors'].append(e_handle)
            available['campaign'].append(bogus_dict)

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

        # settlement events - crazy hacks here
        settlement_events = []
        current_ly = self.get_timeline_year(self.get_current_ly())
        events = current_ly.get('settlement_event', None)
        if events is not None:
            for event_dict in events:
                if event_dict.get('handle', None) is not None:
                    event_asset = self.Events.get_asset(event_dict['handle'])
                    if event_asset.get('endeavors',None) is not None:
                        eligible_endeavor_handles = get_eligible_endeavors(event_asset['endeavors'])
                        if len(eligible_endeavor_handles) >= 1:
                            event_asset['endeavors'] = eligible_endeavor_handles
                            available['settlement_events'].append(event_asset)
                else:
                    self.logger.warn("%s Timeline event dictionary does not have a handle key! Dict was: %s" % (self, event_dict))

        # return a tuple, if we're returning the total as well
        if return_total:
            for k in available.keys():
                for d in available[k]:
                    total += len(d.get('endeavors', []))
            return available, total

        return available


    def get_available_fighting_arts(self, exclude_dead_survivors=True, return_type=False):
        """ Returns a uniqified list of farting art handles based on LIVING
        survivors. """

        # 1.) create a set for live survivors and a set for dead survivors
        dead_survivors = set()
        live_survivors = set()
        for s in self.survivors:
            if s.is_dead():
                dead_survivors = dead_survivors.union(s.survivor['fighting_arts'])
            else:
                live_survivors = live_survivors.union(s.survivor['fighting_arts'])

        # 2.) if we're NOT excluding dead survivors, the final set is the union
        #   of both sets above; otherwise, its just the living survivors' set
        if not exclude_dead_survivors:
            fa_handles = dead_survivors.union(live_survivors)
        else:
            fa_handles = live_survivors

        # 3.) now, initialize our master set and remove the SFA's
        for fa_handle in fa_handles:
            fa_dict = self.FightingArts.get_asset(fa_handle, raise_exception_if_not_found=False)
            if fa_dict.get('sub_type', None) == 'secret_fighting_art':
                fa_handles.remove

        # 4.) now create the output based on requested 'return_type'
        if return_type in [False, list]:
            return sorted(list(fa_handles))
        elif return_type == "JSON":
            output = []
            for fa_handle in sorted(fa_handles):
                fa_dict = self.FightingArts.get_asset(fa_handle, raise_exception_if_not_found=False)
                if fa_handle in dead_survivors and fa_handle not in live_survivors:
                    fa_dict['select_disabled'] = True
                output.append(fa_dict)
            return output

        # raise an exception for un-handled return type
        raise utils.InvalidUsage('get_available_fighting_arts() does not support %s returns!' % return_type)


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
            for s in self.survivors:
                if s.is_dead():
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


    def get_event_log(self, return_type=None, ly=None, lines=None, get_lines_after=None, survivor_id=None):
        """ Returns the settlement's event log as a cursor object unless told to
        do otherwise.
        
        Checks for a request and, if one exists, tries to search for lines after
        a certain time.
        """

        if request and hasattr(self, 'params'):
            if 'lines' in self.params:
                lines = self.params['lines']
            if 'get_lines_after' in self.params:
                get_lines_after = self.params['get_lines_after']
            if 'survivor_id' in self.params:
                survivor_id = self.params['survivor_id']
            if 'ly' in self.params:
                ly = self.params['ly']

        query = {"settlement_id": self.settlement["_id"]}

        # modify the query, if we're doing that
        if get_lines_after is not None and ly is None:
            target_line = utils.mdb.settlement_events.find_one({'_id': ObjectId(get_lines_after)})
            query.update({"created_on": {'$gt': target_line['created_on']}})
        elif ly is not None and get_lines_after is None:
            query.update({'ly': int(ly)})

        if survivor_id is not None:
            query = {'survivor_id': ObjectId(survivor_id)}

        # now do the query
        event_log = utils.mdb.settlement_events.find(query).sort("created_on",-1)

        # limit, if we're doing that
        if lines is not None:
            event_log.limit(lines)

        # process 'return_type' and wrap up
        if return_type=="JSON":
            return json.dumps(list(event_log),default=json_util.default)

        return list(event_log)


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


    def get_gear_lookup(self, organize_by="sub_type"):
        """ This is a sort of...meta-method that renders the settlement's Gear
        and resource options as JSON. """

        # initialize 
        all_gear = copy(self.Gear.assets)

        # set compatible gear list
        compatible_gear = []
        for k in all_gear.keys():
            if self.is_compatible(all_gear[k]):
                compatible_gear.append(all_gear[k])

        output = {}
        for handle in all_gear.keys():
            gear_dict = all_gear[handle]
            if self.is_compatible(gear_dict):
                org_key = gear_dict[organize_by]
                if org_key not in output.keys():
                    output[org_key] = []
                output[org_key].append(gear_dict)

#        final = collections.OrderedDict()
#        for k in sorted(output.keys()):
#            final[k] = output[k]

        return json.dumps(compatible_gear, default=json_util.default)


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
        names, rather than as an object or as handles, etc.

        Unlike other methods, this one accepts a 'debug' kwarg. This was intro-
        duced to help resolve issue #503, which was occurring in production and
        not in test.
        """

        debug = self.params.get('debug', False)
        if debug:
            self.logger.debug("%s get_innovation_deck() debug enabled!" % self)

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


        if 'return_type' in self.params:
            return_type = self.params['return_type']

        #
        #   1.) baseline 'available' innovations
        #

        available = dict(self.get_available_assets(innovations)["innovations"])

        if debug:
            self.logger.debug("%s available innovations: %s" % (self, available.keys()))

        # remove principles and ones we've already got
        for a in available.keys():
            if a in self.settlement["innovations"]:
                del available[a]
                if debug:
                    self.logger.debug("%s already has '%s' innovation!" % (self, a))
            if self.Innovations.get_asset(a).get("sub_type", None) == "principle":
                del available[a]
                if debug:
                    self.logger.debug("%s removing '%s' principle from available innovations..." % (self, a))

        if debug:
            self.logger.debug("%s available innovations AFTER removing principles and assets in the settlement's list: %s" % (self, available.keys()))


        #
        #   2.) now, create a list of consequences (handles) from innovations
        #

        # consequences are a set until we need to sort them!
        consequences = set()
        for i_handle in self.settlement["innovations"]:
            cur_asset = self.Innovations.get_asset(i_handle)
            cur_asset_consequences = cur_asset.get("consequences", [])
            if debug:
                self.logger.debug("%s adding '%s' consequences: %s" % (self, i_handle, cur_asset_consequences))
            consequences = consequences.union(cur_asset_consequences)

        # now change from set to list and sort
        consequences = sorted(list(consequences))
        if debug:
            self.logger.debug("%s ALL consequences: %s" % (self, consequences))


        # now, remove all consequences that aren't available; this upgrades the
        #   'consequences' to 'available consequences', if you think about it
        for c in consequences:
            if c not in available.keys():
                consequences.remove(c)
                if debug:
                    self.logger.debug("%s removing UNAVAILABLE consequence: '%s'" % (self, c))

        # if we're debugging, list our current consequences and check the list
        # for any unavailable consequences that the previous iteration might
        # have mysteriously spared
        if debug:
            self.logger.debug("%s consequences after removing all UNAVAILABLE consequences: %s" % (self, consequences))
            for c in consequences:
                if c not in available.keys():
                    self.logger.error("%s consequences list includes UNAVAILABLE consequence '%s'" % (self, c))

        # 
        #   3.) initialize the deck dict using 'available consequences' (see
        #       above); now we have a proper deck to work with
        #
        deck_dict = {}
        for c in consequences:
            if c not in self.settlement["innovations"] and c in available.keys():
                asset_dict = self.Innovations.get_asset(c)
                deck_dict[c] = asset_dict

        if debug:
            self.logger.debug("%s deck dict initialized based on AVAILABLE consequences: %s" % (self, deck_dict.keys()))

        #
        #   4.) now iterate through remaining 'available' assets and give them
        #       a 'last chance' (i.e. see if we want them, even though they're
        #       not consequences)
        #

        for i_handle, i_dict in available.iteritems():
            if i_dict.get("available_if", None) is not None:
                for tup in i_dict['available_if']:
                    asset, collection = tup
                    if asset in self.settlement[collection]:
                        deck_dict[i_handle] = i_dict
                        self.logger.debug("%s Found value '%s' in settlement['%s']. Adding '%s' to innovation deck." % (self, asset, collection, i_dict['name']))

        #
        #   sanity/QA check on the way out
        #

        for c in deck_dict.keys():
            if c not in available.keys():
                self.logger.error("%s Unavailable consequence '%s' present in innovation deck!" % (self, c))


        #
        #   5.) now that we have a deck, make a sorted list version of it
        #
        deck_list = []
        for k in sorted(deck_dict.keys()):
            deck_list.append(deck_dict[k]["name"])
        deck_list = sorted(deck_list)

        #
        #   6.) optional dict-style return; requires 'consequences' cleanup
        #

        if return_type in ['dict', dict]:

            output = collections.OrderedDict()

            sorting_hat = {}
            for k,v in deck_dict.iteritems():
                sorting_hat[v['name']] = k

            for i_name in sorted(sorting_hat.keys()):
                i_dict = deepcopy(deck_dict[sorting_hat[i_name]])
                for c_handle in i_dict.get('consequences', []):
                    consequences_dict = self.Innovations.get_asset(c_handle)
                    if not self.is_compatible(consequences_dict):
                        i_dict['consequences'].remove(c_handle)
                output[i_dict['handle']] = i_dict

            return json.dumps(output)


        #
        #   Default return (i.e. dump the list of strings)
        #

        return json.dumps(deck_list)



    def get_lantern_research_level(self):
        """ Returns self.settlement['lantern_resarch_level']. Always an int."""

        return self.settlement.get('lantern_research_level', 0)


    def get_latest_defeated_monster(self):
        """ Tries to get the last handle in the defeated monsters list. Returns
        None if there is no such thing. """

        try:
            return self.settlement['defeated_monsters'][-1]
        except:
            return None


    def get_latest_milestone(self):
        """ Tries to get the last handle in the milestones list. Returns None if
        there is no such thing. """

        try:
            return self.settlement['milestone_story_events'][-1]
        except:
            return None


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

        gear_keywords = {}
        gear_rules = {}
        resources_keywords = {}
        resources_rules = {}


        def rollup_keywords(kw_dict, kw_list):
            """ Private func to add a list of keywords to a dictionary that keeps
            a running tally of them ."""

            for kw in kw_list:
                if kw not in kw_dict.keys():
                    kw_dict[kw] = 1
                else:
                    kw_dict[kw] += 1


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
                else:
                    raise utils.InvalidUsage("Unknown item sub_type '%s'!" % S.sub_type)

                # now that we've got an item object, touch it up and add it to the
                # locations 'collection' dict, updating the keywords rollup as we go
                if self.is_compatible(item_obj):
                    item_obj.quantity = self.settlement['storage'].count(item_obj.handle)

                    if S.sub_type == 'gear':
                        gear_total += item_obj.quantity
                        for i in range(item_obj.quantity):
                            rollup_keywords(gear_keywords, item_obj.keywords)
                            rollup_keywords(gear_rules, item_obj.rules)
                    elif S.sub_type == 'resources':
                        resources_total += item_obj.quantity
                        for i in range(item_obj.quantity):
                            rollup_keywords(resources_keywords, item_obj.keywords)
                            rollup_keywords(resources_rules, item_obj.rules)

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
        gear_dict = {
            'storage_type': 'gear',
            'name': 'Gear',
            'locations': [],
            'total': gear_total,
            'keywords': gear_keywords,
            'rules': gear_rules,
        }
        reso_dict = {
            'storage_type': 'resources',
            'name': 'Resource',
            'locations': [],
            'total': resources_total,
            'keywords': resources_keywords,
            'rules': resources_rules,
        }

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
            query = {"settlement": self.settlement["_id"], "removed": {"$exists": False}}

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

            minimum = 1

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


    def get_timeline(self, return_type=None):
        """ Returns the timeline. """

        TL = self.settlement['timeline']

        if return_type=="JSON":
            return json.dumps(TL, default=json_util.default)

        return TL


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
        if self.campaign_dict.get('special_rules', None) is not None:
            for r in self.campaign_dict['special_rules']:
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
        for n in self.settlement.get(monster_type, []):
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
        if "forbidden" in self.campaign_dict.keys() and monster_type in self.campaign_dict["forbidden"].keys():
            forbidden.extend(self.campaign_dict["forbidden"][monster_type])
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


    def get_timeline_year(self, target_ly=0):
        """ Accepts an int 'ly' and returns that LY's dictionary (as a copy). """

        for ly in self.settlement['timeline']:
            if int(ly['year']) == int(target_ly):
                return copy(ly)


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
            candidate_handles.extend(self.settlement.get("quarries", []))
        elif context == "nemesis_encounters":
            candidate_handles.extend(self.settlement.get("nemesis_monsters", []))
            candidate_handles.append(self.campaign.final_boss)
        elif context == "defeated_monsters":
            candidate_handles.extend(self.settlement.get("quarries", []))
            candidate_handles.extend(self.settlement.get("nemesis_monsters",[]))
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

        # data model - required lists
        for req_list in ['nemesis_monsters','quarries','strain_milestones']:
            if not req_list in self.settlement.keys():
                self.settlement[req_list] = []
                self.perform_save = True

        # data model - required dictionaries
        for req_dict in ['nemesis_encounters','innovation_levels','location_levels']:
            if not req_dict in self.settlement.keys():
                self.settlement[req_dict] = {}
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

        # 2018-03-23 - storage handles with apostrophes
        for i in self.settlement['storage']:
            item_index = self.settlement['storage'].index(i)
            if i == "manhunter's_hat":
                self.settlement['storage'].remove(i)
                self.settlement['storage'].insert(item_index, 'manhunters_hat')
                self.logger.warn("%s BUG FIX: changed %s to 'manhunters_hat'" % (self,i))
                self.perform_save = True
            elif i == "hunter's_heart":
                self.settlement['storage'].remove(i)
                self.settlement['storage'].insert(item_index, 'hunters_heart')
                self.logger.warn("%s BUG FIX: changed %s to 'hunters_heart'" % (self,i))
                self.perform_save = True
            elif i == "jack_o'_lantern":
                self.settlement['storage'].remove(i)
                self.settlement['storage'].insert(item_index, 'jack_o_lantern')
                self.logger.warn("%s BUG FIX: changed %s to 'jack_o_lantern'" % (self,i))
                self.perform_save = True

        # 2018-03-20 - missing timeline bug
        if self.settlement.get('timeline', None) is None:
            self.logger.error("%s has no Timeline! Initializing Timeline..." % self)
            self.initialize_timeline()

        # 2017-12-16 - principles in the innovations list
        for i in self.list_assets('innovations'):
            if i.get('sub_type', None) == 'principle':
                self.settlement['innovations'].remove(i['handle'])
                self.logger.warn("%s Removed principle '%s' from innovations list!" % (self, i['name']))

        # 2017-10-05 - legacy data bug
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

        if self.settlement['campaign'] in self.Campaigns.get_handles():
            return True

        sorting_hat = {}
        for handle in self.Campaigns.get_handles():
            c_dict = self.Campaigns.get_asset(handle)
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
                self.log_event("Unknown innovation '%s' removed from settlement!" % i, event_type="sysadmin")
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
                self.log_event("Unknown location '%s' removed from settlement!" % loc, event_type="sysadmin")
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


    def convert_milestones_to_handles(self):
        """ Swaps out milestone name values for handles. """

        new_milestones = []
        for m_dict in self.list_assets('milestone_story_events'):
            if m_dict is not None:
                new_milestones.append(m_dict['handle'])
        self.settlement['milestone_story_events'] = new_milestones
        self.settlement["meta"]["milestones_version"] = 1.0
        self.logger.info("%s Converted %s milestones form names (legacy) to handles." % (self, len(new_milestones)))


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
        self.logger.warn("Migrated %s timeline to version 1.1" % (self))


    def flatten_timeline_events(self):
        """ Takes a 1.1 timeline and un-expands detailed dictionary info."""

        new_timeline = []
        for y in self.settlement['timeline']:
            new_year = {}
            for event_group in y.keys():
                if event_group != 'year':
                    new_event_group = []
                    for event in y[event_group]:
                        # if we have a 'name' and not a 'handle'
                        if event.get('name', None) is not None and event.get('handle', None) is None:
#                            self.logger.debug("OK %s" % event)
                            new_event_group.append(event)
                        else:
                            new_event_group.append({'handle': event['handle']})
#                            self.logger.debug("UPDATED: %s" % event)
                    new_year[event_group] = new_event_group
                else:
                    new_year['year'] = y['year']
            new_timeline.append(new_year)

        self.settlement["timeline"] = new_timeline
        self.settlement["meta"]["timeline_version"] = 1.2
        self.logger.warn("Migrated %s timeline to version 1.2" % (self))


    def enforce_minimums(self):
        """ Enforces settlement minimums for Survival Limit, Death Count, etc.
        """

        # TK this isn't very DRY; could probably use some optimization

        min_sl = self.get_survival_limit("min")
        if self.settlement["survival_limit"] < min_sl:
            self.settlement["survival_limit"] = min_sl
            self.log_event("Survival Limit automatically increased to %s" % min_sl, event_type="sysadmin")
            self.perform_save = True

        min_pop = self.get_population("min")
        if self.settlement["population"] < min_pop:
            self.settlement["population"] = min_pop
            self.log_event("Settlement Population automatically increased to %s" % min_pop, event_type="sysadmin")
            self.perform_save = True

        min_death_count = self.get_death_count("min")
        if self.settlement["death_count"] < min_death_count:
            self.settlement["death_count"] = min_death_count
            self.log_event("Settlement Death Count automatically increased to %s" % min_death_count, event_type="sysadmin")
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
            asset_dict = self.Resources.get_asset(handle, raise_exception_if_not_found=False)

            # die violently if we still can't find it
            if asset_dict is None:
                err = "Storage handle '%s' does not exist in Gear or Resources assets!" % handle
                self.logger.error(err)
                raise utils.InvalidUsage(err)

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
        elif action == 'get_summary':
            return Response(response=self.serialize('dashboard'), status=200, mimetype="application/json")
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
        elif action == "gear_lookup":
            return Response(response=self.get_gear_lookup(), status=200, mimetype="application/json")
        elif action == "get_innovation_deck":
            return Response(response=self.get_innovation_deck(), status=200, mimetype="application/json")
        elif action == "get_timeline":
            return Response(response=self.get_timeline("JSON"), status=200, mimetype="application/json")


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

        # timeline!
        elif action == 'replace_lantern_year':
            self.replace_lantern_year()
        elif action == "add_lantern_years":
            self.add_lantern_years()
        elif action == "rm_lantern_years":
            self.rm_lantern_years()
        elif action == "set_current_lantern_year":
            self.set_current_ly()

        # survivor methods
        elif action == 'update_survivors':
            self.update_survivors()


        # innovations, locations, etc.
        elif action == "replace_game_assets":
            self.replace_game_assets()

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

        # milestone story events
        elif action == "add_milestone":
            self.add_milestone()
        elif action == "rm_milestone":
            self.rm_milestone()

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


        elif action == 'toggle_strain_milestone':
            self.toggle_strain_milestone()

        elif action == 'abandon':
            self.set_abandoned()
        elif action == 'remove':
            self.remove()


        #
        #   meta/admin
        #

        elif action == 'add_admin':
            self.add_settlement_admin()
        elif action == 'rm_admin':
            self.rm_settlement_admin()

        #
        #   campaign notes controllers
        #
        elif action == "add_note":
            return self.add_settlement_note(self.params)
        elif action == "rm_note":
            self.rm_settlement_note()


        elif action == "return_survivors":
            self.return_survivors()



        #
        #   finally, the catch-all/exception-catcher
        #
        else:
            # unknown/unsupported action response
            self.logger.warn("Unsupported settlement action '%s' received!" % action)
            return utils.http_400

        # support special response types
        if "response_method" in self.params:
            exec "payload = self.%s()" % self.params['response_method']
            return Response(payload, status=200, mimetype="application/json")
        elif "serialize_on_response" in self.params:
            return Response(self.serialize(), status=200, mimetype="application/json")

        # default return
        return utils.http_200





# ~fin

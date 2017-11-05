#!/usr/bin/python2.7

from bson import json_util
from bson.objectid import ObjectId
from copy import copy
from datetime import datetime
from flask import request, Response
import json
import random

import Models
import utils

from assets import survivor_sheet_options, survivors
from models import abilities_and_impairments, cursed_items, disorders, endeavors, epithets, fighting_arts, names, saviors, survival_actions, survivor_special_attributes, the_constellations, weapon_proficiency


class Assets(Models.AssetCollection):
    """ These are pre-made survivors, e.g. from the BCS. """

    def __init__(self, *args, **kwargs):
        self.assets = survivors.beta_challenge_scenarios
        self.type = "survivor"
        Models.AssetCollection.__init__(self,  *args, **kwargs)

    def get_specials(self, return_type=dict):
        """ This returns the 'specials' macro dicts, which are basically simple
        'scripts' for operating on a settlement at creation time. """

        d = copy(survivors.specials)

        for k in sorted(d.keys()):
            d[k]["handle"] = k

        if return_type == "JSON":
            output = []
            for k in sorted(d.keys()):
                output.append(d[k])
            return output

        return d

    def get_defaults(self):
        """ Returns a dictionary of default attribute values for survivors. """

        d = copy(survivors.defaults)
        return d




class Survivor(Models.UserAsset):
    """ This is the base class for all expansions. Private methods exist for
    enabling and disabling expansions (within a campaign/settlement). """


    def __repr__(self):
        return "%s [%s] (%s)" % (self.survivor["name"], self.survivor["sex"], self.survivor["_id"])


    def __init__(self, *args, **kwargs):
        self.collection="survivors"
        self.object_version = 0.79

        # initialize AssetCollections for later
        self.CursedItems = cursed_items.Assets()
        self.Disorders = disorders.Assets()
        self.Saviors = saviors.Assets()
        self.SpecialAttributes = survivor_special_attributes.Assets()

        # data model meta data
        self.stats =                ['Movement','Accuracy','Strength','Evasion','Luck','Speed','bleeding_tokens']
        self.game_asset_keys =      ['disorders','epithets','fighting_arts','abilities_and_impairments']
        self.armor_locations =      ['Head', 'Body', 'Arms', 'Waist', 'Legs']
        self.flags =                ['skip_next_hunt','cannot_use_fighting_arts','cannot_spend_survival','departing','cannot_gain_bleeding_tokens']
        self.abs_value_attribs =    ['max_bleeding_tokens', ]
        self.min_zero_attribs =     ["hunt_xp","Courage","Understanding"]
        self.min_one_attribs =      ["Movement"]
        self.damage_locations = [
           "brain_damage_light",
           "head_damage_heavy",
           "arms_damage_light",
           "arms_damage_heavy",
           "body_damage_light",
           "body_damage_heavy",
           "waist_damage_light",
           "waist_damage_heavy",
           "legs_damage_light",
           "legs_damage_heavy",
        ]

        # if we're doing a new survivor, it will happen when we subclass the
        # Models.UserAsset class:
        Models.UserAsset.__init__(self,  *args, **kwargs)

        # this makes the baby jesus cry
        if self.Settlement is None:
            if request and request.collection != 'survivor':
                self.logger.warn("%s Initializing Settlement object! THIS IS BAD FIX IT" % self)
            import settlements
            self.Settlement = settlements.Settlement(_id=self.survivor["settlement"], normalize_on_init=False)

        if self.normalize_on_init:
            self.normalize()


    def new(self):
        """ Creates a new survivor.

        The 'attribs' dictionary will be used, after initialization, to add or
        overwrite all key/value pairs on self.survivor.

        Important! Only attrib keys that are part of the baseline survivor data
        model will be used! Any other keys in 'attribs' will be ignored!

        If this is an internal call, i.e. from the settlement creation method
        or similar, simply set self.new_asset_attribs to be a dictionary of the
        required survivor attribs.

        Otherwise, attribs will come from the request params.

        """

        # if called without attribs dict, assume we're responding to a request
        #   and initialize attribs to be request params
        if self.new_asset_attribs == {}:
            attribs = self.params
        else:
            attribs = self.new_asset_attribs

#        self.logger.debug(attribs)

        #
        #   Can't create a survivor without initializing a settlement! do
        #   that first, an fail bigly if you cannot
        #

        import settlements  # baby jesus, still crying
        self.Settlement = settlements.Settlement(_id=attribs["settlement"])
        self.settlement_id = self.Settlement.settlement["_id"]


        self.survivor = {

            # meta and housekeeping
            "meta": {
                "abilities_and_impairments_version": 1.0,
                "disorders_version": 1.0,
                "epithets_version": 1.0,
                "favorites_version": 1.0,
                "fighting_arts_version": 1.0,
                "special_attributes_version": 1.0,
                "weapon_proficiency_type": 1.0,
            },
            "email":        request.User.login,
            "born_in_ly":   self.get_current_ly(),
            "created_on":   datetime.now(),
            "created_by":   request.User._id,
            "settlement":   self.settlement_id,
            "public":       False,

            # survivor sheet
            "name":     "Anonymous",
            "sex":      "R",
            "survival": 0,
            "hunt_xp":  0,
            "Insanity": 0,
            "Head":     0,
            "Arms":     0,
            "Body":     0,
            "Waist":    0,
            "Legs":     0,
            "Courage":  0,
            "Understanding": 0,
            "affinities": {"red":0,"blue":0,"green":0},

            # misc
            'inherited': {
                'father': {'abilities_and_impairments': [], 'disorders': [], 'fighting_arts': []},
                'mother': {'abilities_and_impairments': [], 'disorders': [], 'fighting_arts': []},
            },
            'departing': False,
            'bleeding_tokens': 0,
            'max_bleeding_tokens': 5,

            # attributes
            "Movement": 5,
            "Accuracy": 0,
            "Strength": 0,
            "Evasion":  0,
            "Luck":     0,
            "Speed":    0,
            "attribute_detail": {
                "Movement": {"tokens": 0, "gear": 0},
                "Accuracy": {"tokens": 0, "gear": 0},
                "Strength": {"tokens": 0, "gear": 0},
                "Evasion":  {"tokens": 0, "gear": 0},
                "Luck":     {"tokens": 0, "gear": 0},
                "Speed":    {"tokens": 0, "gear": 0},
            },

            # weapon proficiency 
            "Weapon Proficiency": 0,
            "weapon_proficiency_type": None,

            # game assets
            "abilities_and_impairments": [],
            "cursed_items": [],
            "disorders": [],
            "epithets": [],
            "favorite": [],
            "fighting_arts": [],
            "fighting_arts_levels": {},
        }

        c_dict = self.get_campaign(dict)

        # 1.a apply/overwrite attribs that go with our data model
        for a in attribs.keys():
            if a in self.survivor.keys():
                forbidden_keys = ['settlement']
                if a not in forbidden_keys and attribs[a] != None:
                    self.survivor[a] = attribs[a]

        # 1.b for bools, keep 'em bool, e.g. in case they come in as 'checked'
        for boolean in ["public"]:
            self.survivor[boolean] = bool(self.survivor[boolean])

        # 1.c if sex is "R", pick a random sex
        if self.survivor["sex"] == "R":
            self.survivor["sex"] = random.choice(["M","F"])

        # 1.d sanity check new attribs; die violently if we fail here
        if self.survivor["sex"] not in ["M","F"]:
            msg = "Invalid survivor 'sex' attrib '%s' received! Must be 'M' or 'F' and str type!" % (self.survivor["sex"])
            self.logger.exception(msg)
            raise utils.InvalidUsage(msg, status_code=400)

        sex_pronoun = "his"
        if self.survivor['sex'] == 'F':
            sex_pronoun = 'her'

        # 1.e random name
        N = names.Assets()
        if self.survivor["name"] == "Anonymous" and request.User.get_preference("random_names_for_unnamed_assets"):
            self.survivor["name"] = N.get_random_survivor_name(self.survivor["sex"])

        # 1.f now save, get an OID so we can start logging and
        #   start calling object/class methods

        self._id = utils.mdb.survivors.insert(self.survivor)
        self.load()
        self.log_event("%s created new survivor %s" % (request.User.login, self.pretty_name()))


        #
        #   2. parents and newborn status/operations
        #

        # 2.a check for incoming parents
        parent_names = []
        for parent in ["father","mother"]:
            if parent in attribs.keys() and attribs[parent] is not None:
                parent_oid = ObjectId(attribs[parent])
                parent_mdb = utils.mdb.survivors.find_one({"_id": parent_oid})
                parent_names.append(parent_mdb["name"])
                self.survivor[parent] = parent_oid

                # check parents for inheritable A&Is
                AI = abilities_and_impairments.Assets()
                for ai in parent_mdb['abilities_and_impairments']:
                    ai_asset = AI.get_asset(ai)
                    if ai_asset.get('inheritable', False):
                        self.survivor['inherited'][parent]['abilities_and_impairments'].append(ai)
                        self.log_event('%s inherited %s from %s %s %s.' % (self.pretty_name(), ai_asset['name'], sex_pronoun, parent, parent_mdb['name']), event_type='survivor_inheritance')
                        self.add_game_asset('abilities_and_impairments', ai)


        # 2.b set newborn status; create parent_string var (for logging)
        survivor_is_a_newborn = False
        if parent_names != []:
            survivor_is_a_newborn = True

            genitive_appellation = "Son"
            parent_string = ' and '.join(parent_names)
            if self.survivor["sex"] == "F":
                genitive_appellation = "Daughter"


        # 2.c log the birth/joining
        if survivor_is_a_newborn:
            self.log_event("%s born to %s!" % (self.pretty_name(), parent_string), event_type="survivor_birth")
        else:
            self.log_event('%s joined the settlement!' % (self.pretty_name()), event_type="survivor_join")

        # 2.d increment survivial if we're named
        if self.survivor["name"] != "Anonymous" and self.survivor["survival"] == 0:
            self.log_event("Automatically added 1 survival to %s" % self.pretty_name())
            self.survivor["survival"] += 1

        # 3.a avatar - LEGACY CODE BELOW
#        if params is not None and "survivor_avatar" in params and params["survivor_avatar"].filename != "":
#        self.update_avatar(params["survivor_avatar"]

        # 3.b settlement buffs - move this to a separate function
        if request.User.get_preference("apply_new_survivor_buffs"):

            def apply_buff_list(l):
                """ Private helper to apply a dictionary of bonuses. """
                for d in l:
                    for k in d.keys():
                        if k == "affinities":
                            self.update_affinities(d[k])
                        elif k == "abilities_and_impairments":
                            if type(d[k]) != list:
                                msg = "The 'abilities_and_impairments' bonus must be a list! Failing on %s" % d
                                self.logger.exception(msg)
                                raise Exception(msg)
                            for a_handle in d[k]:
                                self.add_game_asset("abilities_and_impairments", a_handle)
                        else:
                            self.update_attribute(k, d[k])


            buff_sources = set()
            buff_list = []
            # bonuses come from principles, innovations...
            for attrib in ["principles","innovations"]:
                for d in self.Settlement.list_assets(attrib):
                    if d.get("new_survivor", None) is not None:
                        buff_list.append(d["new_survivor"])
                        buff_sources.add(d["name"])
                    if survivor_is_a_newborn:
                        if d.get("newborn_survivor", None) is not None:
                            buff_list.append(d["newborn_survivor"])
                            buff_sources.add(d["name"])
            # ...and also from the campaign definition for now
            if c_dict.get('new_survivor', None) is not None:
                buff_list.append(c_dict['new_survivor'])
                buff_sources.add("'%s' campaign" % c_dict["name"])
            if survivor_is_a_newborn:
                if c_dict.get('newborn_survivor', None) is not None:
                    buff_list.append(c_dict['newborn_survivor'])
                    buff_sources.add("'%s' campaign" % c_dict["name"])

            if buff_list != []:
                buff_string = utils.list_to_pretty_string(buff_sources)
                self.log_event("Applying %s bonuses to %s" % (buff_string, self.pretty_name()))
                apply_buff_list(buff_list)
        else:
            self.log_event("Settlement bonuses where not applied to %s due to user preference." % self.pretty_name())

        # Add our campaign's founder epithet if the survivor is a founder
        if self.is_founder():
            self.logger.debug("%s is a founder. Adding founder epithet!" % self.pretty_name())
            founder_epithet = self.get_campaign(dict).get("founder_epithet", "founder")
            self.add_game_asset("epithets", founder_epithet)

        # log and save
        self.logger.debug("%s created by %s (%s)" % (self, request.User, self.Settlement))
        self.save()

        return self._id


    def normalize(self):
        """ In which we force the survivor's mdb document to adhere to the biz
        logic of the game and our own data model. """

        self.perform_save = False

        self.bug_fixes()
        self.baseline()
        self.duck_type()

        #
        #   asset migrations (names to handles)
        #

        if self.survivor["meta"].get("abilities_and_impairments_version", None) is None:
            self.convert_abilities_and_impairments()
            self.perform_save = True

        if self.survivor["meta"].get("disorders_version", None) is None:
            self.convert_disorders()
            self.perform_save = True

        if self.survivor["meta"].get("epithets_version", None) is None:
            self.convert_epithets()
            self.perform_save = True

        if self.survivor["meta"].get("favorites_version", None) is None:
            self.convert_favorite()
            self.perform_save = True

        if self.survivor["meta"].get("fighting_arts_version", None) is None:
            self.convert_fighting_arts()
            self.perform_save = True

        if self.survivor["meta"].get("special_attributes_version", None) is None:
            self.convert_special_attributes()
            self.perform_save = True

        if self.survivor["meta"].get("weapon_proficiency_type_version", None) is None:
            self.convert_weapon_proficiency_type()
            self.perform_save = True

        #
        #   game asset normalization - TKTK fix this up
        #

        if 'ability_customizations' in self.survivor.keys():
            del self.survivor['ability_customizations']
            self.logger.debug("%s Removing deprecated attribute 'ability_customizations'." % self)
            self.perform_save = True

        # enforce the partner A&I
        if "partner_id" in self.survivor.keys():
            if "partner" not in self.survivor["abilities_and_impairments"]:
                self.logger.debug("Automatically adding 'Partner' A&I to %s." % self)
                self.survivor["abilities_and_impairments"].append("partner")
                self.perform_save = True

        # add the savior key if we're dealing with a savior
        if self.is_savior() and not "savior" in self.survivor.keys():
            self.survivor["savior"] = self.is_savior()
            self.perform_save

        # enforce minimum attributes for certain attribs
        self.min_attributes()

        if self.perform_save:
            self.logger.info("%s survivor modified during normalization! Saving changes..." % self)
            self.save()


    def serialize(self, return_type=None, include_meta=True):
        """ Renders the survivor as JSON. We don't serialize to anything else."""

        # tidy these up prior to serialization
        for k in ["abilities_and_impairments", "fighting_arts", "disorders"]:
            self.survivor[k] = sorted(self.survivor[k])


        # start the insanity
        output = {}
        if include_meta:
            output = self.get_serialize_meta()

        # build the sheet: don't forget to add cursed items to it
        output.update({"sheet": self.survivor})
        output["sheet"].update({"effective_sex": self.get_sex()})
        output["sheet"].update({"can_be_nominated_for_intimacy": self.can_be_nominated_for_intimacy()})
        output["sheet"].update({"can_gain_bleeding_tokens": self.can_gain_bleeding_tokens()})
        output["sheet"].update({"can_gain_survival": self.can_gain_survival()})
        output["sheet"].update({"cannot_spend_survival": self.cannot_spend_survival()})
        output["sheet"].update({"cannot_use_fighting_arts": self.cannot_use_fighting_arts()})
        output["sheet"].update({"skip_next_hunt": self.skip_next_hunt()})
        output["sheet"].update({"founder": self.is_founder()})
        output["sheet"].update({"savior": self.is_savior()})
        output['sheet'].update({'parents': self.get_parents(dict)})

        # survivors whose campaigns use dragon traits get a top-level element
        if self.get_campaign(dict).get("dragon_traits", False):
            output["dragon_traits"] = {}
            output["dragon_traits"].update({"trait_list": self.get_dragon_traits()})
            output["dragon_traits"].update({"active_cells": self.get_dragon_traits("active_cells")})
            output["dragon_traits"].update({"available_constellations": self.get_dragon_traits("available_constellations")})

        # now add the additional top-level items ("keep it flat!" -khoa)
        output.update({"notes": self.get_notes()})
        output.update({"survival_actions": self.get_survival_actions("JSON")})

        if return_type == dict:
            return output

        return json.dumps(output, default=json_util.default)


    #
    #   normalization/enforcement helper methods
    #

    def apply_survival_limit(self, save=False):
        """ Check the settlement to see if we're enforcing Survival Limit. Then
        enforce it, if indicated. Force values less than zero to zero. """

        # no negative numbers
        if self.survivor["survival"] < 0:
            self.survivor["survival"] = 0

        # see if we want to enforce the Survival Limit
        if self.Settlement.get_survival_limit(bool):
            if self.survivor["survival"] > self.Settlement.get_survival_limit():
                self.survivor["survival"] = self.Settlement.get_survival_limit()

        # save, if params require
        if save:
            self.save()




    #
    #   update/set methods
    #


    def add_custom_ai(self, ai_name=None, ai_desc=None, ai_type=None):
        """ Adds a custom A&I to the survivor. """

        raise Exception("NOT IMPLEMENTED!!")


    def add_cursed_item(self, handle=None):
        """ Adds a cursed item to a survivor. Does a bit of biz logic, based on
        the asset dict for the item.

        If the 'handle' kwarg is None, this method will look for a request
        param, e.g. as if this was a reqeuest_response() call.
        """

        # initialize
        if handle is None:
            self.check_request_params(['handle'])
            handle = self.params["handle"]
        ci_dict = self.CursedItems.get_asset(handle)

        # check for the handle (gracefully fail if it's a dupe)
        if ci_dict["handle"] in self.survivor["cursed_items"]:
            self.logger.error("%s already has cursed item '%s'" % (self, ci_dict["handle"]))
            return False

        # log to settlement event
        self.log_event("%s is cursed! %s added %s to survivor." % (self.pretty_name(), request.User.login, ci_dict["name"]), event_type="survivor_curse")

        # add related A&Is
        if ci_dict.get("abilities_and_impairments", None) is not None:
            for ai_handle in ci_dict["abilities_and_impairments"]:
                self.add_game_asset('abilities_and_impairments', ai_handle)

        self.add_game_asset("epithets", "cursed")

        # append it, save and exit
        self.survivor["cursed_items"].append(ci_dict["handle"])
        self.save()


    def rm_cursed_item(self, handle=None):
        """ Removes cursed items from the survivor, to include any A&Is that go
        along with that cursed item. Does NOT remove any A&Is that are caused by
        any remaining cursed items, i.e. so you can have multiple items with the
        King's Curse, etc. """

        # initialize
        if handle is None:
            self.check_request_params(['handle'])
            handle = self.params['handle']
        ci_dict = self.CursedItems.get_asset(handle)

        # check for the handle (gracefully fail if it's no thtere)
        if ci_dict["handle"] not in self.survivor["cursed_items"]:
            self.logger.error("%s does not have cursed item '%s'. Ignoring bogus request..." % (self, ci_dict["handle"]))
            return False

        # log to settlement event
        self.log_event("%s removed %s from %s" % (request.User.login, ci_dict["name"], self.pretty_name()))

        # remove any A&Is that are no longer required/present
        if ci_dict.get("abilities_and_impairments", None) is not None:

            # create a set of the curse A&Is that are sticking around
            remaining_curse_ai = set()

            for ci_handle in self.survivor["cursed_items"]:
                if ci_handle == ci_dict["handle"]:     # ignore the one we're processing currently
                    pass
                else:
                    remaining_ci_dict = self.CursedItems.get_asset(ci_handle)
                    if remaining_ci_dict.get("abilities_and_impairments", None) is not None:
                        remaining_curse_ai.update(remaining_ci_dict["abilities_and_impairments"])

            # now check the CI we're processing against the list we created
            for ai_handle in ci_dict["abilities_and_impairments"]:
                if ai_handle not in remaining_curse_ai:
                    self.rm_game_asset('abilities_and_impairments', ai_handle)
                else:
#                    self.logger.debug("%s is still in %s" % (ai_handle, remaining_curse_ai))
                    self.logger.info("%s Not removing '%s' A&I; survivor is still cursed." % (self, ai_handle))

        # rm the epithet if we have no curses
        if self.survivor['cursed_items'] == []:
            self.rm_game_asset("epithets", "cursed")

        # remove it, save and exit
        self.survivor["cursed_items"].remove(ci_dict["handle"])
        self.save()


    def add_favorite(self, user_email=None):
        """Adds the value of the incoming 'user_email' kwarg to the survivor's
        'favorite' attribute (which is a list of users who have favorited the
        survivor. """

        if user_email is None:
            self.check_request_params(['user_email'])
            user_email = self.params['user_email']

        if user_email in self.survivor['favorite']:
            self.logger.error("%s User '%s' is already in this survivor's favorite list. Ignoring bogus add request." % (self, user_email))
            return True
        else:
            self.survivor['favorite'].append(user_email)
            self.log_event('%s added %s to their favorite survivors.' % (user_email, self.pretty_name()))

        self.save()


    def rm_favorite(self, user_email=None):
        """Removes the value of the incoming 'user_email' kwarg from the
        survivor's 'favorite' attribute (which is a list of users who have
        favorited the survivor. """

        if user_email is None:
            self.check_request_params(['user_email'])
            user_email = self.params['user_email']

        if user_email not in self.survivor['favorite']:
            self.logger.error("%s User '%s' is not in this survivor's favorite list. Ignoring bogus remove request." % (self, user_email))
            return True
        else:
            self.survivor['favorite'].remove(user_email)
            self.log_event('%s removed %s from their favorite survivors.' % (user_email, self.pretty_name()))

        self.save()



    def add_game_asset(self, asset_class=None, asset_handle=None, apply_related=True, save=True):
        """ Port of the legacy method of the same name.

        Does not apply nearly as much business logic as the legacy webapp
        method, however, so don't expect a ton of user-friendliness out of this
        one.

        If the 'asset_class' value is None, then the method assumes that it is
        being called by a request_response() method and looks for request
        params.

        Important! All incoming asset handles are turned into asset dicts using
        their AssetCollection class's get_asset() method! Any handle that cannot
        be turned into a dict in this way will bomb out and raise an exception!

        Here is the order of operations on how an incoming handle is evaluated:

            1.) the "max" attribute of any incoming asset is respected. The
                asset WILL NOT be added if doing so would go above the asset's
                "max", as defined by its asset dict. The call will return False.
            2.) if an asset dict contains one of our survivor 'flag' values,
                this method will try to set it, if the flag's value evaluates to
                Boolean True.
            3.) any keys of the asset dictionary are also attributes of the
                self.survivor dict get a call to self.update_attribute, i.e. to
                add them to whatever the survivor's existing attribute happens
                to be.
            4.) if the asset dict has an 'epithet' key, the value of that key
                (which should always be an epithet handle) will be added to the
                survivor.
            5.) the survivor's permanent affinities are modified if the asset
                dict contains the 'affinities' key
            6.) similarly, if the asset dict has a 'related' key, any related
                asset handles are applied to the survivr.

        Once added to the survivor, the following 'post-processing' business
        logic is automatically handled by this method:

            1.) Weapon masteries get a log_event() call. They are also added
                to the settlement's Innovations (via add_innovation() call.)


        That's it! Have fun!
        """

        #   method preprocessing first

        asset_class, asset_dict = self.asset_operation_preprocess(asset_class, asset_handle)

        # 1.) MAX - check the asset's 'max' attribute:
        if asset_dict.get("max", None) is not None:
            if self.survivor[asset_class].count(asset_dict["handle"]) >= asset_dict["max"]:
                self.logger.warn("%s max for '%s' (%s) has already been reached! Ignoring..." % (self, asset_dict["handle"], asset_class))
                return False

        # 2.) STATUS - set status flags if they're in the dict
        for flag in self.flags:
            if asset_dict.get(flag, None) is True:
                self.set_status_flag(flag)

        # 3.) ATTRIBS - now check asset dict keys for survivor dict attribs
        for ak in asset_dict.keys():
            if ak in self.stats:
                self.update_attribute(ak, asset_dict[ak])
            if ak in self.abs_value_attribs:
                self.set_attribute(ak, asset_dict[ak])

        # RETIRED mostly this is for the 'Fear of the Dark' disorder, TBH
        if 'retire' in asset_dict.keys():
            self.set_retired(True)

        # levels!?
        if asset_dict.get('levels', None) is not None:
            self.survivor["fighting_arts_levels"][asset_dict["handle"]] = []

        # 4.) EPITHETS - check for 'epithet' key
        if asset_dict.get("epithet", None) is not None:
            self.add_game_asset("epithets", asset_dict["epithet"])

        # 5.) AFFINITIES - some assets add permanent affinities
        if asset_dict.get('affinities', None) is not None:
            self.update_affinities(asset_dict["affinities"])

        # 6.) RELATED - add any related 
        if apply_related and asset_dict.get("related", None) is not None:
            self.logger.info("Automatically applying %s related asset handles to %s" % (len(asset_dict["related"]), self))
            for related_handle in asset_dict["related"]:
                self.add_game_asset(asset_class, related_handle, apply_related=False)

        # finally, if we're still here, add it and log_event() it
        self.survivor[asset_class].append(asset_dict["handle"])
        self.survivor[asset_class].sort()
        self.log_event("%s added '%s' (%s) to %s" % (request.User.login, asset_dict["name"], asset_dict["type_pretty"], self.pretty_name()))


        #
        #   post-processing/special handling starts here
        #

        # special handling for certain game asset types
        if asset_dict.get("type", None) == "weapon_mastery":
            self.log_event("%s has become a %s master!" % (self.pretty_name(), asset_dict["weapon_name"]), event_type="survivor_mastery")
            if asset_dict.get("add_to_innovations", True):
                self.Settlement.add_innovation(asset_dict["handle"])


        # finally, save the survivor and return
        if save:
            self.save()


    def asset_operation_preprocess(self, asset_class=None, asset_handle=None):
        """ As its name suggests, the purpose of this method is to 'stage up' or
        prepare to do the add_game_asset() method (above). The idea is that you
        call this method at the beginning of add_game_asset() to sanity check it
        and do any other preprocessing tasks.

        Set 'asset_class' kwarg to the string of an asset collection and
        'asset_handle' to any handle within that asset collection and this
        func will return the value of 'asset_class' and an asset dict for the
        'asset_handle' value.

        This method will back off to the incoming request if 'asset_type' is
        None.
        """

        #
        #   1.) initialize the request. Try to use kwargs, but back off to
        #   request params if incoming kwargs are None
        #

        if asset_class is None:
            self.check_request_params(["type", "handle"])
            asset_class = self.params["type"]
            asset_handle = self.params["handle"]
        elif asset_class is not None and asset_handle is None:
            self.check_request_params(["handle"])
            asset_handle = self.params["handle"]


        #   2.) initialize/import the AssetModule and an AssetCollection object
        exec "AssetModule = %s" % asset_class
        A = AssetModule.Assets()


        #   3.) handle the _random pseudo/bogus/magic handle
        if asset_handle == "_random":
            self.logger.info("%s selecting random '%s' asset..." % (self, asset_class))
            available = copy(self.Settlement.get_available_assets(AssetModule)[asset_class])

            # filter out assets that the survivor already has
            for h in self.survivor[asset_class]:
                if available.get(h, None) is not None:
                    del available[h]

            # filter out 'secret' assets
            for k in available.keys():
                if A.get_asset(k).get('type', None) == 'secret_fighting_art':
                    del available[k]

            asset_handle = random.choice(available.keys())
            self.logger.info("%s selected '%s' asset handle at random." % (self, asset_handle))


        #   4.) try to get the asset; bomb out if we can't
        asset_dict = A.get_asset(asset_handle)
        if asset_dict is None:
            msg = "%s.Assets() class does not include handle '%s'!" % (asset_class, asset_handle)
            self.logger.exception(msg)
            raise utils.InvalidUsage(msg, status_code=400)


        # exit preprocessing with a valid class name and asset dictionary
        return asset_class, asset_dict


    def set_many_game_assets(self):
        """ Much like the set_many_attributes() route/method, this one WILL ONLY
        WORK WITH A REQUEST object present.

        Iterates over a list of assets to add and calls add_game_asset() once for
        every asset in the array. """

        # initialize and sanity check!
        self.check_request_params(['game_assets','action'])
        action = self.params['action']
        updates = self.params['game_assets']

        if type(updates) != list:
            raise utils.InvalidUsage("The add_many_game_assets() method requires the 'assets' param to be an array/list!")
        elif action not in ['add','rm']:
            raise utils.InvalidUsage("add_many_game_assets() 'action' param must be 'add' or 'rm'.")

        for u in updates:
            asset_class = u.get('type', None)
            asset_handle = u.get('handle', None)

            err = "set_many_game_assets() is unable to process hash: %s" % u
            usg = " Should be: {handle: 'string', type: 'string'}"
            err_msg = err + usg
            if asset_class is None:
                raise utils.InvalidUsage(err_msg)
            elif asset_handle is None:
                raise utils.InvalidUsage(err_msg)

            if action == 'add':
                self.add_game_asset(str(asset_class), str(asset_handle), save=False)
            elif action == 'rm':
                self.rm_game_asset(str(asset_class), str(asset_handle), save=False)

        self.save()


    def replace_game_assets(self):
        """ Much like set_many_game_assets(), this route facilitates The Watcher
        UI/UX and SHOULD ONLY BE USED WITH A REQUEST OBJECT since it pulls all
        params from there and cannot be called directly.

        This one takes a game asset category and overwrites it with an incoming
        list of handles.
        """

        self.check_request_params(['type','handles'])
        asset_class = self.params['type']
        asset_handles = self.params['handles']

        if asset_class not in self.game_asset_keys:
            raise utils.InvalidUsage("The replace_game_assets() method cannot modify asset type '%s'. Allowed types include: %s" % (asset_class, self.game_asset_keys))

        # start the riot
        handles_to_rm = set()
        handles_to_add = set()

        # process the current list: figure out what has to be removed
        for h in self.survivor[asset_class]:
            if h not in asset_handles:
                handles_to_rm.add(h)
        # process the incoming list: figure out what we need to add
        for h in asset_handles:
            if h not in self.survivor[asset_class]:
                handles_to_add.add(h)

        # bail if we've got no changes
        if handles_to_add == set() and handles_to_rm == set():
            self.logger.warn('Ignoring bogus replace_game_assets() operation: no changes to make...')
            return True

        for h in handles_to_rm:
            self.rm_game_asset(asset_class, h, save=False)
        for h in handles_to_add:
            self.add_game_asset(asset_class, h, save=False)

        self.save()



    def rm_game_asset(self, asset_class=None, asset_handle=None, rm_related=True, save=True):
        """ The inverse of the add_game_asset() method, this one most all the
        same stuff, except it does it in reverse order:

        One thing it does NOT do is check the asset dict's 'max' attribute, since
        that is irrelevant.
        """

        asset_class, asset_dict = self.asset_operation_preprocess(asset_class, asset_handle)

        # 1.) fail gracefully if this is a bogus request
        if asset_dict["handle"] not in self.survivor[asset_class]:
            self.logger.warn("%s Attempt to remove non-existent key '%s' from '%s'. Ignoring..." % (self, asset_dict["handle"], asset_class))
            return False

        # 2.) STATUS - unset status flags if they're in the dict
        for flag in self.flags:
            if asset_dict.get(flag, None) is True:
                self.set_status_flag(flag, unset=True)

        # 3.) ATTRIBS - now check asset dict keys for survivor dict attribs
        for ak in asset_dict.keys():
            if ak in self.stats:
                self.update_attribute(ak, -asset_dict[ak])
            if ak in self.abs_value_attribs:
                self.default_attribute(ak)

        # RETIRED mostly this is for the 'Fear of the Dark' disorder, TBH
        if 'retire' in asset_dict.keys():
            self.set_retired(False)

        # 4.) EPITHETS - check for 'epithet' key
        if asset_dict.get("epithet", None) is not None:
            self.rm_game_asset("epithets", asset_dict["epithet"])

        # 5.) AFFINITIES - some assets add permanent affinities: rm those
        if asset_dict.get('affinities', None) is not None:
            self.update_affinities(asset_dict["affinities"], operation="rm")

        # 6.) RELATED - rm any related 
        if rm_related and asset_dict.get("related", None) is not None:
            self.logger.info("Automatically removing %s related asset handles from %s" % (len(asset_dict["related"]), self))
            for related_handle in asset_dict["related"]:
                self.rm_game_asset(asset_class, related_handle, rm_related=False)

        # finally, if we're still here, add it and log_event() it
        self.survivor[asset_class].remove(asset_dict["handle"])
        self.log_event("%s removed '%s' (%s) from %s" % (request.User.login, asset_dict["name"], asset_dict["type_pretty"], self.pretty_name()))

        if save:
            self.save()


    def add_note(self):
        """ Adds a Survivor note to the mdb. Expects a request context. """

        self.check_request_params(['note'])
        note = self.params['note']

        note_dict = {
            "created_by": request.User._id,
            "created_on": datetime.now(),
            "survivor_id": self.survivor["_id"],
            "settlement_id": self.Settlement.settlement['_id'],
            "note": note,
        }

        note_oid = utils.mdb.survivor_notes.insert(note_dict)
        self.logger.debug("%s Added a note to %s" % (request.User, self))
        return Response(response={'note_oid': note_oid}, status=200)


    def rm_note(self):
        """ Removes a Survivor note from the MDB. Expects a request context. """

        self.check_request_params(['_id'])
        _id = ObjectId(self.params['_id'])

        utils.mdb.survivor_notes.remove({'_id': _id})
        self.logger.debug("%s Removed a note from %s" % (request.User, self))


    def update_affinities(self, aff_dict={}, operation="add"):
        """ Set the kwarg 'operation' to either 'add' or 'rm' in order to
        do that operation on self.survivor["affinities"], which looks like this:

            {'red': 0, 'blue': 0, 'green': 0}

        The 'aff_dict' should mirror the actual affinities dict, except without
        all of the color keys. For example:

            {'red': 1, 'blue': 2}
            {'green': -1}

        If 'aff_dict' is unspecified or an empty dict, this method will assume
        that it is being called by request_response() and check for 'aff_dict'
        in self.params.
        """

        # initialize
        if aff_dict == {}:
            self.check_request_params(['aff_dict'])
            aff_dict = self.params["aff_dict"]
            if 'operation' in self.params:
                operation = self.params["operation"]

        # sanity check
        if operation not in ["add","rm"]:
            msg = "The '%s' operation is not supported by the update_affinities() method!" % (operation)
            self.logger.exception(msg)
            raise utils.InvalidUsage(msg, status_code=400)

        # now do it and log_event() the results for each key
        for aff_key in aff_dict.keys():
            if operation == "add":
                self.survivor["affinities"][aff_key] += aff_dict[aff_key]
            elif operation == 'rm':
                self.survivor["affinities"][aff_key] -= aff_dict[aff_key]
            self.log_event("%s set %s '%s' affinity to %s" % (request.User.login, self.pretty_name(), aff_key, self.survivor["affinities"][aff_key]))

        self.save()


    def update_attribute(self, attribute=None, modifier=None):
        """ Adds 'modifier' value to self.survivor value for 'attribute'. """

        if attribute is None or modifier is None:
            self.check_request_params(['attribute','modifier'])
            attribute = self.params["attribute"]
            modifier = self.params["modifier"]

        # hand off to update_survival or damage_brain if that's the shot
        if attribute == 'survival':
            self.update_survival(modifier)
            return True
        elif attribute == 'brain_event_damage':
            self.damage_brain(modifier)
            return True

        # sanity check!
        if attribute not in self.survivor.keys():
            msg = "%s does not have '%s' attribute!" % (self, attribute)
            self.logger.exception(msg)
            raise utils.InvalidUsage(msg, status_code=400)
        elif type(self.survivor[attribute]) != int:
            msg = "%s '%s' attribute is not an int type! (It's a '%s')" % (self, attribute, type(self.survivor[attribute]))
            self.logger.exception(msg)
            raise utils.InvalidUsage(msg, status_code=400)
        else:
            pass

        # ok, do it, but enforce mins
        self.survivor[attribute] = self.survivor[attribute] + modifier
        if attribute in self.min_zero_attribs and self.survivor[attribute] < 0:
            self.survivor[attribute] = 0
        if attribute in self.min_one_attribs and self.survivor[attribute] < 1:
            self.survivor[attribute] = 1

        # force a max of 9 for courage and understanding
        if attribute in ['Courage','Understanding']:
            if self.survivor[attribute] > 9:
                self.survivor[attribute] = 9

        # log completion of the update 
        self.log_event("%s set %s attribute '%s' to %s" % (request.User.login, self.pretty_name(), attribute, self.survivor[attribute]))
        self.save()

        # biz logic for weapon proficiency - POST PROCESS
        if attribute == "Weapon Proficiency" and self.survivor[attribute] >= 3:
            if self.survivor["weapon_proficiency_type"] is not None:
                W = weapon_proficiency.Assets()
                w_handle = self.survivor["weapon_proficiency_type"]
                w_dict = W.get_asset(w_handle)
                if self.survivor[attribute] == 3:
                    self.log_event("%s is a %s specialist!" % (self.pretty_name(), w_dict["name"]))
                    self.add_game_asset("abilities_and_impairments", "%s_specialization" % w_handle)
                elif self.survivor[attribute] == 8:
                    self.add_game_asset("abilities_and_impairments", "mastery_%s" % w_handle)


    def update_bleeding_tokens(self, modifier=None):
        """ Adds 'modifier' to the survivor["bleeding_tokens"]. Cannot go below
        zero, e.g. by adding a negative number, or above
        survivor["max_bleeding_tokens"]. Fails gracefully in either case. """

        if modifier is None:
            self.check_request_params(['modifier'])
            modifier = int(self.params["modifier"])

        current_value = self.survivor["bleeding_tokens"]
        self.survivor['bleeding_tokens'] = current_value + modifier

        if self.survivor["bleeding_tokens"] > 0:
            self.survivor["bleeding_tokens"] = 0
        elif self.survivor["bleeding_tokens"] > self.survivor["max_bleeding_tokens"]:
            self.survivor["bleeding_tokens"] = self.survivor["max_bleding_tokens"]

        self.log_event('%s set %s bleeding tokens to %s.' % (request.User.login, self.survivor.pretty_name(), self.survivor["bleeding_tokens"]))
        self.save()


    def update_returning_survivor_years(self, add_year=None, save=True):
        """ Adds the current LY to the survivor's 'returning_survivor' attrib
        (i.e. list) by default. Set 'add_year' to any integer to add an arbitrary
        value. """

        if add_year is None:
            add_year = self.Settlement.get_current_ly()

        if not 'returning_survivor' in self.survivor.keys():
            self.survivor['returning_survivor'] = []

        self.survivor['returning_survivor'].append(add_year)

        self.survivor['returning_survivor'] = list(set(self.survivor['returning_survivor']))

        if save:
            self.save()


    def update_survival(self, modifier=None):
        """ Adds 'modifier' to survivor["survival"]. Respects settlement rules
        about whether to enforce the Survival Limit. Will not go below zero. """

        if modifier is None:
            self.check_request_params(["modifier"])
            modifier = int(self.params["modifier"])

        self.survivor["survival"] += modifier
        self.apply_survival_limit()
        self.logger.debug("%s set %s survival to %s" % (request.User, self, self.survivor["survival"]))
        self.save()



    #
    #   toggles and flags!
    #

    def toggle_boolean(self, attribute=None):
        """ This is a generic toggle that will toggle any attribute of the
        survivor that is Boolean. Note that this will only work on attributes
        that are part of the survivor data model (check the baseline() method)
        and will not work, for example, on status flags such as 'skip_next_hunt'
        and similar. """

        if attribute is None:
            self.check_request_params(["attribute"])
            attribute = self.params["attribute"]

        if attribute not in self.survivor.keys():
            msg = "The attribute '%s' is not part of the survivor data model!" % attribute
            self.logger.error(msg)
            raise utils.InvalidUsage(msg, status_code=400)
        elif type(self.survivor[attribute]) != bool:
            msg = "The attribute '%s' is not type 'bool'!" % attribute
            self.logger.error(msg)
            raise utils.InvalidUsage(msg, status_code=400)

        if self.survivor[attribute]:
            self.survivor[attribute] = False
        else:
            self.survivor[attribute] = True

        self.log_event("%s changed %s attribute '%s' to %s" % (request.User.login, self.pretty_name(), attribute, self.survivor[attribute]))
        self.save()

        pass


    def toggle_fighting_arts_level(self):
        """ Toggles a fighting arts level on or off, e.g. by adding it to or
        removing it from the array for a particular FA's handle.

        Assumes that this is an API request and does not process any args that
        do not come in the request object.
        """

        self.check_request_params(['handle', 'level'])
        fa_handle = self.params["handle"]
        fa_level = int(self.params["level"])

        FA = fighting_arts.Assets()
        fa_dict = FA.get_asset(fa_handle)

        if fa_handle not in self.survivor['fighting_arts_levels'].keys():
            self.survivor["fighting_arts_levels"][fa_handle] = []
            self.logger.warn("%s Adding fighting art handle '%s' to 'fighting_arts_levels' dict." % (self, fa_handle))

        if fa_level in self.survivor['fighting_arts_levels'][fa_handle]:
            toggle_operation = "off"
            self.survivor['fighting_arts_levels'][fa_handle].remove(fa_level)
        else:
            toggle_operation = "on"
            self.survivor['fighting_arts_levels'][fa_handle].append(fa_level)

        self.survivor['fighting_arts_levels'][fa_handle] = sorted(self.survivor['fighting_arts_levels'][fa_handle])

        self.logger.debug("%s toggled '%s' fighting art level %s %s for %s." % (request.User.login, fa_dict["name"], fa_level, toggle_operation, self.pretty_name()))

        self.save()


    def toggle_sotf_reroll(self):
        """ toggles the survivor's Survival of the Fittest once-in-a-lifetime
        reroll on or off. This is self.survivor["sotf_reroll"] and it's a bool
        and it's not part of the data model, so creating it is necessary some
        times. """

        if not "sotf_reroll" in self.survivor.keys():
            self.survivor["sotf_reroll"] = True
            self.log_event("%s toggled SotF reroll on for %s" % (request.User.login, self.pretty_name()))
        elif self.survivor["sotf_reroll"]:
            self.survivor["sotf_reroll"] = False
            self.log_event("%s toggled SotF reroll off for %s" % (request.User.login, self.pretty_name()))
        elif not self.survivor["sotf_reroll"]:
            self.survivor["sotf_reroll"] = True
            self.log_event("%s toggled SotF reroll on for %s" % (request.User.login, self.pretty_name()))
        else:
            self.logger.error("Unhandled logic in toggle_sotf_reroll() method!")
            raise Exception

        self.save()


    def toggle_status_flag(self, flag=None):
        """ Toggles a status flag on or off. Available status flags:

            - cannot_spend_survival
            - cannot_use_fighting_arts
            - skip_next_hunt
            - retired

        If 'flag' is None, this method assumes that it is being called by a the
        request_response() method and will check for incoming params.
        """

        if flag is None:
            self.check_request_params(['flag'])
            flag = self.params["flag"]

        if flag not in self.flags:
            msg = "Survivor status flag '%s' cannot be toggled!" % flag
            raise utils.InvalidUsage(msg, status_code=400)

        flag_pretty = flag.replace("_", " ").capitalize()

        flag_current_status = self.survivor.get(flag, None)
        if flag_current_status is None:
            self.survivor[flag] = True
            self.log_event("%s set '%s' on %s" % (request.User.login, flag_pretty, self.pretty_name()))
        elif flag_current_status is False:
            self.survivor[flag] = True
            self.log_event("%s set '%s' on %s" % (request.User.login, flag_pretty, self.pretty_name()))
        else:
            del self.survivor[flag]
            self.log_event("%s removed '%s' from %s" % (request.User.login, flag_pretty, self.pretty_name()))

        self.save()


    #
    #   special game controls
    #

    def controls_of_death(self):
        """ Manage all aspects of the survivor's death here. This is tied to a
        a number of settlement methods/values, so be cautious with this one. """

        self.check_request_params(["dead"])
        dead = self.params["dead"]

        if dead is False:
            for death_key in ["died_on","died_in","cause_of_death","dead"]:
                if death_key in self.survivor.keys():
                    del self.survivor[death_key]
                    self.logger.debug("%s Removed '%s' from %s" % (request.User, death_key, self))
            self.log_event("%s has resurrected %s!" % (request.User.login, self.pretty_name()))
        else:
            self.survivor["dead"] = True
            self.survivor["died_on"] = datetime.now()

            # this isn't very DRY, but we've got to strictly type here
            if 'died_in' in self.params:
                self.survivor['died_in'] = int(self.params["died_in"])
            else:
                self.survivor["died_in"] = self.Settlement.get_current_ly()

            if 'cause_of_death' in self.params:
                self.survivor['cause_of_death'] = str(self.params["cause_of_death"])
            else:
                self.survivor['cause_of_death'] = "Unspecified"

            self.log_event('%s has died! Cause of death: %s' % (self.pretty_name(), self.survivor["cause_of_death"]), event_type="survivor_death")
            self.Settlement.update_population(-1)

        self.save()


    def damage_brain(self, dmg=0):
        """ Inflicts brain event damage on the survivor."""

        remainder = self.survivor['Insanity'] - dmg

        log_damage = False
        if remainder < 0:
            if self.survivor.get('brain_damage_light', None) is None:
                self.survivor['brain_damage_light'] = 'checked' #transitional
                log_damage = True
            self.survivor['Insanity'] = 0
        elif remainder == 0:
            self.survivor['Insanity'] = 0
        elif remainder > 0:
            self.survivor['Insanity'] = remainder
        else:
            raise Exception('%s Impossible damage_brain() result!' % self)

        self.log_event("%s inflicted %s Brain Event Damage on %s. The survivor's Insanity is now %s" % (request.User.login, dmg, self.pretty_name(), self.survivor["Insanity"]), event_type="brain_event_damage")
        if log_damage:
            self.log_event("%s has suffered a Brain injury due to Brain Event Damage!" % (self.pretty_name()))
        self.save()


    def return_survivor(self, showdown_type=None):
        """ Returns the departing survivor. This is a minimized port of the legacy
        webapp's heal() method (which was super overkill in the first place).

        This method assumes a request context, so don't try if it you haven't got
        a request object initialized and in the global namespace. """


        #
        #   initialize/sanity check
        #

        if not 'departing' in self.survivor.keys():
            self.logger.warn('%s is not a Departing Survivor! Skipping bogus return() request...' % self)

        def finish():
            """ Private method for concluding the return. Enhances DRYness. """
            msg = "%s returned %s to %s" % (request.User.login, self.pretty_name(), self.Settlement.settlement['name'])
            self.log_event(msg, event_type="survivor_return")
            self.save()


        #
        #   Living and dead survivor return operations
        #

        # 1.) update meta data
        self.survivor['departing'] = False

        if showdown_type == 'normal':
            self.update_returning_survivor_years(save=False)

        # 2.) remove armor
        for loc in self.armor_locations:
            self.survivor[loc] = 0

        # 3.) remove tokens/gear modifiers
        self.reset_attribute_details(save=False)

        # 4.) heal injury boxes
        self.reset_damage(save=False)

        # 5.) finish if the survivor is dead
        if self.is_dead():
            finish()


        #
        #   Living survivors only from here!
        #

        # 6.) zero-out bleeding tokens
        self.set_bleeding_tokens(0, save=False)

        # 7.) increment Hunt XP
#        if self.is_savior():
#            self.update_attribute('hunt_xp', 4)
#        else:
#            self.update_attribute('hunt_xp', 1)

        # 8.) process disorders with 'on_return' attribs
        for d in self.survivor['disorders']:
            d_dict = self.Disorders.get_asset(d)
            if d_dict.get('on_return', None) is not None:
                for k,v in d_dict['on_return'].iteritems():
                    self.survivor[k] = v

        # OK, we out!
        finish()




    #
    #   set methods!
    #

    def set_affinity(self, color=None, value=None):
        """ Adds 'modifier' value to self.survivor value for 'attribute'. If the
        'attrib' kwarg is None, the function assumes that this is part of a call
        to request_response() and will get request params. """

        if color is None:
            self.check_request_params(['color','value'])
            color = self.params["color"]
            value = int(self.params["value"])

        # sanity check!
        if color not in self.survivor["affinities"].keys():
            msg = "%s does not have a '%s' affinity!" % (self, color)
            self.logger.exception(msg)
            raise utils.InvalidUsage(msg, status_code=400)

        self.survivor["affinities"][color] = value
        self.log_event("%s set %s %s affinity to %s" % (request.User.login, self.pretty_name(), color, value))
        self.save()


    def set_attribute(self, attrib=None, value=None, save=True):
        """ Adds 'modifier' value to self.survivor value for 'attribute'. If the
        'attrib' kwarg is None, the function assumes that this is part of a call
        to request_response() and will get request params. """

        if attrib is None:
            self.check_request_params(['attribute','value'])
            attrib = self.params["attribute"]
            value = int(self.params["value"])

        # sanity check!
        if attrib not in self.survivor.keys():
            msg = "%s does not have '%s' attribute!" % (self, attrib)
            self.logger.exception(msg)
            raise utils.InvalidUsage(msg, status_code=400)
        elif type(self.survivor[attrib]) != int:
            msg = "%s '%s' attribute is not an int type!" % (self, attrib)
            self.logger.exception(msg)
            raise utils.InvalidUsage(msg, status_code=400)

        self.survivor[attrib] = value
        self.log_event("%s set %s '%s' to %s" % (request.User.login, self.pretty_name(), attrib, value))

        if save:
            self.save()


    def set_many_attributes(self):
        """ This is an API-only route and therefore ONLY WORKS IF YOU HAVE
        request parameters!

        This basically reads a list of attributes to update and then updates
        them in the order they appear.
        """

        # initialize and sanity check!
        self.check_request_params(['attributes'])
        updates = self.params['attributes']

        if type(updates) != list:
            raise utils.InvalidUsage("The set_many_attributes() method requires 'attributes' param to be an array/list!")

        for u in updates:
            if type(u) != dict:
                raise utils.InvalidUsage("The set_many_attributes() method 'attributes' must be hashes/dicts!")
            attrib = u.get('attribute', None)
            value = u.get('value', None)

            err = "set_many_attributes() is unable to process hash: %s" % u
            usg = " Should be: {attribute: 'string', value: 'int'}"
            err_msg = err + usg
            if attrib is None:
                raise utils.InvalidUsage(err_msg)
            elif value is None:
                raise utils.InvalidUsage(err_msg)

            self.set_attribute(str(attrib), int(value), False)

        self.save()


    def set_attribute_detail(self, attrib=None, detail=None, value=False):
        """ Use to update the 'attribute_detail' dictionary for the survivor.
        If this is called without an 'attrib' value, it will assume that it is
        being called as part of a request_response() call and look for request
        parameters.

        The 'attrib' value should be 'Strength', 'Luck', etc. and the 'detail'
        should be one of the following:

            - 'tokens'
            - 'gear'

        The 'value' must be an int.

        """

        if attrib is None:
            self.check_request_params(["attribute","detail","value"])
            attrib = self.params["attribute"]
            detail = self.params["detail"]
            value =  int(self.params["value"])

        if attrib not in self.survivor["attribute_detail"].keys():
            msg = "Survivor attribute '%s' does not support details!" % (attrib)
            self.logger.error(msg)
            raise utils.InvalidUsage(msg, status_code=400)

        if detail not in ['tokens','gear']:
            msg = "Survivor 'attribute_detail' detail type '%s' is not supported!" % (detail)
            self.logger.error(msg)
            raise utils.InvalidUsage(msg, status_code=400)

        self.survivor["attribute_detail"][attrib][detail] = value
        self.log_event("%s set %s '%s' detail '%s' to %s" % (request.User.login, self.pretty_name(), attrib, detail, value))
        self.save()



    def set_bleeding_tokens(self, value=None, save=True):
        """ Sets self.survivor['bleeding_tokens'] to 'value', respecting the
        survivor's max and refusing to go below zero. """

        if value is None:
            self.check_request_params(['value'])
            value = int(self.params["value"])

        self.survivor['bleeding_tokens'] = value

        if self.survivor["bleeding_tokens"] < 0:
            self.survivor["bleeding_tokens"] = 0
        elif self.survivor["bleeding_tokens"] > self.survivor["max_bleeding_tokens"]:
            self.survivor["bleeding_tokens"] = self.survivor["max_bleding_tokens"]

        self.log_event('%s set %s bleeding tokens to %s.' % (request.User.login, self.pretty_name(), self.survivor["bleeding_tokens"]))

        if save:
            self.save()


    def set_constellation(self, constellation=None, unset=None):
        """ Sets or unsets the survivor's self.survivor["constellation"]. """

        current_constellation = self.survivor.get("constellation", False)

        # figure out if we're unsetting
        if unset is None:
            if "unset" in self.params:
                unset = True
            else:
                unset = False

        if unset and current_constellation:
            del self.survivor["constellation"]
            self.log_event("%s unset the constellation for %s" % (request.User.login, self.pretty_name()))
            self.rm_game_asset("epithets", "the_%s" % current_constellation.lower())
            return True
        elif unset and not current_constellation:
            self.logger.warn("%s Does not have a constellation! Ignoring unset request..." % (self))
            return False

        if constellation is None:
            self.check_request_params(['constellation'])
            constellation = self.params["constellation"]

        if current_constellation == constellation:
            self.logger.warn("%s Constellation is already %s. Ignoring request..." % (self, constellation))
            return False
        else:
            if current_constellation:
                self.rm_game_asset("epithets", "the_%s" % current_constellation.lower())
            self.survivor["constellation"] = constellation
            self.add_game_asset("epithets", "the_%s" % constellation.lower())
            self.log_event("%s set %s constellation to '%s'" % (request.User.login, self.pretty_name(), constellation))
            self.log_event("%s has become one of the People of the Stars!" % (self.pretty_name), event_type="potstars_constellation")
            self.save()



    def set_email(self, new_email=None):
        """ Validates an incoming email address and attempts to set it as the
        survivor's new email. It has to a.) be different, b.) look like an email
        address and c.) belong to a registered user before we'll set it."""

        if new_email is None:
            self.check_request_params(["email"])
            new_email = self.params["email"]

        # sanity checks
        if new_email == self.survivor["email"]:
            msg = "%s Survivor email unchanged! Ignoring request..." % self
            self.logger.warn(msg)
            return Response(response=msg, status=200)
        elif not '@' in new_email:
            msg = "'%s Survivor email '%s' does not look like an email address! Ignoring..." % (self, new_email)
            self.logger.warn(msg)
            return Response(response=msg, status=200)
        elif utils.mdb.users.find_one({'login': new_email}) is None:
            msg = "The email address '%s' is not associated with any known user." % new_email
            self.logger.error(msg)
            return Response(response=msg, status=422)

        # if we're still here, do it.
        old_email = self.survivor["email"]
        self.survivor["email"] = new_email

        self.log_event("%s changed the manager of %s to %s." % (request.User.login, old_email, self.survivor["email"]))
        self.save()
        return utils.http_200


    def set_name(self, new_name=None):
        """ Sets the survivor's name. Logs it. """

        if new_name is None:
            self.check_request_params(["name"])
            new_name = self.params["name"]

        if new_name == self.survivor["name"]:
            self.logger.warn("%s Survivor name unchanged! Ignoring set_name() call..." % self)
            return True

        if new_name in ["", u""]:
            new_name = "Anonymous"

        old_name = self.survivor["name"]
        self.survivor["name"] = new_name

        self.log_event("%s renamed %s to %s" % (request.User.login, old_name, new_name))
        self.save()


    def set_parent(self, role=None, oid=None):
        """ Sets the survivor's 'mother' or 'father' attribute. """

        if role is None or oid is None:
            self.check_request_params(['role', 'oid'])
            role = self.params['role']
            oid = self.params['oid']

        oid = ObjectId(oid)

        if role not in ['father','mother']:
            utils.invalidUsage("Parent 'role' value must be 'father' or 'mother'!")

        new_parent = utils.mdb.survivors.find_one({"_id": oid})
        if new_parent is None:
            utils.invalidUsage("Parent OID '%s' does not exist!" % oid)

        if oid == self.survivor.get(role, None):
            self.logger.warn("%s %s is already %s. Ignoring request..." % (self, role, new_parent["name"]))
            return True

        self.survivor[role] = ObjectId(oid)
        self.log_event("%s updated %s lineage: %s is now %s" % (request.User.login, self.pretty_name(), role, new_parent["name"]))
        self.save()


    def set_retired(self, retired=None):
        """ Set to true or false. Backs off to request params is 'retired' kwarg
        is None. Does a little user-friendliness/sanity-checking."""

        if retired == None:
            self.check_request_params(["retired"])
            retired=self.params["retired"]

        if type(retired) != bool:
            retired = bool(retired)

        if "retired" in self.survivor.keys() and self.survivor["retired"] == retired:
            self.logger.warn("%s Already has 'retired' set to '%s'. Ignoring bogus request..." % (self, retired))
            return True

        self.survivor["retired"] = retired
        if self.survivor["retired"]:
            self.log_event("%s has retired %s." % (request.User.login, self.pretty_name()))
            self.survivor['retired_in'] = self.get_current_ly()
        else:
            del self.survivor["retired"]
            try:
                del self.survivor['retired_in']
            except:
                pass
            self.log_event("%s has taken %s out of retirement." % (request.User.login, self.pretty_name()))
        self.save()


    def set_savior_status(self, color=None, unset=False):
        """ Makes the survivor a savior or removes all savior A&Is. """

        if "unset" in self.params:
            unset = True

        # handle 'unset' operations first
        if unset and self.is_savior():
            s_dict = self.Saviors.get_asset_by_color(self.is_savior())

            for ai_handle in s_dict["abilities_and_impairments"]:
                self.rm_game_asset("abilities_and_impairments", ai_handle, rm_related=False)

            del self.survivor["savior"]
            self.save()
            self.log_event("%s unset savior status for %s" % (request.User.login, self.pretty_name()))
            return True
        elif unset and not self.is_savior():
            self.logger.error("%s Not a savior: cannot unset savior status!" % (self))
            return False
        else:
            pass    # moving along...

        # now handle 'set' operations
        if color is None:
            self.check_request_params(["color"])
            color = self.params["color"]

        # bail if this is redundant/double-click
        if color == self.is_savior():
            self.logger.error("%s is already a %s savior. Ignoring..." % (self, color))
            return False

        # remove previous if we're switching
        if self.is_savior() and color != self.is_savior():
            self.logger.warn("%s changing savior color from %s to %s..." % (self, self.is_savior(), color))
            s_dict = self.Saviors.get_asset_by_color(self.is_savior())
            for ai_handle in s_dict["abilities_and_impairments"]:
                self.rm_game_asset("abilities_and_impairments", ai_handle, rm_related=False)

        # finally, if we're still here, set it
        self.survivor["savior"] = color
        s_dict = self.Saviors.get_asset_by_color(color)
        for ai_handle in s_dict["abilities_and_impairments"]:
            self.add_game_asset("abilities_and_impairments", ai_handle, apply_related=False)

        self.log_event("A savior is born! %s applied %s savior status to %s" % (request.User.login, color, self.pretty_name()), event_type="savior_birth")

        self.save()


    def set_sex(self, sex=None):
        """ Sets self.survivor["sex"] attribute. Can only be 'M' or 'F'.

        Note that this should not be used to set the survivor's 'effective sex',
        i.e. in the event of a Gender Swap curse, etc.

        'Effective sex' is determined automatically (see the get_effective_sex()
        method in this module for more info.

        If the 'sex' kwarg is None, this method assumes that it is being called
        by request_response() and will look for 'sex' in self.params.
        """

        if sex is None:
            self.check_request_params(['sex'])
            sex = self.params["sex"]

        if sex not in ["M","F"]:
            msg = "Survivor sex must be 'M' or 'F'. Survivor sex cannot be '%s'." % sex
            self.logger.exception(msg)
            raise utils.InvalidUsage(msg, status_code=400)

        self.survivor["sex"] = sex
        self.log_event("%s set %s sex to '%s'." % (request.User.login, self.pretty_name(), sex))
        self.save()


    def set_special_attribute(self):
        """ Sets an arbitrary attribute handle on the survivor. Saves. Expects a
        request context. """

        # initialize and validate
        self.check_request_params(['handle','value'])
        handle = self.params['handle']
        value = self.params['value']

        sa_dict = self.SpecialAttributes.get_asset(handle)

        self.survivor[handle] = value

        if value and 'epithet' in sa_dict:
            self.add_game_asset('epithets', sa_dict['epithet'])
        elif not value and 'epithet' in sa_dict:
            self.rm_game_asset('epithets', sa_dict['epithet'])

        if value:
            msg = "%s added '%s' to %s." % (request.User.login, sa_dict['name'], self.pretty_name())
        else:
            msg = "%s removed '%s' from %s." % (request.User.login, sa_dict['name'], self.pretty_name())
        self.log_event(msg)

        self.save()



    def set_status_flag(self, flag=None, unset=False):
        """ Sets or unsets a status flag, regardless of previous status of that
        flag. Supported flags include:

            - cannot_spend_survival
            - cannot_use_fighting_arts
            - skip_next_hunt

        If 'flag' is None, this method assumes that it is being called by a the
        request_response() method and will check for incoming params.

        Set the 'unset' kwarg to True to force unset the value.
        """

        if flag is None:
            self.check_request_params(['flag'])
            flag = self.params["flag"]

        if 'unset' in self.params:
            unset = True

        if flag not in self.flags:
            msg = "Survivor status flag '%s' cannot be set!" % flag
            raise utils.InvalidUsage(msg, status_code=400)

        flag_pretty = flag.replace("_", " ").capitalize()

        if unset and self.survivor.get(flag, None) is not None:
            del self.survivor[flag]
            self.log_event("%s removed '%s' from %s" % (request.User.login, flag_pretty, self.pretty_name()))
        else:
            self.survivor[flag] = True
            self.log_event("%s set '%s' on %s" % (request.User.login, flag_pretty, self.pretty_name()))

        self.save()


    def set_survival(self, value=0):
        """ Sets survivor["survival"] to 'value'. Respects settlement rules
        about whether to enforce the Survival Limit. Will not go below zero. """

        self.check_request_params(["value"])
        value = int(self.params["value"])
        self.survivor["survival"] = value
        self.apply_survival_limit()
        self.logger.debug("%s set %s survival to %s" % (request.User, self, self.survivor["survival"]))
        self.save()


    def set_weapon_proficiency_type(self, handle=None, unset=False):
        """ Sets the self.survivor["weapon_proficiency_type"] string to a
        handle. """

        if handle is None:
            self.check_request_params(["handle"])
            handle = self.params["handle"]

        W = weapon_proficiency.Assets()
        h_dict = W.get_asset(handle)

        self.survivor["weapon_proficiency_type"] = handle
        self.log_event("%s set weapon proficiency type to '%s' for %s" % (request.User.login, h_dict["handle"], self.pretty_name()))
        self.save()


    #
    #   defaults and resets
    #

    def default_attribute(self, attrib=None):
        """ Defaults a Survivor attribute to its base value, as determined the
        assets.survivors.py module. This absolutely will clobber the current
        value, leaving no trace of it. YHBW. """

        if attrib is None:
            self.check_request_params(['attribute'])
            attrib = self.params["attribute"]

        # sanity check!
        SA = Assets()
        defaults = SA.get_defaults()
        if attrib not in defaults.keys():
            msg = "%s does not have a default value!" % (attrib)
            self.logger.exception(msg)
            raise utils.InvalidUsage(msg, status_code=400)
        if attrib not in self.survivor.keys():
            msg = "%s does not have '%s' attribute!" % (self, attrib)
            self.logger.exception(msg)
            raise utils.InvalidUsage(msg, status_code=400)

        self.survivor[attrib] = defaults[attrib]
        self.log_event("%s defaulted %s '%s' to %s" % (request.User.login, self.pretty_name(), attrib, defaults[attrib]))
        self.save()


    def reset_attribute_details(self, save=True):
        """ Zero-out all attribute_detail values and will overwrite with
        extreme prejudice. """

        self.survivor["attribute_detail"] = {
            "Strength": {"tokens": 0, "gear": 0},
            "Evasion":  {"tokens": 0, "gear": 0},
            "Movement": {"tokens": 0, "gear": 0},
            "Luck":     {"tokens": 0, "gear": 0},
            "Speed":    {"tokens": 0, "gear": 0},
            "Accuracy": {"tokens": 0, "gear": 0},
        }

        if save:
            self.save()


    def reset_damage(self, save=True):
        """ Remove all damage attribs/bools from the survivor. """

        for d in self.damage_locations:
            if d in self.survivor.keys():
                del self.survivor[d]

        if save:
            self.save()

    #
    #   get methods
    #

    def pretty_name(self):
        """ Returns the survivor's name in a prettified way, e.g. 'Timothy [M]'.
        Meant to be an alternative for the __repr__() way of doing it, which
        includes the asset's OID. Use this method when calling log_event().

        NB! This returns the survivor's effective sex (i.e. calls self.get_sex()
        instead of using the base attribute), which is different from the way
        the __repr__() method does it!
        """

        return "%s [%s]" % (self.survivor["name"], self.get_sex())


    def get_available_endeavors(self, return_type=None):
        """ Works like a miniature version of the Settlement method of the same
        name. Returns a list of handles instead of a big-ass JSON thing, however.

        Set 'return_type' to dict to get a dictionary instead of a list of handles.
        """

        E = endeavors.Assets()


        def check_availability(e_handle):
            """ Private method that checks whether an endeavor is currently
            available to the survivor. """
            e_dict = E.get_asset(e_handle)
            available = True
            if e_dict.get('requires_returning_survivor',False):
                if self.get_current_ly() not in self.survivor.get('returning_survivor', []):
                    available = False
            return available


        e_handles = set()
        for a_dict in self.list_assets('abilities_and_impairments'):
            for e_handle in a_dict.get('endeavors', []):
                if check_availability(e_handle):
                    e_handles.add(e_handle)
        e_handles = sorted(list(e_handles))

        # return dictionary.
        if return_type == dict:
            output = {}
            for e_handle in e_handles:
                output[e] = E.get_asset(e_handle)
            return output

        return e_handles


    def get_dragon_traits(self, return_type=dict):
        """ Returns survivor Dragon Traits. """

        traits = []

        # check Understanding for 9+
        if int(self.survivor["Understanding"]) >= 9:
            traits.append("9 Understanding (max)")

        # check self.survivor["expansion_attribs"] for "Reincarnated surname","Scar","Noble surname"
        if "expansion_attribs" in self.survivor.keys():
            for attrib in ["potstars_reincarnated_surname", "potstars_scar", "potstars_noble_surname"]:
                if attrib in self.survivor.keys():
                    traits.append(attrib)

        # check the actual survivor name too, you know, for the real role players
        split_name = self.survivor["name"].split(" ")
        for surname in ["Noble","Reincarnated"]:
            if surname in split_name and "%s surname" % surname not in traits:
                traits.append(surname + " surname")

        # check abilities_and_impairments for Oracle's Eye, Iridescent Hide, Pristine,
        AI = abilities_and_impairments.Assets()
        for a in [AI.get_asset('oracles_eye'), AI.get_asset('pristine'), AI.get_asset('iridescent_hide')]:
            if a["handle"] in self.survivor["abilities_and_impairments"]:
                traits.append("%s ability" % a["name"])

        # check for any weapon mastery
        AI.filter("type", ["weapon_mastery"], reverse=True)
        for wm in AI.get_dicts():
            if wm["handle"] in self.survivor["abilities_and_impairments"]:
                traits.append("Weapon Mastery")

        # check disorders for "Destined"
        if "destined" in self.survivor["disorders"]:
            traits.append("Destined disorder")

        # check fighting arts for "Fated Blow", "Frozen Star", "Unbreakable", "Champion's Rite"
#        for fa in ["Fated Blow","Frozen Star","Unbreakable","Champion's Rite"]:
        FA = fighting_arts.Assets()
        for fa in ['champions_rite', 'fated_blow', 'frozen_star', 'unbreakable']:
            if fa in self.survivor["fighting_arts"]:
                fa_dict = FA.get_asset(fa)
                fa_name = copy(fa_dict["name"])
                if fa_name == "Frozen Star":
                    fa_name = "Frozen Star secret"
                traits.append("%s fighting art" % fa_name)

        # check for 3+ strength
        if int(self.survivor["Strength"]) >= 3:
            traits.append("3+ Strength attribute")

        # check for 1+ Accuracy
        if int(self.survivor["Accuracy"]) >= 1:
            traits.append("1+ Accuracy attribute")

        # check Courage for 9+
        if int(self.survivor["Courage"]) >= 9:
            traits.append("9 Courage (max)")

        if return_type == "active_cells":
            cells = set()
            C = the_constellations.Assets()
            c_map = C.get_asset('lookups')["map"]
            for t in traits:
                if t in c_map.keys():
                    cells.add(c_map[t])
            return list(cells)
        elif return_type == 'available_constellations':
            constellations = set()
            active_cells = self.get_dragon_traits('active_cells')
            C = the_constellations.Assets()
            c_formulae = C.get_asset('lookups')["formulae"]
            for k,v in c_formulae.iteritems():      # k = "Witch", v = set(["A1","A2","A3","A4"])
                if v.issubset(active_cells):
                    constellations.add(k)
            return list(constellations)

        # if no return_type, just return the trait list

        return traits

    def get_epithets(self, return_type=None):
        """ Returns survivor epithet (handles) as a list, unless the
        'return_type' kwarg is set to 'pretty', which gets you a nice
        string. """

        e = self.survivor["epithets"]

        if return_type == "pretty":
            E = epithets.Assets()
            output = ""
            for e_handle in e:
                e_asset = E.get_asset(e_handle)
                output += e_asset["name"]
            return output

        return e



    def get_lineage(self):
        """ DO NOT call this method during normal serialization: it is a PIG and
        running it on more than one survivor at once is a really, really bad
        idea.

        Also, it returns a Response object. So yeah.

        This method creates a dictionary of survivor lineage information. """

        # initialize
        output = {
            'intimacy_partners': set(),
            'siblings': { 'full': [], 'half': [] },
        }

        # PROCESS parents first w the survivor version of get_parents() b/c that's easy
        survivor_parents = self.get_parents(dict)
        output['parents'] = survivor_parents

        # now PROCESS the settlement's get_parents() output for partners, children and sibs
        children = set()
        siblings = {'full': set(), 'half': set()}

        couplings = self.Settlement.get_parents()
        for coupling in couplings:
            if self.survivor['_id'] == coupling['father']:
                output['intimacy_partners'].add(coupling['mother'])
                children = children.union(coupling['children'])
            elif self.survivor['_id'] == coupling['mother']:
                output['intimacy_partners'].add(coupling['father'])
                children = children.union(coupling['children'])

            # full-blood sibs
            if self.survivor['_id'] in coupling['children']:
                siblings['full'] = coupling['children'] # you can only have one set of full-blood sibs, right?

            # half-blood sibs
            if survivor_parents != {'father': None, 'mother': None}:
                if survivor_parents['father']['_id'] == coupling['father'] and survivor_parents['mother']['_id'] != coupling['mother']:
                    siblings['half'] = siblings['half'].union(coupling['children'])
                if survivor_parents['father']['_id'] != coupling['father'] and survivor_parents['mother']['_id'] == coupling['mother']:
                    siblings['half'] = siblings['half'].union(coupling['children'])


        #
        #   Post-process
        #

        # process sibling oids and make lists of dictionaries
        for k in siblings: # i.e. 'half' or 'full'
            for s in siblings[k]:
                if s == self.survivor["_id"]:
                    pass # can't be your own sib
                else:
                    output['siblings'][k].append(utils.mdb.survivors.find_one({'_id': s}))

        # retrieve children from mdb; process oid lists into dictionaries
        output['children'] = {}
        for p in output['intimacy_partners']:
            output['children'][str(p)] = []
        for c in children:
            c_dict = utils.mdb.survivors.find_one({'_id': c})
            if c_dict['father'] == self.survivor['_id']:
                output['children'][str(c_dict['mother'])].append(c_dict)
            elif c_dict['mother'] == self.survivor['_id']:
                output['children'][str(c_dict['father'])].append(c_dict)

        # sort the children on their born in LY
        for p_id in output['children']:
            output['children'][p_id] = sorted(output['children'][p_id], key=lambda k: k['born_in_ly'])

        # get fuck buddy survivor data from mdb
        output['intimacy_partners'] = [utils.mdb.survivors.find_one({'_id': s}) for s in output['intimacy_partners']]


        return Response(
            response=json.dumps(output, default=json_util.default),
            status=200,
            mimetype="application/json"
        )


    def get_notes(self):
        """ Gets the survivor's notes as a list of dictionaries. """
        notes = utils.mdb.survivor_notes.find({
            "survivor_id": self.survivor["_id"],
            "created_on": {"$gte": self.survivor["created_on"]}
        }, sort=[("created_on",1)])
        return list(notes)


    def get_parents(self, return_type=None):
        """ Returns survivor OIDs for survivor parents by default. Set
        'return_type' to 'dict' (w/o the quotes) to get survivor dictionaries
        back. """

        parents = []
        for p in ["father","mother"]:
            if p in self.survivor.keys():
                parents.append(self.survivor[p])

        if return_type == dict:
            output = {'mother': None, 'father': None}
            for p_oid in parents:
                p = utils.mdb.survivors.find_one({'_id': p_oid})
                if p is not None:
                    if p["sex"] == 'M':
                        output['father'] = p
                    elif p['sex'] == 'F':
                        output['mother'] = p
                    else:
                        raise
            return output

        return parents


    def get_sex(self):
        """ Returns a string value of 'M' or 'F' representing the survivor's
        current effective sex. The basic math here is that we start from the
        survivor's sheet on their sex and then apply any curses, etc. to get
        our answer. """

        sex = self.survivor["sex"]

        def invert_sex(s):
            if s == "M":
                return "F"
            elif s == "F":
                return "M"

        for ai_dict in self.list_assets("abilities_and_impairments"):
            if ai_dict.get("reverse_sex", False):
                sex = invert_sex(sex)

        return sex


    def get_survival_actions(self, return_type=dict):
        """ Returns the SA's available to the survivor based on current
        impairments, etc. Use 'return_type' = 'JSON' to get a list of dicts
        back, rather than a single dict.

        Important! There's a ton of business logic here, given that there's a
        lot of interplay among game assets, so read this carefully and all the
        way through before making changes!
        """

        # helper called later
        def update_available(sa_key_list, available=False, title_tip=None):
            """ Inline helper func to update the list of available_actions while
            iterating over survivor attributes. """

            for sa_key in sa_key_list:
                if not available:
                    if sa_key in available_actions.keys():
                        available_actions[sa_key]["available"] = False
                        available_actions[sa_key]["title_tip"] = title_tip
                elif available:
                    sa = SA.get_asset(sa_key)
                    sa["available"] = True
                    sa["title_tip"] = title_tip
                    available_actions[sa_key] = sa


        #
        #   action starts here. initialize and set defaults first:
        #

        AI = abilities_and_impairments.Assets()
        SA = survival_actions.Assets()

        available_actions = self.Settlement.get_survival_actions()


        # check A&Is and FAs/SFAs   # disorders coming soon! TKTK
        attrib_keys = ['abilities_and_impairments', 'fighting_arts']

        for ak in attrib_keys:
            for a_dict in self.list_assets(ak):             # iterate assets
                if "survival_actions" in a_dict.keys():     # check for SA key

                    # handle 'enable' keys; special logic re: can't use FAs
                    if ak == 'fighting_arts' and self.cannot_use_fighting_arts():
                        pass
                    else:
                        update_available(
                            a_dict["survival_actions"].get("enable", []),
                            available = True,
                            title_tip = "Available due to '%s'" % a_dict["name"],
                        )

                    # handle 'disable' keys
                    update_available(
                        a_dict["survival_actions"].get("disable", []),
                        available = False,
                        title_tip = "Impairment '%s' prevents %s from using this ability." % (a_dict["name"], self.survivor["name"])
                    )


        # support JSON return
        if return_type == 'JSON':
            output = []
            for k, v in available_actions.iteritems():
                output.append(v)
            return sorted(output, key=lambda k: k['sort_order'])

        # dict return
        return available_actions



    #
    #   evaluation / biz logic methods
    #

    def can_be_nominated_for_intimacy(self):
        """ Returns a bool representing whether the survivor can do the
        mommmy-daddy dance. """


        for ai_dict in self.list_assets("abilities_and_impairments"):
            if ai_dict.get("cannot_be_nominated_for_intimacy", False):
                return False

        if self.is_dead():
            return False

        return True


    def can_gain_survival(self):
        """ Returns a bool representing whether or not the survivor can GAIN
        survival. This is not whether they can SPEND survival. """

        for ai_dict in self.list_assets("abilities_and_impairments"):
            if ai_dict.get("cannot_gain_survival", False):
                return False

        return True


    def can_gain_bleeding_tokens(self):
        """ Returns a bool describing whether the survivor can gain bleeding
        tokens. """

        if self.survivor.get('cannot_gain_bleeding_tokens', None) is None:
            return True
        return False


    def cannot_spend_survival(self):
        """ Returns a bool representing whether or not the survivor can SPEND
        survival. This is not whether they can GAIN survival. """

        if self.survivor.get("cannot_spend_survival", None) is True:
            return True

        for ai_dict in self.list_assets("abilities_and_impairments"):
            if ai_dict.get("cannot_spend_survival", False):
                return True

        return False


    def cannot_use_fighting_arts(self):
        """Returns a bool representing whether or not the survivor can use
        Fighting Arts. """

        if self.survivor.get("cannot_use_fighting_arts", None) is True:
            return True

        for ai_dict in self.list_assets("abilities_and_impairments"):
            if ai_dict.get("cannot_use_fighting_arts", False):
                return True

        return False


    def is_dead(self):
        """Returns a bool of whether the survivor is dead."""

        if "dead" in self.survivor.keys():
            return True

        return False


    def is_departing(self):
        """ Returns a bool of whether the survivor is departing. """

        return self.survivor.get('departing', False)


    def is_founder(self):
        """Returns a bool of whether the survivor is a founding survivor. """

        if self.survivor["born_in_ly"] == 0:
            return True

        return False


    def is_savior(self):
        """ Returns False if the survivor is NOT a savior; returns their color
        if they are (which should evaluate to Boolean true wherever we evaluate
        it, right?). """

        # automatically return false if the campaign doesn't have saviors
        if self.get_campaign(dict).get("saviors", None) is None:
            return False

        # automatically return the survivor's 'savior' attrib if the survivor
        # is a savior
        if self.survivor.get("savior", False):
            return self.survivor["savior"]

        # now do the legacy check
        for s_dict in self.Saviors.get_dicts():
            for s_ai in s_dict["abilities_and_impairments"]:
                if s_ai in self.survivor["abilities_and_impairments"]:
                    return s_dict["color"]

        return False


    def skip_next_hunt(self):
        """Returns a bool representing whether or not the survivor has to sit
        the next one out. """

        if self.survivor.get("skip_next_hunt", None) is True:
            return True

        return False






    #
    #   conversion and normalization methods
    #

    def baseline(self):
        """ Baselines the MDB doc to bring it into compliance with our general
        data model for survivors.

        We update the actual data in the MDB, rather than simply having a base-
        line model (e.g. in a config file somewhere) and then initializing new
        assets such that they overwrite/fill-in the blanks.

        This might seem like an odd design decision, but the data is designed to
        be portable, so we inflict/enforce a lot of the model on the 'database'.
        """

        if not "meta" in self.survivor.keys():
            self.logger.warn("Creating 'meta' key for %s" % self)
            self.survivor["meta"] = {}
            self.perform_save = True

        if not "attribute_detail" in self.survivor.keys():
            self.reset_attribute_details(save=False)
            self.perform_save = True

        if not 'affinities' in self.survivor.keys():
            self.survivor["affinities"] = {"red":0,"blue":0,"green":0}
            self.perform_save = True

        if not 'bleeding_tokens' in self.survivor.keys():
            self.survivor["bleeding_tokens"] = 0
            self.logger.info("Adding baseline 'bleeding_tokens' (int) attrib to %s" % self)
            self.perform_save = True

        if not 'max_bleeding_tokens' in self.survivor.keys():
            self.survivor["max_bleeding_tokens"] = 5
            self.logger.info("Adding baseline 'max_bleeding_tokens' (int) attrib to %s" % self)
            self.perform_save = True

        if not 'cursed_items' in self.survivor.keys():
            self.survivor["cursed_items"] = []
            self.perform_save = True

        if not 'public' in self.survivor.keys():
            self.survivor["public"] = False
            self.perform_save = True
        elif self.survivor["public"] == "checked":
            self.survivor["public"] = True
            self.perform_save = True

        if not 'fighting_arts_levels' in self.survivor.keys():
            self.survivor['fighting_arts_levels'] = {}
            self.perform_save = True

        if 'in_hunting_party' in self.survivor.keys():
            if self.survivor['in_hunting_party'] == True:
                self.survivor['departing'] = True
            else:
                self.survivor['departing'] = False
            del self.survivor['in_hunting_party']
            self.logger.info("Removed deprecated attribute 'in_hunting_party' from %s" % self)
            self.perform_save = True

        if not 'favorite' in self.survivor.keys():
            self.survivor["favorite"] = []
            self.perform_save = True


    def bug_fixes(self, force_save=False):
        """ This should be called during normalize() BEFORE you call baseline().

        Compare with the way this works on the Settlement object. Make sure all
        bugs are dated and have a ticket number, so we can remove them after a
        year has passed.
        """

        # 2017-10-25 The "king's_step" bug
        if "king's_step" in self.survivor['fighting_arts']:
            self.logger.debug("%s King's Step bad asset handle detected! Fixing..." % (self))
            self.survivor['fighting_arts'].remove("king's_step")
            self.survivor['fighting_arts'].append('kings_step')
            self.perform_save = True

        # 2017-10-28 The "weak spot" bug (other bad A&Is)
        for bad_handle in ['Weak Spot', 'Intracranial hemmorhage','Weak spot: arms', "Weak spot is body."]:
            if bad_handle in self.survivor['abilities_and_impairments']:
                self.logger.debug("%s Bad asset handle '%s' detected! Fixing..." % (self, bad_handle))
                self.survivor['abilities_and_impairments'].remove(bad_handle)
                self.perform_save = True

        # 2017-10-22 'acid_palms' asset handle Issue #341
        # https://github.com/toconnell/kdm-manager/issues/341

        if 'acid_palms' in self.survivor['abilities_and_impairments']:
            self.logger.warn("[BUG] Detected 'acid_palms' in survivor A&I list!")
            self.survivor['abilities_and_impairments'].remove('acid_palms')
            if 'gorm' in self.Settlement.get_expansions():
                self.survivor['abilities_and_impairments'].append('acid_palms_gorm')
                self.logger.info("%s Replaced 'acid_palms' with 'acid_palms_gorm'" % self)
            elif 'dragon_king' in self.Settlement.get_expansions():
                self.survivor['abilities_and_impairments'].append('acid_palms_dk')
                self.logger.info("%s Replaced 'acid_palms' with 'acid_palms_dk'" % self)
            else:
                self.logger.error("Unable to replace 'acid_palms' A&I with a real handle!")
            self.perform_save = True


        # now, if we're forcing a save (e.g. because the settlement is calling
        # method or something, do it
        if force_save and hasattr(self, 'perform_save') and self.perform_save:
            self.save()



    def duck_type(self):
        """ Duck-types certain survivor sheet attributes, e.g. to make sure they
        didn't experience a type change due to bad form input, etc. """

        # enforce ints first
        int_types = [
            "Insanity",
            "Accuracy",
            "Evasion",
            "Luck",
            "Movement",
            "Speed",
            "Strength",
            "Arms",
            "Body",
            "Head",
            "Legs",
            "Waist",
            "Understanding",
            "Courage",
            "survival",
            "hunt_xp",
            "bleeding_tokens",
            "max_bleeding_tokens",
        ]

        for attrib in int_types:
            if type(self.survivor[attrib]) != int:
                self.logger.warn("%s Duck-typed '%s' attrib to int." % (self, attrib))
                self.survivor[attrib] = int(self.survivor[attrib])
                self.perform_save = True

        # now translate checkbox ui stuff to bools
        for checked_attrib in ['dead','sotf_reroll','retired']:
            if checked_attrib in self.survivor.keys() and self.survivor[checked_attrib] == 'checked':
                self.survivor[checked_attrib] = True
                self.logger.warn("%s Duck-typed '%s' attrib from 'checked' to True" % (self, checked_attrib))
                self.perform_save = True

        if type(self.survivor["name"]) not in [unicode, str]:
            self.survivor["name"] = str(self.survivor["name"])
            self.perform_save = True


    def min_attributes(self):
        """ Applies assorted game rules to the survivor. """

        for attrib in self.min_zero_attribs:
            if self.survivor[attrib] < 0:
                self.survivor[attrib] = 0
                self.logger.warn("%s Survivor '%s' attrib normalized to minimum value of zero." % (self, attrib))
                self.perform_save = True

        for attrib in self.min_one_attribs:
            if self.survivor[attrib] < 1:
                self.survivor[attrib] = 0
                self.logger.warn("%s Survivor '%s' attrib normalized to minimum value of one." % (self, attrib))
                self.perform_save = True


    def convert_abilities_and_impairments(self):
        """ Swaps out A&I names for handles. """

        new_ai = []

        for ai_dict in self.list_assets("abilities_and_impairments", log_failures=True):
            new_ai.append(ai_dict["handle"])
            self.logger.info("%s Migrated A&I '%s' to '%s'" % (self, ai_dict["name"], ai_dict["handle"]))

        self.survivor["abilities_and_impairments"] = new_ai
        self.survivor["meta"]["abilities_and_impairments_version"] = 1.0
        self.logger.info("Converted A&Is from names (legacy) to handles for %s" % (self))


    def convert_disorders(self):
        """ Swaps out disorder names for handles. """

        new_d = []

        for d_dict in self.list_assets("disorders", log_failures=True):
            new_d.append(d_dict["handle"])
            self.logger.info("%s Migrated Disorder '%s' to '%s'" % (self, d_dict["name"], d_dict["handle"]))

        self.survivor["disorders"] = new_d
        self.survivor["meta"]["disorders_version"] = 1.0
        self.logger.info("Converted Disorders from names (legacy) to handles for %s" % (self))


    def convert_epithets(self):
        """ Tries to convert epithets to handles. Drops anything it cannot. """

        E = epithets

        new_epithets = []

        for e_dict in self.list_assets("epithets"):
            new_epithets.append(e_dict["handle"])
            self.logger.info("%s Converted '%s' epithet name to handle '%s'" % (self, e_dict["name"], e_dict["handle"]))

        self.survivor["epithets"] = new_epithets
        self.survivor["meta"]["epithets_version"] = 1.0
        self.logger.info("Converted epithets from names (legacy) to handles for %s" % (self))


    def convert_favorite(self):
        """ Turns the 'favorite' attribute from a string to a list of email
        addresses. """

        if self.survivor.get('favorite', None) is None:
            self.survivor['favorite'] = []
        else:
            self.survivor['favorite'] = []
            self.add_favorite(self.survivor["email"])

        self.survivor["meta"]["favorites_version"] = 1.0
        self.logger.info("Converted 'favorite' attrib from str (legacy) to list for %s" % (self))


    def convert_fighting_arts(self):
        """ Tries to convert Fighting Art names to to handles. Drops anything
        that it cannot convert. """

        FA = fighting_arts

        new_fa_list = []

        for fa_dict in self.list_assets("fighting_arts"):
            if fa_dict is None:
                pass
            else:
                new_fa_list.append(fa_dict["handle"])
                self.logger.info("%s Converted '%s' Fighting Art name to handle '%s'" % (self, fa_dict["name"], fa_dict["handle"]))

        self.survivor["fighting_arts"] = new_fa_list
        self.survivor["meta"]["fighting_arts_version"] = 1.0
        self.logger.info("Converted Fighting Arts from names (legacy) to handles for %s" % (self))


    def convert_weapon_proficiency_type(self):
        """ Swaps out names for handles. """

        # first normalize an empty string to None type
        if self.survivor["weapon_proficiency_type"] == "":
            self.survivor["weapon_proficiency_type"] = None

        if self.survivor["weapon_proficiency_type"] != None:
            w_name = self.survivor["weapon_proficiency_type"]
            W = weapon_proficiency.Assets()
            w_dict = W.get_asset_from_name(w_name)
            if w_dict is None:
                self.logger.error("%s Weapon proficiency type '%s' could not be migrated!" % (self, w_name))
            else:
                self.survivor["weapon_proficiency_type"] = w_dict["handle"]
                self.logger.info("%s Migrated weapon proficiency type '%s' to '%s'" % (self, w_name, w_dict["handle"]))

        self.survivor["meta"]["weapon_proficiency_type_version"] = 1.0
        self.logger.info("Converted weapon proficiency type name (legacy) to handle for %s" % (self))


    def convert_special_attributes(self):
        """ This one's...a hot mess on account of this feature having never
        been properly implemented in the legacy app.

        Basically, there's a list of known special attribute names, and we're
        going to manually crosswalk them to modern handles.
        """

        crosswalk = [
            ('Purified', 'potsun_purified'),
            ('Sun Eater', 'potsun_sun_eater'),
            ('Child of the Sun', 'potsun_child_of_the_sun'),
            ('Scar', 'potstars_scar'),
            ('Reincarnated surname', 'potstars_noble_surname'),
            ('Noble surname', 'potstars_reincarnated_surname'),
        ]

        if 'expansion_attribs' in self.survivor.keys():
            for i in crosswalk:
                name, handle = i
                if name in self.survivor['expansion_attribs'].keys():
                    self.survivor[handle] = True
                    self.logger.debug(name)
            del self.survivor['expansion_attribs']
        else:
            pass

        self.survivor["meta"]["special_attributes_version"] = 1.0
        self.logger.info("Converted survivor special attributes for %s" % (self))

    #
    #   NO METHODS BELOW THIS POINT other than request_response()
    #

    def request_response(self, action=None):
        """ Initializes params from the request and then response to the
        'action' kwarg appropriately. This is the ancestor of the legacy app
        assets.Survivor.modify() method. """

        self.get_request_params()


        # get methods first
        if action == "get":
            return self.return_json()
        elif action == "get_lineage":
            return self.get_lineage()
        elif action == "get_survival_actions":
            sa = self.get_survival_actions("JSON")
            return json.dumps(sa, default=json_util.default)


        # controllers with biz logic - i.e. fancy-pants methods
        elif action == "controls_of_death":
            self.controls_of_death()
        elif action == "update_bleeding_tokens":
            self.update_bleeding_tokens()
        elif action == "set_bleeding_tokens":
            self.set_bleeding_tokens()

        # add/rm assets
        elif action == "add_favorite":
            self.add_favorite()
        elif action == "rm_favorite":
            self.rm_favorite()
        elif action == "add_game_asset":
            self.add_game_asset()
        elif action == "rm_game_asset":
            self.rm_game_asset()
        elif action == "set_many_game_assets":  # serial add/rm game asset calls
            self.set_many_game_assets()
        elif action == "replace_game_assets":
            self.replace_game_assets()


        elif action == "toggle_fighting_arts_level":
            self.toggle_fighting_arts_level()

        # Cursed item methods
        elif action == "add_cursed_item":
            self.add_cursed_item()
        elif action == "rm_cursed_item":
            self.rm_cursed_item()

        # savior stuff
        elif action == "set_savior_status":
            self.set_savior_status()

        # misc sheet operations
        elif action == "set_name":
            self.set_name()
        elif action == "set_email":
            return self.set_email()     # because we're doing server-side validation
        elif action == "set_retired":
            self.set_retired()
        elif action == "set_sex":
            self.set_sex()
        elif action == "set_constellation":
            self.set_constellation()
        elif action == "set_weapon_proficiency_type":
            self.set_weapon_proficiency_type()
        elif action == 'set_special_attribute':
            self.set_special_attribute()

        # sheet attribute operations
        elif action == "set_attribute":
            self.set_attribute()
        elif action == "set_many_attributes":   # serial set_attribute()
            self.set_many_attributes()
        elif action == "set_attribute_detail":  # tokens/gear
            self.set_attribute_detail()
        elif action == "update_attribute":
            self.update_attribute()

        # notes
        elif action == 'add_note':
            self.add_note()
        elif action == 'rm_note':
            self.rm_note()


        # affinities
        elif action == "update_affinities":
            self.update_affinities()
        elif action == "set_affinity":
            self.set_affinity()

        # status flags!
        elif action == 'set_status_flag':
            self.set_status_flag()
        elif action == 'toggle_status_flag':
            self.toggle_status_flag()
        elif action == 'toggle_boolean':
            self.toggle_boolean()

        # survival
        elif action == "update_survival":
            self.update_survival()
        elif action == "set_survival":
            self.set_survival()


        # manager-only / non-game methods
        elif action == "toggle_sotf_reroll":
            self.toggle_sotf_reroll()
        elif action == 'set_parent':
            self.set_parent()


        else:
            # unknown/unsupported action response
            self.logger.warn("Unsupported survivor action '%s' received!" % action)
            return utils.http_400



        # finish successfully
        if self.params.get('serialize_on_response', False):
            return Response(response=self.serialize(), status=200)
        else:
            return utils.http_200





# ~fin

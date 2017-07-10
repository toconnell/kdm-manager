#!/usr/bin/python2.7

from bson import json_util
from datetime import datetime
from flask import request
import json

import Models
import utils

from assets import survivor_sheet_options, survivors
from models import abilities_and_impairments, cursed_items, epithets, saviors, survival_actions


class Assets(Models.AssetCollection):
    """ These are pre-made survivors, e.g. from the BCS. """

    def __init__(self, *args, **kwargs):
        self.assets = survivors.beta_challenge_scenarios
        self.type = "survivor"
        Models.AssetCollection.__init__(self,  *args, **kwargs)

    def get_specials(self):
        """ This returns the 'specials' macro dicts, which are basically simple
        'scripts' for operating on a settlement at creation time. """

        return survivors.specials



class Survivor(Models.UserAsset):
    """ This is the base class for all expansions. Private methods exist for
    enabling and disabling expansions (within a campaign/settlement). """


    def __repr__(self):
        return "%s [%s] (%s)" % (self.survivor["name"], self.survivor["sex"], self.survivor["_id"])


    def __init__(self, *args, **kwargs):
        self.collection="survivors"
        self.object_version = 0.48

        # data model meta data
        self.stats =            ['Movement','Accuracy','Strength','Evasion','Luck','Speed']
        self.flags =            ['skip_next_hunt','cannot_use_fighting_arts','cannot_spend_survival']
        self.min_zero_attribs =  ["hunt_xp","Courage","Understanding"]
        self.min_one_attribs =   ["Movement"]

        Models.UserAsset.__init__(self,  *args, **kwargs)

        # this makes the baby jesus cry
        import settlements
        self.Settlement = settlements.Settlement(_id=self.survivor["settlement"], normalize_on_init=False)

        if self.normalize_on_init:
            self.normalize()


    def new(self):
        """ Creates a new survivor. """

        #
        #   TO-DO
        #
        #   

        # Add our campaign's founder epithet if the survivor is a founder
        if self.is_founder():
            self.logger.debug("%s is a founder. Adding founder epithet!" % self)
            founder_epithet = self.get_campaign(dict).get("founder_epithet", "founder")
            self.add_game_asset("epithets", founder_epithet)

        self.save()


    def normalize(self):
        """ In which we force the survivor's mdb document to adhere to the biz
        logic of the game and our own data model. """

        self.perform_save = False

        self.baseline()
        self.duck_type()

        #
        #   asset migrations (names to handles)
        #

        if self.survivor["meta"].get("abilities_and_impairments_version", None) is None:
            self.convert_abilities_and_impairments()
            self.perform_save = True

        if self.survivor["meta"].get("epithets", None) is None:
            self.convert_epithets()
            self.perform_save = True

        #
        #   game asset normalization - TKTK fix this up
        #

        # enforce the partner A&I
        if "partner_id" in self.survivor.keys():
            if "Partner" not in self.survivor["abilities_and_impairments"]:
                self.logger.debug("Automatically adding 'Partner' A&I to %s." % self)
                self.survivor["abilities_and_impairments"].append("Partner")
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


    def serialize(self):
        """ Renders the survivor as JSON. We don't serialize to anything else."""

        # tidy these up prior to serialization
        for k in ["abilities_and_impairments", "fighting_arts", "disorders"]:
            self.survivor[k] = sorted(self.survivor[k])


        # start the insanity
        output = self.get_serialize_meta()

        # build the sheet: don't forget to add cursed items to it
        output.update({"sheet": self.survivor})
        output["sheet"].update({"effective_sex": self.get_sex()})
        output["sheet"].update({"can_be_nominated_for_intimacy": self.can_be_nominated_for_intimacy()})
        output["sheet"].update({"can_gain_survival": self.can_gain_survival()})
        output["sheet"].update({"cannot_spend_survival": self.cannot_spend_survival()})
        output["sheet"].update({"cannot_use_fighting_arts": self.cannot_use_fighting_arts()})
        output["sheet"].update({"skip_next_hunt": self.skip_next_hunt()})
        output["sheet"].update({"founder": self.is_founder()})
        output["sheet"].update({"savior": self.is_savior()})

        # now add the additional top-level items ("keep it flat!" -khoa)
        output.update({"notes": self.get_notes()})
        output.update({"survival_actions": self.get_survival_actions("JSON")})

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
        asset_class, ci_dict = self.get_asset('cursed_items', handle)

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
        asset_class, ci_dict = self.get_asset('cursed_items', handle)

        # log to settlement event
        self.log_event("%s removed %s from %s" % (request.User.login, ci_dict["name"], self.pretty_name()))

        # remove any A&Is that are no longer required/present
        if ci_dict.get("abilities_and_impairments", None) is not None:

            # create a set of the curse A&Is that are sticking around
            CI = cursed_items.Assets()
            remaining_curse_ai = set()

            for ci_handle in self.survivor["cursed_items"]:
                if ci_handle == handle:     # ignore the one we're processing currently
                    pass
                else:
                    remaining_ci_dict = CI.get_asset(ci_handle)
                    if remaining_ci_dict.get("abilities_and_impairments", None) is not None:
                        remaining_curse_ai.update(remaining_ci_dict["abilities_and_impairments"])

            # now check the CI we're processing against the list we created
            for ai_handle in ci_dict["abilities_and_impairments"]:
                if ai_handle not in remaining_curse_ai:
                    self.rm_game_asset('abilities_and_impairments', ai_handle)
                else:
                    self.logger.info("%s Not removing '%s' A&I; survivor is still cursed." % (self, ai_handle))

        # remove it, save and exit
        self.survivor["cursed_items"].remove(ci_dict["handle"])
        self.save()


    def add_game_asset(self, asset_class=None, asset_handle=None, apply_related=True):
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

        asset_class, asset_dict = self.get_asset(asset_class, asset_handle)

        #
        #   at this point, we have an asset dict and we're ready to plow
        #

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
        self.log_event("%s added '%s' (%s) to %s" % (request.User.login, asset_dict["name"], asset_dict["type_pretty"], self.pretty_name()))


        #
        #   post-processing/special handling starts here
        #

        # special handling for certain game asset types
        if asset_dict.get("type", None) == "weapon_mastery":
            self.log_event("%s has become a %s master!" % (self.pretty_name(), asset_dict["weapon"]), event_type="survivor_mastery")
            if asset_dict.get("add_to_innovations", True):
                self.Settlement.add_innovation(asset_dict["handle"])


        # finally, save the survivor and return
        self.save()


    def rm_game_asset(self, asset_class=None, asset_handle=None, rm_related=True):
        """ The inverse of the add_game_asset() method, this one most all the
        same stuff, except it does it in reverse order:

        One thing it does NOT do is check the asset dict's 'max' attribute, since
        that is irrelevant.
        """

        asset_class, asset_dict = self.get_asset(asset_class, asset_handle)

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

        self.save()


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

        # log and save
        self.log_event("%s set %s attribute '%s' to %s" % (request.User.login, self.pretty_name(), attribute, self.survivor[attribute]))
        self.save()


    def update_survival(self, modifier=0):
        """ Adds 'modifier' to survivor["survival"]. Respects settlement rules
        about whether to enforce the Survival Limit. Will not go below zero. """

        self.check_request_params(["modifier"])
        modifier = int(self.params["modifier"])
        self.survivor["survival"] += modifier
        self.apply_survival_limit()
        self.logger.debug("%s set %s survival to %s" % (request.User, self, self.survivor["survival"]))
        self.save()



    #
    #   toggles and flags!
    #

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
    #   controls of death! THE CHEESE STANDS ALONE
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

            self.log_event('%s has died! Cause of death: %s' % (self.pretty_name(), self.survivor["cause_of_death"]))
            self.Settlement.update_population(-1)

        self.save()




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


    def set_attribute(self, attrib=None, value=None):
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


    def set_savior_status(self, color=None, unset=False):
        """ Makes the survivor a savior or removes all savior A&Is. """

        # initialize!
        S = saviors.Assets()
        S.filter("version", [self.get_campaign(dict)["saviors"]], reverse=True)

        if "unset" in self.params:
            unset = True

        # handle 'unset' operations first
        if unset and self.is_savior():
            s_dict = S.get_asset_by_color(self.is_savior())

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
            s_dict = S.get_asset_by_color(self.is_savior())
            for ai_handle in s_dict["abilities_and_impairments"]:
                self.rm_game_asset("abilities_and_impairments", ai_handle, rm_related=False)

        # finally, if we're still here, set it
        self.survivor["savior"] = color
        s_dict = S.get_asset_by_color(color)
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


    def get_notes(self):
        """ Gets the survivor's notes as a list of dictionaries. """
        notes = utils.mdb.survivor_notes.find({
            "survivor_id": self.survivor["_id"],
            "created_on": {"$gte": self.survivor["created_on"]}
        }, sort=[("created_on",-1)])
        return list(notes)


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
        S = saviors.Assets()
        S.filter('version', [self.get_campaign(dict)["saviors"]], reverse=True)
        for s_dict in S.get_dicts():
            for s_ai in s_dict["abilities_and_impairments"]:
                if s_ai in self.survivor["abilities_and_impairments"]:
                    return s_ai["color"]

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
            self.survivor["attribute_detail"] = {
                "Strength": {"tokens": 0, "gear": 0},
                "Evasion":  {"tokens": 0, "gear": 0},
                "Movement": {"tokens": 0, "gear": 0},
                "Luck":     {"tokens": 0, "gear": 0},
                "Speed":    {"tokens": 0, "gear": 0},
                "Accuracy": {"tokens": 0, "gear": 0},
            }
            self.perform_save = True

        if not 'affinities' in self.survivor.keys():
            self.survivor["affinities"] = {"red":0,"blue":0,"green":0}
            self.perform_save = True

        if not 'cursed_items' in self.survivor.keys():
            self.survivor["cursed_items"] = []
            self.perform_save = True


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
        ]

        for attrib in int_types:
            if type(self.survivor[attrib]) != int:
                self.logger.warn("%s Duck-typed '%s' attrib to int." % (self, attrib))
                self.survivor[attrib] = int(self.survivor[attrib])
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

        AI = abilities_and_impairments

        new_ai = []

        for ai_dict in self.list_assets("abilities_and_impairments", log_failures=True):
            new_ai.append(ai_dict["handle"])
            self.logger.info("%s Migrated A&I '%s' to '%s'" % (self, ai_dict["name"], ai_dict["handle"]))

        self.survivor["abilities_and_impairments"] = new_ai
        self.survivor["meta"]["abilities_and_impairments_version"] = 1.0
        self.logger.info("Converted A&Is from names (legacy) to handles for %s" % (self))


    def convert_epithets(self):
        """ Tries to convert epithets to handles. Drops anything it cannot. """

        E = epithets

        new_epithets = []

        for e_dict in self.list_assets("epithets", log_failures=True):
            new_epithets.append(e_dict["handle"])
            self.logger.info("%s Converted '%s' epithet name to handle '%s'" % (self, e_dict["name"], e_dict["handle"]))

        self.survivor["epithets"] = new_epithets
        self.survivor["meta"]["epithets"] = 1.0
        self.logger.info("Converted epithets from names (legacy) to handles for %s" % (self))



    #
    #   NO METHODS BELOW THIS POINT other than request_response()
    #

    def request_response(self, action=None):
        """ Initializes params from the request and then response to the
        'action' kwarg appropriately. This is the ancestor of the legacy app
        assets.Survivor.modify() method. """

        self.get_request_params()

        if action == "get":
            return self.return_json()
        elif action == "get_survival_actions":
            sa = self.get_survival_actions("JSON")
            return json.dumps(sa, default=json_util.default)

        # controllers with biz logic
        elif action == "controls_of_death":
            self.controls_of_death()

        # add/rm assets
        elif action == "add_game_asset":
            self.add_game_asset()
        elif action == "rm_game_asset":
            self.rm_game_asset()

        # add cursed_item
        elif action == "add_cursed_item":
            self.add_cursed_item()
        elif action == "rm_cursed_item":
            self.rm_cursed_item()

        # savior stuff
        elif action == "set_savior_status":
            self.set_savior_status()

        # sheet attribute operations
        elif action == "set_sex":
            self.set_sex()
        elif action == "update_attribute":
            self.update_attribute()
        elif action == "set_attribute":
            self.set_attribute()
        elif action == "set_attribute_detail":  # tokens/gear
            self.set_attribute_detail()

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

        # survival
        elif action == "update_survival":
            self.update_survival()
        elif action == "set_survival":
            self.set_survival()

        elif action == "toggle_sotf_reroll":
            self.toggle_sotf_reroll()

        else:
            # unknown/unsupported action response
            self.logger.warn("Unsupported survivor action '%s' received!" % action)
            return utils.http_400


        # finish successfully
        return utils.http_200





# ~fin

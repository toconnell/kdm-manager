#!/usr/bin/python2.7

from bson import json_util
from datetime import datetime
from flask import request
import json

import Models
import utils

from assets import survivor_sheet_options, survivors
from models import abilities_and_impairments, epithets, survival_actions


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
        self.object_version = 0.32
        self.stats = ['Movement','Accuracy','Strength','Evasion','Luck','Speed']
        self.flags = ['skip_next_hunt','cannot_use_fighting_arts','cannot_spend_survival']

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
            founder_epithet = self.Settlement.get_campaign(dict).get("founder_epithet", "founder")
            self.add_game_asset("epithets", founder_epithet)

        self.save()

    def normalize(self):
        """ In which we force the survivor's mdb document to adhere to the biz
        logic of the game and our own data model. """

        self.perform_save = False

        self.baseline()


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

        output["sheet"].update({"cursed_items": self.get_cursed_items()})

        # now add the additional top-level items ("keep it flat!" -khoa)
        output.update({"notes": self.get_notes()})
        output.update({"survival_actions": self.get_survival_actions("JSON")})

        return json.dumps(output, default=json_util.default)


    #
    #   normalization and data model normalization/enforcement methods
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

    @utils.error_log
    def add_custom_ai(self, ai_name=None, ai_desc=None, ai_type=None):
        """ Adds a custom A&I to the survivor. """

        raise Exception("NOT IMPLEMENTED!!")


    @utils.error_log
    def add_game_asset(self, asset_class=None, handle=None, quantity=1):
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

        The following business logic is automatically implemented by this
        method:

            1.) Weapon masteries get a log_event() call. They are also added
                to the settlement's Innovations (via add_innovation() call.)

        Finally, here are the rules that apply to adding assets to survivors:

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

        That's it! Have fun!
        """

        # check the request
        if asset_class is None:
            self.check_request_params(["type", "handle"])
            asset_class = self.params["type"]
            handle = self.params["handle"]
            if "quantity" in self.params:
                quantity = self.params["quantity"]

        # try to get the asset; bomb out if we can't
        exec "A = %s.Assets()" % asset_class
        asset_dict = A.get_asset(handle)
        if asset_dict is None:
            msg = "%s.Assets() class does not include handle '%s'!" % (asset_class, handle)
            self.logger.exception(msg)
            raise utils.InvalidUsage(msg, status_code=400)

        #
        #   at this point, we have an asset dict and we're ready to plow
        #

        # special handling for certain game asset types
        if asset_dict.get("type", None) == "weapon_mastery":
            self.log_event("%s has become a %s master!" % (self.pretty_name(), asset_dict["weapon"]), event_type="survivor_mastery")
            if asset_dict.get("add_to_innovations", True):
                self.Settlement.add_innovation(asset_dict["handle"])


        # check the asset's 'max' attribute:
        if asset_dict.get("max", None) is not None:
            if self.survivor[asset_class].count(asset_dict["handle"]) >= asset_dict["max"]:
                self.logger.warn("%s max for '%s' (%s) has already been reached! Ignoring..." % (self, asset_dict["handle"], asset_class))
                return False

        # set status flags if they're in the dict
        for flag in self.flags:
            if asset_dict.get(flag, None) is True:
                self.set_status_flag(flag)

        # now check asset dict keys for survivor dict attribs
        for ak in asset_dict.keys():
            if ak in self.stats:
                self.update_attribute(ak, asset_dict[ak])

        #
        #   NEXT to port:
        #
        #   - affinities
        #   - related abilities

        # check for 'epithet' key
        if asset_dict.get("epithet", None) is not None:
            self.add_game_asset("epithets", asset_dict["epithet"])

        # finally, if we're still here, add it and save!
        self.survivor[asset_class].append(asset_dict["handle"])
        self.log_event("%s added '%s' to %s" % (request.User.login, asset_dict["name"], self.pretty_name()))
        self.save()


    @utils.error_log
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
            msg = "%s '%s' attribute is not an int type!" % (self, attribute)
            self.logger.exception(msg)
            raise utils.InvalidUsage(msg, status_code=400)
        else:
            pass

        # ok, do it!
        self.survivor[attribute] = self.survivor[attribute] + modifier

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


    def get_cursed_items(self):
        """ Returns a list of cursed item handles on the survivor. """
        if not "cursed_items" in self.survivor.keys():
            return []
        else:
            return self.survivor["cursed_items"]


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
        "Returns a bool of whether the survivor is dead."

        if "dead" in self.survivor.keys():
            return True

        return False


    def skip_next_hunt(self):
        """Returns a bool representing whether or not the survivor has to sit
        the next one out. """

        if self.survivor.get("skip_next_hunt", None) is True:
            return True

        return False



    #
    #   UPDATE and POST Methods
    #

    def update_from_dict(self, d):
        """ Updates the survivor's MDB record from a dictionary. Saves it. Be
        REAL careful with this one.

        TKTKTK DEPRECATE THIS SOON! 2017-07-06
        """

        for k in d:
            self.survivor[k] = d[k]
        utils.mdb.survivors.save(self.survivor)





    #
    #   conversion and normalization methods
    #

    def baseline(self):
        """ Baselines the MDB doc to bring it into compliance with our general
        data model for survivors. """

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

        # add assets
        elif action == "add_game_asset":
            self.add_game_asset()

        # sheet attribute operations
        elif action == "update_attribute":
            self.update_attribute()
        elif action == "set_attribute":
            self.set_attribute()
        elif action == "set_attribute_detail":  # tokens/gear
            self.set_attribute_detail()

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

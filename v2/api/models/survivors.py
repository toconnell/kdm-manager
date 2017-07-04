#!/usr/bin/python2.7

from bson import json_util
from datetime import datetime
from flask import request
import json

import Models
import utils

from assets import survivor_sheet_options, survivors
from models import abilities_and_impairments, survival_actions

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
        self.object_version = 0.20
        Models.UserAsset.__init__(self,  *args, **kwargs)
        self.normalize()

        # this makes the baby jesus cry
        import settlements
        self.Settlement = settlements.Settlement(_id=self.survivor["settlement"], normalize_on_init=False)


    def normalize(self):
        """ In which we force the survivor's mdb document to adhere to the biz
        logic of the game and our own data model. """

        perform_save = False

        # enforce the partner A&I
        if "partner_id" in self.survivor.keys():
            if "Partner" not in self.survivor["abilities_and_impairments"]:
                perform_save = True
                self.logger.debug("Automatically adding 'Partner' A&I to %s." % self)
                self.survivor["abilities_and_impairments"].append("Partner")


        if perform_save:
            self.logger.debug("Normalized %s" % self)
            self.save()


    def serialize(self):
        """ Renders the survivor as JSON. We don't serialize to anything else."""

        self.survivor["effective_sex"] = self.get_sex()
        self.survivor["can_be_nominated_for_intimacy"] = self.can_be_nominated_for_intimacy()
        self.survivor["can_gain_survival"] = self.can_gain_survival()
        self.survivor["can_spend_survival"] = self.can_spend_survival()

        output = self.get_serialize_meta()
        output.update({"sheet": self.survivor})
        output["sheet"].update({"cursed_items": self.get_cursed_items()})

        # now add the additional top-level items ("keep it flat!" -khoa)

        output.update({"bonuses": self.Settlement.get_bonuses("json")})
        output.update({"notes": self.get_notes()})
        output.update({"survival_actions": self.get_survival_actions()})

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

    def update_attribute(self, attribute=None, modifier=None, verbose=False):
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

        self.survivor[attribute] = self.survivor[attribute] + modifier
        if verbose:
            self.logger.debug("%s Set %s attribute '%s' to %s" % (request.User.login, self, attribute, self.survivor[attribute]))
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



    def update_survival(self, modifier=0):
        """ Adds 'modifier' to survivor["survival"]. Respects settlement rules
        about whether to enforce the Survival Limit. Will not go below zero. """

        self.check_request_params(["modifier"])
        modifier = int(self.params["modifier"])
        self.survivor["survival"] += modifier
        self.apply_survival_limit()
        self.logger.debug("%s set %s survival to %s" % (request.User, self, self.survivor["survival"]))
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


    def get_survival_actions(self):
        """ Returns the SA's available to the survivor based on current
        impairments, etc. """


        #
        #   initialize and set defaults
        #

        AI = abilities_and_impairments.Assets()
        SA = survival_actions.Assets()

        available_actions = self.Settlement.get_survival_actions("JSON")

        #
        # now check AIs and FAs and see if any add or rm an SA
        #

        add_sa_keys = set()
        rm_sa_keys = set()

        # check A&Is and FAs/SFAs   # disorders coming soon! TKTK
        attrib_keys = ['abilities_and_impairments', 'fighting_arts']
        for ak in attrib_keys:
            for ai_dict in self.list_assets(ak):
                if "survival_actions" in ai_dict.keys():
                    add_sa_keys.update(ai_dict["survival_actions"].get("enable", []))
                    rm_sa_keys.update(ai_dict["survival_actions"].get("disable", []))


        # now add keys
        for k in add_sa_keys:
            sa = SA.get_asset(k)
            sa["available"] = True
            if sa not in available_actions:
                available_actions.append(sa)

        # finally, disable anything that needs to be disabled
        for sa in available_actions:
            if sa["handle"] in rm_sa_keys:
                sa["available"] = False

        return sorted(available_actions, key=lambda k: k['sort_order'])




    #
    #   evaluation / biz logic methods
    #

    def is_dead(self):
        "Returns a bool of whether the survivor is dead."

        if "dead" in self.survivor.keys():
            return True

        return False


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


    def can_spend_survival(self):
        """ Returns a bool representing whether or not the survivor can SPEND
        survival. This is not whether they can GAIN survival. """

        for ai_dict in self.list_assets("abilities_and_impairments"):
            if ai_dict.get("cannot_spend_survival", False):
                return False

        return True



    #
    #   UPDATE and POST Methods
    #

    @utils.error_log
    def update_from_dict(self, d):
        """ Updates the survivor's MDB record from a dictionary. Saves it. Be
        REAL careful with this one. """

        for k in d:
            self.survivor[k] = d[k]
        utils.mdb.survivors.save(self.survivor)





    #
    #   NO METHODS BELOW THIS POINT
    #

    def request_response(self, action=None):
        """ Initializes params from the request and then response to the
        'action' kwarg appropriately. This is the ancestor of the legacy app
        assets.Survivor.modify() method. """

        self.get_request_params()

        if action == "get":
            return self.return_json()

        # controllers with biz logic
        elif action == "controls_of_death":
            self.controls_of_death()

        # sheet operations
        elif action == "update_attribute":
            self.update_attribute()
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

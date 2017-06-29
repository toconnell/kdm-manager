#!/usr/bin/python2.7

from bson import json_util
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
        self.object_version = 0.17
        Models.UserAsset.__init__(self,  *args, **kwargs)
        self.normalize()

        # this makes the baby jesus cry
        import settlements
        self.Settlement = settlements.Settlement(_id=self.survivor["settlement"])


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
    #   update/set methods
    #

    def toggle_sotf_reroll(self):
        """ toggles the survivor's Survival of the Fittest once-in-a-lifetime
        reroll on or off. This is self.survivor["sotf_reroll"] and it's a bool
        and it's not part of the data model, so creating it is necessary some
        times. """

        if not "sotf_reroll" in self.survivor.keys():
            self.survivor["sotf_reroll"] = True
            self.log_event("%s toggled SotF reroll on for %s" % (request.User.login, self))
        elif self.survivor["sotf_reroll"]:
            self.survivor["sotf_reroll"] = False
            self.log_event("%s toggled SotF reroll off for %s" % (request.User.login, self))
        elif not self.survivor["sotf_reroll"]:
            self.survivor["sotf_reroll"] = True
            self.log_event("%s toggled SotF reroll on for %s" % (request.User.login, self))
        else:
            self.logger.error("Unhandled logic in toggle_sotf_reroll() method!")
            raise Exception

        self.save()


    def update_survival(self, modifier=0):
        """ Adds 'modifier' to survivor["survival"]. Will not go below zero. """

        if self.check_request_params("modifier"):
            modifier = int(self.params["modifier"])
        else:
            self.logger.error('Insufficient parameters for updating survival!')
            raise Exception

        self.survivor["survival"] += modifier

        if self.survivor["survival"] < 0:
            self.survivor["survival"] = 0

        if self.survivor["survival"] > self.Settlement.get_survival_limit():
            self.survivor["survival"] = self.Settlement.get_survival_limit()

        self.logger.debug("%s set %s survival to %s" % (request.User, self, self.survivor["survival"]))

        self.save()




    #
    #   get methods
    #

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

        # first check A&Is
        for ai_dict in self.list_assets("abilities_and_impairments"):
            if "survival_actions" in ai_dict.keys():
                add_sa_keys.update(ai_dict["survival_actions"].get("enable", []))
                rm_sa_keys.update(ai_dict["survival_actions"].get("disable", []))

        # now check fighting arts
        #   COMING SOON!

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
        elif action == "toggle_sotf_reroll":
            self.toggle_sotf_reroll()
        elif action == "update_survival":
            self.update_survival()
        else:
            # unknown/unsupported action response
            self.logger.warn("Unsupported survivor action '%s' received!" % action)
            return utils.http_400


        # finish successfully
        return utils.http_200





# ~fin

#!/usr/bin/python2.7

from bson import json_util
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
        self.object_version = 0.14
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

        output = self.get_serialize_meta()
        output.update({"sheet": self.survivor})
        output["sheet"].update({"cursed_items": self.get_cursed_items()})

        # now add the additional top-level items ("keep it flat!" -khoa)

        output.update({"bonuses": self.Settlement.get_bonuses("json")})
        output.update({"notes": self.get_notes()})
        output.update({"survival_actions": self.get_survival_actions()})

        return json.dumps(output, default=json_util.default)


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

        if "belt_of_gender_swap" in self.get_cursed_items():    # TK fix this
            sex = invert_sex(sex)

        return sex

    def get_survival_actions(self):
        """ Returns the SA's available to the survivor based on current
        impairments, etc. """

        SA = survival_actions

        available_actions = self.Settlement.get_survival_actions("JSON")


        # check AIs and see if any add a survival action
        AI = abilities_and_impairments.Assets()
        for ai in self.survivor["abilities_and_impairments"]:
            ai_dict = AI.get_asset(ai)
            if ai_dict is not None:
                add_sa = ai_dict.get("survival_action", None)
                if add_sa is not None:
                    sa_dict = SA.get_asset(add_sa)
                    sa_dict["available"] = True
                    available_actions.append(sa_dict)

        return available_actions




    #
    #   evaluation / biz logic methods
    #

    def is_dead(self):
        "Returns a bool of whether the survivor is dead."

        dead = False
        if "dead" in self.survivor.keys():
            dead = True

        return dead


    def can_be_nominated_for_intimacy(self):
        """ Returns a bool representing whether the survivor can do the
        mommmy-daddy dance. """

        output = True

        if "Destroyed Genitals" in self.survivor["abilities_and_impairments"]:
            output = False
        elif self.is_dead():
            output = False

        return output


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
        else:
            # unknown/unsupported action response
            self.logger.warn("Unsupported survivor action '%s' received!" % action)
            return utils.http_400


        # finish successfully
        return utils.http_200





# ~fin

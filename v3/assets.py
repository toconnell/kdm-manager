"""

    The Settlement and Survivor class definitions in this module are deprecated
    in v4.

    The User class/object def will persist and be the basis for its successor
    method in the Flask app.

"""

from bson.objectid import ObjectId
from bson import json_util
from copy import copy
from collections import defaultdict
from cStringIO import StringIO
from datetime import datetime, timedelta
import gridfs
from hashlib import md5
import inspect
import json
import operator
import os
import pickle
import random
from string import Template, capwords, punctuation
import time
import types

import api
import admin
import html
import utils
from session import Session
from utils import (
    mdb,
    get_logger,
    load_settings,
    get_user_agent,
    ymdhms,
    stack_list,
    to_handle,
    thirty_days_ago,
    recent_session_cutoff,
    ymd,
    u_to_str
)

settings = load_settings()


class User:

    def __init__(self, user_id, session_object=None):
        """ Initialize with a user's _id to create an object with his complete
        user object and all settlements. Like all asset classes, you cannot
        initialize this one without a valid session object. """

        self.logger = get_logger()
        user_id = ObjectId(user_id)
        self.user = mdb.users.find_one({"_id": user_id})

        # 2017-11-13 - sign-in bug - https://github.com/toconnell/kdm-manager/issues/401
        if not 'preferences' in self.user.keys():
            self.user['preferences'] = {}
            self.logger.warn("%s Adding 'preferences' attribute to user!" % self)
            self.save()

        self.Session = session_object
        if self.Session is None:
            raise Exception("User Objects may not be initialized without a session object!")



    def __repr__(self):
        return self.get_name_and_id()


    def save(self):
        """ Save method for user objects. """

        mdb.users.save(self.user)
        self.logger.info("[%s] saved changes to %s" % (self, self))


    def mark_usage(self, action=None):
        """ Updates the user's mdb object with some data. """
        self.user["latest_action"] = action
        self.user["latest_activity"] = datetime.now()
        self.user["latest_user_agent"] = str(get_user_agent())
        mdb.users.save(self.user)


    def update_password(self, password, password_again=False):
        """ Leave the 'password_again' kwarg blank if you're not checking two
        passwords to see if they match, e.g. if you're doing this from the CLI.
        """

        user_admin_log_dict = {
            "created_on": datetime.now(),
            "u_id": self.user["_id"],
        }

        if password_again:
            if password != password_again:
                err_msg = "Could not change password for '%s' (passwords did not match)!" % self.user["login"]
                self.logger.error(err_msg)
                user_admin_log_dict["msg"] = err_msg
                mdb.user_admin.insert(user_admin_log_dict)
                return False
        self.user["password"] = md5(password).hexdigest()
        self.logger.info("Password update for '%s' was successful!" % self.user["login"])
        mdb.users.save(self.user)
        user_admin_log_dict["msg"] = "Password Updated!"
        mdb.user_admin.insert(user_admin_log_dict)
        return True


    def get_name_and_id(self):
        """ Returns a string of the user login and _id value. """
        return "%s (%s)" % (self.user["login"], self.user["_id"])


    def dump_assets(self, dump_type=None):
        """ Returns a dictionary representation of a user's complete assets. Due
        to the...kind of arbitrary design of things, this is a multi-stage sort
        of export: first we get the user info and the user's settlements and
        settlement events, then we get his survivors in a separate bit of logic.
        The last thing we do is get his GridFS stuff, e.g. avatars."""

        self.logger.debug("Beginning '%s' dump for %s" % (dump_type, self))

        assets_dict = {
            "user": self.user,
            "settlements": list(mdb.settlements.find({"created_by": self.user["_id"]})),
            "settlement_events": list(mdb.settlement_events.find({"created_by": self.user["_id"]})),
            "survivor_notes": list(mdb.survivor_notes.find({"created_by": self.user["_id"]})),
            "survivors": [],
            "avatars": [],
        }

        # get all survivors (including those created by other users) for the
        #   user's settlements; then get all survivors created by the user.
        for s in assets_dict["settlements"]:
            assets_dict["settlement_events"].extend(mdb.settlement_events.find({"settlement_id": s["_id"]}))
            survivors = mdb.survivors.find({"settlement": s["_id"]})
            assets_dict["survivors"].extend(survivors)
        other_survivors = mdb.survivors.find({"created_by": self.user["_id"]})
        for s in other_survivors:
            if s not in assets_dict["survivors"]:
                assets_dict["survivors"].append(s)
        self.logger.debug("Dumping %s survivors for %s" % (len(assets_dict["survivors"]), self.get_name_and_id()))

        # now we have to go to GridFS to get avatars
        for s in assets_dict["survivors"]:
            if "avatar" in s.keys():
                try:
                    img = gridfs.GridFS(mdb).get(ObjectId(s["avatar"]))
                    img_dict = {
                        "blob": img.read(),
                        "_id": ObjectId(s["avatar"]),
                        "content_type": img.content_type,
                        "created_by": img.created_by,
                        "created_on": img.created_on,
                    }
                    assets_dict["avatars"].append(img_dict)
                except gridfs.errors.NoFile:
                    self.logger.error("Could not retrieve avatar for survivor %s during asset dump!" % s["_id"])

        # some quick debug tallies
        for a in ["settlements","survivors","avatars"]:
            self.logger.debug("Added %s %s to asset dump for %s." % (len(assets_dict[a]), a, self.get_name_and_id()))

        # now we (finally) do returns:
        if dump_type == "pickle":
            return pickle.dumps(assets_dict)
        elif dump_type == "json":
            return json.dumps(assets_dict, default=json_util.default)

        return assets_dict



    def get_survivors(self, return_type=False):
        """ Returns all of the survivors that a user can access. Leave
        the 'return_type' kwarg unspecified/False if you want a mongo cursor
        back (instead of fruity HTML crap). """

        survivors = list(mdb.survivors.find({"$or": [
            {"email": self.user["login"]},
            {"created_by": self.user["_id"]},
            ], "removed": {"$exists": False}}
        ).sort("name"))

        # user version

        if return_type == "asset_links":
            output = ""
            for s in survivors:
                S = Survivor(survivor_id=s["_id"], session_object=self.Session)
                output += S.asset_link()
            return output

        return survivors



    def mark_auth(self, auth_dt=None):
        self.mark_usage("successful sign-in")
        self.user["latest_succesful_authentication"] = auth_dt
        mdb.users.save(self.user)






#
#   SURVIVOR CLASS
#

class Survivor:


    def __repr__(self):
        return self.get_name_and_id(include_id=False, include_sex=True)


    def __init__(self, survivor_id=None, params=None, session_object=None, suppress_event_logging=False, update_mins=True):
        """ This class definition is maintained for legacy purposes. It is fully
        deprecated in v4, since the webapp should not be managing user assets
        such as survivors. """

        self.logger = get_logger()

        self.suppress_event_logging = suppress_event_logging
        self.update_mins = update_mins


        #
        #   Now start initializing and setting object attribs
        #
        self.survivor = None
        if survivor_id is not None:
            self.survivor = mdb.survivors.find_one({"_id": ObjectId(survivor_id)})

        # whether we've got a survivor from MDB or not, set the attribs of the 
        #   survivor object, because we'll need them for everything below here
        self.set_objects_from_session(session_object)

        # make a new survivor if we haven't retrieved one
        if self.survivor is None:
            raise Exception('Survivor OID not found!')


    #
    #   Survivor meta and manager-only methods below
    #

    @utils.deprecated
    def set_objects_from_session(self, session_object=None):
        """ Tries (hard) to set the current self.Session, .User and .Settlement.
        Makes a ton of noise if it can't. """

        self.Session = session_object

        if self.Session is None or not self.Session:
            err_msg = "Survivor objects may not be initialized without a Session object!"
            self.logger.error(err_msg)
            raise Exception(err_msg)

        self.User = session_object.User
        if self.User is None or not self.User:
            self.logger.error("Survivor objects should not be initialized without a User object!")
            self.logger.critical("Initializing without a User object...")

        self.Settlement = session_object.Settlement
        if self.Settlement is None or not self.Settlement:
            if self.survivor is not None:
                self.Settlement = Settlement(settlement_id=self.survivor["settlement"], session_object=self.Session)
            else:
                self.logger.warn("[%s] initializing survivor object without a Settlement..." % (self.User))


    @utils.deprecated
    def save(self, quiet=False):
        """ Saves a survivor's self.survivor to the mdb. Logs it. """

        mdb.survivors.save(self.survivor)
        self.logger.info("[%s] saved changes to %s" % (self.User, self))


    def get_name_and_id(self, include_id=True, include_sex=False):
        """ Laziness function to return a string of the Survivor's name, _id and
        sex values (i.e. so we can write DRYer log entries, etc.). """

        output = [self.survivor["name"]]
        if include_sex:
            output.append("[%s]" % self.survivor["sex"])
        if include_id:
            output.append("(%s)" % self.survivor["_id"])
        return " ".join(output)




#
#   SETTLEMENT CLASS
#

class Settlement:


    def __repr__(self):
        return self.get_name_and_id()


    def __init__(self, settlement_id=False, name=False, campaign=False, session_object=None):
        """ Initialize with a settlement from mdb. """
        self.logger = get_logger()

        # initialize session and user objects
        self.Session = session_object
        if self.Session is None or not self.Session:
            raise Exception("Settlements may not be initialized without a Session object!")
        try:
            self.User = self.Session.User
        except:
            self.logger.warn("Settlement %s initialized without a User object!" % settlement_id)

        # now set self.settlement
        self.set_settlement(ObjectId(settlement_id))


    #
    #   Settlement meta and manager-only methods below
    #

    @utils.deprecated
    def set_settlement(self, s_id, update_mins=False):
        """ Sets self.settlement. """

        self.settlement = mdb.settlements.find_one({"_id": s_id})

        if self.settlement is None:
            self.logger.error("[%s] failed to initialize settlement _id: %s" % (self.User, s_id))
            raise Exception("Could not initialize requested settlement %s!" % s_id)


    @utils.deprecated
    def update_mins(self):
        """ check 'population' and 'death_count' minimums and update the
        settlement's attribs if necessary.

        There's also some misc. house-keeping that happens here, e.g. changing
        sets to lists (since MDB doesn't support sets), etc.

        This one should be called FREQUENTLY, as it enforces the data model and
        sanitizes the settlement object's settlement dict.
        """

        for min_key in ["population", "death_count", "survival_limit"]:
            min_val = self.get_min(min_key)
            orig_val = int(self.settlement[min_key])
            if orig_val < min_val:
                self.settlement[min_key] = min_val
                self.logger.debug("Automatically updated settlement %s (%s) %s from %s to %s" % (self.settlement["name"], self.settlement["_id"], min_key, orig_val, min_val))
                self.log_event("Automatically changed %s from %s to %s" % (min_key.replace("_"," "), orig_val, min_val))

            # just a little idiot- and user-proofing against negative values
            if self.settlement[min_key] < 0:
                self.settlement[min_key] = 0

        self.enforce_data_model()
        self.save(quiet=True)


    def enforce_data_model(self):
        """ NB: this method is a dead man walking as of the Anniversary Release:
        we're moving data model normalization to the API as of December 2016, so
        doing this kind of processing here is officially deprecated!

        mongo will FTFO if it sees a set(): uniquify our unique lists before
        saving them and exclude any non str/unicode objects that might have
        snuck in while iterating over the cgi.FieldStorage(). """

        # de-dupe keys in certain groups. Probably not necessary here anymore,
        # but let's hang onto this as long as we're still updating from HTML
        # forms (because they're messy)
        set_attribs = ["milestone_story_events", "innovations", "locations", "principles", "quarries"]
        for a in set_attribs:
            self.settlement[a] = list(set([i.strip() for i in self.settlement[a] if type(i) in (str, unicode)]))



    def save(self, quiet=False):
        """ Saves the settlement. Logs it. """

        mdb.settlements.save(self.settlement)
        self.logger.info("[%s] saved changes to %s" % (self.User, self))


    #
    #   Settlement management and administration methods below
    #

    @utils.deprecated
    def log_event(self, msg, event_type=None):
        """ Logs a settlement event to mdb.settlement_events. """

        d = {
            "created_on": datetime.now(),
            "created_by": self.User.user["_id"],
            "settlement_id": self.settlement["_id"],
            "ly": self.settlement["lantern_year"],
            "event": msg,
            "event_type": event_type,
        }
        mdb.settlement_events.insert(d)
        self.logger.debug("Settlement event logged for %s" % self.get_name_and_id())




    #
    #   Settlement reference, retrieval and look-up methods below
    #

    @utils.deprecated
    def get_expansions(self, return_type=None):
        """ Returns expansions as a list. """

        if "expansions" in self.settlement.keys():
            expansions = list(set(self.settlement["expansions"]))
            self.settlement["expansions"] = expansions
        else:
            expansions = []

        if return_type == "dict":
            exp_dict = {}
            for exp_key in expansions:
                exp_dict[exp_key] = game_assets.expansions[exp_key]
            return exp_dict
        elif return_type == "comma-delimited":
            if expansions == []:
                return None
            else:
                return ", ".join(expansions)
        elif return_type == "list_of_names":
            self.logger.error('Calling get_expansions(return_type="list_of_names") is deprecated!')
            return expansions

        return expansions


    def get_ly(self):
        """ Returns self.settlement["lantern_year"] as an int. """
        return int(self.settlement["lantern_year"])


    def get_name_and_id(self):
        """ Laziness function for DRYer log construction. Called by self.__repr__() """
        return "'%s' (%s)" % (self.settlement["name"], self.settlement["_id"])


    def get_attribute(self, attrib=None):
        """ Returns the settlement attribute associated with 'attrib'. Using this
        is preferable to going straight to self.settlement[attrib] because we do
        business logic on these returns.

        Also, this will duck type settlement attributes to integers if it can,
        so using this method contributes to DRYness by removing the need for
        this type of thing:

            value = int(self.settlement["my thing I want"])

        Anyway, when in doubt, use this method.
        """

        if attrib in ["population","death_count","survival_limit"]:
            min_val = self.get_min(attrib)
            if int(self.settlement[attrib]) < min_val:
                return min_val  # this is an int because get_min always returns an int

        raw_value = self.settlement[attrib]

        try:
            return int(raw_value)
        except ValueError:
            return raw_value


    @utils.deprecated
    def get_survivors(self, return_type=False, user_id=None, exclude=[], exclude_dead=False):
        """ Returns the settlement's survivors. Leave 'return_type' unspecified
        if you want a mongo cursor object back. """

        query = {"removed": {"$exists": False}, "settlement": self.settlement["_id"], "_id": {"$nin": exclude}}

        if exclude_dead:
            query["dead"] = {"$exists": False}

        survivors = mdb.survivors.find(query).sort("name")

        if self.User is not None:
            user_login = self.User.user["login"]
        elif self.User is None and user_id is not None:
            self.User = User(user_id=user_id)
            user_login = self.User.user["login"]
        else:
            self.User = None
            user_login = None

        current_user_is_settlement_creator = False
        if self.User is not None and self.User.user["_id"] == self.settlement["created_by"]:
            current_user_is_settlement_creator = True
        elif self.User is not None and "admins" in self.settlement.keys() and self.User.user["login"] in self.settlement["admins"]:
            current_user_is_settlement_creator = True

        if return_type == "hunting_party":
            raise Exception("Using get_survivors() with the 'hunting_party' return type is not supported!")

        if return_type == "html_buttons":
            output = ""
            for survivor in survivors:
                S = Survivor(survivor_id=survivor["_id"])
                output += S.asset_link()
            return output

        if return_type == "sex_count":
            male = 0
            female = 0
            for s in survivors:
                if s["sex"] == "M":
                    male += 1
                elif s["sex"] == "F":
                    female += 1
            return "%sM/%sF" % (male,female)

        if return_type == "chronological_order":
            return mdb.survivors.find(query).sort("created_on")

        # finally, capture and scream bloody murder about deprecated return_types
        if return_type in ["angularjs", "JSON"]:
            raise Exception("Return type '%s' no longer supported by this method!" % return_type)

        return survivors


    def get_campaign(self, return_type=None):
        """ Returns the campaign of the settlement as a handle. Not to be
        confused with the User.get_campaigns() method, which returns campaigns a
        user is currently  associated with.

        For transitional/legacy purposes, this method can accept a few different
        'return_type' kwargs:

            - "dict"        returns the campaign definition dict
            - "name"        returns the campaign name (rather than handle)
            - "forbidden"   returns a list of 'forbidden' game assets

        NB: that the 'forbidden' return type includes innovations, locations,
        etc. and is not limited to one type of 'forbidden' game asset.

        """

        # legacy app data noramlization required because the dashboard breaks
        #   if it doesn't have this (and it doesn't do an API call)
        if self.settlement.get("campaign", None) is None:
            self.settlement["campaign"] = "People of the Lantern"
            self.logger.debug("[%s] defaulting 'campaign' attrib for %s" % (self.User, self))
            self.save()

        if return_type is not None:
            c_dict = self.get_api_asset("game_assets","campaign")

        if return_type == "dict":
            return c_dict
        elif return_type == "name":
            return c_dict["name"]
        elif return_type == "forbidden":
            forbidden = []
            f_dict = c_dict.get("forbidden",{})
            for k in f_dict.keys():
                forbidden.extend(f_dict[k])
            return list(set(forbidden))

        return self.settlement["campaign"]


    def get_min(self, value=None):
        """ Returns the settlement's minimum necessary values for the following:

            'population': the minimum number of survivors based on which have
                'dead' in their Survivor.survivor.keys().
            'deaths' or 'death_count': the minimum number of dead survivors.
            'survival_limit': the minimum survival limit, based on innovations.

        Returns an int. ALWAYS.
        """
        results = False
        settlement_id = ObjectId(self.settlement["_id"])

        if value == "population":
            results = mdb.survivors.find({"settlement": settlement_id, "dead": {"$exists": False}, "removed": {"$exists": False}}).count()
        elif value == "deaths" or value == "death_count":
            results = mdb.survivors.find({"settlement": settlement_id, "dead": {"$exists": True}}).count()
        elif value == "survival_limit":
            min_survival = 0

            if self.settlement["name"] != "":
                min_survival +=1

            innovations = copy(self.settlement["innovations"])
            innovations.extend(self.settlement["principles"])
            innovations = list(set(innovations))
            for innovation_key in innovations:
                if innovation_key in Innovations.get_keys() and "survival_limit" in Innovations.get_asset(innovation_key).keys():
                    min_survival += Innovations.get_asset(innovation_key)["survival_limit"]
            results = min_survival

        return int(results)


    def get_players(self, return_type=None, count_only=False):
        """ The Settlement's generic method for getting players. Comes back as a
        set of email addresses (i.e. user["login"] values). """

        creator = mdb.users.find_one({"_id": self.settlement["created_by"]})
        player_set = set([creator["login"]])
        survivors = mdb.survivors.find({"settlement": self.settlement["_id"]})
        for s in survivors:
            player_set.add(s["email"])

        if count_only:
            return len(player_set)

        return player_set


    @utils.deprecated
    def asset_link(self, context=None, update_mins=False):
        """ Returns an asset link (i.e. html form with button) for the
        settlement.

        Specify one of the following contexts, or leave the 'context' kwarg set
        to None if you want a generic link to the settlement back:

            'campaign_summary':         the "Edit Settlement" link that floats
                                        over the campaign summary view
            'asset_management':         the "Campaign Summary" link that floats
                                        over the create new asset forms,
                                        survior and settlement sheets, etc.

        Anything else will get you the default, gradient_yellow link with the
        settlement flash and the name.
        """

        if context == "campaign_summary":
            button_class = "campaign_summary_gradient"
            link_text = html.dashboard.settlement_flash
            desktop_text = "Edit %s" % self.settlement["name"]
            asset_type = "settlement"
        elif context == "asset_management":
            button_class = "settlement_sheet_gradient"
            link_text = html.dashboard.campaign_flash
            desktop_text = "%s Campaign Summary" % self.settlement["name"]
            asset_type = "campaign"
        else:
            button_class = "kd_dying_lantern dashboard_settlement_list_settlement_button"
            link_text = "<b class='dashboard_settlement_list_settlement_name'>%s</b>" % self.settlement["name"]
            link_text += "<br/><i>%s</i>" % game_assets.campaign_look_up[self.get_campaign()]

            if "abandoned" in self.settlement.keys():
                link_text += ' [ABANDONED]'

            link_text += "<br/>- Created: %s" % self.settlement["created_on"].strftime(ymd)
            link_text += "<br/>- %s expansions / %s player(s)" % (len(self.get_expansions()), self.get_players(count_only=True))
            link_text += "<br/>- LY: %s" % (self.get_ly())
            link_text += "<br/>- Population: %s" % (self.settlement["population"])
            link_text += "<br/>- Deaths: %s" % (self.settlement["death_count"])

            desktop_text = ""
            asset_type = "settlement"

        return html.dashboard.view_asset_button.safe_substitute(
            button_class = button_class,
            asset_type = asset_type,
            asset_id = self.settlement["_id"],
            asset_name = link_text,
            desktop_text = desktop_text,
        )

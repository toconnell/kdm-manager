#!/usr/bin/env python

from bson.objectid import ObjectId
from bson import json_util
from copy import copy
from collections import defaultdict
from cStringIO import StringIO
from datetime import datetime, timedelta
import gridfs
from hashlib import md5
from PIL import Image
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
from modular_assets import survivor_attrib_controls
import game_assets
import html
from models import Disorders, Locations, Items, Innovations, Resources, userPreferences, mutually_exclusive_principles 
from session import Session
from utils import mdb, get_logger, load_settings, get_user_agent, ymdhms, stack_list, to_handle, thirty_days_ago, recent_session_cutoff, ymd, u_to_str
import world

settings = load_settings()


def ua_decorator(render_func=None):
    """ Decorate User Asset render methods with this guy to get some additional
    template variables and header/footer HTML. The 'render_func' kwarg must be
    a User Asset HTML-rendering method.

    We do a few things here:

        - take the output of the render method (as a string), turn it back
        into a template and then plug in some additional variables from the
        self.User object, etc.
        - tack on some additional HTML to the literal bottom of the second
        rendering pass (i.e. the one that happens in the previous bullet)

    """

    if render_func is None:
        raise Exception("This decorator must wrap a User Asset HTML rendering method!")

    def wrapper(self, *args, **kwargs):

        view_html = Template(render_func(self, *args, **kwargs))

        return view_html.safe_substitute(

            application_version = settings.get("application", "version"),

            # angularjs appRoot and other app stuff
            MEDIA_URL = settings.get("application", "STATIC_URL"),
            user_login = self.User.user["login"],
            user_id = self.User.user["_id"],
            settlement_id = self.Session.Settlement.settlement["_id"],

        ) + html.angularJS.timeline + html.angularJS.new_survivor + html.angularJS.settlement_notes + html.angularJS.bulk_add_survivors + html.angularJS.expansions_manager

    return wrapper



class User:

    def __init__(self, user_id, session_object=None):
        """ Initialize with a user's _id to create an object with his complete
        user object and all settlements. Like all asset classes, you cannot
        initialize this one without a valid session object. """

        self.logger = get_logger()
        user_id = ObjectId(user_id)
        self.user = mdb.users.find_one({"_id": user_id})

        self.Session = session_object
        if self.Session is None:
            raise Exception("User Objects may not be initialized without a session object!")

        self.get_settlements()
        self.get_survivors()

        self.preference_keys = [t[0] for t in settings.items("users")]


    def __repr__(self):
        return self.get_name_and_id()


    def save(self):
        """ Save method for user objects. """

        mdb.users.save(self.user)
        self.logger.info("[%s] saved changes to %s" % (self, self))


    def is_admin(self):
        """ Returns True if the user is an application admin. This only returns
        python bools because it should only be used for internal application
        logic and so on.

        Check out the is_settlement_admin() method if you're
        working in user-space."""

        if "admin" in self.user.keys() and type(self.user["admin"]) == datetime:
            return True
        else:
            return False


    def is_settlement_admin(self, return_type=None):
        """ Checks self.Session.Settlement.settlement admins to see if the user
        is a settlement admin. Returns a python bool by default, but can also
        return JS-friendly 'truthy/falsy' strings if required. """

        is_settlement_admin = False

        if self.user["_id"] == self.Session.Settlement.settlement["created_by"]:
            is_settlement_admin = True
        elif "admins" in self.Session.Settlement.settlement.keys():
            if self.user["login"] in self.Session.Settlement.settlement["admins"]:
                is_settlement_admin = True

        if return_type == "truthy":
            return str(is_settlement_admin).lower()

        return is_settlement_admin


    def can_manage_survivor(self, survivor_id=None):
        """ Returns a bool expressing whether the user may manage a given the
        survivor who has the mdb _id of '$survivor_id'. """

        if survivor_id is None:
            self.logger.warn("[%s] 'survivor_id' kwarg must not be None." % (self))
            return False

        if self.is_settlement_admin():
            return True

        s = mdb.survivors.find_one({"_id": ObjectId(survivor_id)})
        if s is None:
            self.logger.warn("[%s] survivor _id '%s' was not found!" % (self, survivor_id))
            return False

        if s["created_by"] == self.user["_id"]:
            return True
        if s["email"] == self.user["login"]:
            return True

        return False


    def can_manage_departing_survivors(self):
        """ Checks 'settlement_id' settlement to see if the user can manage the
        Departing Survivors on the Campaign Summary. This is different than just
        being a settlement admin, because it takes into account whether there
        are, in fact, departing survivors to manage. """

        if self.Session.Settlement is None:
            return False

        if self.Session.Settlement.get_departing_survivors() == []:
            return False

        if self.is_settlement_admin:
            return True

        return False


    def get_preference(self, p_key):
        """ The 'p_key' kwarg should be a preference key. This funciton returns
        a bool for a preference, e.g. if the user has it set to True or False.
        If the user has no preferences set, or no preference for the key, this
        function returns the preference's default value. """

        default_value = settings.getboolean("users", p_key)

        if "preferences" not in self.user.keys():
            return default_value

        if p_key not in self.user["preferences"].keys():
            return default_value

        return self.user["preferences"][p_key]


    def get_name_and_id(self):
        """ Returns a string of the user login and _id value. """
        return "%s (%s)" % (self.user["login"], self.user["_id"])


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


    def update_preferences(self, params):
        """ Processes a cgi.FieldStorage() containing user preferences. Updates
        the mdb object for the user. """

        if not "preferences" in self.user.keys():
            self.user["preferences"] = {}

        user_admin_log_dict = {
            "created_on": datetime.now(),
            "u_id": self.user["_id"],
            "msg" : "Updated Preferences. "
        }

        for p in self.preference_keys:  # this is created when we __init__()
            if p in params:
                p_value = params[p].value
                if p_value == "True":
                    p_value = True
                elif p_value == "False":
                    p_value = False
                self.user["preferences"][p] = p_value
                user_admin_log_dict["msg"] += "'%s' -> %s; " % (p, p_value)
                self.logger.debug("[%s] set preference '%s' -> '%s'" % (self, p, p_value))

        user_admin_log_dict["msg"] = user_admin_log_dict["msg"].strip()
        mdb.user_admin.insert(user_admin_log_dict)
        self.logger.debug("%s updated preferences." % self.user["login"])


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


    def get_campaigns(self):
        """ This function gets all campaigns in which the user is involved. """

        self.get_settlements()
        game_list = set()

        if self.settlements is not None:
            for s in self.settlements:
                if s is not None:
                    game_list.add(s["_id"])

        for s in self.get_survivors():
            game_list.add(s["settlement"])

        output = ""

        game_dict = {}
        for settlement_id in game_list:
            S = Settlement(settlement_id=settlement_id, session_object=self.Session, update_mins=False)
            if S.settlement is not None:
                if not "abandoned" in S.settlement.keys():
                    game_dict[settlement_id] = S.settlement["name"]
            else:
                self.logger.error("Could not find settlement %s while loading campaigns for %s" % (settlement_id, self.get_name_and_id()))
        sorted_game_tuples = sorted(game_dict.items(), key=operator.itemgetter(1))

        for settlement_tuple in sorted_game_tuples:
            settlement_id = settlement_tuple[0]
            S = Settlement(settlement_id=settlement_id, session_object=self.Session, update_mins=False)
            if S.settlement is not None:
                output += S.asset_link(context="dashboard_campaign_list")
        return output


    def get_settlements(self, return_as=False):
        """ Returns the user's settlements in a number of ways. Leave
        'return_as' unspecified if you want a mongo cursor back. """

        self.settlements = list(mdb.settlements.find({
            "created_by": self.user["_id"],
            "removed": {"$exists": False},
            }).sort("created_on"))

        if self.settlements is None:
            return "NONE!"

        if return_as == "html_option":
            output = ""
            for settlement in self.settlements:
                output += '<option value="%s">%s</option>' % (settlement["_id"], settlement["name"])
            return output

        if return_as == "asset_links":
            output = ""
            for settlement in self.settlements:
                S = Settlement(settlement_id=settlement["_id"], session_object=self.Session, update_mins=False)
                output += S.asset_link()
            return output

        return self.settlements


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


    def get_favorites(self, scope=None):
        """ Returns a list of the user's favorite survivors. For the purposes of
        this method, a survivor "belongs" to a user if it has their 'login' attr
        as its 'email' attr. Only returns live survivors."""

        all_favorites = mdb.survivors.find({
            "$or":
            [
                {"email": self.user["login"],},
                {"created_by": self.user["_id"],}
            ],
            "favorite": {"$exists": True},
            "dead": {"$exists": False},
        })


        if scope == "current_settlement":
            out_list = []
            for f in all_favorites:
                if f["settlement"] == self.Session.Settlement.settlement["_id"]:
                    out_list.append(f)
            return out_list

        return all_favorites




    def get_last_n_user_admin_logs(self, logs):
        if logs == 1:
            return mdb.user_admin.find_one({"u_id": self.user["_id"]}, sort=[("created_on", -1)])
        else:
            return mdb.user_admin.find({"u_id": self.user["_id"]}).sort("created_on").limit(logs)


    def mark_usage(self, action=None):
        """ Updates the user's mdb object with some data. """
        if not "activity_log" in self.user.keys():
            self.user["activity_log"] = []

        self.user["activity_log"].append((datetime.now(), action))
        self.user["activity_log"] = self.user["activity_log"][-10:] # only save the last 10

        self.user["latest_action"] = action
        self.user["latest_activity"] = datetime.now()
        self.user["latest_user_agent"] = str(get_user_agent())
        mdb.users.save(self.user)


    def mark_auth(self, auth_dt=None):
        self.mark_usage("successful sign-in")
        self.user["latest_succesful_authentication"] = auth_dt
        mdb.users.save(self.user)


    def html_motd(self):
        """ Creates an HTML MoTD for the user. This needs a refactor that
        breaks it up into a few more intelligently named methods.

        This function is basically the "System" panel and nothing else.

        """

        formatted_log_msg = ""
        last_log_msg = self.get_last_n_user_admin_logs(1)
        if last_log_msg is not None:
            formatted_log_msg = "<p>&nbsp;Latest user admin activity:</p><p>&nbsp;<b>%s</b>:</b> %s</p>" % (last_log_msg["created_on"].strftime(ymdhms), last_log_msg["msg"])

        pref_html = ""
        pref_models = userPreferences()

        organized_prefs = pref_models.get_category_dict()
        for category in sorted(organized_prefs.keys()):
            pref_html += html.dashboard.preference_header.safe_substitute(title=category)
            for k in organized_prefs[category]: #list of keys
                d = pref_models.pref(self, k)
                pref_html += html.dashboard.preference_block.safe_substitute(
                    desc=d["desc"],
                    pref_key=k,
                    pref_true_checked=d["affirmative_selected"],
                    pref_false_checked=d["negative_selected"],
                    affirmative=d["affirmative"],
                    negative=d["negative"]
                )
            pref_html += html.dashboard.preference_footer


        output = html.dashboard.motd.safe_substitute(
            user_preferences = pref_html,
            session_id = self.Session.session["_id"],
            login = self.user["login"],
            last_sign_in = self.user["latest_sign_in"].strftime(ymdhms),
            version = settings.get("application", "version"),
            last_log_msg = formatted_log_msg,
        )
        return output




#
#   SURVIVOR CLASS
#

class Survivor:


    def __repr__(self):
        return self.get_name_and_id(include_id=False, include_sex=True)


    def __init__(self, survivor_id=None, params=None, session_object=None, suppress_event_logging=False, update_mins=True):
        """ Initialize this with a cgi.FieldStorage() as the 'params' kwarg
        to create a new survivor. Otherwise, use a mdb survivor _id value
        to initalize with survivor data from mongo. """

        self.logger = get_logger()

        self.suppress_event_logging = suppress_event_logging
        self.update_mins = update_mins
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
        self.flag_attribs = [
            "cannot_spend_survival",
            "cannot_use_fighting_arts",
            "skip_next_hunt",
            "dead",
            "retired",
            "favorite",
            "public",
        ]
        self.flags = self.damage_locations + self.flag_attribs


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
            survivor_id = self.new(params)

        self.set_api_asset()

        if self.Settlement is not None:
            self.normalize()


    #
    #   Survivor meta and manager-only methods below
    #

    def set_api_asset(self):
        """ Tries to set the survivor's API asset from the session. Fails
        gracefully if it cannot. """

        self.api_asset = {}
        if not hasattr(self.Session, "api_survivors") or self.Session.session["current_view"] == "dashboard":
            return None
        try:
            self.api_asset = self.Session.api_survivors[self.survivor["_id"]]["sheet"]
        except Exception as e:
            self.logger.error("[%s] could not set API asset for %s! Current view: '%s'" % (self.User, self, self.Session.session["current_view"]))
            pass


    def get_api_asset(self, asset_key):
        """ Tries to get an asset from the api_asset attribute/dict. This is the
        version of this for SURVIVORS, not for settlements (which is below). """

        if not hasattr(self, "api_asset"):
            self.set_api_asset()

        if not asset_key in self.api_asset.keys():
            self.logger.warn("[%s] api_asset key '%s' does not exist for %s!" % (self.User, asset_key, self))
            self.logger.debug("[%s] available API asset keys for %s: %s" % (self.User, self, self.api_asset.keys()))
            return {}
        else:
            return self.api_asset[asset_key]


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
            self.logger.critical("Initializing without a User obejct...")

        self.Settlement = session_object.Settlement
        if self.Settlement is None or not self.Settlement:
            if self.survivor is not None:
                self.Settlement = Settlement(settlement_id=self.survivor["settlement"], session_object=self.Session)
            else:
                self.logger.warn("[%s] initializing survivor object without a Settlement..." % (self.User))


    def save(self, quiet=False):
        """ Saves a survivor's self.survivor to the mdb. Logs it. """
        mdb.survivors.save(self.survivor)
        if not quiet:
            self.logger.debug("[%s] saved changes to %s" % (self.User, self))


    def normalize(self):
        """ Run this when a Survivor object is initialized: it will enforce
        the data model and apply settlements defaults to the survivor. """

        # 2016-12 dupe note js bug
        seen = set()
        for n in self.get_survivor_notes():
            if n["note"] in seen:
                self.logger.debug("[%s] duplicate note ('%s') detected. Removing note..." % (self.User, n["note"]))
                mdb.survivor_notes.remove(n)
            seen.add(n["note"])

        # 2016-11 RANDOM_FIGHTING_ART bug
        if "RANDOM_FIGHTING_ART" in self.survivor["fighting_arts"]:
            self.survivor["fighting_arts"].remove("RANDOM_FIGHTING_ART")

        # see if we need to retire this guy, based on recent updates
        if int(self.survivor["hunt_xp"]) >= 16 and not "retired" in self.survivor.keys():
            self.retire()


        # if the survivor is legacy data model, he doesn't have a born_in_ly
        #   attrib, so we have to get him one:
        if not "born_in_ly" in self.survivor.keys():
            self.logger.warn("%s has no 'born_in_ly' value!" % self)
            if "father" not in self.survivor.keys() and "mother" not in self.survivor.keys():
                self.logger.warn("Defaulting birth year to 1 for %s" % self)
                self.survivor["born_in_ly"] = 1
            parent_birth_years = [self.Settlement.get_ly() - 1]
            for p in ["father","mother"]:
                if p in self.survivor.keys():
                    P = Survivor(survivor_id=self.survivor[p], session_object=self.Session)
                    if not "born_in_ly" in P.survivor.keys():
                        self.logger.warn("%s has no 'born_in_ly' value!" % P.get_name_and_id())
                    else:
                        self.logger.debug("%s %s was born in LY %s" % (p.capitalize(), P, P.survivor["born_in_ly"]))
                        parent_birth_years.append(P.survivor["born_in_ly"])
            self.logger.debug("Highest parent birth year is %s for %s: (%s parents)" % (max(parent_birth_years), self, (len(parent_birth_years) - 1)))
            self.survivor["born_in_ly"] = max(parent_birth_years) + 1
            self.logger.warn("Defaulting birth year to %s for %s" % (self.survivor["born_in_ly"], self))

        # if "father" or "mother" keys aren't Object ID's, we need to normalize them:
        for p in ["father","mother"]:
            if p in self.survivor.keys() and type(self.survivor[p]) == unicode:
                self.logger.warn("Normalizing unicode '%s' value to bson ObjectID for %s" % (p, self.get_name_and_id()))
                self.survivor[p] = ObjectId(self.survivor[p])

        # delete bogus attribs
        for a in ["view_game"]:
            if a in self.survivor.keys():
                del self.survivor[a]
                self.logger.debug("Automatically removed bogus key '%s' from %s." % (a, self.get_name_and_id()))

        # remove accidental dupes
        for s in ["disorders"]:
            self.survivor[s] = list(set(self.survivor[s]))

#        self.logger.debug("[%s] normalized %s" % (self.User, self))
        self.save(quiet=True)



    def remove(self):
        """ Marks the survivor 'removed' with a datetime.now(). """

        self.logger.info("[%s] removing survivor %s" % (self.User, self))
        self.survivor["removed"] = datetime.now()
        self.save()

        self.Settlement.increment_population(-1)

        self.Settlement.log_event("%s has <b>permanently removed</b> %s from the settlement!" % (self.User.user["login"], self))
        self.logger.warn("[%s] marked %s as removed!" % (self.User, self))



    def get_name_and_id(self, include_id=True, include_sex=False):
        """ Laziness function to return a string of the Survivor's name, _id and
        sex values (i.e. so we can write DRYer log entries, etc.). """

        output = [self.survivor["name"]]
        if include_sex:
            output.append("[%s]" % self.survivor["sex"])
        if include_id:
            output.append("(%s)" % self.survivor["_id"])
        return " ".join(output)


    def set_attrs(self, attrs_dict):
        """ Accepts a dictionary and updates self.survivor with its keys and
        values. There's no user-friendliness or checking here--this is an admin
        type method--so make sure you know what you're doing with this. """

        for k in attrs_dict.keys():
            self.survivor[k] = attrs_dict[k]
            self.logger.debug("%s set '%s' = '%s' for %s" % (self.User.user["login"], k, attrs_dict[k], self.get_name_and_id()))
            if not self.suppress_event_logging:
                self.Settlement.log_event("Set %s to '%s' for %s" % (k,attrs_dict[k],self.get_name_and_id(include_id=False,include_sex=True)))
        mdb.survivors.save(self.survivor)


    def is_founder(self):
        """ Returns True or False, erring on the side of False. We only want to
        return True when we're sure the survivor was a founder. """

        if not "born_in_ly" in self.survivor.keys():
            return False

        if "father" in self.survivor.keys() or "mother" in self.survivor.keys():
            return False

        if self.survivor["born_in_ly"] == 0:
            return True
        elif "founder" in self.survivor["epithets"]:
            return True
        else:
            return False


    def retire(self):
        """ Retires the survivor. Saves them afterwards, since this can be done
        pretty much anywhere.  This is the only way a survivor should ever be
        retired: if you're doing it somewhere else, fucking stop it."""

        self.survivor["retired"] = "checked"
        self.survivor["retired_in"] = self.Settlement.settlement["lantern_year"]
        self.logger.debug("[%s] just retired %s" % (self.User, self))
        self.Settlement.log_event("%s has retired." % self)
        mdb.survivors.save(self.survivor)


    def get_disorders(self, return_as=False):
        """ Gets a survivors disorders. Returns them as HTMl, if necessary. """

        disorders = self.survivor["disorders"]

        if return_as == "formatted_html":
            output = ""
            for disorder_key in disorders:
                if disorder_key not in Disorders.get_keys():
                    output += '<p><b>%s:</b> custom disorder.</p>' % disorder_key
                else:
                    d_dict = Disorders.get_asset(disorder_key)

                    const = ""
                    if "constellation" in d_dict.keys():
                        const = "card_constellation"
                    flav = ""
                    if "flavor_text" in d_dict.keys():
                        flav = d_dict["flavor_text"] + "<br/>"

                    output += html.survivor.survivor_sheet_disorder_box.safe_substitute(
                        name = disorder_key,
                        constellation = const,
                        flavor = flav,
                        effect = d_dict["survivor_effect"]
                    )

            return output

        if return_as == "html_select_remove":
            if disorders == []:
                return ""
            output = ""
            output = '<select name="remove_disorder" onchange="this.form.submit()">'
            output += '<option selected disabled hidden value="">Remove Disorder</option>'
            for disorder in disorders:
                output += '<option>%s</option>' % disorder
            output += '</select>'
            return output

        return disorders


    def get_returning_survivor_status(self, return_type=None):
        """ Returns a bool of whether the survivor is currently a Returning
        Survivor. Use different return_type values for prettiness. """

        cur_ly = self.Settlement.get_ly()

        departing = False
        if cur_ly in self.get_returning_survivor_years():
            departing = True

        returning = False
        if cur_ly - 1 in self.get_returning_survivor_years():
            returning = True

        if return_type == "html_badge":
            if not returning and not departing:
                return ""

            if returning:
                r_tup = ("R%s" % (cur_ly-1), "returning_survivor_badge_color", "Returning survivor in LY %s" % (cur_ly - 1))
            if departing:
                r_tup = ("R%s" % (cur_ly), "departing_survivor_badge_color", "Returning survivor in LY %s" % cur_ly)

            letter, color, title = r_tup
            return html.survivor.returning_survivor_badge.safe_substitute(
                flag_letter = letter,
                color_class = color,
                div_title = title,
            )

        return returning


    def heal(self, cmd, heal_armor=False, increment_hunt_xp=False, remove_attribute_detail=False, return_to_settlement=False):
        """ This removes the keys defined in self.damage_locations from the
        survivor's MDB object. It can also do some game logic, e.g. remove armor
        points and increment hunt XP.

            'heal_armor'        -> bool; use to zero out armor in addition to
                removing self.damage_location keys
            'increment_hunt_xp' -> int; increment hunt XP by whatever

        """

        if cmd == "Heal Injuries and Remove Armor":
            heal_armor=True
        elif cmd == "Return from Hunt":
            return_to_settlement = True
            remove_attribute_detail=True
            heal_armor=True
            increment_hunt_xp=1

            # record this as a year that we're a returning survivor
            self.update_returning_survivor_years(self.Settlement.settlement["lantern_year"])

            # bump up the increment number for saviors
            if "savior" in self.survivor.keys():
                increment_hunt_xp=4


        if return_to_settlement:
#            if "in_hunting_party" in self.survivor.keys():
            if self.survivor.get("in_hunting_party", None) == "checked":
                del self.survivor["in_hunting_party"]


        for damage_loc in self.damage_locations:
            try:
                del self.survivor[damage_loc]
            except:
                pass

        if heal_armor:
            for armor_loc in ["Head","Arms","Body","Waist","Legs"]:
                self.survivor[armor_loc] = 0

        if increment_hunt_xp and not "dead" in self.survivor.keys():
            current_xp = int(self.survivor["hunt_xp"])
            self.survivor["hunt_xp"] = current_xp + increment_hunt_xp

        if remove_attribute_detail:
            if "attribute_detail" in self.survivor.keys():
                del self.survivor["attribute_detail"]


        self.logger.debug("[%s] has healed %s: command = '%s'" % (self.User, self, cmd))
        mdb.survivors.save(self.survivor)


    def update_returning_survivor_years(self, add_year=None):
        """ Update/modify the self.survivor["returning_survivor"] list (which
        is a list of lantern years normalized to be a set of integers). """

        r = "returning_survivor"

        if not r in self.survivor.keys():
            self.survivor[r] = []

        if add_year is not None and not "dead" in self.survivor.keys():
            add_year = int(add_year)
            self.survivor[r].append(add_year)

        self.survivor[r] = list(set(self.survivor[r]))


    def brain_damage(self, dmg=1):
        """ Damages the survivor's brain, removing insanity or toggling the
        brain box "on" as appropriate. """

        ins = int(self.survivor["Insanity"])

        if ins > 0:
            self.survivor["Insanity"] = int(self.survivor["Insanity"]) - dmg
        elif ins <= 0 and "brain_damage_light" in self.survivor.keys():
            self.logger.debug("%s would suffer Brain Trauma." % self)
        elif ins <= 0 and not "brain_damage_light" in self.survivor.keys():
            self.survivor["brain_damage_light"] = "checked"
        else:
            self.logger.exception("Something bad happened!")

        self.logger.debug("Inflicted brain damage on %s successfully!" % self)



    def add_game_asset(self, asset_type, asset_key, asset_desc=None):
        """ Our generic function for adding a game_asset to a survivor. Some biz
        logic/game rules happen here.

        The kwarg 'asset_type' should always be the self.name value of the
        game_asset model (see models.py for more details).

        Finally, if, for whatever reason, we can't add the asset, we return
        False.
        """

        self.logger.debug("[%s] Adding '%s' to %s of %s..." % (self.User, asset_key, self, self.Settlement))

        asset_key = asset_key.strip()

        if asset_type == "disorder":
            self.survivor["disorders"] = list(set([d for d in self.survivor["disorders"]])) # uniquify
            if len(self.survivor["disorders"]) >= 3:
                return False

            if asset_key == "RANDOM_DISORDER":
                disorder_deck = Disorders.build_asset_deck(self.Settlement)
                for disorder in self.survivor["disorders"]:
                    if disorder in disorder_deck:
                        disorder_deck.remove(disorder)
                self.survivor["disorders"].append(random.choice(disorder_deck))
            elif asset_key not in Disorders.get_keys():
                self.survivor["disorders"].append(asset_key)
                return True
            elif asset_key in Disorders.get_keys():
                asset_dict = Disorders.get_asset(asset_key)
                self.survivor["disorders"].append(asset_key)
                if "skip_next_hunt" in asset_dict.keys():
                    self.survivor["skip_next_hunt"] = "checked"
                if "retire" in asset_dict.keys():
                    self.retire()
                mdb.survivors.save(self.survivor)
                return True
            else:
                return False
        elif asset_type == "fighting_art":
            msg = "Adding Fighting Arts to survivors is not supported by the legacy webapp!"
            self.logger.exception(msg)
            raise Exception(msg)
        elif asset_type == "abilities_and_impairments":
            msg = "Adding A&Is to survivors is not supported by the legacy webapp!"
            self.logger.exception(msg)
            raise Exception(msg)
        else:
            self.logger.critical("Attempted to add unknown game_asset type '%s'. Doing nothing!" % asset_type)



    def rm_game_asset(self, asset_type, asset_key):
        """ This is the reverse of the above function: give it a type and a key
        to remove that key from that type of asset on the survivor. """

        asset_key = asset_key.strip()

        if asset_key not in self.survivor[asset_type]:
            self.logger.debug("[%s] tried to remove '%s' from %s ('%s'), but the asset does not exist!" % (self.User, asset_key, self, asset_type))
            return False

        if asset_type == "abilities_and_impairments":
            msg = "Removing A&Is from survivors is not supported by the legacy webapp!"
            self.logger.exception(msg)
            raise Exception(msg)
        else:
            self.survivor[asset_type].remove(asset_key)

        # save
        mdb.survivors.save(self.survivor)
        self.logger.debug("[%s] removed '%s' from %s (%s)" % (self.User, asset_key, self, asset_type))


    def toggle(self, toggle_key, toggle_value, toggle_type="implicit"):
        """ Toggles an attribute on or off. The 'toggle_value' arg is either
        going to be a MiniFieldStorage list (from cgi.FieldStorage) or its going
        to be a single value, e.g. a string.

        If it's a list, assume we're toggling something on; if it's a single
        value, assume we're toggling it off.

        Review the hidden form inputs to see more about how this works.
        """

        # handle explicit toggles (i.e. input[type=submit] here)
        if "damage" in toggle_key.split("_"):
            toggle_type="explicit"


        if toggle_type == "explicit":
            if toggle_key not in self.survivor.keys():
                self.survivor[toggle_key] = "checked"
                self.logger.debug("%s toggled '%s' ON for survivor %s." % (self.User.user["login"], toggle_key, self.get_name_and_id()))
                if toggle_key == "retired":
                    self.retire()
                return True
            elif toggle_key in self.survivor.keys():
                del self.survivor[toggle_key]
                self.logger.debug("[%s] toggled '%s' OFF for survivor %s." % (self.User, toggle_key, self))
                return True

        mdb.survivors.save(self.survivor)


    def get_avatar(self, return_type=False):
        """ Returns the avatar's GridFS id AS A STRING if you don't specify a
        'return_type'. Use 'html' to get an img element back. """

        if return_type in ["html_desktop", "html_mobile"]:
            if return_type == "html_desktop":
                hide_class = "desktop_only"
            elif return_type == "html_mobile":
                hide_class = "mobile_and_tablet"

            avatar_url = "/media/default_avatar_male.png"
            if self.get_api_asset("effective_sex") == "F":
                avatar_url = "/media/default_avatar_female.png"
            if "avatar" in self.survivor.keys():
                avatar_url = "/get_image?id=%s" % self.survivor["avatar"]

            return html.survivor.clickable_avatar_upload.safe_substitute(
                survivor_id=self.survivor["_id"],
                alt_text="Click to change the avatar image for %s" % self,
                img_src=avatar_url,
                img_class=hide_class,
            )

        if return_type == "html_campaign_summary":
            img_element = '<img class="survivor_avatar_image_campaign_summary" src="/get_image?id=%s"/>' % (self.survivor["avatar"])
            return img_element

        return self.survivor["avatar"]





    def get_constellation(self, return_type=None):
        """ Returns the survivor's constellation. Non if they haven't got one.
        Use the 'html_badge' return type for asset links. """

        const = None
        if "constellation" in self.survivor.keys():
            const = self.survivor["constellation"]

        if return_type == "html_badge":
            if const:
                return html.survivor.survivor_constellation_badge.safe_substitute(value=const)
            else:
                return ""

        return const


    def update_partner(self, p_id):
        """ Updates the survivor's 'partner_id' with the ObjectID of another
        survivor in the settlement. Also pulls up and updates the partner's mdb
        record during the update. """

        p_id = ObjectId(p_id)
        self.survivor["partner_id"] = p_id
        partner = Survivor(survivor_id=p_id, session_object=self.Session)
        partner.survivor["partner_id"] = self.survivor["_id"]
        mdb.survivors.save(partner.survivor)
        self.logger.debug("[%s] %s and %s are now partners." % (self.Settlement, self, partner))


    def update_avatar(self, file_instance):
        """ Changes the survivor's avatar. """

        # if we get a list instead of an instance, throw away items in the list
        # that don't have a file name (because if they don't have a filename,
        # they probably won't have a file either, know what I mean?
        if type(file_instance) == list:
            for i in file_instance:
                if i.filename == "":
                    file_instance.remove(i)
            file_instance = file_instance[0]

        if not type(file_instance) == types.InstanceType:

            self.logger.error("Avatar update failed! 'survivor_avatar' must be %s instead of %s." % (types.InstanceType, type(file_instance)))
            return None

        fs = gridfs.GridFS(mdb)

        if "avatar" in self.survivor.keys():
            fs.delete(self.survivor["avatar"])
            self.logger.debug("%s removed an avatar image (%s) from GridFS." % (self.User.user["login"], self.survivor["avatar"]))

        processed_image = StringIO()
        try:
            im = Image.open(file_instance.file)
        except Exception as e:
            self.logger.error("[%s] Image file could not be opened! Traceback!" % self.User)
            self.logger.exception(e)
            raise

        resize_tuple = tuple([int(n) for n in settings.get("application","avatar_size").split(",")])
        im.thumbnail(resize_tuple, Image.ANTIALIAS)
        im.save(processed_image, format="PNG")

        avatar_id = fs.put(processed_image.getvalue(), content_type=file_instance.type, created_by=self.User.user["_id"], created_on=datetime.now())
        self.survivor["avatar"] = ObjectId(avatar_id)

        mdb.survivors.save(self.survivor)
        self.logger.debug("%s updated the avatar for survivor %s." % (self.User.user["login"], self.get_name_and_id()))



    def get_intimacy_partners(self, return_type=None):
        """ Gets a list of survivors with whom the survivor has done the mommy-
        daddy dance. """
        partners = []
        for s in self.Settlement.get_survivors():
            S = Survivor(survivor_id=s["_id"], session_object=self.Session)
            if self.survivor["_id"] in S.get_parents():
                partners.extend(S.get_parents())
        partners = set(partners)
        try:
            partners.remove(self.survivor["_id"])
        except:
            pass

        if return_type == "html":
            list_of_names = []

            for s_id in partners:
                try:
                    S = Survivor(survivor_id=s_id, session_object=self.Session)
                    list_of_names.append(S.survivor["name"])
                except Exception as e:
                    self.logger.exception(e)
                    self.logger.warn("[%s] intimacy partner '%s' for %s could not be initialized!" % (self.User, s_id, self))
                    list_of_names.append("Unknown/Removed survivor")
            output = ", ".join(sorted(list_of_names))
            if list_of_names != []:
                return "<p>%s</p>" % output
            else:
                return ""

        return partners


    def get_siblings(self, return_type=None):
        """ Gets a survivors siblings and returns it as a dictionary (by
        default). Our pretty/HTML return comes back as a list. """

        siblings = {}

        for s in self.Settlement.get_survivors():
            S = Survivor(survivor_id=s["_id"], session_object=self.Session)
            for p in self.get_parents():
                if p in S.get_parents():
                    siblings[S.survivor["_id"]] = "half"
            if self.get_parents() != [] and S.get_parents() == self.get_parents():
                siblings[S.survivor["_id"]] = "full"

        try:
            del siblings[self.survivor["_id"]]   # remove yourself
        except:
            pass

        if return_type == "html":
            if siblings == {}:
                return ""
            sib_list = []
            for s in siblings.keys():
                S = Survivor(survivor_id=s, session_object=self.Session)
                if siblings[s] == "half":
                    sib_list.append("%s (half)" % S.get_name_and_id(include_sex=True, include_id=False))
                else:
                    sib_list.append("%s" % S.get_name_and_id(include_sex=True, include_id=False))
            return "<p>%s</p>" % ", ".join(sib_list)

        return siblings


    def get_parents(self, return_type=None):
        """ Uses Settlement.get_ancestors() sort of like the new Survivor
        creation screen to allow parent changes. """

        parents = []
        for p in ["father","mother"]:
            if p in self.survivor.keys():
                parents.append(self.survivor[p])

        if return_type == "html_select":
            output = ""

            if self.is_founder():
                return "<p>None. %s is a founding member of %s.</p>" % (self.survivor["name"], self.Settlement.settlement["name"])   # founders don't have parents

            for role in [("father", "M"), ("mother", "F")]:
                output += html.survivor.change_ancestor_select_top.safe_substitute(parent_role=role[0], pretty_role=role[0].capitalize())
                for s in self.Settlement.get_survivors():
                    S = Survivor(survivor_id=s["_id"], session_object=self.Session)
                    if S.get_api_asset("effective_sex") == role[1]:
                        selected = ""
                        if S.survivor["_id"] in parents:
                            selected = "selected"
                        output += html.survivor.change_ancestor_select_row.safe_substitute(parent_id=S.survivor["_id"], parent_name=S.survivor["name"], selected=selected)
                output += html.survivor.add_ancestor_select_bot
            return output

        return parents


    def get_children(self, return_type=None):
        """ Returns a dictionary of the survivor's children. """
        children = set()
        children_raw = []
        survivors = self.Settlement.get_survivors()
        for s in survivors:
            survivor_parents = []
            for p in ["father","mother"]:
                if p in s.keys():
                    survivor_parents.append(s[p])
            for p in ["father","mother"]:
                if p in s.keys() and s[p] == self.survivor["_id"]:
                    other_parent = None
                    survivor_parents.remove(s[p])
                    if survivor_parents != []:
                        other_parent = survivor_parents[0]
                    if other_parent is not None:
                        try:
                            O = Survivor(survivor_id=other_parent, session_object=self.Session)
                            children.add("%s (with %s)" % (s["name"], O.survivor["name"]))
                            children_raw.append(s)
                        except:
                            pass
                    else:
                        children.add(s["name"])
                        children_raw.append(s)

        if return_type == "html":
            if children == set():
                return ""
            else:
                return "<p>%s<p>" % (", ".join(list(children)))

        return list(children_raw)


    def get_partner(self, return_type="html_controls"):
        """ Returns the survivor's partner's Survivor object by default. Use the
        'return_type' kwarg to get different types of returns.  """

        if not "partner_id" in self.survivor.keys():
            partner = None
        else:
            try:
                partner = Survivor(survivor_id=self.survivor["partner_id"], session_object=self.Session)
            except Exception as e:
                self.logger.exception(e.message)
                self.logger.error("[%s] Survivor %s partner ID not found in MDB! (%s)" % (self.Settlement, self, self.survivor["partner_id"]))
                del self.survivor["partner_id"]
                self.logger.info("[%s] Removed 'partner_id' attrib from %s" % (self.Settlement, self))
                partner = None

        if return_type == "html_controls":

            output = html.survivor.partner_controls_top
            if partner is None:
                output += html.survivor.partner_controls_none
            for s in self.Settlement.get_survivors():
                selected = ""
                if s["_id"] == self.survivor["_id"]:
                    pass
                else:
                    if partner is not None and partner.survivor["_id"] == s["_id"]:
                        selected = "selected"
                    output += html.survivor.partner_controls_opt.safe_substitute(name=s["name"], value=s["_id"], selected=selected)
            output += html.survivor.partner_controls_bot
            return output

        return partner


    def get_expansion_attribs(self, return_type=False):
        """ Expansion content that has the 'survivor_attribs' key is retrieved
        using this. The 'expansion_attribs' of a survivor is a dict of attribs
        and their values. These things are totally arbitrary. """

        survivor_expansion_attribs = {}
        if "expansion_attribs" in self.survivor.keys() and type(self.survivor["expansion_attribs"]) == dict:
            survivor_expansion_attribs = self.survivor["expansion_attribs"]

        if return_type == "html_controls":
            # first, figure out if we're using expansion content with these
            # attributes, so we can decide whether to go forward
            expansion_attrib_keys = set()

            # 1.) check the campaign for survivor_attribs
            c_dict = self.Settlement.get_campaign("dict")
            if "survivor_attribs" in c_dict.keys():
                expansion_attrib_keys.update(
                    c_dict["survivor_attribs"]
                )

            # 2.) check the expansions for survivor_attribs
            for exp_key in self.Settlement.get_expansions():
                if "survivor_attribs" in self.Settlement.get_api_asset("game_assets","expansions")[exp_key]:
                    expansion_attrib_keys.update(self.Settlement.get_api_asset("game_assets","expansions")[exp_key]["survivor_attribs"])

            # as usual, bail early if we don't need to show anything
            if expansion_attrib_keys == set():
                return ""

            control_html = ""
            for expansion_attrib_key in expansion_attrib_keys:
                c = ""
                if expansion_attrib_key in survivor_expansion_attribs.keys():
                    c = survivor_expansion_attribs[expansion_attrib_key]
                control_html += html.survivor.expansion_attrib_item.safe_substitute(item_id=to_handle(expansion_attrib_key), key=expansion_attrib_key, checked=c)
            output = html.survivor.expansion_attrib_controls.safe_substitute(control_items=control_html)
            return output

        return survivor_expansion_attribs


    def update_expansion_attribs(self, attribs):
        """ Expansion content with 'survivor_attribs' updates survivors with
        special attribs. Update them here using cgi.FieldStorage() key/value
        pairs. """

        active = set()
        for pair in attribs:
            if pair.value != "None":
                active.add(pair.value)

        if not "expansion_attribs" in self.survivor.keys():
            self.survivor["expansion_attribs"] = {}

        for attrib in active:
            if not attrib in self.get_expansion_attribs().keys():
                self.survivor["expansion_attribs"][attrib] = "checked"
#                self.update_epithets(epithet=attrib)    # issue #81
                self.logger.debug("[%s] toggled ON expansion attribute '%s' for %s" % (self.User, attrib, self))
        for attrib in self.get_expansion_attribs().keys():
            if not attrib in active:
                del self.survivor["expansion_attribs"][attrib]
#                self.update_epithets(action="rm", epithet=attrib)
                self.logger.debug("[%s] toggled OFF expansion attribute '%s' for %s" % (self.User, attrib, self))



    def update_email(self, email):
        """ Changes the survivor's email. Does some normalization and checks."""
        email = email.lower().strip()

        if email == "":
            return
        elif email == self.survivor["email"]:
            return
        else:
            self.survivor["email"] = email
            self.Settlement.log_event("%s is now managed by %s." % (self, email))
            self.logger.debug("[%s] changed survivor %s email to %s." % (self.User, self, email))



    def get_survivor_attribute(self, attrib=None, attrib_detail=None):
        """ Returns a survivor attribute (MOV, ACC, EVA, etc.) as an integer.
        Use the 'attrib_detail' kwarg to retrieve attribute details, if they
        exist (if they don't you'll get a zero back). """

        if attrib is None:
            self.logger.error("get_survivor_attribute() requires a non-None attribute!")

        if attrib_detail is None and attrib in self.survivor.keys():
            return int(self.survivor[attrib])

        if attrib_detail in ["gear","tokens"] and "attribute_detail" in self.survivor.keys():
            return int(self.survivor["attribute_detail"][attrib][attrib_detail])

        return 0


    def update_survivor_attribute(self, attrib, attrib_type, attrib_type_value):
        """ Processes input from the angularjs attributeController app. Updates
        a survivor's base, gear and token attribute stats. Logs. """

        if not "attribute_detail" in self.survivor.keys():
            self.survivor["attribute_detail"] = {
                "Movement": {"gear": 0, "tokens": 0},
                "Accuracy": {"gear": 0, "tokens": 0},
                "Strength": {"gear": 0, "tokens": 0},
                "Evasion": {"gear": 0, "tokens": 0},
                "Luck": {"gear": 0, "tokens": 0},
                "Speed": {"gear": 0, "tokens": 0},
            }

        if attrib_type == "base":
            self.survivor[attrib] = attrib_type_value
            self.logger.debug("[%s] set %s '%s' to %s!" % (self.User, self, attrib, attrib_type_value))
        elif attrib_type in ["gear","tokens"]:
            self.survivor["attribute_detail"][attrib][attrib_type] = int(attrib_type_value)
            self.logger.debug("[%s] set %s '%s' ('%s' detail) to %s!" % (
                self.User, self, attrib, attrib_type, attrib_type_value
            ))
        else:
            self.logger.error("[%s] unknown attribute type '%s' cannot be processed!" % (self.User, attrib_type))


    def remove_survivor_attribute(self, attrib):
        """ Tries to delete an attribute from a survivor's MDB document. Fails
        gracefully if it cannot. Includes special handling for certain
        attributes. """

        if attrib == "in_hunting_party":
            self.join_departing_survivors()
        else:
            try:
                del self.survivor[attrib]
                self.logger.debug("[%s] removed '%s' key from %s" % (self.User, attrib, self))
            except:
                self.logger.error("[%s] attempted to remove '%s' key from %s, but that key does not exist!" % self.User, attrib, self)


    def update_survivor_notes(self, action="add", note=None):
        """ Use this to add or remove notes. Works on strings, rather than IDs,
        for the sake of making the REST/form side of things simple. """

        if note is None:
            self.logger.warn("[%s] note is None!" % self.User)

        if action=="add":
            note_handle = "%s_%s" % (datetime.now().strftime("%Y%m%d%H%M%S"), self.survivor["_id"])
            note_dict = {
                "created_by": self.User.user["_id"],
                "created_on": datetime.now(),
                "survivor_id": self.survivor["_id"],
                "settlement_id": self.Settlement.settlement["_id"],
                "note": note,
                "note_zero_punctuation": unicode(note.translate(None, punctuation).replace(" ","").strip()),
                "name": "%s note" % self,
            }


            mdb.survivor_notes.insert(note_dict)
            self.logger.debug("[%s] added note '%s' to %s." % (self.User, note, self))
        elif action=="rm":
            try:
                note = str(note.decode('ascii', 'ignore'))
                note_zp = unicode(note.translate(None, punctuation).replace(" ","").strip())
            except Exception as e:
                self.logger.exception(e)
                raise
            target_note = mdb.survivor_notes.find_one({"note_zero_punctuation":note_zp, "survivor_id": self.survivor["_id"]})
            if target_note is None:
                self.logger.error("[%s] attempted to remove a note from survivor %s (%s) that could not be found!" % (self.User, self, self.survivor["_id"]))
                self.logger.error(note_zp)
            else:
                mdb.survivor_notes.remove(target_note)
                self.logger.debug("[%s] removed note '%s' from %s." % (self.User, note, self))


    def get_survivor_notes(self, return_type=None):
        """ Tries to retrieve documents from mdb.survivor_notes registered to
        the survivor's _id. Sorts them for return on the Survivor Sheet, etc.
        Only searches notes created LATER than the survivor's 'created_on'
        attribute, i.e. to speed up return. """

        notes = mdb.survivor_notes.find({
            "survivor_id": self.survivor["_id"],
            "created_on": {"$gte": self.survivor["created_on"]}
        }, sort=[("created_on",-1)])

        if return_type == "angularjs":
            sorted_note_strings = []
            for note in notes:
                sorted_note_strings.append(str(note["note"]).replace("'","&#8217;").replace('"','&quot;'))

            output = html.survivor.survivor_notes.safe_substitute(
                name = self.survivor["name"],
                survivor_id = self.survivor["_id"],
                note_strings_list = sorted_note_strings,
            )
            return output

        if return_type == list:
            out_list = []
            for n in notes:
                out_list.append(n["note"])
            return out_list

        return notes




    def get_returning_survivor_years(self):
        """ Returns a list of integers representing the lantern years during
        which a survivor is considered to be a Returning Survivor. """

        if not "returning_survivor" in self.survivor.keys():
            return []
        else:
            return self.survivor["returning_survivor"]



    def join_departing_survivors(self):
        """ Toggles whether the survivor is in the Departing Survivors group or
        not. Watch out for biz logic here! """

        if not "in_hunting_party" in self.survivor.keys():
            self.survivor["in_hunting_party"] = "checked"
            msg = "added %s to" % self
        else:
            del self.survivor["in_hunting_party"]
            msg = "removed %s from" % self

        self.Settlement.log_event("%s %s the Departing Survivors group." % (self.User.user["login"], msg))
        self.logger.debug("[%s] %s the Departing Survivors group." % (self.User, msg))



    def modify(self, params):
        """ Reads through a cgi.FieldStorage() (i.e. 'params') and modifies the
        survivor. """

#        self.logger.debug("[%s] is modifying survivor %s" % (self.User, self))

        ignore_keys = [
            # legacy keys (soon to be deprecated)
            "heal_survivor","form_id",
            # misc controls that we're already done with by now
            "norefresh", "modify", "view_game", "asset_id",
        ]

        for p in params:

            game_asset_key = params[p]
            if type(params[p]) != list and p not in ignore_keys:
                game_asset_key = params[p].value.strip()
                if game_asset_key == 'true':
                    game_asset_key = True
                elif game_asset_key == 'false':
                    game_asset_key = False
                else:
                    pass

#                self.logger.debug("%s -> '%s' (type=%s)" % (p, game_asset_key, type(params[p])))

            if p in ignore_keys:
                pass
            elif p == "survivor_avatar":
                self.update_avatar(params[p])
            elif p == "add_disorder":
                self.add_game_asset("disorder", game_asset_key)
            elif p == "remove_disorder":
                self.rm_game_asset('disorders',game_asset_key)
            elif p == "email":
                self.update_email(game_asset_key)
            elif p == "in_hunting_party":
                self.join_departing_survivors()
            elif p == "partner_id":
                self.update_partner(game_asset_key)
            elif p == "expansion_attribs":
                self.update_expansion_attribs(params[p])
            elif p.split("_")[0] == "toggle" and "norefresh" in params:
                toggle_key = "_".join(p.split("_")[1:])
                self.toggle(toggle_key, game_asset_key, toggle_type="explicit")
            elif p.split("_")[0] == "toggle" and "damage" in p.split("_"):
                toggle_key = "_".join(p.split("_")[1:])
                self.toggle(toggle_key, game_asset_key, toggle_type="explicit")
            elif p == "add_survivor_note":
                self.update_survivor_notes("add", game_asset_key)
            elif p == "rm_survivor_note":
                self.update_survivor_notes("rm", game_asset_key)
            elif p in ["Insanity","Head","Arms","Body","Waist","Legs"]:
                self.update_survivor_attribute(p, "base", game_asset_key)
            elif game_asset_key == "None":
                self.remove_survivor_attribute(p)
            else:
                self.logger.debug("[%s] direct Survivor Sheet update: %s -> %s (%s)" % (self.User, p, game_asset_key, self))
                self.survivor[p] = game_asset_key



        # idiot-proof the hit boxes
        for hit_tuplet in [("arms_damage_light","arms_damage_heavy"), ("body_damage_light", "body_damage_heavy"), ("legs_damage_light", "legs_damage_heavy"), ("waist_damage_light", "waist_damage_heavy")]:
            light, heavy = hit_tuplet
            if heavy in self.survivor.keys() and not light in self.survivor.keys():
                self.survivor[light] = "checked"

        # do healing absolutely last
        if "heal_survivor" in params:
            self.heal(params["heal_survivor"].value)

        # this is the big save. This should be the ONLY SAVE we do during a self.modify()
        self.save()


    def asset_link(self, view="survivor", button_class="survivor", link_text=False, include=["hunt_xp", "insanity", "sex", "dead", "retired", "returning"], disabled=False):
        """ Returns an asset link (i.e. html form with button) for the
        survivor. """

        if not link_text:
            link_text = '<b>%s</b>' % self.survivor["name"]
            if "sex" in include:
                link_text += " [%s]" % self.get_api_asset("effective_sex")

        if disabled:
            link_text += "<br />%s" % self.survivor["email"]

        if include != []:
            attribs = []


            if "dead" in include:
                if "dead" in self.survivor.keys():
                    button_class = "grey"
                    attribs.append("Dead")

            if "retired" in include:
                if "retired" in self.survivor.keys():
                    button_class = "warn"
                    attribs.append("Retired")

            if "returning" in include:
                if self.Settlement.get_ly() in self.get_returning_survivor_years():
                    attribs.append("Returning Survivor")

            if "settlement_name" in include:
                attribs.append(self.Settlement.settlement["name"])

            if "hunt_xp" in include:
                attribs.append("XP: %s" % self.survivor["hunt_xp"])

            if "insanity" in include:
                attribs.append("Insanity: %s" % self.survivor["Insanity"])

            if attribs != []:
                suffix = "<br /> "
                suffix += ", ".join(attribs)
                suffix += ""
                link_text += suffix

        if disabled:
            disabled = "disabled"
            button_class= "unclickable"

        output = html.dashboard.view_asset_button.safe_substitute(
            button_class = button_class,
            asset_type = view,
            asset_id = self.survivor["_id"],
            asset_name = link_text,
            disabled = disabled,
            desktop_text = "",
        )

        return output



    def render_hit_box_controls(self, hit_location=None):
        """ Fills in the html template for hit box controls and spits out HTML
        for the controller. Kind of kludgey, but slims down the rendering
        process/outout ."""

        if hit_location is None:
            self.logger.error("The 'hit_location' may not be None!")
            return None
        elif hit_location not in self.survivor.keys():
            self.logger.error("The '%s' hit location does not exist!" % hit_location)

        dmg_l = "damage_box_"
        if "%s_damage_light" % hit_location.lower() in self.survivor.keys():
            dmg_l += self.survivor["%s_damage_light" % hit_location.lower()]
        dmg_h = "damage_box_"
        if "%s_damage_heavy" % hit_location.lower() in self.survivor.keys():
            dmg_h += self.survivor["%s_damage_heavy" % hit_location.lower()]

        return html.survivor.survivor_sheet_hit_box_controls.safe_substitute(
            dmg_light_checked = dmg_l,
            dmg_heavy_checked = dmg_h,
            damage_location_light = "damage_%s_light" % hit_location.lower(),
            damage_location_heavy = "damage_%s_heavy" % hit_location.lower(),
            toggle_location_damage_light = "toggle_%s_damage_light" % hit_location.lower(),
            toggle_location_damage_heavy = "toggle_%s_damage_heavy" % hit_location.lower(),
            hit_location = hit_location,
            survivor_id = self.survivor["_id"],
            location_lower = hit_location.lower(),
            number_input_id = "%sHitBoxInput" % hit_location.lower(),
            hit_location_value = self.survivor[hit_location],
        )




    @ua_decorator
    def render_html_form(self):
        """ Render a Survivor Sheet for the survivor.

        This is just like the render_html_form() method of the settlement
        class: a giant tangle-fuck of UI/UX logic that creates the form for
        modifying a survivor.

        It's going on one year and this is still a total debacle. This needs to
        be refactored in the next big clean-up push.
        """


        flags = {}
        for flag in self.flags:
            flags[flag] = ""
            if flag in self.survivor.keys():
                flags[flag] = self.survivor[flag]

        exp = self.Settlement.get_expansions("list_of_names")

        # disorders widgets
        disorders_picker = Disorders.render_as_html_dropdown(exclude=self.survivor["disorders"], Settlement=self.Settlement)
        if len(self.survivor["disorders"]) >= 3:
            disorders_picker = ""


        rm_controls = ""
        if self.User.get_preference("show_remove_button"):
            rm_controls = html.survivor.survivor_sheet_rm_controls.safe_substitute(
                name=self.survivor["name"],
                survivor_id=self.survivor["_id"],
            )

        output = html.survivor.form.safe_substitute(
            survivor_id = self.survivor["_id"],
            name = self.survivor["name"],
            email = self.survivor["email"],

            # controls
            remove_survivor_controls = rm_controls,

            # checkbox status
            favorite_checked = flags["favorite"],

            # manually generated hit boxes
            insanity = self.survivor["Insanity"],
            brain_damage_light_checked = flags["brain_damage_light"],
            head_damage_heavy_checked = flags["head_damage_heavy"],
            head = self.survivor["Head"],

            # procedurally generated hit boxes
            arms_hit_box = self.render_hit_box_controls("Arms"),
            body_hit_box = self.render_hit_box_controls("Body"),
            waist_hit_box = self.render_hit_box_controls("Waist"),
            legs_hit_box = self.render_hit_box_controls("Legs"),

            disorders = self.get_disorders(return_as="formatted_html"),
            add_disorders = disorders_picker,
            rm_disorders = self.get_disorders(return_as="html_select_remove"),

            # lineage
            parents = self.get_parents(return_type="html_select"),
            children = self.get_children(return_type="html"),
            siblings = self.get_siblings(return_type="html"),
            partners = self.get_intimacy_partners("html"),

            # optional and/or campaign-specific controls and modals
            partner_controls = self.get_partner("html_controls"),
            expansion_attrib_controls = self.get_expansion_attribs("html_controls"),

            # angularjs application controls
            survivor_notes = self.get_survivor_notes("angularjs"),
        )
        return output



#
#   SETTLEMENT CLASS
#

class Settlement:


    def __repr__(self):
        return self.get_name_and_id()


    def __init__(self, settlement_id=False, name=False, campaign=False, session_object=None, update_mins=True):
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

        # if we initialize a settlement without an ID, make a new one
        if not settlement_id:
            settlement_id = self.new()
        else:
            settlement_id = ObjectId(settlement_id)

        # now set self.settlement
        self.set_settlement(settlement_id, update_mins)

        # uncomment these to log which methods are initializing 
#        curframe = inspect.currentframe()
#        calframe = inspect.getouterframes(curframe, 2)
#        self.logger.debug("settlement initialized by %s" % calframe[1][3])



    #
    #   Settlement meta and manager-only methods below
    #

    def set_settlement(self, s_id, update_mins=False):
        """ Sets self.settlement. """

        self.settlement = mdb.settlements.find_one({"_id": s_id})

        if self.settlement is None:
            self.logger.error("[%s] failed to initialize settlement _id: %s" % (self.User, s_id))
            raise Exception("Could not initialize requested settlement %s!" % s_id)

        if update_mins:
            self.update_mins()


    def update_mins(self):
        """ check 'population' and 'death_count' minimums and update the
        settlement's attribs if necessary.

        There's also some misc. house-keeping that happens here, e.g. changing
        sets to lists (since MDB doesn't support sets), etc.

        This one should be called FREQUENTLY, as it enforces the data model and
        sanitizes the settlement object's settlement dict.
        """

        # uncomment these to log which methods are calling update_mins()
#        curframe = inspect.currentframe()
#        calframe = inspect.getouterframes(curframe, 2)
#        self.logger.debug("update_mins() called by %s" % calframe[1][3])

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

        # auto-update the timeline here, if the user wants us to
        if self.User.get_preference("update_timeline"):
            self.update_timeline_with_story_events()

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
        if not quiet:
            self.logger.debug("[%s] saved changes to %s" % (self.User, self))



    def set_api_asset(self, refresh=False):
        """ Tries to set the settlement's API asset from the session. Fails
        gracelessly if it cannot: if we've got methods looking for API data,
        they need to scream bloody murder if they can't get it."""

#        self.logger.debug("[%s] setting API asset for %s..." % (self.User, self))

        cv = self.Session.get_current_view()

        # if we're looking at any view other than the dashboard or the panel,
        # throw an error if we haven't got a settlement asset loaded up for the
        # session (because that's a big fucking problem).
        if cv not in ["dashboard","panel"] and not hasattr(self.Session, "api_settlement"):
            self.logger.error("[%s] session has no API settlement asset!" % (self.User))

        if cv not in ["dashboard","panel"]:
            if not hasattr(self.Session, "api_settlement"):
                raise Exception("[%s] session has no API assets!" % self.User)
            if refresh:
                self.Session.set_api_assets()
            self.api_asset = self.Session.api_settlement
            if not "game_assets" in self.api_asset.keys():
                self.logger.error("[%s] API asset for %s does not contain a 'game_assets' key!" % (self.User, self))
        elif cv == "panel":
            self.logger.warn("[%s] current view is admin panel. API asset was requested, but cannot be initialized!" % self.User)

        if not hasattr(self, "api_asset"):
            self.logger.warn("[%s] no API asset initialized for %s!" % (self.User, self))



    def refresh_from_API(self,k):
        """ Retrives the settlement from the API and sets self.settlement[k] to
        whatever the API currently thinks self.settlement happens to be. """

        self.set_api_asset(refresh=True)
        self.settlement[k] = self.api_asset["sheet"][k]
        self.logger.info("[%s] reloaded self.settlement[%s] from API data" % (self.User, k))


    def get_api_asset(self, asset_type="sheet", asset_key=None):
        """ Tries to get an asset from the api_asset attribute/dict. Fails
        gracefully. Settlement assets are more information-rich than survivor
        assets, so there's more conditional navigation here. """

        if not hasattr(self, "api_asset"):
            self.set_api_asset()
            if not hasattr(self, "api_asset"):
                msg = "[%s] failed to initialize API asset for %s" % (self.User, self)
                self.logger.error(msg)
                raise AttributeError(msg)

        if asset_key is None:
            return {}
        elif not asset_type in self.api_asset.keys():
            self.logger.warn("[%s] asset type '%s' not found in API asset for %s. Current view: '%s'" % (self.User, asset_type, self, self.Session.session["current_view"]))
            self.logger.debug("[%s] available API asset_types for %s: %s" % (self.User, self, self.api_asset))
            return {}
        elif not asset_key in self.api_asset[asset_type]:
            self.logger.warn("[%s] asset key '[%s][%s]' not found in API asset for %s" % (self.User, asset_type, asset_key, self))
            self.logger.debug("[%s] available API asset_keys for %s [%s]: %s" % (self.User, self, asset_type, self.api_asset[asset_type].keys()))
            return {}
        else:
            return self.api_asset[asset_type][asset_key]


    #
    #   Settlement management and administration methods below
    #


    def remove(self):
        """ Marks the settlement and the survivors as "removed", which prevents
        them from showing up on the dashboard. """

        self.logger.warn("[%s] is removing settlement %s " % (self.User, self))
        for survivor in self.get_survivors():
            S = Survivor(survivor_id=survivor["_id"], session_object=self.Session)
            S.remove()
        self.settlement["removed"] = datetime.now()
        self.log_event("%s removed the settlement!" % (self.User.user["login"]))
        self.logger.warn("[%s] Finished marking %s as 'removed'." % (self.User, self))
        self.save()


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


    def get_event(self, event_name=None):
        """ Searches through the settlement's API asset for an event matching
        'event_name'. Returns an empty dict if no event exists. """

        all_events = self.get_api_asset("game_assets","events")

        lookup_dict = {}
        for h in all_events.keys():
            lookup_dict[all_events[h]["name"]] = h

        if event_name not in lookup_dict.keys():
            self.logger.warn("[%s] event name '%s' not found in API event asset list!" % (self.User, event_name))
            return {}

        event_handle = lookup_dict[event_name]
        return all_events[event_handle]


    def get_story_event(self, event=None):
        """ Accepts certain 'event' values and spits out a string of HTML
        reflecting page numbers, etc.. """

        c_dict = self.get_campaign("dict")
        if "replaced_story_events" in c_dict.keys():
            if event in c_dict["replaced_story_events"]:
                event = c_dict["replaced_story_events"][event]

        if event == "Bold":
            v = 3
        elif event == "Insight":
            v = 3
        elif event == "Awake":
            v = 3
        else:
            return None

        p = self.get_event(event).get("page",None)

        if p == None:
            self.logger.warn("[%s] the 'page' attrib of event '%s' could not be retrieved!" % (self.User, event))

        output = html.survivor.stat_story_event_stub.safe_substitute(
            event=event,
            page=p,
            attrib_value=v,
        )

        return output


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
            expansions_dict = self.get_api_asset("game_assets","expansions")
            output_list = []
            for e in expansions:
                output_list.append(expansions_dict[e]["name"])
            return output_list

        return expansions


    def get_ly(self):
        """ Returns self.settlement["lantern_year"] as an int. """
        return int(self.settlement["lantern_year"])


    def increment_population(self, amount):
        """ Modifies settlement population. Saves the settlement to MDB. """
        current_pop = int(self.settlement["population"])
        new_pop = current_pop + amount
        self.log_event("Settlement population automatically adjusted by %s" % amount)
        self.settlement["population"] = current_pop
        mdb.settlements.save(self.settlement)
        self.logger.info("[%s] auto-incremented settlement %s population by %s" % (self.User, self, amount))


    def get_story_events(self, return_type="handles"):
        """ Returns a list of the settlement's story events (as strings). Checks
        the whole timeline and supports old and new style timeline entries. """

        all_story_events = []
        for ly in self.settlement["timeline"]:
            if "story_event" in ly.keys():
                if type(ly["story_event"]) == list:
                    all_story_events.extend(ly["story_event"])
                else:
                    all_story_events.append(ly["story_event"])

        if return_type=="handles":
            output = set()
            for e in all_story_events:
                if "handle" in e.keys():
                    output.add(e["handle"])
            return output

        return all_story_events


    def update_timeline_with_story_events(self):
        """ This runs during Settlement normalization to automatically add story
        events to the Settlement timeline when the threshold for adding the
        event has been reached. """

        updates_made = False

        milestones_dict = self.get_api_asset("game_assets", "milestones_dictionary")

        for m_key in self.get_campaign("dict")["milestones"]:

            m_dict = milestones_dict[m_key]

            event = self.get_event(m_dict["story_event"])

            # first, if the milestone has an 'add_to_timeline' key, create a 
            # string from that key to determine whether we've met the criteria 
            # for adding the story event to the timeline. The string gets an
            # eval below
            add_to_timeline = False
            if "add_to_timeline" in milestones_dict[m_key].keys():
                add_to_timeline = eval(milestones_dict[m_key]["add_to_timeline"])

            # now, here's our real logic
            condition_met = False
            if m_key in self.settlement["milestone_story_events"]:
                condition_met = True
            elif add_to_timeline:
                condition_met = True


            # final evaluation:
            if condition_met and event["handle"] not in self.get_story_events("handles"):
                self.logger.debug("[%s] automatically adding %s story event to LY %s" % (self.User, event["name"], self.get_ly()))
                event.update({"ly": self.get_ly(),})
                self.add_timeline_event(event)
                self.log_event('Automatically added <b><font class="kdm_font">g</font> %s</b> to LY %s.' % (event["name"], self.get_ly()))
                updates_made = True

        return updates_made






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




    def get_genealogy(self, return_type=False):
        """ Creates a dictionary of the settlement's various clans. """

        # helper func to render survivors as html spans
        def survivor_to_span(S, display="inline"):
            """ Turns a survivor into an HTML span for genealogy use. """
            span = ""
            class_color = "green_text"
            born = ""
            if "born_in_ly" in S.survivor.keys():
                born = "- born in LY %s" % S.survivor["born_in_ly"]
            dead = ""
            if "dead" in S.survivor.keys():
                class_color = "maroon_text"
                dead = "- died"
                if "died_in" in S.survivor.keys():
                    dead = "- died in LY %s" % S.survivor["died_in"]

            span += html.settlement.genealogy_survivor_span.safe_substitute(
                name=S.get_name_and_id(include_sex=True, include_id=False),
                dead = dead,
                born = born,
                class_color=class_color,
                display=display,
            )
            return span

        # now, start the insanity:
        genealogy = {"has_no_parents": set(), "is_a_parent": set(), "has_no_children": set(), "no_family": set(), "founders": set(), "parent_pairs": set(), "tree": [], "has_parents": set(),}

        survivors = list(self.get_survivors())

        # determine who has no parents
        for s in survivors:
            if not "father" in s.keys() and not "mother" in s.keys():
                genealogy["has_no_parents"].add(s["_id"])
            else:
                genealogy["has_parents"].add(s["_id"])

        # determine who IS a parent
        for s in survivors:
            for parent in ["father","mother"]:
                if parent in s.keys():
                    genealogy["is_a_parent"].add(s[parent])

        # ...and use that to figure out who is NOT a parent
        for s in survivors:
            if s["_id"] not in genealogy["is_a_parent"]:
                genealogy["has_no_children"].add(s["_id"])

        # ...and then create our list of no family survivors
        for s in survivors:
            if s["_id"] in genealogy["has_no_parents"] and s["_id"] in genealogy["has_no_children"]:
                genealogy["no_family"].add(s["_id"])

        # ...and finally determine who the settlement founders are
        for s in survivors:
            if s["_id"] in genealogy["has_no_parents"] and s["born_in_ly"] in [0,1]:
                genealogy["founders"].add(s["_id"])

        # create a set of parent "pairs"; also include single parents, in case
        #   anyone's been a clever dick (looking at you, Kendal)
        for s in survivors:
            if "father" in s.keys() and "mother" in s.keys():
                genealogy["parent_pairs"].add((s["father"], s["mother"]))
            if "father" in s.keys() and "mother" not in s.keys():
                genealogy["parent_pairs"].add((s["father"]))
            if "mother" in s.keys() and "father" not in s.keys():
                genealogy["parent_pairs"].add((s["mother"]))

        generation = 0
        generations = {}
        for s in genealogy["founders"]:
#            self.logger.debug("%s is a founder." % s)
            generations[s] = 0

        everyone = list(self.get_survivors("chronological_order").sort("created_on",-1))
        loops = 0
        while everyone != []:
            for s in everyone:
                if s["_id"] in generations.keys():
                    everyone.remove(s)
                elif s["_id"] in genealogy["founders"]:
                    everyone.remove(s)
                elif s["_id"] in genealogy["no_family"]:
                    everyone.remove(s)
                elif "father" in s.keys() and s["father"] in generations.keys():
                    generations[s["_id"]] = generations[s["father"]] + 1
                elif "mother" in s.keys() and s["mother"] in generations.keys():
                    generations[s["_id"]] = generations[s["mother"]] + 1
                # and now we start the wild and wolly batshit insanity for
                # handling incomplete records and single parents
                elif s["_id"] in genealogy["is_a_parent"]:
                    for parent_pair in genealogy["parent_pairs"]:
                        if type(parent_pair) == tuple and s["_id"] in parent_pair:
#                            self.logger.debug("%s belongs to parent pair %s" % (s["name"], parent_pair))
                            for partner in parent_pair:
                                if partner in generations.keys():
                                    generations[s["_id"]] = generations[partner]
                    S = Survivor(survivor_id=s["_id"], session_object=self.Session)
                    for child in S.get_children():
                        if child["_id"] in generations.keys():
                            generations[s["_id"]] = generations[child["_id"]] + 1
                else:
                    if loops >= 5:
                        pass
                        self.logger.debug("Unable to determine generation for %s after %s loops." % (s["name"], loops))
            loops += 1
            if loops == 10:
                self.logger.error("Settlement %s hit %s loops while calculating generations!" % (self.get_name_and_id(), loops))
                self.logger.debug(generations)
                for survivor in everyone:
                    self.logger.error("Could not determine generation for '%s' -> %s" % (survivor["name"], survivor["_id"]))
                    genealogy["no_family"].add(survivor["_id"])

        # now, finally, start creating representations of the genealogy
        genealogy["tree"] = ""
        genealogy["summary"] = ""
        for generation in sorted(list(set(generations.values())))[:-1]:
            genealogy["summary"] += '<h4>Generation %s</h4>' % generation
            generators = set()
            for s, s_gen in generations.iteritems():
                if s_gen == generation:
                    for parent_pair in genealogy["parent_pairs"]:
                        if type(parent_pair) == tuple and s in parent_pair:
                            generators.add(parent_pair)
            for parent_pair in generators:
                try:
                    parent_pair_list = [Survivor(survivor_id=p, session_object=self.Session).get_name_and_id(include_id=False, include_sex=True) for p in parent_pair]
                except TypeError:
                    parent_pair_list = [Survivor(survivor_id=p, session_object=self.Session).get_name_and_id(include_id=False, include_sex=True)]
                parent_pair_string = " and ".join(parent_pair_list)
                children = []
                for s in genealogy["has_parents"]:
                    if generations[s] == generation + 1:
                        S = Survivor(survivor_id=s, session_object=self.Session)
                        parent_tuple = None
                        if "father" in S.survivor.keys() and "mother" in S.survivor.keys():
                            parent_tuple = (S.survivor["father"], S.survivor["mother"])
                        if "father" in S.survivor.keys() and "mother" not in S.survivor.keys():
                            parent_tuple = (S.survivor["father"])
                        if "father" not in S.survivor.keys() and "mother" in S.survivor.keys():
                            parent_tuple = (S.survivor["mother"])
                        if parent_tuple == parent_pair:
                            children.append(S)

                def generation_html(children_list, recursion=False):
                    """ Helper that makes ul's of survivors. """
                    output = '<ul>\n'
                    if children_list == []:
                        return ""
                    for child in children_list:
                        grand_children = [Survivor(survivor_id=c["_id"], session_object=self.Session) for c in child.get_children()]
                        if not recursion:
                            gc_html = ""
                        else:
                            gc_html = generation_html(grand_children, recursion=recursion)
                        output += '\n\t<a><li>%s</li></a>\n' % survivor_to_span(child)
                    output += '</ul>\n'
                    return output

                if children != []:
                    genealogy["tree"] += '\t<div class="tree desktop_only">\n<ul><li><a>%s</a>\n\t\t' % parent_pair_string
                    genealogy["tree"] += generation_html(children)
                    genealogy["tree"] += '\n\t</li>\n</ul></div><!-- tree -->\n'
                    genealogy["summary"] += '<p>&ensp; %s gave birth to:</p>' % parent_pair_string
                    genealogy["summary"] += "<p>%s</p>" % generation_html(children, recursion=False)

            genealogy["summary"] += "<hr/>"
            genealogy["tree"] += '<hr class="desktop_only"/>'




        if return_type == "html_no_family":
            output = html.settlement.genealogy_headline.safe_substitute(value="Founders")
            sorted_survivor_list = mdb.survivors.find({"_id": {"$in": list(genealogy["founders"])}}).sort("created_on")
            for s in sorted_survivor_list:
                S = Survivor(survivor_id=s["_id"], session_object=self.Session)
                output += survivor_to_span(S, display="block")
            output += html.settlement.genealogy_headline.safe_substitute(value="Undetermined Lineage")
            sorted_survivor_list = mdb.survivors.find({"_id": {"$in": list(genealogy["no_family"])}}).sort("created_on")
            return output
        if return_type == "html_tree":
            return genealogy["tree"]
        if return_type == "html_generations":
            return genealogy["summary"]

        return genealogy



    def get_storage(self, return_type=False):
        """ Returns the settlement's storage in a number of ways. """

        # first, normalize storage to try to fix case-sensitivity PEBKAC
        normalization_exceptions = [key_tuple[1] for key_tuple in game_assets.item_normalization_exceptions]
        storage = []
        for i in self.settlement["storage"]:
            if i in normalization_exceptions:
                storage.append(i)
            else:
                storage.append(capwords(i))
        self.settlement["storage"] = storage
        mdb.settlements.save(self.settlement)

        if self.settlement["storage"] == []:
            return ""

        # Now handle our normalization exceptions, so they don't get mix-cased
        # incorrectly/automatically
        for normalization_exception in game_assets.item_normalization_exceptions:
            broken, fixed = normalization_exception
            if broken in storage:
                broken_items = storage.count(broken)
                for i in range(broken_items):
                    storage.remove(broken)
                    storage.append(fixed)
                self.logger.debug("[%s] Re-normalized '%s' to '%s' (%s times)" % (self, broken, fixed, broken_items))
                self.save()

        if return_type == "html_buttons":
            custom_items = {}
            gear = {}
            resources = {}

            def add_to_gear_dict(item_key):
                item_dict = Items.get_asset(item_key)
                item_location = item_dict["location"]

                font_color = "000"
                if item_location in Resources.get_keys():
                    item_color = Resources.get_asset(item_location)["color"]
                    if "font_color" in Resources.get_asset(item_location):
                        font_color = Resources.get_asset(item_location)["font_color"]
                    target_item_dict = resources
                elif item_location in Locations.get_keys():
                    target_item_dict = gear
                    item_color = Locations.get_asset(item_location)["color"]
                    if "font_color" in Locations.get_asset(item_location):
                        font_color = Locations.get_asset(item_location)["font_color"]

                if "type" in item_dict.keys():
                    if item_dict["type"] == "gear":
                        target_item_dict = gear
                    else:
                        target_item_dict = resources
                if not item_dict["location"] in target_item_dict.keys():
                    target_item_dict[item_location] = {}
                if not item_key in target_item_dict[item_location].keys():
                    target_item_dict[item_location][item_key] = {"count": 1, "color": item_color, "font_color": font_color}
                else:
                    target_item_dict[item_location][item_key]["count"] += 1

            for item_key in storage:
                if item_key in Items.get_keys():
                    add_to_gear_dict(item_key)
                else:
                    if not item_key in custom_items.keys():
                        custom_items[item_key] = 1
                    else:
                        custom_items[item_key] += 1

            output = '<hr class="invisible"/>\n\t<p>\nClick or tap an item to remove it once:\n\t</p>\n<hr />'
            for item_dict in [gear, resources]:
                for location in sorted(item_dict.keys()):
                    for item_key in sorted(item_dict[location].keys()):
                        quantity = item_dict[location][item_key]["count"]
                        color = item_dict[location][item_key]["color"]
                        font_color = item_dict[location][item_key]["font_color"]
                        suffix = ""
                        if item_key in Items.get_keys() and "resource_family" in Items.get_asset(item_key):
                            suffix = " <sup>%s</sup>" % "/".join([c[0].upper() for c in sorted(Items.get_asset(item_key)["resource_family"])])
                        if quantity > 1:
                            pretty_text = "%s %s x %s" % (item_key, suffix, quantity)
                        else:
                            pretty_text = item_key + suffix

                        # check preferences and include a pop-up if the user
                        #   prefers to be warned
                        confirmation_pop_up = ""
                        if self.User.get_preference("confirm_on_remove_from_storage"):
                            confirmation_pop_up = html.settlement.storage_warning.safe_substitute(item_name=item_key)

                        output += html.settlement.storage_remove_button.safe_substitute(
                            confirmation = confirmation_pop_up,
                            item_key = item_key,
                            item_font_color = font_color,
                            item_color = color,
                            item_key_and_count = pretty_text
                        )
                    output += "<div class='item_rack'>"
                    output += '</div><!-- item_rack -->'
                    output += html.settlement.storage_tag.safe_substitute(name=location, color=color)
            if custom_items != {}:
                for item_key in custom_items.keys():
                    color = "FFAF0A"
                    if custom_items[item_key] > 1:
                        pretty_text = "%s x %s" % (item_key, custom_items[item_key])
                    else:
                        pretty_text = item_key
                    output += html.settlement.storage_remove_button.safe_substitute( item_key = item_key, item_color = color, item_key_and_count = pretty_text)
                output += html.settlement.storage_tag.safe_substitute(name="Custom Items", color=color)

            resource_pool = {"hide": 0, "scrap": 0, "bone": 0, "organ": 0}
            pool_is_empty = True
            for item_key in storage:
                if item_key in Items.get_keys() and "resource_family" in Items.get_asset(item_key).keys():
                    item_dict = Items.get_asset(item_key)
                    for resource_key in item_dict["resource_family"]:
                        resource_pool[resource_key] += 1
                        pool_is_empty = False
            if not pool_is_empty:
                output += html.settlement.storage_resource_pool.safe_substitute(
                    hide = resource_pool["hide"],
                    bone = resource_pool["bone"],
                    scrap = resource_pool["scrap"],
                    organ =resource_pool["organ"],
                )

            return output


        if return_type == "comma-delimited":
            return "<p>%s</p>" % ", ".join(storage)

        return storage



    def get_timeline_events(self, ly=None, event_type=None):
        """ Returns the timeline events for the specified year. Defaults to the
        current LY if the 'ly' kwarg is None. """

        if ly is None:
            ly = self.get_ly()

        target_year = {}
        for year_dict in self.settlement["timeline"]:
            if year_dict["year"] == ly:
                target_year = year_dict

        if event_type is not None:
            if event_type not in target_year.keys():
                target_year[event_type] = []
            return target_year[event_type]
        else:
            return target_year



    def get_principles(self, return_type=None, query=None):
        """ Returns the settlement's principles. Use the 'return_type' arg to
        specify one of the following, or leave it unspecified to get a sorted
        list back:

            'comma-delimited': a comma-delimited list wrapped in <p> tags.
            'checked': use this with kwarg 'query' to return an empty string if
                if the principle is not present or the string 'checked' if it is
            'html_select_remove': html controls that allow users to remove an
                item from the settlement principles list.
            'html_controls': html controls for the Settlement Sheet that use
                radio buttons and evaluate campaign logic/attribute rules.

        """

        principles = sorted(self.settlement["principles"])

        if return_type in ["list"]:
            if principles == []:
                return ""
            else:
                output = '\n\n<ul>\n'
                for p in principles:
                    output += "<li>%s</li>\n" % p
                output += "\n</ul>\n\n"
                return output
        elif return_type == "checked" and query is not None:
            if query in self.settlement["principles"]:
                return "checked"
            else:
                return ""
        elif return_type in ["html_select_remove","json"]:
            msg = "The 'return_type' value '%s' is no longer supported by this method!" % return_type
            self.logger.error(msg)
            raise AttributeError(msg)

        return sorted(self.settlement["principles"])


    def get_milestones(self, return_type=None, query=None):
        """ Returns the settlement's milestones as a list. If the 'return_type'
        kwarg is "checked" and the 'query' kwarg is a string, this returns an
        empty string if the 'query' is NOT in the settlement's milestones and
        the string 'checked' if it is present."""

        milestones = self.settlement["milestone_story_events"]

        if return_type in ["html_controls"]:
            msg = "The 'return_type' value '%s' is no longer supported by get_milestones()" % return_type
            self.logger.error(msg)
            raise Exception(msg)

        if return_type == "checked" and query is not None:
            if query in milestones:
                return "checked"
            else:
                return ""

        return milestones




    def get_endeavors(self, return_type=False):
        """ Returns available endeavors. This used to be in 'get_bonuses()', but
        it's such an insane coke-fest of business logic, it got promoted into
        it's own method. """


        innovation_names_list = copy(self.get_game_asset("innovations", update_mins=False, handles_to_names=True))
        location_names_list = copy(self.get_game_asset("locations", update_mins=False, handles_to_names=True))

        # this is a list of locations and innovations together that will be used
        #  later to determine if the settlement meets the requirements for an
        #  endeavor
        prereq_assets = innovation_names_list
        prereq_assets.extend(location_names_list)

        # now create our list of all possible sources: any game asset with an
        #  an endeavor should be in this
        sources = copy(self.get_game_asset("innovations", update_mins=False, handles_to_names=True))
        sources = copy(self.get_game_asset("locations", update_mins=False, handles_to_names=True))
        sources.extend(self.settlement["principles"])
        sources.extend(self.settlement["storage"])

        buffs = {}
        for source_key in sources:
            if source_key in Innovations.get_keys() and "endeavors" in Innovations.get_asset(source_key).keys():
                buffs[source_key] = Innovations.get_asset(source_key)["endeavors"]
            elif source_key in Locations.get_keys() and "endeavors" in Locations.get_asset(source_key).keys():
                buffs[source_key] = Locations.get_asset(source_key)["endeavors"]
            elif source_key in Items.get_keys() and "endeavors" in Items.get_asset(source_key).keys():
                buffs[source_key] = Items.get_asset(source_key)["endeavors"]

        # fucking bloom people
        if "endeavors" in self.get_campaign("dict"):
            buffs[self.get_campaign("name")] = self.get_campaign("dict")["endeavors"]

        if return_type == "html":
            output = ""
            for k in sorted(buffs.keys()):          # e.g. [u'Lantern Hoard', u'Cooking', u'Drums', u'Bloodletting']
                endeavor_string = ""
                for endeavor_key in sorted(buffs[k].keys()):
                    requirements_met = True             # endeavor_key is 'Bone Beats'
                    e = buffs[k][endeavor_key]         # e is {'cost': 1, 'type': 'music'}
                    if "requires" in e.keys():
                        for req in e["requires"]:
                            if req not in prereq_assets:
                                requirements_met = False

                    if "remove_after" in e.keys() and e["remove_after"] in prereq_assets:
                        requirements_met = False

                    if requirements_met:
                        e_type = ""
                        e_desc = ""

                        if "desc" in e.keys():
                            e_desc = "%s" % e["desc"]
                        if "type" in e.keys():
                            e_type = "(%s)" % e["type"]

                        e_name = "<i>%s</i>" % endeavor_key
                        if "hide_name" in e.keys():
                            e_name = ""

                        punc = ""
                        if e_desc != "" and not "hide_name" in e.keys():
                            punc = ": "

                        bg = ""
                        fg = ""

                        p_class = ""

                        if endeavor_key.strip() == "Build":
                            p_class = "available_endeavors_build"
                        elif endeavor_key.strip() == "Special Innovate":
                            p_class = "available_endeavors_special_innovate"

                        endeavor_string += html.settlement.endeavor.safe_substitute(
                            p_class = p_class,
                            cost = '<font class="kdm_font">%s</font>' % (e["cost"]*"d "),
                            name = e_name,
                            punc = punc,
                            desc = e_desc,
                            type = e_type,
                        )

                if endeavor_string == "":
                    pass
                else:
                    sub = ""
                    show = False
                    if k in Innovations.get_keys() and "subhead" in Innovations.get_asset(k):
                        sub = Innovations.get_asset(k)["subhead"]
                        show = True
                    output += html.settlement.innovation_heading.safe_substitute(
                        name = k,
                        show_subhead = show,
                        subhead = sub,
                    )
                    output += endeavor_string
            return output

        return buffs


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
            hunting_party = []
            for survivor in survivors:
                if survivor.get("in_hunting_party", None) == "checked":
                    hunting_party.append(survivor)
            return hunting_party


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

        if return_type == "html_campaign_summary":
            # this is our big boy, full-featured controls for survivor management
            if survivors.count() == 0:
                return html.survivor.no_survivors_error

            groups = {
                1: {"name": "Departing", "survivors": [], },
                2: {"name": "Favorite", "survivors": [], },
                3: {"name": "Available", "survivors": [], },
                4: {"name": "Skipping Next Hunt", "survivors": [], },
                5: {"name": "Retired", "survivors": [], },
                6: {"name": "The Dead", "survivors": [], },
            }

            anonymous = []
            available = []
            for survivor in survivors:

                S = Survivor(survivor_id=survivor["_id"], session_object=self.Session)
                annotation = ""
                user_owns_survivor = False
                disabled = "disabled"

                if survivor["email"] == user_login or current_user_is_settlement_creator or survivor.get("public", False) is not False:
                    disabled = ""
                    user_owns_survivor = True

                button_class = ""
                if user_owns_survivor:
                    button_class = "survivor_sheet_gradient touch_me"

                if "skip_next_hunt" in S.survivor.keys():
                    annotation += "&ensp; <i>Skipping next hunt</i><br/>"
                    button_class = "tan"

                for t in [("retired", "retired_in", "tan"),("dead", "died_in", "silver")]:
                    attrib, event, color = t
                    if attrib in S.survivor.keys():
                        if event in S.survivor.keys():
                            annotation += "&ensp; <i>%s LY %s</i><br/>" % (event.replace("_"," ").capitalize(), S.survivor[event])
                        else:
                            annotation += "&ensp; <i>%s</i><br/>" % attrib.title()
                        button_class = color


                s_id = S.survivor["_id"]
                if not user_owns_survivor:
                    s_id = None


                can_hunt = ""
                if "dead" in S.survivor.keys() or "retired" in S.survivor.keys() or "skip_next_hunt" in S.survivor.keys():
                    can_hunt = "disabled"

                in_hunting_party = "checked"
#                if "in_hunting_party" in S.survivor.keys():
                if S.survivor.get("in_hunting_party", None):
                    in_hunting_party = None
                    can_hunt = ""

                is_favorite = "hidden"
                if "favorite" in S.survivor.keys():
                    is_favorite = "favorite"

                avatar_img = ""
                if "avatar" in S.survivor.keys():
                    avatar_img = S.get_avatar("html_campaign_summary")

                survivor_html = html.survivor.campaign_asset.safe_substitute(
                    avatar = avatar_img,
                    sex = S.get_api_asset("effective_sex"),
                    survivor_id = s_id,
                    settlement_id = self.settlement["_id"],
                    hunting_party_checked = in_hunting_party,
                    settlement_name = self.settlement["name"],
                    b_class = button_class,
                    able_to_hunt = can_hunt,
                    returning = S.get_returning_survivor_status("html_badge"),
                    constellation = S.get_constellation("html_badge"),
                    special_annotation = annotation,
                    disabled = disabled,
                    name = S.survivor["name"],
                    favorite = is_favorite,
                    hunt_xp = S.survivor["hunt_xp"],
                    survival = S.survivor["survival"],
                    insanity = S.survivor["Insanity"],
                    courage = S.survivor["Courage"],
                    understanding = S.survivor["Understanding"],
                )

                # finally, file our newly minted survivor in a group:
#                if "in_hunting_party" in S.survivor.keys():
                if S.survivor.get("in_hunting_party", None) == "checked":
                    groups[1]["survivors"].append(survivor_html)
                elif "dead" in S.survivor.keys():
                    groups[6]["survivors"].append(survivor_html)
                elif "retired" in S.survivor.keys():
                    groups[5]["survivors"].append(survivor_html)
                elif "skip_next_hunt" in S.survivor.keys():
                    groups[4]["survivors"].append(survivor_html)
                elif "favorite" in S.survivor.keys():
                    groups[2]["survivors"].append(survivor_html)
                else:
                    if S.survivor["name"] == "Anonymous":
                        anonymous.append(survivor_html)
                    else:
                        available.append(survivor_html)

            # build the "available" group
            groups[3]["survivors"].extend(available)
            groups[3]["survivors"].extend(anonymous)

            #
            #   Start assembling HTML here
            #
            output = html.settlement.campaign_summary_survivors_top

            for g in sorted(groups.keys()):
                group = groups[g]


                if group["name"] in ["The Dead", "Retired"]:
                    color = None
                    if group["name"] == "The Dead":
                        color = "grey"
                    elif group["name"] == "Retired":
                        color = "tan"
                    the_dead = "\n".join(group["survivors"])
                    g = group["name"].replace(" ","").lower() + "BlockGroup"
                    output += html.survivor.campaign_summary_hide_show.safe_substitute(color=color, group_id=g, heading=group["name"], death_count = len(group["survivors"]), dead_survivors=the_dead)
                else:
                    output += "<h4>%s (%s)</h4>\n" % (group["name"], len(group["survivors"]))


                    for s in group["survivors"]:
                        output += "  %s\n" % s


                if group["name"] == "Departing" and group["survivors"] == []:
                    output += "<p>Use [::] to add survivors to the Departing group.</p>"


            return output + html.settlement.campaign_summary_survivors_bot

        if return_type == "chronological_order":
            return mdb.survivors.find(query).sort("created_on")

        # finally, capture and scream bloody murder about deprecated return_types
        if return_type in ["angularjs", "JSON"]:
            raise Exception("Return type '%s' no longer supported by this method!" % return_type)

        return survivors


    def get_departing_survivors(self):
        """ Returns a list of survivors who are currently departing. """

        departing=set()

        for s in self.get_survivors():
            if s.get("in_hunting_party", None) == "checked":
                departing.add(s["_id"])

        return list(departing)


    def return_departing_survivors(self, aftermath="victory"):
        """ Processes departing survivors, returning them from the hunt. Specify
        'aftermath' as either 'victory' or 'defeat' to update the departing
        survivors and settlement according. Log everything. """


        healed_survivors = 0
        returning_survivor_id_list = []
        returning_survivor_name_list = []


        # operations for either type of aftermath

        if "hunt_started" in self.settlement.keys():
            del self.settlement["hunt_started"]

        quarry_key = None
        if "current_quarry" in self.settlement.keys() and self.settlement["current_quarry"] is not None:
            quarry_key = self.settlement["current_quarry"]
            self.settlement["current_quarry"] = None


        for survivor in self.get_survivors("hunting_party"):
            S = Survivor(survivor_id=survivor["_id"], session_object=self.Session)
            returning_survivor_id_list.append(S.survivor["_id"])

            if "dead" not in S.survivor.keys():
                returning_survivor_name_list.append(S.survivor["name"])

            if aftermath == "victory":
                S.heal("Return from Hunt")
            elif aftermath == "defeat":
                S.heal("defeated", heal_armor=True, increment_hunt_xp=False, remove_attribute_detail=True, return_to_settlement=True)

            healed_survivors += 1

            # Check for disorders with an "on_return" effect
            for d in S.survivor["disorders"]:
                if d in Disorders.get_keys() and "on_return" in Disorders.get_asset(d):
                    for k, v in Disorders.get_asset(d)["on_return"].iteritems():
                        S.survivor[k] = v

            # save the survivor last
            S.save()


        # remove "skip_next_hunt" from anyone who has it but didn't return
        for survivor in self.get_survivors(exclude=returning_survivor_id_list, exclude_dead=False):
            if "skip_next_hunt" in survivor.keys():
                del survivor["skip_next_hunt"]
                mdb.survivors.save(survivor)


        #
        #   victory!
        #

        if aftermath == "victory":

            if quarry_key not in ["None",None]:
                response = api.post_JSON_to_route("/settlement/add_defeated_monster/%s" % self.settlement["_id"], {'monster': quarry_key}, Session=self.Session)
                if response.status_code == 200:
                    self.logger.debug("[%s] added '%s' kill via API POST!" % (quarry_key, self.User))
                    self.refresh_from_API("defeated_monsters")
                else:
                    self.logger.error("[%s] failed to POST kill '%s' to API!" % (self.User, quarry_key))
                    self.logger.error("%s: %s" % (response.status_code, response.reason))

            if quarry_key not in self.get_timeline_events(event_type="showdown_event"):
                e = {
                    "ly": self.get_ly(),
                    "type": "showdown_event",
                    "name": quarry_key,
                }
                self.add_timeline_event(e)
            else:
                self.logger.debug("[%s] monster '%s' already in timeline for this year: %s. Skipping timeline update..." % (self, quarry_key, self.get_timeline_events(event_type="showdown_event")))

        if len(returning_survivor_name_list) > 0:
            if self.settlement["endeavor_tokens"] == 0:
                self.settlement["endeavor_tokens"] += len(returning_survivor_name_list)
                self.log_event("Automatically set endeavor tokens to %s" % len(returning_survivor_name_list))
                self.logger.debug("[%s] automatically applied endeavor tokens for %s returning survivors" % (self.User, len(returning_survivor_name_list)))

        returners = ", ".join(returning_survivor_name_list)
        self.log_event("Departing Survivors (%s) have returned in %s!" % (returners, aftermath))



    def modify_departing_survivors(self, params=None):
        """ Modifies all hunters in the settlement's departing survivors group
        according to cgi.FieldStorage() params. """

        target_attrib = params["hunting_party_operation"].value
        target_action = params["operation"].value

        for s in self.get_survivors("hunting_party", exclude_dead=True):
            S = Survivor(survivor_id=s["_id"], session_object=self.Session)
            if target_action == "increment" and target_attrib == "Brain Event Damage":
                S.brain_damage()
            elif target_action == "increment":
                S.survivor[target_attrib] = int(s[target_attrib]) + 1
            elif target_action == "decrement":
                S.survivor[target_attrib] = int(s[target_attrib]) - 1
            self.logger.debug("[%s] %sed %s %s by 1" % (self.User, target_action, S, target_attrib))

            # enforce settlement survival limit/min
            if target_attrib == "survival":
                if S.survivor[target_attrib] > int(self.settlement["survival_limit"]):
                    S.survivor[target_attrib] = self.settlement["survival_limit"]

            # enforce a minimum of zero for all attribs
            if target_attrib != "Brain Event Damage" and S.survivor[target_attrib] < 0:
                S.survivor[target_attrib] = 0

            S.save()

        self.logger.debug("[%s] completed Departing Survivors management operation." % (self.User))
        self.log_event("%s %sed Departing Survivors %s" % (self.User.user["login"], target_action, target_attrib))


    def get_recently_added_items(self):
        """ Returns the three items most recently appended to storage. """
        max_items = 10
        all_items = copy(self.settlement["storage"])
        return_list = set()
        while len(return_list) < max_items:
            if all_items == []:
                break
            return_list.add(all_items.pop())
        return sorted(list([i for i in return_list]))


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


    def add_timeline_event(self, event = {}):
        """ Interim/migration support method for V1. Wraps up an event into an
        API-safe dict and then uses the api.py module to POST it to the API. """

        if event in self.get_timeline_events(ly=event["ly"],event_type=event["type"]):
            self.logger.warn("[%s] attempting to add a duplicate event to %s timeline!" % (self.User, self))
            self.logger.error("[%s] duplicate event was: %s" % (self.User, event) )
            return False

        event["user_login"] = self.User.user["login"]
        response = api.post_JSON_to_route("/settlement/add_timeline_event/%s" % self.settlement["_id"], event, Session=self.Session)
        if response.status_code == 200:
            self.logger.debug("[%s] added '%s' to %s timeline via POST to API" % (self.User, event["name"], self))
        else:
            self.logger.error("[%s] failed to POST '%s' to %s timeline!" % (self.User, event["name"], self))
            self.logger.error(response)
        self.refresh_from_API("timeline") # gotta pull the updated timeline back



    def rm_timeline_event(self, event = {}):
        """ Interim/migration support method for V1. Wraps up an event into an
        API-safe dict and then uses the api.py module to POST it to the API's
        route for removing timeline events. Logs it. """

        event["user_login"] = self.User.user["login"]
        response = api.post_JSON_to_route("/settlement/rm_timeline_event/%s" % self.settlement["_id"], event, Session=self.Session)
        if response.status_code == 200:
            self.logger.debug("[%s] removed '%s' from %s timeline via API" % (self.User, event["name"], self))
        else:
            self.logger.error("[%s] failed to remove '%s' from %s timeline!" % (self.User, event["name"], self))
            self.logger.error(response)
        self.refresh_from_API("timeline") # gotta pull the updated timeline back


    def get_admins(self):
        """ Creates an admins list if one doesn't exist; adds the settlement
        creator to it if it's new; returns the list. """

        if not "admins" in self.settlement.keys():
            self.settlement["admins"] = []

        creator = mdb.users.find_one({"_id": self.settlement["created_by"]})
        if creator is not None and self.settlement["admins"] == []:
            self.settlement["admins"].append(creator["login"])

        return self.settlement["admins"]


    def toggle_admin_status(self, login):
        """ Adds or removes a login from self.settlement["admins"], depending
        on whether it's already there or not. """

        if login in self.settlement["admins"]:
            self.settlement["admins"].remove(login)
            msg = "removed %s from" % login
        else:
            self.settlement["admins"].append(login)
            msg = "added %s to" % login

        self.logger.debug("[%s] %s %s admins." % (self.User, msg, self))



    def update_current_survivors(self, buff_dict, reason, rm_buff=False):
        """ Updates all current survivors with the keys in 'buff_dict'. Uses
        'reason' to log a settlement event. """

        operation = "add"

        successful_updates = 0
        for s in self.get_survivors(exclude_dead=True):
            for k,v in buff_dict.iteritems():
                if rm_buff:
                    v = -v
                    operation = 'remove'
                s[k] = int(s[k]) + v
                self.log_event("%s [%s] -> '%s' + %s (%s %s bonus) " % (s["name"], s["sex"], k, v, operation, reason))
            mdb.survivors.save(s)
            successful_updates += 1
        self.logger.debug("[%s] Automatically updated %s survivors!" % (self.User, successful_updates))


        if election != "UNSET":
            election = principle["options"][election]
            if election["name"] in self.settlement["principles"]:
                self.logger.warn("[%s] attempting to set principle that is already set!" % self.User)
                return None


    def update_milestones(self, m):
        """ Expects checkbox input. """

        if m not in self.settlement["milestone_story_events"]:
            self.settlement["milestone_story_events"].append(m)
            self.log_event("'%s' milestone added to settlement milestones." % m)
            self.logger.debug("[%s] added '%s' to milestone story events for %s." % (self.User, m, self))
        elif m in self.settlement["milestone_story_events"]:
            self.settlement["milestone_story_events"].remove(m)
            self.log_event("'%s' milestone removed from settlement milestones." % m)
            self.logger.debug("[%s] removed '%s' from milestone story events for %s." % (self.User, m, self))



    def update_settlement_name(self, new_name):
        """ Updates the settlement's name. Logs an event if it does. """
        if new_name != self.settlement["name"]:
            old_name = self.settlement["name"]
            self.settlement["name"] = new_name
            
            self.logger.debug("%s updated settlement name: '%s' is now '%s'." % (self.User, old_name, new_name))
            self.log_event("'%s' is now known as '%s'." % (old_name, new_name))
        else:
            pass


    def remove_item_from_storage(self, quantity=1, item_name=None):
        """ Removes an item from storage by name or handle 'quantity' number of
        times. Logs it. """

        # normalize/duck-type
        quantity = int(quantity)

        # try to remove 'quantity' items. fail gracefully if you can't.
        if item_name is not None:
            self.logger.debug("[%s] is removing '%s' from %s settlement storage..." % (self.User, item_name, self))
            rm_candidates = []
            for i in self.settlement["storage"]:
                if i.upper() == item_name.upper():
                    rm_candidates.append(i)
            if rm_candidates == []:
                self.logger.error("[%s] attempted to remove '%s' from settlement storage, but no items matching that name could be found!" % (self.User, item_name))
            else:
                for i in range(quantity):
                    self.settlement["storage"].remove(rm_candidates[0])
                self.log_event("%s removed %s '%s' item(s) from settlement storage." % (self.User.user["login"], quantity, item_name))
                self.logger.debug("[%s] removed %s '%s' item(s) from settlement storage." % (self.User, quantity, item_name))



    def add_item_to_storage(self, quantity=1, item_name=None):
        """ Adds 'quantity' of an item (by name or handle) to settlement
        storage using the self.add_game_asset method, which has nice logging and
        normalization.

        We might end up moving that normalization here, as this
        one gets built out to suppor thandles."""

        self.add_game_asset("storage", item_name, quantity)



    def update_settlement_storage(self, update_from=None, params=None):
        """ Updates settlement storage. Capable of accepting several different
        inputs and doing a few operations at once. """


        if update_from == "html_form" and params is not None:
            if "remove_item" in params:
                self.remove_item_from_storage(1, params["remove_item"].value)
            elif "add_item" in params and "add_item_quantity" in params:
                self.add_item_to_storage(params["add_item_quantity"].value, params["add_item"].value)
            elif "add_item" in params and not "add_item_quantity" in params:
                self.add_item_to_storage(1, params["add_item"].value)
            else:
                self.logger.warn("[%s] submitted un-actionable form input to update_settlement_storage()" % self.User)
                self.logger.debug(params)


    def get_special_rules(self, return_type=None):
        """ Checks locations and returns special rules from locations in the
        settlement. Use "html_campaign_summary" as the 'return_type' to get
        fancy HTML banners. """

        special_rules = []

        # check locations, expansions and the campaign, as each might have a
        # a list of special rules dict items
        for location in self.settlement["locations"]:
            if location in Locations.get_keys() and "special_rules" in Locations.get_asset(location).keys():
                special_rules.extend(Locations.get_asset(location)["special_rules"])
        for expansion in self.get_expansions():
            if "special_rules" in self.get_api_asset("game_assets","expansions")[expansion]:
                special_rules.extend(self.get_api_asset("game_assets","expansions")[expansion]["special_rules"])
        campaign_dict = self.get_campaign("dict")
        if "special_rules" in campaign_dict.keys():
            special_rules.extend(campaign_dict["special_rules"])

        # now do returns
        if return_type == "html_campaign_summary":
            # bail if we've got nothing and return a blank string
            if special_rules == []:
                return ""
            # otherwise, do it:
            output = ""
            for r in special_rules:
                output += html.settlement.special_rule.safe_substitute(
                    name = r["name"],
                    desc = r["desc"],
                    bg_color = r["bg_color"],
                    font_color = r["font_color"],
                )
            return output

        return special_rules


    def get_game_asset_deck(self, asset_type, return_type=None, exclude_always_available=False):
        """ The 'asset_type' kwarg should be 'locations', 'innovations', etc.
        and the class should be one of our classes from models, e.g.
        'Locations', 'Innovations', etc.

        What you get back is going to be a list of available options, i.e. which
        game assets you may add to the settlement based on what they've already
        got.

        Any model in game_assets.py that has "consequences" as a key should be
        compatible with this func.
        """

        if asset_type == "defeated_monsters":
            Asset = DefeatedMonsters
        else:
            exec "Asset = %s" % asset_type.capitalize()

        current_assets = self.settlement[asset_type]


        if exclude_always_available:
            asset_deck = set()
        else:
            asset_deck = Asset.get_always_available(self)

        for asset_key in current_assets:
            if asset_key in Asset.get_keys() and "consequences" in Asset.get_asset(asset_key).keys():
                for c in Asset.get_asset(asset_key)["consequences"]:
                    asset_deck.add(c)

        # check for requirements and remove stuff if we don't have them
        for asset_key in Asset.get_keys():
            asset_dict = Asset.get_asset(asset_key)
            if "requires" in asset_dict.keys():
                requirement_type, requirement_key = asset_dict["requires"]
                if requirement_key in self.settlement[requirement_type]:
                    asset_deck.add(asset_key)

        for asset_key in current_assets:
            if asset_key in asset_deck:
                asset_deck.discard(asset_key)

        # if the Asset model has its own deck-building method, call that and
        #   overwrite whatever we've got so far.
        if hasattr(Asset, "build_asset_deck"):
            asset_deck = Asset.build_asset_deck(self)   # pass the whole settlement obj

        # set the final_list object
        final_list = sorted(list(set(asset_deck)))

        # filter expansion content that's not enabled
        for asset_key in asset_deck:
            if asset_key in Asset.get_keys() and "expansion" in Asset.get_asset(asset_key).keys():
                if "expansions" in self.settlement.keys():
                    if Asset.get_asset(asset_key)["expansion"] not in self.get_expansions("list_of_names"):
                        final_list.remove(asset_key)
                else:   # if we've got no expansions, don't show any expansion stuff
                    final_list.remove(asset_key)

        # filter campaign-forbidden items
        c_dict = self.get_campaign("dict")
        if "forbidden" in c_dict.keys():
            for f in c_dict["forbidden"]:
                if f in final_list:
                    final_list.remove(f)


        if return_type in ["list"]:
            if final_list == []:
                return ""
            else:
                output = '\n<ul class="asset_deck">%s</ul>' % "\n".join(["<li>%s</li>" % i for i in final_list])
                return output

        return final_list


    def get_current_quarry(self, return_type=None):
        """ Returns the settlement's current quarry, if it has one. Otherwise,
        returns a None. """

        current_quarry = None
        if "current_quarry" in self.settlement.keys():
            current_quarry = self.settlement["current_quarry"]

        return current_quarry


    def get_game_asset(self, asset_type=None, return_type=False, exclude=[], update_mins=True, admin=False, handles_to_names=False):
        """ This is the generic method for getting a list of the settlement's
        game assets, e.g. innovations, locations, principles, etc.

        The 'exclude' kwarg lets you put in a list of keys that will not show
        up in ANY OF THE RESULTING OUTPUT. Use it with careful strategery.

        The 'return_type' kwarg is optional. If you leave it unspecified, you
        get back whatever is saved in the mdb, e.g. a list, etc.

        As their names imply, the 'html_add' and 'html_remove' options for
        'return_type' return HTML. If there are game assets to remove from the
        settlement, you'll get an HTML <select> back.

        Both of these return types return an empty string (i.e. "") if the game
        asset is a blank list (i.e. []): this is useful when writing the form,
        because if we've got no options, we display no select element.
        """
        # uncomment these to log which methods are calling
#        curframe = inspect.currentframe()
#        calframe = inspect.getouterframes(curframe, 2)
#        self.logger.debug("get_game_asset() called by %s" % calframe[1][3])

        # first, scream bloody murder if we get a banned return_type value
        if return_type in ["angularjs","json","angularjs_options"]:
            raise ValueError("The get_game_asset() method no longer supports '%s' returns!" % return_type)

        if update_mins:
            self.update_mins()

        if asset_type == "defeated_monsters":   # our pseudo model
            Asset = DefeatedMonsters
        elif asset_type == "nemesis_monsters":
            Asset = NemesisMonsters             # another pseudo model
        else:
            exec "Asset = %s" % asset_type.capitalize() # if asset_type is 'innovations', initialize 'Innovations'

        asset_name = asset_type[:-1]                # if asset_type is 'locations', asset_name is 'location'
        asset_keys = copy(self.settlement[asset_type])

        for asset_key in exclude:                   # process the exclude list
            while asset_key in asset_keys:
                asset_keys.remove(asset_key)

        for asset_key in exclude:                   # this is a double-check
            if asset_key in asset_keys:
                msg = "Asset key '%s' could not be excluded from '%s'!" % (asset_key, asset_type)
                self.logger.error(msg)
                raise Exception(msg)

        # ban any asset keys forbidden by the campaign
        campaign_dict = self.get_campaign("dict")
        if "forbidden" in campaign_dict.keys():
            for asset_key in asset_keys:
                if asset_key in campaign_dict["forbidden"]:
                    asset_keys.remove(asset_key)
            for f in campaign_dict["forbidden"]:
                if f in asset_keys:
                    self.error.log("Forbidden asset '%s' is present in %s after filtering!" % (f, asset_name))

        pretty_asset_name = asset_name.replace("_"," ").title()

        if return_type in ["list"]:
            if hasattr(Asset, "uniquify"):
                asset_keys = list(set(asset_keys))
            if hasattr(Asset, "sort_alpha"):
                asset_keys = sorted(asset_keys)
            if hasattr(Asset, "stack"):
                asset_keys = stack_list(asset_keys)

            return "\n".join(['\t<div class="line_item"><span class="bullet"></span><span class="item">%s</span></div>' % i for i in asset_keys])

        elif return_type in ["html_add"]:
            op = "add"
            output = html.ui.game_asset_select_top.safe_substitute(
                operation="%s_" % op,
                operation_pretty=op.capitalize(),
                name=asset_name,
                name_pretty=pretty_asset_name,
                ng_model="newInnovation",
                ng_change="addInnovation()",
                on_change="",
            )

            deck = self.get_game_asset_deck(asset_type)

            # Special Innovate bullshit here
            if asset_type == "innovations":
                for late_key in Innovations.get_keys():
                    if "special_innovate" in Innovations.get_asset(late_key):
                        special_innovate = Innovations.get_asset(late_key)["special_innovate"]
                        if special_innovate[1] in self.settlement[special_innovate[0]]:
                            if late_key not in deck:
                                deck.append(late_key)

            if return_type == "html_add":
                for asset_key in sorted(deck):
                    output += html.ui.game_asset_select_row.safe_substitute(asset=asset_key)
                output += html.ui.game_asset_select_bot
                return output
            elif return_type == "angularjs_options":
                msg = "JSON and angularjs 'return_type' values are not supported!"
                raise Exception(msg)

        elif return_type in ["html_remove","html_rm"]:
            if asset_keys == []:
                return ""
            op = "remove"
            output = '<span class="empty_bullet rm_bullet"></span>'
            output += html.ui.game_asset_select_top.safe_substitute(
                operation="%s_" % op, operation_pretty=op.capitalize(),
                name=asset_name,
                name_pretty=pretty_asset_name,
            )
            options = self.settlement[asset_type]

            if hasattr(Asset, "sort_alpha"):
                options = sorted(options)

            for asset_key in options:
                output += html.ui.game_asset_select_row.safe_substitute(asset=asset_key)
            output += html.ui.game_asset_select_bot
            return output

        elif return_type == "options":
            return self.get_game_asset_deck(asset_type)

        elif not return_type:
            if handles_to_names:
                name_list = []
                lookup_dict = self.get_api_asset("game_assets",asset_type)
                for a_name in asset_keys:
                    name_list.append(lookup_dict[a_name]["name"])
                asset_keys = name_list
            return sorted(asset_keys)

        else:
            self.logger.error("An error occurred while retrieving settlement game assets ('%s')!" % asset_type)




    def add_game_asset(self, asset_class, game_asset_key=None, game_asset_quantity=1):
        """ Generic function for adding game assets to a settlement.

        The 'asset_class' kwarg needs to be one of the game asset classes from
        models.py, e.g. Innovations, Locations, etc.

        This updates mdb and saves the update. Don't look for any semaphore on
        its returns (because there isn't any).
        """

        # if we don't get a string for some reason, we need to bail gracefully
        if type(game_asset_key) != str:
            self.logger.warn("Could not add asset '%s' (%s) to settlement %s!" % (game_asset_key, type(game_asset_key), self.settlement["_id"]))
            return None

        # otherwise, if we've got a str, let's get busy; handle storage first
        # since its such a big baby, then move on to the other stuff
        if asset_class == "storage":
            game_asset_key = capwords(game_asset_key)

            # un-normalize from capwords for our orthography exceptions
            for normalization_exception in game_assets.item_normalization_exceptions:
                broken, fixed = normalization_exception
                if game_asset_key == broken:
                    game_asset_key = fixed

            for i in range(int(game_asset_quantity)):
                self.settlement[asset_class].append(game_asset_key)

            self.log_event("%s added '%s' x%s to settlement storage." % (self.User.user["login"], game_asset_key, game_asset_quantity))
            self.logger.info("[%s] added '%s' x%s to settlement %s." % (self.User, game_asset_key, game_asset_quantity, self))
            return True

        if asset_class == "nemesis_monsters":
            if game_asset_key in self.settlement["nemesis_monsters"]:
                self.logger.error("[%s] attempting to add '%s' to %s." % (self.User, game_asset_key, self.settlement["nemesis_monsters"]))
                return False
            else:
                self.settlement["nemesis_monsters"].append(game_asset_key)
                self.settlement["nemesis_encounters"][game_asset_key] = []
                M = self.get_api_asset("game_assets","monsters")[game_asset_key]
                self.log_event("%s added %s to settlement nemesis monsters." % (self.User.user["login"], M["name"]))
                self.logger.debug("[%s] added '%s' to %s nemesis monsters." % (self.User, game_asset_key, self))
                return True

        if asset_class == "locations":
            if game_asset_key in self.settlement["locations"]:
                self.logger.error("[%s] attempting to add '%s' to %s." % (self.User, game_asset_key, self.settlement["locations"]))
                return False
            else:
                self.settlement["locations"].append(game_asset_key)
                loc_dict = game_assets.locations[game_asset_key]

                if "levels" in loc_dict.keys():
                    if not "location_levels" in self.settlement.keys():
                        self.settlement["location_levels"] = {}
                    self.settlement["location_levels"][game_asset_key] = 1

                self.log_event("%s added %s to settlement locations." % (self.User.user["login"], game_asset_key))
                self.logger.debug("[%s] added '%s' to %s locations." % (self.User, game_asset_key, self))

                return True

        # done with storage. processing other asset types
        exec "Asset = %s" % asset_class.capitalize()

        self.logger.debug("[%s] is adding '%s' asset '%s' (%s) to settlement %s..." % (self.User, asset_class, game_asset_key, type(game_asset_key), self))

        if hasattr(Asset, "uniquify"):
            current_assets = set([a for a in self.settlement[asset_class] if type(a) in [str, unicode]])
            current_assets.add(game_asset_key)
            current_assets = list(current_assets)
        else:
            current_assets = self.settlement[asset_class]
            current_assets.append(game_asset_key)

        if hasattr(Asset, "sort_alpha"):
            current_assets = sorted(current_assets)

        self.settlement[asset_class] = current_assets
        if game_asset_key in self.settlement[asset_class]:
            self.logger.info("'%s' added '%s' to '%s' ['%s'] successfully!" % (self.User.user["login"], game_asset_key, self.settlement["name"], asset_class))

        self.log_event("%s added to settlement %s!" % (game_asset_key, asset_class.title()))

        mdb.settlements.save(self.settlement)


    def rm_game_asset(self, asset_class, game_asset_key=None):
        """ Generic function for removing game assets from a settlement.
        """

        if game_asset_key not in self.settlement[asset_class]:
            self.logger.error("[%s] attempted to remove non-existent asset '%s' from settlement %s!" % (self.User,game_asset_key,asset_class))
            return False

        self.settlement[asset_class].remove(game_asset_key)
        self.logger.debug("[%s] removed asset '%s' from settlement %s" % (self.User, game_asset_key, self))

        ac_pretty = asset_class.replace("_"," ")
        self.log_event("%s removed '%s' from settlement %s." % (self.User.user["login"], game_asset_key, ac_pretty))

        mdb.settlements.save(self.settlement)


    def modify(self, params):
        """ Pulls a settlement from the mdb, updates it and saves it using a
        cgi.FieldStorage() object.

        All of the business logic lives here.
        """

        ignore_keys = [
            "norefresh", "asset_id", "modify",
            "add_item_quantity", "rm_item_quantity",
            "male_survivors","female_survivors", "bulk_add_survivors",
            "timeline_update_ly","timeline_update_event_type","timeline_update_event_handle",
            "operation", "nemesis_levels"
        ]

        for p in params:

            game_asset_key = None
            if type(params[p]) != list:
                game_asset_key = params[p].value.strip()

#            self.logger.debug("%s -> %s (%s)" % (p, params[p], type(params[p])))


            if p in ignore_keys:
                pass
            elif p == "name":
                self.update_settlement_name(game_asset_key)
            elif p == "toggle_admin_status":
                self.toggle_admin_status(game_asset_key)
            elif p == "toggle_milestone":
                self.update_milestones(game_asset_key)
            elif p in ["add_item","remove_item"]:
                self.update_settlement_storage("html_form", params)
            elif p == "abandon_settlement":
                self.log_event("Settlement abandoned!")
                self.settlement["abandoned"] = datetime.now()
            elif p == "hunting_party_operation":
                self.modify_departing_survivors(params)
            else:
                self.settlement[p] = game_asset_key
                self.logger.debug("%s set '%s' = '%s' for %s" % (self.User.user["login"], p, game_asset_key, self.get_name_and_id()))
        #
        #   settlement post-processing starts here!
        #

        #   auto-add milestones for principles:
        for principle in self.settlement["principles"]:
            p_dict = self.get_api_asset("game_assets", "innovations")[principle]
            if p_dict.get("milestone", None) is not None:
                if p_dict["milestone"] not in self.settlement["milestone_story_events"]:
                    self.settlement["milestone_story_events"].append(p_dict["milestone"])
                    msg = "utomatically marking milestone story event '%s' due to selection of related principle, '%s'." % (principle_dict["milestone"], principle)
                    self.log_event("A%s" % (msg))
                    self.logger.debug("[%s] a%s" % (self.User, msg))

        # update mins will call self.enforce_data_model() and save
        self.update_mins()



    @ua_decorator
    def render_html_summary(self, user_id=False):
        """ Prints the Campaign Summary view. Remember that this isn't really a
        form: the survivor asset tag buttons are a method of assets.Survivor."""

        return html.settlement.summary.safe_substitute(
            settlement_id=self.settlement["_id"],
            population = self.settlement["population"],
            death_count = self.settlement["death_count"],
            sex_count = self.get_survivors(return_type="sex_count", exclude_dead=True),
            lantern_year = self.settlement["lantern_year"],
            survival_limit = self.settlement["survival_limit"],
            endeavors = self.get_endeavors("html"),
            survivors = self.get_survivors(return_type="html_campaign_summary", user_id=user_id),
            special_rules = self.get_special_rules("html_campaign_summary"),

            show_departing_survivors_management_button=self.User.can_manage_departing_survivors(),
            show_endeavor_controls = self.User.get_preference("show_endeavor_token_controls"),

        )


    @ua_decorator
    def render_html_form(self):
        """ Render settlement.form from html.py. Do a few substitutions during
        the render (i.e. things that aren't yet managed by the angularjs app.

        Remember that this passes through @ua_decorator, so it gets some more
        substitutions done up there. """

        # show the settlement rm button if the user prefers
        rm_button = ""
        if self.User.get_preference("show_remove_button"):
            rm_button = html.settlement.remove_settlement_button.safe_substitute(
                settlement_id=self.settlement["_id"],
                settlement_name=self.settlement["name"],
            )

        return html.settlement.form.safe_substitute(

            survival_limit = self.get_attribute("survival_limit"),
            min_survival_limit = self.get_min("survival_limit"),

            storage = self.get_storage("html_buttons"),
            add_to_storage_controls = Items.render_as_html_multiple_dropdowns(
                recently_added=self.get_recently_added_items(),
                expansions=self.get_expansions("list_of_names"),
            ),

            remove_settlement_button = rm_button,

        )



    def render_admin_panel_html(self):
        """ Renders a settlement as admin panel style HTML. This honestly
        probably belongs under a master render method for this class but...
        dang, you know? These render methods are monsters. I really gotta
        abstract further in one of these major refactor revisions..."""

        # write the top line
        output = "\n\n<b>%s</b> LY:%s (%s) - %s/%s<br/>\n" % (
            self.settlement["name"],
            self.settlement["lantern_year"],
            self.settlement["created_on"].strftime(ymd),
            self.settlement["population"],
            self.settlement["death_count"],
            )

        # write the removal info, if any exists
        removal_string = ""
        for removal_key in ["abandoned", "removed"]:
            if removal_key in self.settlement.keys():
                removal_string += '<font class="alert">%s</font> ' % removal_key.upper()
        if removal_string != "":
            removal_string = "&ensp; %s <br/>\n" % removal_string
        output += removal_string

        # now do the rest
        output += "&ensp;<i>%s</i><br/>\n" % self.get_campaign()
        output += "&ensp;Players: %s<br/>\n" % ", ".join(self.get_players())
        output += "&ensp;Expansions: %s\n" % ", ".join(self.get_expansions())

        return output


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
            'dashboard_campaign_list':  gradient_violet links with a summary of
                                        campaign facts.

        Anything else will get you the default, gradient_yellow link with the
        settlement flash and the name.
        """

        if update_mins:
            self.update_mins()  # update settlement mins before we create any text

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
        elif context == "dashboard_campaign_list":
            players = self.get_players()
            if len(players) > 1:
                players = "<br/>Players: %s" % (", ".join(players))
            else:
                players = ""
            return html.settlement.dashboard_campaign_asset.safe_substitute(
                asset_id=self.settlement["_id"],
                name=self.settlement["name"],
                campaign=game_assets.campaign_look_up[self.get_campaign()],
                ly=self.get_ly(),
                pop=self.settlement["population"],
                players_block=players,
            )
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






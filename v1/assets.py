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
import export_to_file
from modular_assets import survivor_names, settlement_names, survivor_attrib_controls
import game_assets
import html
from models import Abilities, Disorders, Epithets, FightingArts, Locations, Items, Innovations, Resources, WeaponMasteries, WeaponProficiencies, userPreferences, mutually_exclusive_principles, SurvivalActions
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


    def html_world(self):
        """ Creates the HTML world panel for the user. This is a method of the
        User object because it will do stuff with the user's friends.

        ...at some point, e.g. when I get around to it. """

        try:
            W = api.route_to_dict("world")["world"]
        except Exception as e:
            self.logger.error("[%s] could not render World panel!" % (self))
            self.logger.error(e)
            return "<!-- World info could not be retrieved! -->"

        return html.dashboard.world.safe_substitute(
            # results with custom HTML in v1
            latest_kill = world.api_monster_to_html(W["latest_kill"]),
            top_principles = world.api_top_principles(W["principle_selection_rates"]),
            current_hunt = world.api_current_hunt(W["current_hunt"]),
            expansion_popularity_bullets = world.api_pop_con_to_html(W["settlement_popularity_contest_expansions"]),
            campaign_popularity_bullets = world.api_pop_con_to_html(W["settlement_popularity_contest_campaigns"]),
            latest_fatality =  world.api_survivor_to_html(W["latest_fatality"]),
            latest_survivor = world.api_survivor_to_html(W["latest_survivor"], supplemental_info=["birth"]),
            latest_settlement = world.api_settlement_to_html(W["latest_settlement"]),
            top_settlement_names = world.api_top_five_list(W["top_settlement_names"]),
            top_survivor_names = world.api_top_five_list(W["top_survivor_names"]),
            top_COD = world.api_top_five_list(W["top_causes_of_death"]),
            defeated_monsters = world.api_killboard_to_html(W["killboard"]),
            # settlement numerics
            max_pop = W["max_pop"]["value"],
            max_death = W["max_death_count"]["value"],
            max_survival = W["max_survival_limit"]["value"],
            active_settlements = W["active_settlements"]["value"],
            abandoned_settlements = W["abandoned_and_removed_settlements"]["value"],
            avg_ly = W["avg_ly"]["value"],
            avg_lost_settlements = W["avg_lost_settlements"]["value"],
            avg_pop = W["avg_pop"]["value"],
            avg_death = W["avg_death_count"]["value"],
            avg_survival_limit = W["avg_survival_limit"]["value"],
            avg_milestones = W["avg_milestones"]["value"],
            avg_storage = W["avg_storage"]["value"],
            avg_defeated = W["avg_defeated_monsters"]["value"],
            avg_expansions = W["avg_expansions"]["value"],
            avg_innovations = W["avg_innovations"]["value"],
            # survivor numerics
            dead_survivors = W["dead_survivors"]["value"],
            live_survivors = W["live_survivors"]["value"],
            avg_disorders = W["avg_disorders"]["value"],
            avg_abilities = W["avg_abilities"]["value"],
            avg_hunt_xp = W["avg_hunt_xp"]["value"],
            avg_insanity = W["avg_insanity"]["value"],
            avg_courage = W["avg_courage"]["value"],
            avg_understanding = W["avg_understanding"]["value"],
            avg_fighting_arts = W["avg_fighting_arts"]["value"],
            # user numerics
            avg_user_settlements = W["avg_user_settlements"]["value"],
            avg_user_survivors = W["avg_user_survivors"]["value"],
            avg_user_avatars = W["avg_user_avatars"]["value"],
            total_users = W["total_users"]["value"],
            total_users_last_30 = W["total_users_last_30"]["value"],
            total_multiplayer = W["total_multiplayer_settlements"]["value"],
            recent_sessions = W["recent_sessions"]["value"],
            new_settlements_last_30 = W["new_settlements_last_30"]["value"],
        )



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



        # 2016-12 "hemmorhage" fix; expand as needed for the next typo
        error_ai = {
            "Intracranial hemmorhage": "Intracranial hemorrhage",
        }
        for ai in self.survivor["abilities_and_impairments"]:
            if ai in error_ai.keys():
                self.survivor["abilities_and_impairments"].remove(ai)
                self.survivor["abilities_and_impairments"].append(error_ai[ai])
                self.logger.debug("[%s] normalized '%s' to '%s" % (self.User, ai, error_ai[ai]))

        # 2016-11 RANDOM_FIGHTING_ART bug
        if "RANDOM_FIGHTING_ART" in self.survivor["fighting_arts"]:
            self.survivor["fighting_arts"].remove("RANDOM_FIGHTING_ART")

        # 2016-11 epithet bug
        for e in self.survivor["epithets"]:
            if '"' in e:
                self.update_epithets(action="remove", epithet=e)
            if e.split(":")[0].strip() == "object":
                self.logger.debug("[%s] bogus epithet '%s' detected on survivor %s" % (self.User, e, self))
                self.update_epithets(action="remove", epithet=e)

        # see if we need to retire this guy, based on recent updates
        if int(self.survivor["hunt_xp"]) >= 16 and not "retired" in self.survivor.keys():
            self.retire()

        # normalize weapon proficiency type
        if "weapon_proficiency_type" in self.survivor.keys() and self.survivor["weapon_proficiency_type"] != "":
            raw_value = str(self.survivor["weapon_proficiency_type"])
            sanitized = raw_value.strip().title()
            sanitized = " ".join(sanitized.split())
            if sanitized[-1] == "s":
                sanitized = sanitized[:-1]
            self.survivor["weapon_proficiency_type"] = sanitized
            if self.survivor["weapon_proficiency_type"] == "Fist And Tooth":
                self.survivor["weapon_proficiency_type"] = "Fist & Tooth"
        else:
            self.survivor["weapon_proficiency_type"] = ""

        # check the settlements innovations and auto-add Weapon Specializations
        #   if there are any masteries in the settlement innovations 
        if not "dead" in self.survivor.keys():
            for innovation_key in self.Settlement.get_game_asset("innovations", update_mins=False, handles_to_names=True):
                if innovation_key in WeaponMasteries.get_keys():
                    prof_dict = WeaponMasteries.get_asset(innovation_key)
                    if "auto-apply_specialization" in prof_dict.keys() and not prof_dict["auto-apply_specialization"]:
                        pass
                    else:
                        if prof_dict["all_survivors"] not in self.survivor["abilities_and_impairments"]:
                            if self.User.get_preference("apply_weapon_specialization"):
                                if prof_dict["all_survivors"] not in self.survivor["abilities_and_impairments"]:
                                    self.survivor["abilities_and_impairments"].append(prof_dict["all_survivors"])
                                    self.logger.debug("Auto-applied settlement default '%s' to survivor '%s' of '%s'." % (prof_dict["all_survivors"], self.survivor["name"], self.Settlement.settlement["name"]))
                                    self.Settlement.log_event("Automatically added '%s' to %s's abilities!" % (prof_dict["all_survivors"], self.survivor["name"]))
                elif innovation_key.split("-")[0].strip() == "Mastery":
                    custom_weapon = " ".join(innovation_key.split("-")[1:]).title().strip()
                    spec_str = "Specialization - %s" % custom_weapon
                    if spec_str not in self.survivor["abilities_and_impairments"]:
                        self.survivor["abilities_and_impairments"].append(spec_str)
                        self.logger.debug("Auto-applied settlement default '%s' to survivor '%s'." % (spec_str, self.survivor["name"]))

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
        for s in ["fighting_arts","abilities_and_impairments","disorders"]:
            self.survivor[s] = list(set(self.survivor[s]))

#        self.logger.debug("[%s] normalized %s" % (self.User, self))
        self.save(quiet=True)


    def new(self, params, name="Anonymous", sex="M"):
        """ All that is required to make a new survivor is a name, a sex and an
        email address for its owner/operator. If you have those in a
        cgi.FieldStorage(), you may pass that in as the first arg and leave it
        at that.

        If the cgi.FieldStorage() contains "father" and "mother" params, those
        will be applied during initialization.

        Otherwise, pass a None in place of a cgi.FieldStorage to use default
        values or use the appropriate kwargs to provide that information in the
        function call."""

        self.logger.debug("[%s] is creating a new survivor..." % self.User)
        self.Settlement.log_event("%s is adding a new survivor to the settlement!" % (self.User.user["login"]))

        email = self.User.user["login"]

        # if we have a cgi.FieldStorage() as our first arg
        if params is not None:
            if "name" in params and params["name"].value != "":
                name = params["name"].value.strip()
            if "sex" in params:
                try:
                    sex = params["sex"].value
                except AttributeError:
                    sex = params["sex"].strip()
            if "email" in params:
                email = params["email"].value.strip()

        # if we're doing random names for survivors, do it here before we save
        if name == "Anonymous" and self.User.get_preference("random_names_for_unnamed_assets"):
            name_list = survivor_names.other
            if sex == "M":
                name_list = name_list + survivor_names.male
            elif sex == "F":
                name_list = name_list + survivor_names.female
            else:
                self.logger.error("[%s] unknown survivor sex! '%s' is not allowed!" % (self.User, sex))
            name = random.choice(name_list)
            self.Settlement.log_event("A random name has been assigned to the new survivor due to user preference.")

        survivor_dict = {
            "name": name,
            "email": email,
            "sex": sex,
            "born_in_ly": self.Settlement.settlement["lantern_year"],
            "created_on": datetime.now(),
            "created_by": self.User.user["_id"],
            "settlement": self.Settlement.settlement["_id"],
            "survival": 0,
            "hunt_xp": 0,
            "Movement": 5,
            "Accuracy": 0,
            "Strength": 0,
            "Evasion": 0,
            "Luck": 0,
            "Speed": 0,
            "Insanity": 0,
            "Head": 0,
            "Arms": 0,
            "Body": 0,
            "Waist": 0,
            "Legs": 0,
            "Courage": 0,
            "Understanding": 0,
            "Weapon Proficiency": 0,
            "weapon_proficiency_type": "",
            "disorders": [],
            "abilities_and_impairments": [],
            "fighting_arts": [],
            "epithets": [],
        }


        # check the campaign for additional attribs
        c_dict = self.Settlement.get_campaign("dict")
        if "new_survivor_additional_attribs" in c_dict.keys():
            for k,v in c_dict["new_survivor_additional_attribs"].iteritems():
                survivor_dict[k] = v

        # set the public bit if it's supplied:
        if params is not None and "toggle_public" in params:
            survivor_dict["public"] = "checked"

        # add parents if they're specified
        parents = []
        for parent in ["father", "mother"]:
            if params is not None and parent in params:
                p_id = params[parent].value
                if len(p_id.split(":")) >= 1:
#                    self.logger.debug(p_id)
                    p_id = p_id.split(":")[1]
                p_id = ObjectId(p_id)
                parents.append(mdb.survivors.find_one({"_id": p_id})["name"])
                survivor_dict[parent] = ObjectId(p_id)

        newborn = False
        if parents != []:
            newborn = True
            self.logger.debug("New survivor %s is a newborn." % name)
            if sex == "M":
                genitive_appellation = "Son"
            elif sex == "F":
                genitive_appellation = "Daughter"
            survivor_dict["epithets"].append("%s of %s" % (genitive_appellation, " and ".join(parents)))

        # insert the new survivor into mdb and use its newly minted id to set
        #   self.survivor with the info we just inserted
        survivor_id = mdb.survivors.insert(survivor_dict)
        self.survivor = mdb.survivors.find_one({"_id": survivor_id})

        # Add our campaign's founder epithet if the survivor is a founder
        founder_epithet = "Founder"
        if "founder_epithet" in self.Settlement.get_campaign("dict"):
            founder_epithet = self.Settlement.get_campaign("dict")["founder_epithet"]
        if self.is_founder():
            self.logger.debug("%s is a founder. Adding founder epithet!" % self)
            self.update_epithets(epithet=founder_epithet)
        else:
            self.logger.debug("%s is not a founder. Skipping founder epithet." % self)

        # log the addition or birth of the new survivor
        name_pretty = self.get_name_and_id(include_sex=True, include_id=False)
        current_ly = self.Settlement.settlement["lantern_year"]
        if not self.suppress_event_logging:
            if newborn:
                self.Settlement.log_event("%s born to %s!" % (name_pretty, " and ".join(parents)))
            else:
                self.Settlement.log_event("%s joined the settlement!" % (name_pretty))

        # increment survival if the survivor has a name
        if self.survivor["name"] != "Anonymous":
            self.Settlement.log_event("Automatically adding 1 survival to %s" % self.survivor["name"])
            self.survivor["survival"] += 1
        else:
            self.logger.debug("[%s] is creating an anonymous survivor. Survivor survival = %s" % (self.User, self.survivor["survival"]))

        # apply settlement buffs to the new guy depending on preference
        if self.User.get_preference("apply_new_survivor_buffs"):
            new_survivor_buffs = self.Settlement.get_bonuses("new_survivor", update_mins=self.update_mins)
            newborn_survivor_buffs = self.Settlement.get_bonuses("newborn_survivor", update_mins=self.update_mins)

            def apply_buffs(buff_dict, buff_desc):
                for b in buff_dict.keys():
                    buffs = buff_dict[b]
                    for attrib in buffs.keys():
                        if attrib == "affinities":
                            self.update_affinities(buffs[attrib])
                        elif attrib == "abilities_and_impairments":
                            self.survivor["abilities_and_impairments"].append(buffs[attrib])
                        else:
                            self.survivor[attrib] = self.survivor[attrib] + buffs[attrib]
                    self.logger.debug("Applied %s survivor buffs for '%s' successfully: %s" % (buff_desc, b, buffs))
                    self.Settlement.log_event("Applied '%s' bonus to %s." % (b, self))

            # now do it !
            self.logger.debug("Applying %s new survivor buffs to %s." % (len(new_survivor_buffs.keys()), self))
            apply_buffs(new_survivor_buffs, "new")
            if newborn:
                self.logger.debug("Applying %s newborn survivor buffs to %s." % (len(newborn_survivor_buffs.keys()), self))
                apply_buffs(newborn_survivor_buffs, "newborn")

        else:
            self.Settlement.log_event("Settlement bonuses were not applied to %s." % (name))
            self.logger.debug("Skipping auto-application of new survivor buffs for %s." % self.get_name_and_id())

        # if we've got an avatar, do that AFTER we insert the survivor record
        if params is not None and "survivor_avatar" in params and params["survivor_avatar"].filename != "":
            self.update_avatar(params["survivor_avatar"])

        # save the survivor (in case it got changed above), update settlement
        #   mins and log our successful creation

        if self.update_mins:
            self.Settlement.update_mins()

        self.logger.info("User '%s' created new survivor %s successfully." % (self.User.user["login"], self.get_name_and_id(include_sex=True)))

        self.save()

        return survivor_id


    def remove(self):
        """ Markes the survivor 'removed' with a datetime.now(). """

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
            output.append("[%s]" % self.get_sex())
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
        elif "Founder" in self.survivor["epithets"]:
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



    def death(self, undo_death=False, cause_of_death=None, save=False):
        """ Call this method when a survivor dies. Call it with the 'undo_death'
        kwarg to undo the death.

        This returns a True or False that reflects the life/death status of the
        survivor (which is a little strange, but bear with me).

        We return True if the survivor is marked with the 'dead' attrib and we
        return False if the survivor is NOT marked with the 'dead' attrib.
        """


        # do cause of death updates before we do anything else.
        if cause_of_death is not None:
            self.survivor["cause_of_death"] = cause_of_death
            self.logger.debug("[%s] set %s cause of death to '%s'" % (self.User, self, cause_of_death))

        if undo_death:
            self.logger.debug("[%s] is resurrecting '%s'" % (self.User, self))
            for death_key in ["died_on","died_in","cause_of_death","dead"]:
                try:
                    del self.survivor[death_key]
                    self.logger.debug("[%s] removed '%s' attrib from survivor %s" % (self.User, death_key, self))
                except Exception as e:
                    self.logger.warn("Could not unset '%s'" % death_key)
                    pass
            self.logger.debug("[%s] has resurrected %s" % (self.User, self))
        elif not undo_death and "dead" not in self.survivor.keys():
            self.survivor["dead"] = True
            self.survivor["died_on"] = datetime.now()
            self.survivor["died_in"] = self.Settlement.settlement["lantern_year"]
            if cause_of_death is None:
                self.Settlement.log_event("%s has died!" % self, "survivor_death")
            else:
                self.Settlement.log_event("%s has died! Cause of death: %s" % (self, cause_of_death), "survivor_death")
            self.logger.debug("[%s] survivor %s is dead!" % (self.User, self))
        else:
            self.logger.warn("[%s] activated the Controls of Death and made no changes." % self.User)

        # saving isn't required if we're calling this from modify()
        if save:
            self.save()


    def get_survival_actions(self, return_as=False):
        """ Creates a list of survival actions that the survivor can do. """
        possible_actions = SurvivalActions.get_keys(Settlement=self.Settlement)

        available_actions = []
        for a in possible_actions:
            if a in self.Settlement.get_survival_actions():
                available_actions.append(a)

        for i in self.get_impairments():
            if i in Abilities.get_keys():
                if "survival_actions_disabled" in Abilities.get_asset(i).keys():
                    for action in Abilities.get_asset(i)["survival_actions_disabled"]:
                        try:
                            available_actions.remove(action)
                        except:
                            pass

        emphasized_actions = copy(available_actions)
        if "cannot_spend_survival" in self.survivor.keys():
            emphasized_actions = []

        if return_as == "html_checkboxes":
            sorted_actions = {}
            for a in possible_actions:
                sorted_actions[SurvivalActions.get_asset(a)["sort_order"]] = a
            possible_actions = []
            for k in sorted(sorted_actions.keys()):
                possible_actions.append(sorted_actions[k])

            output = ""
            for a in possible_actions:
                p_class = ""
                font_class = ""
                if a in available_actions:
                    font_class += "survival_action_available"
                if a in emphasized_actions:
                    font_class += " survival_action_emphasize"
                output += html.survivor.survival_action_item.safe_substitute(
                    action = a,
                    f_class=font_class,
                )

            return output

        return available_actions



    def get_abilities_and_impairments(self, return_type=False):
        """ This...really needs to be deprecated soon. """

        all_list = sorted(self.survivor["abilities_and_impairments"])

        for old_attrib in ["courage_attribute", "understanding_attribute"]:
            if old_attrib in self.survivor.keys():
                all_list.append(self.survivor[old_attrib])

        if return_type == "comma-delimited":
            return ", ".join(all_list)

        if return_type == "html_select_remove":
            if all_list == []:
                return ""

            output = html.ui.game_asset_select_top.safe_substitute(
                operation = "remove_",
                operation_pretty = "Remove",
                name = "ability",
                name_pretty = "Ability or Impairment",
            )
            for ability in all_list:
                output += '<option>%s</option>' % ability
            output += '</select>'
            return output

        if return_type == "html_formatted":
            pretty_list = []
            for ability in all_list:
                suffix = ""
                if "ability_customizations" in self.survivor.keys() and ability in self.survivor["ability_customizations"]:
                    suffix = self.survivor["ability_customizations"][ability]
                if ability in Abilities.get_keys():
                    desc = Abilities.get_asset(ability)["desc"]
                    if "constellation" in Abilities.get_asset(ability).keys():
                        ability = '<font class="maroon_text">%s</font>' % ability
                    pretty_list.append("<p><b>%s:</b> %s %s</p>" % (ability, desc, suffix))
                elif ability not in Abilities.get_keys() and suffix != "":
                    pretty_list.append("<p><b>%s:</b> %s" % (ability, suffix))
                else:
                    pretty_list.append("<p><b>%s:</b> custom ability or impairment (use fields below to add a description).</p>" % ability)
            return "\n".join(pretty_list)

        return all_list


    def get_fighting_arts(self, return_type=False):
        """ Returns a survivor's fighting arts. As HTML with level controls, if necessary. """

        fighting_arts = self.survivor["fighting_arts"]

        if return_type == "formatted_html":
            output = ""
            for fa_key in fighting_arts:
                fa_dict = FightingArts.get_asset(fa_key)

                level_controls = ""
                if "levels" in fa_dict:
                    l_dict = fa_dict["levels"]
                    level_controls = ""
                    for lvl in sorted(l_dict.keys()):
                        checked = ""
                        if lvl == 0:
                            checked = "checked"
                        if lvl in self.get_fighting_art_levels(fa_key):
                            checked = "checked"
                        level_controls += html.survivor.survivor_sheet_fa_level_toggle.safe_substitute(
                            checked = checked,
                            name = fa_key,
                            lvl = lvl,
                            desc = l_dict[lvl],
                            input_id = "%sFightingArtLevel%sControls" % (fa_key,lvl),
                            survivor_id = self.survivor["_id"],
                        )

                const = ""
                if "constellation" in fa_dict.keys():
                    const = "card_constellation"

                sec = ""
                if "secret" in fa_dict.keys():
                    sec = "secret_fighting_art"

                output += html.survivor.survivor_sheet_fighting_art_box.safe_substitute(
                    name = fa_key,
                    desc = fa_dict["desc"],
                    constellation=const,
                    secret = sec,
                    lvl_cont = level_controls,
                )

            return output


        if return_type == "html_select_remove":
            if fighting_arts == []:
                return ""
            output = ""
            output = '<select name="remove_fighting_art" onchange="this.form.submit()">'
            output += '<option selected disabled hidden value="">Remove Fighting Art</option>'
            for fa in fighting_arts:
                output += '<option>%s</option>' % fa
            output += '</select>'
            return output

        return disorders


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


    def get_epithets(self, return_type=False):
        """ Returns survivor epithets in a number of different formats. """

        epithets = self.survivor["epithets"]

        if return_type == "comma-delimited":
            return ", ".join(epithets)

        if return_type == "html_angular":
            js_epithets = []
            for e in epithets:
                e_bgcolor = None
                e_color = None
                if e in game_assets.epithets:
                    e_dict = game_assets.epithets[e]
                    if "bgcolor" in e_dict:
                        e_bgcolor = e_dict["bgcolor"]
                    if "color" in e_dict:
                        e_color = e_dict["color"]
                js_epithets.append("{'name':'%s', 'bgcolor':'%s', 'color':'%s'}" % (e, e_bgcolor, e_color))

            return html.survivor.epithet_angular_controls.safe_substitute(
                survivor_id = self.survivor["_id"],
                current_epithets = ",".join(js_epithets),
                epithet_options = Epithets.render_as_html_dropdown(
                    select_type="angularjs",
                    survivor_id = self.survivor["_id"],
#                    exclude=self.survivor["epithets"], # the .js app prevents dupes
                    Settlement=self.Settlement,
                    submit_on_change=False,
                ),
            )

        if return_type == "html_formatted":
            if epithets == []:
                return ""
            else:
                return '<p class="subhead_p_block">%s</p>' % ", ".join(epithets)

        return epithets


    def get_affinities(self, return_type=False):
        no_affinities = {"red": 0, "green": 0, "blue": 0}

        s_affinities = no_affinities
        if "affinities" in self.survivor.keys():
            s_affinities = self.survivor["affinities"]

        for color in ["red","green","blue"]:
            if color not in s_affinities.keys():
                s_affinities[color] = 0


        if return_type == "survivor_sheet_controls":
            if s_affinities == no_affinities:
                return html.survivor.affinity_controls.safe_substitute(
                    button_class = "no_affinities",
                    text="&#9633; &#9633; &#9633;",
                )
            else:
                button_text = ""
                for affinity_key in ["red","blue","green"]:
                    a_value = s_affinities[affinity_key]
                    span_class = affinity_key
                    if a_value != 0:
                        button_text += html.survivor.affinity_span.safe_substitute(
                            value = a_value,
                            span_class = span_class
                        )
                return html.survivor.affinity_controls.safe_substitute(
                    button_class = "affinities",
                    text = button_text
                )

        return s_affinities


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
            if self.is_savior():
                increment_hunt_xp=4


        if return_to_settlement:
            if "in_hunting_party" in self.survivor.keys():
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


    def add_custom_AI(self, params=None):
        """ Processes cgi.FieldStorage() params and creates a custom A&I entry
        for the survivor. """

        if params is None:
            self.logger.error("Must supply a valid cgi.FieldStorage() object!")
            return False

        try:
            ai_name = params["custom_AI_name"].value
            ai_desc = params["custom_AI_desc"].value
            ai_type = params["custom_AI_type"].value
        except Exception as e:
            self.logger.exception(e)
            self.logger.error("[%s] attempted to add a custom AI but did not provide all required values!" % (self.User))
            return False

        # add the asset key
        self.add_game_asset("abilities_and_impairments", ai_name)

        # see if we've got an ability_customizations dict on the survivor yet
        if not "ability_customizations" in self.survivor.keys():
            self.survivor["ability_customizations"] = {}

        self.survivor["ability_customizations"][ai_name] = ai_desc
        self.logger.debug("[%s] added custom A&I '%s: %s' (%s) to %s" % (self.User, ai_name, ai_desc, ai_type, self))



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
            if asset_key == "RANDOM_FIGHTING_ART":
                fa_deck = FightingArts.build_survivor_deck(self, self.Settlement)
                self.update_fighting_arts(random.choice(fa_deck), action="add")
            elif asset_key in FightingArts.get_keys():
                self.survivor["fighting_arts"].append(asset_key)
                asset_dict = FightingArts.get_asset(asset_key)
                if "epithet" in asset_dict.keys():
                    self.update_epithets(epithet=asset_dict["epithet"])
                if "Movement" in asset_dict.keys():
                    self.survivor["Movement"] = int(self.survivor["Movement"]) + asset_dict["Movement"] 
            else:
                self.logger.exception("[%s] Attempted to add unknown fighting art!" % self)
                return False

        elif asset_type == "abilities_and_impairments":
            # log twilight sword reciept
            if asset_key == "Twilight Sword":
                self.Settlement.log_event("%s got the Twilight Sword!" % self.get_name_and_id(include_id=False, include_sex=True))

            # handle weapon masteries
            if asset_key.split("-")[0] == "Mastery ":
                self.Settlement.add_weapon_mastery(self, asset_key)

            # add custom abilities and impairments
            if asset_key not in Abilities.get_keys():
                self.survivor["abilities_and_impairments"].append("%s" % asset_key)
                return True

            # now, add standard/supported abilities defined in game_assets.py
            elif asset_key in Abilities.get_keys():
                asset_dict = Abilities.get_asset(asset_key)
                self.survivor["abilities_and_impairments"].append(asset_key)

                # toggle flags on if their keys are in the asset dict
                for flag_attrib in ["cannot_spend_survival", "cannot_use_fighting_arts", "skip_next_hunt"]:
                    if flag_attrib in asset_dict.keys():
                        self.survivor[flag_attrib] = "checked"
                        self.logger.debug("Automatically toggling '%s' on for survivor '%s' (%s)" % (flag_attrib, self.survivor["name"], self.survivor["_id"]))

                # apply Understanding, Accuracy, etc. mods here
                for attrib in game_assets.survivor_attributes:
                    if attrib in asset_dict and attrib in self.survivor.keys():
                        old_value = int(self.survivor[attrib])
                        new_value = old_value + asset_dict[attrib]
                        self.survivor[attrib] = new_value

                # update affinities, if the ability indicates an update:
                if "affinities" in asset_dict.keys():
                    if not "affinities" in self.survivor:
                        self.survivor["affinities"] = {"red":0,"blue":0,"green":0}
                    for affinity_key in asset_dict["affinities"].keys():
                        a_adjustment = asset_dict["affinities"][affinity_key]
                        self.survivor["affinities"][affinity_key] += a_adjustment
                        self.logger.debug("Automatically updated '%s' affinity for %s. + %s due to '%s'" % (affinity_key, self, a_adjustment, asset_key))

                # auto-add any mandatory epithets
                if "epithet" in asset_dict.keys():
                    self.update_epithets(epithet=asset_dict["epithet"])


                # now that we're basically done, handle related abilities:
                if "related" in asset_dict.keys():
                    for related_ability in asset_dict["related"]:
                        if related_ability not in self.survivor["abilities_and_impairments"]:
                            self.logger.debug("%s is adding '%s' to '%s': automatically adding related '%s' ability." % (self.User.user["login"], asset_key, self.survivor["name"], related_ability))
                            self.add_game_asset("abilities_and_impairments", related_ability)


                return True
            else:
                return False
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
            if asset_key not in Abilities.get_keys():
                self.survivor["abilities_and_impairments"].remove(asset_key)
            elif asset_key in Abilities.get_keys():
                asset_dict = Abilities.get_asset(asset_key)
                self.survivor["abilities_and_impairments"].remove(asset_key)
                if "epithet" in asset_dict.keys():
                    self.update_epithets(action="rm", epithet=asset_dict["epithet"])
                if "cannot_spend_survival" in asset_dict.keys() and "cannot_spend_survival" in self.survivor.keys():
                    del self.survivor["cannot_spend_survival"]

                if "affinities" in asset_dict.keys():
                    for k in asset_dict["affinities"].keys():
                        if "affinities" in self.survivor.keys() and self.survivor["affinities"][k] >= asset_dict["affinities"][k]:
                            self.logger.debug("[%s] automatically decrementing %s affinity by %s for %s" % (self.User, k,asset_dict["affinities"][k], self))
                            self.survivor["affinities"][k] -= 1

                mdb.survivors.save(self.survivor)

        # do this after removing game assets from survivors
        self.Settlement.validate_weapon_masteries()


    def get_fighting_art_levels(self, fighting_art=None):
        """ Gets a list of the active levels for 'fighting_art'. Returns an
        empty list if the survivor doesn't have anything. """

        if not "fighting_art_levels" in self.survivor.keys():
            return []

        if fighting_art in self.survivor["fighting_art_levels"].keys():
            return self.survivor["fighting_art_levels"][fighting_art]

        return []


    def toggle_fighting_art_level(self, fighting_art=None, lvl=0):
        """ Toggles a fighting art level on or off. """

        lvl = int(lvl)

        if fighting_art is None or lvl == 0:
            return None

        fa_dict = FightingArts.get_asset(fighting_art)
        if not "fighting_art_levels" in self.survivor.keys():
            self.survivor["fighting_art_levels"] = {fighting_art: []}

        if lvl in self.survivor["fighting_art_levels"][fighting_art]:
            self.survivor["fighting_art_levels"][fighting_art].remove(lvl)
            self.logger.debug("[%s] toggled '%s' level %s off" % (self.User, fighting_art, lvl))
        else:
            self.survivor["fighting_art_levels"][fighting_art].append(lvl)
            self.logger.debug("[%s] toggled '%s' level %s on" % (self.User, fighting_art, lvl))



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

#        if type(toggle_value) != list:
#            try:
#                del self.survivor[toggle_key]
#                self.logger.debug("%s toggled '%s' OFF for survivor %s." % (self.User.user["login"], toggle_key, self.get_name_and_id()))
#                if toggle_key == "dead":
#                    if self.death(undo_death=True):
#                        self.logger.debug("Survivor '%s' (%s) has not returned from death!" % (self.survivor["name"], self.survivor["_id"]))
#            except Exception as e:
#                pass
#        else:
#            self.survivor[toggle_key] = "checked"
#            if toggle_key == "dead":
#                if not self.death():
#                    self.logger.error("Could not process death for survivor '%s' (%s)." % (self.survivor["name"], self.survivor["_id"]))
#            if toggle_key == "retired":
#                self.retire()


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
            if self.get_sex() == "F":
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




    def update_constellation(self, new_value):
        """ Sets (or unsets) the survivor's constellation. """

        def rm():
            self.update_epithets("rm","The %s" % self.survivor["constellation"])
            self.survivor["constellation"] = None

        def add():
            self.survivor["constellation"] = new_value
            self.update_epithets("add", "The %s" % new_value)
            self.Settlement.log_event("%s has been reborn under the sign of The %s as one of the <b>People of the Stars</b>!" % (self, new_value))

        if new_value == "UNSET" and "constellation" in self.survivor.keys():
            rm()
        elif "constellation" in self.survivor.keys() and self.survivor["constellation"] is not None:
            rm()
            add()
        else:
            add()


        self.logger.debug("[%s] set survivor %s constellation ('%s')." % (self.User, self, new_value))


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


    def set_constellation_traits(self):
        """ Checks the survivor for the presence of the 16 constellation traits.
        Sets self.survivor["constellation_traits"] dict. """

        traits = []

        # check Understanding for 9+
        if int(self.survivor["Understanding"]) >= 9:
            traits.append("9 Understanding (max)")

        # check self.survivor["expansion_attribs"] for "Reincarnated surname","Scar","Noble surname"
        if "expansion_attribs" in self.survivor.keys():
            for attrib in ["Reincarnated surname", "Scar", "Noble surname"]:
                if attrib in self.survivor["expansion_attribs"].keys():
                    traits.append(attrib)

        split_name = self.survivor["name"].split(" ")
        for surname in ["Noble","Reincarnated"]:
            if surname in split_name and "%s surname" % surname not in traits:
                traits.append(surname + " surname")

        # check abilities_and_impairments for Oracle's Eye, Iridescent Hide, any weapon mastery, Pristine,
        for a in ["Oracle's Eye","Iridescent Hide","Pristine"]:
            if a in self.survivor["abilities_and_impairments"]:
                traits.append("%s ability" % a)

        for a in self.survivor["abilities_and_impairments"]:
            if a.split(" ")[0] == "Mastery":
                traits.append("Weapon Mastery")

        # check disorders for "Destined"
        if "Destined" in self.survivor["disorders"]:
            traits.append("Destined disorder")

        # check fighting arts for "Fated Blow", "Frozen Star", "Unbreakable", "Champion's Rite"
        for fa in ["Fated Blow","Frozen Star","Unbreakable","Champion's Rite"]:
            if fa in self.survivor["fighting_arts"]:
                if fa == "Frozen Star":
                    fa = "Frozen Star secret"
                traits.append("%s fighting art" % fa)

        # check for 3+ strength
        if int(self.survivor["Strength"]) >= 3:
            traits.append("3+ Strength attribute")

        # check for 1+ Accuracy
        if int(self.survivor["Accuracy"]) >= 1:
            traits.append("1+ Accuracy attribute")

        # check Courage for 9+
        if int(self.survivor["Courage"]) >= 9:
            traits.append("9 Courage (max)")


        # done.
        self.survivor["constellation_traits"] = list(set(traits))
        mdb.survivors.save(self.survivor)


    def update_epithets(self, action="add", epithet=None):
        """ Adds and removes epithets from self.survivor["epithets"]. """

        if epithet is None:
            self.logger.warn("[%s] update_epithets() -> epithet is None!" % self.User)
            return

        if action == "add":
            if epithet.split(":")[0].strip() == "object":
                self.logger.warn("[%s] ignoring bogus epithet '%s'." % (self.User, epithet))
            elif epithet not in self.survivor["epithets"]:
                self.survivor["epithets"].append(epithet)
                self.logger.debug("[%s] added epithet '%s' to %s." % (self.User, epithet, self))
            else:
                self.logger.warn("[%s] epithet '%s' has already been added to %s!" % (self.User, epithet, self))
        elif action in ["rm","remove"]:
            if epithet in self.survivor["epithets"]:
                self.survivor["epithets"].remove(epithet)
                self.logger.debug("[%s] removed epithet '%s' from %s." % (self.User, epithet, self))
            else:
                self.logger.warn("[%s] attempted to remove epithet '%s' from %s. Epithet does not exist!" % (self.User, epithet, self))

        # uniquify and sort on exit
        self.survivor["epithets"] = sorted(list(set(self.survivor["epithets"])))


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


    def get_impairments(self):
        """ Returns a list of survivor impairments (i.e. returns the survivor's
        'abilities_and_impairments' attribute without the abilities). """

        impairment_set = set()
        for a in self.survivor["abilities_and_impairments"]:
            if a in Abilities.get_keys():
                if Abilities.get_asset(a)["type"] in ["impairment","severe_injury","curse"]:
                    impairment_set.add(a)
        return list(impairment_set)


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
                    if S.get_sex() == role[1]:
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

            # bail if the settlement hasn't got partnership
            if not "Partnership" in self.Settlement.settlement["innovations"]:
                return ""

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
            if "survivor_attribs" in self.Settlement.get_campaign("dict"):
                expansion_attrib_keys.update(
                    game_assets.campaigns[self.Settlement.get_campaign()]["survivor_attribs"]
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
                self.update_epithets(epithet=attrib)    # issue #81
                self.logger.debug("[%s] toggled ON expansion attribute '%s' for %s" % (self.User, attrib, self))
        for attrib in self.get_expansion_attribs().keys():
            if not attrib in active:
                del self.survivor["expansion_attribs"][attrib]
                self.update_epithets(action="rm", epithet=attrib)
                self.logger.debug("[%s] toggled OFF expansion attribute '%s' for %s" % (self.User, attrib, self))


    def update_sex(self, new_sex):
        """ Method for updating a survivor's sex. """

        # return false if we get a bogus value
        if new_sex not in ["M","F"]:
            return False

        # check for Gender Swap A&I
        if "Gender Swap" in self.survivor["abilities_and_impairments"]:
            return False

        if new_sex == self.survivor["sex"]:
            return False

        self.logger.debug("[%s] changed survivor %s sex to %s" % (self.User, self, new_sex))
        self.Settlement.log_event("%s sex changed to %s!" % (self, new_sex))
        self.survivor["sex"] = new_sex


    def update_fighting_arts(self, fighting_art=None, action=None):
        """ Adds/removes a fighting art from a survivor. Logs it. """

        if action == "add":
            if fighting_art in self.survivor["fighting_arts"]:
                return False

            if len(self.survivor["fighting_arts"]) >= 3:
                self.logger.warn("[%s] attempting to add a fourth fighting art to %s" % (self.User, self))
                return False
            else:
                self.survivor["fighting_arts"].append(fighting_art)
                self.logger.debug("[%s] added the '%s' fighting art to %s" % (self.User, fighting_art, self))
                self.Settlement.log_event("%s acquired the '%s' fighting art!" % (self, fighting_art))

        if action in ["rm","remove"]:
            if fighting_art not in self.survivor["fighting_arts"]:
                return False
            else:
                self.survivor["fighting_arts"].remove(fighting_art)
                self.logger.debug("[%s] removed the '%s' fighting art from %s" % (self.User, fighting_art, self))
                self.Settlement.log_event("%s lost the '%s' fighting art!" % (self, fighting_art))


    def update_affinities(self, params):
        """ Updates the survivor's "affinities" attrib. The 'params' arg can be
        either a dict or a cgi.FieldStorage(). The function will handle either
        automatically."""

        if type(params) == dict:
            new_affinities = params
        else:
            new_affinities = {
                "red": int(params["red_affinities"].value),
                "blue": int(params["blue_affinities"].value),
                "green": int(params["green_affinities"].value),
            }
        self.survivor["affinities"] = new_affinities
        self.logger.debug("[%s] updated affinities for %s. New affinities: %s" % (self.User, self, new_affinities))


    def update_cod(self, cod):
        """ Updates the COD. If the survivor is already among the dead, try to
        update it there as well. """

        if "cause_of_death" in self.survivor and cod == self.survivor["cause_of_death"]:
            return
        self.survivor["cause_of_death"] = cod
        self.logger.debug("[%s] set cause of death to '%s' for %s." % (self.User, cod, self))


    def update_survival(self, new_value):
        """ Updates the survivor's 'survival' attrib. Tries to force 'new_value'
        to an int and fails gracefully if it can't (to protect us from rogue
        orm input, PEBKAC, etc. """

        try:
            survival = int(new_value)
        except:
            return False

        self.survivor["survival"] = survival
        self.logger.debug("[%s] set %s survival to %s" % (self.User, self, survival))


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


    def get_sex(self, return_type=None):
        """ Gets the survivor's sex. Takes abilities_and_impairments into
        account: anything with the 'reverse_sex' attribute will reverse this."""

        functional_sex = self.survivor["sex"]

        reverse_sex = False
        impairment_keys = self.get_impairments()
        for i in impairment_keys:
            if i in Abilities.get_keys():
                if "reverse_sex" in Abilities.get_asset(i).keys():
                    reverse_sex = True

        if reverse_sex:
            if functional_sex == "M":
                functional_sex = "F"
            elif functional_sex == "F":
                functional_sex = "M"

        if return_type=="html":
            functional_sex = '<b>%s</b>' % functional_sex
            if reverse_sex:
                functional_sex = '<font class="alert">%s</font>' % functional_sex

        return functional_sex


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



    def modify_weapon_proficiency(self, target_lvl=None, new_type=None):
        """ Wherein we update the survivor's 'Weapon Proficiency' attrib. There
        is some biz logic here re: specializations and masteries. """

        if target_lvl is None and new_type is not None:
            self.survivor["weapon_proficiency_type"] = new_type
            self.Settlement.log_event("%s set '%s' as their weapon proficiency." % (self, new_type))
            self.logger.debug("[%s] set weapon proficiency type to '%s' for %s." %(self.User, new_type, self))
            return True

        # if we do nothing else, at least update the level
        self.survivor["Weapon Proficiency"] = target_lvl
        self.logger.debug("[%s] set Weapon Proficiency to %s for %s" % (self.User, target_lvl, self))

        # bail if the user hasn't selected a weapon type
        if self.survivor["weapon_proficiency_type"] == "":
            return True

        # otherwise, do the logic for setting/unsetting specialize and master
        weapon = self.survivor["weapon_proficiency_type"].title().strip()
        specialization_string = "Specialization - %s" % weapon
        mastery_string = "Mastery - %s" % weapon

        for proficiency_tuple in [(3, specialization_string), (8, mastery_string)]:
            lvl, p_str = proficiency_tuple
            if target_lvl < lvl and p_str in self.survivor["abilities_and_impairments"]:
                self.survivor["abilities_and_impairments"].remove(p_str)
            if target_lvl >= lvl and p_str not in self.survivor["abilities_and_impairments"]:
                self.survivor["abilities_and_impairments"].append(p_str)

        if mastery_string in self.survivor["abilities_and_impairments"] and mastery_string not in self.Settlement.settlement["innovations"]:
            self.Settlement.add_weapon_mastery(self, mastery_string)


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


    def is_savior(self):
        """ Returns False if the survivor is NOT a savior. Returns their color
        otherwise. """

        for red_ai in ["Dream of the Beast", "Red Life Exchange", "Caratosis"]:
            if red_ai in self.survivor["abilities_and_impairments"]:
                return "red"
        for red_ai in ["Dream of the Crown", "Green Life Exchange", "Dormenatus"]:
            if red_ai in self.survivor["abilities_and_impairments"]:
                return "green"
        for red_ai in ["Dream of the Lantern", "Blue Life Exchange", "Lucernae"]:
            if red_ai in self.survivor["abilities_and_impairments"]:
                return "blue"

        return False


    def update_savior_status(self, savior_type=None):
        """ Method for working with a Survivor's savior status. """

        def rm(rm_tuple):
            for ai in rm_tuple:
                if ai in self.survivor["abilities_and_impairments"]:
                    self.rm_game_asset("abilities_and_impairments", ai)
                    self.update_epithets("rm",ai)
            self.logger.debug("[%s] removed savior status from %s." % (self.User, self))
            self.Settlement.log_event("%s is no longer a %s savior." % (self, savior_type))

        def add(add_tuple):
            for ai in add_tuple:
                self.add_game_asset("abilities_and_impairments", ai)
            self.update_epithets("add",add_tuple[2])
            self.logger.debug("[%s] added savior status to %s." % (self.User, self))
            self.Settlement.log_event("A savior was born! %s is a %s savior!" % (self, savior_type))

        ai_tuples = {
            "red": ("Dream of the Beast", "Red Life Exchange", "Caratosis"),
            "green": ("Dream of the Crown", "Green Life Exchange", "Dormenatus"),
            "blue":  ("Dream of the Lantern", "Blue Life Exchange", "Lucernae"),
        }


        if savior_type is None:
            return None
        elif savior_type == "UNSET":
            if self.is_savior():
                rm(ai_tuples[self.is_savior()])
            return True
        elif self.is_savior() == savior_type:
            self.logger.debug("[%s] survivor %s is already a %s savior. No change." % (self.User, self, savior_type))
            return None
        elif self.is_savior() and self.is_savior() != savior_type:   # the toggle!
            rm(ai_tuples[self.is_savior()])
            add(ai_tuples[savior_type])
            return True
        elif not self.is_savior():
            add(ai_tuples[savior_type])
            return True
        else:
            self.logger.error("Unknown condition encountered during assets.Survivor.update_savior_status()!")
            return False


    def modify(self, params):
        """ Reads through a cgi.FieldStorage() (i.e. 'params') and modifies the
        survivor. """

#        self.logger.debug("[%s] is modifying survivor %s" % (self.User, self))

        ignore_keys = [
            # legacy keys (soon to be deprecated)
            "heal_survivor","form_id",
            # misc controls that we're already done with by now
            "norefresh", "modify", "view_game", "asset_id",
            # app.js -> attributeController elements
            "gear","tokens","base","angularjs_attrib_type","angularjs_attrib_value",
            # custom_AI form
            "custom_AI_name", "custom_AI_desc", "custom_AI_type", "custom_AI_color",
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
            elif p == "toggle_cursed_item":
                self.update_cursed_items("toggle",game_asset_key)
            elif p == "set_constellation":
                self.update_constellation(game_asset_key)
            elif p == "set_savior_type":
                self.update_savior_status(game_asset_key)
            elif p == "survivor_avatar":
                self.update_avatar(params[p])
            elif p == "add_custom_AI":
                self.add_custom_AI(params)
            elif p == "add_epithet":
                self.update_epithets(epithet=game_asset_key)
            elif p == "remove_epithet":
                self.update_epithets(action="rm", epithet=game_asset_key)
            elif p == "add_ability":
                self.add_game_asset("abilities_and_impairments", game_asset_key)
            elif p == "remove_ability":
                self.rm_game_asset("abilities_and_impairments", game_asset_key)
            elif p == "add_disorder":
                self.add_game_asset("disorder", game_asset_key)
            elif p == "remove_disorder":
                self.survivor["disorders"].remove(params[p].value)
            elif p == "add_fighting_art":
                self.add_game_asset("fighting_art", game_asset_key)
            elif p == "remove_fighting_art":
                self.update_fighting_arts(game_asset_key, action="rm")
            elif p == "resurrect_survivor":
                self.death(undo_death=True)
            elif p == "cause_of_death":
                self.death(cause_of_death=game_asset_key)
            elif p == "name":
                if game_asset_key != self.survivor[p]:
                    self.logger.debug("[%s] renamed %s to '%s'." % (self.User, self, game_asset_key) )
                    self.Settlement.log_event("%s was renamed to '%s'" % (self, game_asset_key))
                    self.survivor["name"] = game_asset_key
            elif p == "email":
                self.update_email(game_asset_key)
            elif p == "Weapon Proficiency":
                self.modify_weapon_proficiency(int(game_asset_key))
            elif p == "add_weapon_proficiency_type":
                self.modify_weapon_proficiency(target_lvl=None, new_type=game_asset_key)
            elif p == "in_hunting_party":
                self.join_departing_survivors()
            elif p == "sex":
                new_sex = game_asset_key.strip()[0].upper()
                self.update_sex(new_sex)
            elif p == "partner_id":
                self.update_partner(game_asset_key)
            elif p == "expansion_attribs":
                self.update_expansion_attribs(params[p])
            elif p == "modal_update":
                if game_asset_key == "affinities":
                    self.update_affinities(params)
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
            elif p.split("_")[0:4] == ["fighting","art","level","toggle"]:
                fighting_art = p.split("_")[-1]
                self.toggle_fighting_art_level(fighting_art, game_asset_key)
            elif p == "angularjs_attrib_update":
                attribute = params["angularjs_attrib_update"].value
                attribute_type = params["angularjs_attrib_type"].value
                attribute_type_value = params["angularjs_attrib_value"].value
                self.update_survivor_attribute(attribute, attribute_type, attribute_type_value)
            elif p == "survival":
                self.update_survival(game_asset_key)
            elif p in ["Insanity","Head","Arms","Body","Waist","Legs"]:
                self.update_survivor_attribute(p, "base", game_asset_key)
            elif game_asset_key == "None":
                self.remove_survivor_attribute(p)
            else:
                self.logger.debug("[%s] direct Survivor Sheet update: %s -> %s (%s)" % (self.User, p, game_asset_key, self))
                self.survivor[p] = game_asset_key


        # enforce ability and impairment maxes
        for asset_key in self.survivor["abilities_and_impairments"]:
            if asset_key not in Abilities.get_keys():
                pass
            else:
                asset_dict = Abilities.get_asset(asset_key)
                if "max" in asset_dict.keys():
                    asset_count = self.survivor["abilities_and_impairments"].count(asset_key)
                    while asset_count > asset_dict["max"]:
                        self.logger.warn("[%s] survivor '%s' has '%s' x%s (max is %s)." % (self.User, self, asset_key, asset_count, asset_dict["max"]))
                        self.survivor["abilities_and_impairments"].remove(asset_key)
                        self.logger.info("[%s] automatically removed extra asset key '%s' from survivor '%s'." % (self.User, asset_key, self))
                        asset_count = self.survivor["abilities_and_impairments"].count(asset_key)

        # idiot-proof the hit boxes
        for hit_tuplet in [("arms_damage_light","arms_damage_heavy"), ("body_damage_light", "body_damage_heavy"), ("legs_damage_light", "legs_damage_heavy"), ("waist_damage_light", "waist_damage_heavy")]:
            light, heavy = hit_tuplet
            if heavy in self.survivor.keys() and not light in self.survivor.keys():
                self.survivor[light] = "checked"

        # prevent movement from going below 1
        if int(self.survivor["Movement"]) < 1:
            self.survivor["Movement"] = 1

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
                link_text += " [%s]" % self.get_sex("html")

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





    def update_cursed_items(self, action=None, cursed_item=None):
        """ Manages a survivor's cursed_items attribute, which is just a list
        of items. Logs to the setttlement event log, etc. """

        if action is None or cursed_item is None:
            self.logger.warn("[%s] 'action' and 'cursed_item' kwargs must not be None type." % (self.User))
            return None

        # now do it to it
        if not "cursed_items" in self.survivor.keys():
            self.survivor["cursed_items"] = []

        all_cursed_items = self.Settlement.get_api_asset("game_assets", "cursed_items")
        ci_dict = all_cursed_items[cursed_item]


        def add(cursed_item):
            self.survivor["cursed_items"].append(cursed_item)
            if "abilities_and_impairments" in ci_dict.keys():
                for ai in ci_dict["abilities_and_impairments"]:
                    ai_dict = self.Settlement.get_api_asset("game_assets","abilities_and_impairments")[ai]
                    self.add_game_asset("abilities_and_impairments", ai_dict["name"])
            self.Settlement.log_event("%s is cursed! %s added %s to %s's cursed items." % (self, self.User.user["login"], ci_dict["name"], self.survivor["name"]))
            self.logger.debug("[%s] added cursed item key '%s' to %s." % (self.User, cursed_item, self))
        def rm(cursed_item):
            self.survivor["cursed_items"].remove(cursed_item)
            if "abilities_and_impairments" in ci_dict.keys():
                for ai in ci_dict["abilities_and_impairments"]:
                    self.rm_game_asset("abilities_and_impairments", ai)
            self.Settlement.log_event("%s removed %s from %s's cursed items." % (self.User.user["login"], ci_dict["name"], self.survivor["name"]))
            
            self.logger.debug("[%s] removed cursed item key '%s' from %s." % (self.User, cursed_item, self))

        if action=="toggle":
            if cursed_item in self.get_api_asset("cursed_items"):
                rm(cursed_item)
                return False
            elif cursed_item not in self.get_api_asset("cursed_items"):
                add(cursed_item)
                return True
        else:
            self.logger.warn("[%s] unknown action '%s' specified!" % (self.User, action))
            return None



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


    def render_dragon_controls(self, return_type=None):
        """ Returns the survivor's constellation table, either as a dict of
        component info or as an HTML table. """

        if self.Settlement.get_campaign() != "People of the Stars":
            return ""

        self.set_constellation_traits()

        table_map = game_assets.potstars_constellation["map"]

        rows = {}
        for k,v in table_map.iteritems():
            col = v[0]
            row = int(v[1])
            if not row in rows.keys():
                rows[row] = {col: k}
            else:
                rows[row][col] = k

        active_td = []
        for t in self.survivor["constellation_traits"]:
            if t in table_map.keys():
                active_td.append(table_map[t])

        table_formulae = game_assets.potstars_constellation["formulae"]
        active_th = []
        for const in table_formulae.keys():
            jackpot = set(table_formulae[const])
            if jackpot.issubset(set(active_td)):
                active_th.append(const)

        constellation_table = (active_th, active_td)


        html_table = html.survivor.constellation_table_top
        html_table += html.survivor.constellation_table_row_top.safe_substitute(
        )

        for t in [(1,"Gambler"),(2,"Absolute"),(3,"Sculptor"),(4,"Goblin")]:
            row, const = t
            row_cells = ""
            for col in sorted(rows[row]):
                cell_id = "%s%s" % (col,row)
                td_class = ""
                if cell_id in active_td:
                    td_class="active"
                row_cells += html.survivor.constellation_table_cell.safe_substitute(
                    value=rows[row][col],
                    td_class=td_class
                )
            html_table += html.survivor.constellation_table_row.safe_substitute(
                th = const,
                cells = row_cells,
            )

        html_table += html.survivor.constellation_table_bot

        const_options = ""
        for const in sorted(table_formulae.keys()):
            selected = ""
            if const in active_th:
                 selected = "selected"
            if self.survivor["constellation"] is not None:
                if const == self.survivor["constellation"]:
                    selected = "selected"
            const_options += html.survivor.constellation_table_select_option.safe_substitute(
                selected=selected,
                value=const
            )

        html_table += html.survivor.constellation_table_select_top.safe_substitute(
            survivor_id = self.survivor["_id"],
            options=const_options,
        )
        html_table += html.survivor.constellation_table_select_bot.safe_substitute(
            survivor_id = self.survivor["_id"],
        )

        output = html.survivor.dragon_traits_controls.safe_substitute(
            trait_count=len(self.survivor["constellation_traits"]),
            constellation_table = html_table,
        )
        return output




    def render_attribute_controls(self, return_type="survivor_sheet"):
        """ Renders the controls for modifying/managing/investigating the
        survivor's attributes, e.g. MOV, ACC, STR, etc. """

        if return_type == "survivor_sheet":
            output = html.survivor.survivor_sheet_attrib_controls_top
            for token in survivor_attrib_controls.tokens:
                output += html.survivor.survivor_sheet_attrib_controls_token.safe_substitute(
                    survivor_id=self.survivor["_id"],
                    controls_id=token["long_name"] + "_controller",
                    base_value=self.survivor[token["long_name"]],
                    gear_value=self.get_survivor_attribute(token["long_name"],"gear"),
                    tokens_value=self.get_survivor_attribute(token["long_name"],"tokens"),
                    token_class=token["token_button_class"],
                    short_name=token["short_name"],
                    long_name=token["long_name"],
                )
            output += html.survivor.survivor_sheet_attrib_controls_bot
            return output
        else:
            self.logger.error("Unsupported 'return_type' kwarg value: %s" % return_type)
            return ""


    @ua_decorator
    def render_html_form(self):
        """ Render a Survivor Sheet for the survivor.

        This is just like the render_html_form() method of the settlement
        class: a giant tangle-fuck of UI/UX logic that creates the form for
        modifying a survivor.

        It's going on one year and this is still a total debacle. This needs to
        be refactored in the next big clean-up push.
        """


        survivor_survival_points = int(self.survivor["survival"])
        if survivor_survival_points > int(self.Settlement.settlement["survival_limit"]):
            if 'Beta Challenge Scenarios' in self.Settlement.get_expansions("list_of_names"):  # do not enforce survival limit if BCS is
                pass                                                            # active
            else:
                survivor_survival_points = int(self.Settlement.settlement["survival_limit"])

        flags = {}
        for flag in self.flags:
            flags[flag] = ""
            if flag in self.survivor.keys():
                flags[flag] = self.survivor[flag]

        exp = self.Settlement.get_expansions("list_of_names")

        # fighting arts widgets
        fighting_arts_picker = FightingArts.render_as_html_dropdown(exclude=self.survivor["fighting_arts"], Settlement=self.Settlement)
        if len(self.survivor["fighting_arts"]) >= 3:
            fighting_arts_picker = ""

        # disorders widgets
        disorders_picker = Disorders.render_as_html_dropdown(exclude=self.survivor["disorders"], Settlement=self.Settlement)
        if len(self.survivor["disorders"]) >= 3:
            disorders_picker = ""


        death_button_class = "unpressed_button"
        if "dead" in self.survivor.keys():
            death_button_class = "survivor_is_dead"

        COD = ""
        custom_COD = ""
        if "cause_of_death" in self.survivor.keys():
            COD = self.survivor["cause_of_death"]
            custom_COD = self.survivor["cause_of_death"]

        rm_controls = ""
        if self.User.get_preference("show_remove_button"):
            rm_controls = html.survivor.survivor_sheet_rm_controls.safe_substitute(
                name=self.survivor["name"],
                survivor_id=self.survivor["_id"],
            )

        output = html.survivor.form.safe_substitute(
            survivor_id = self.survivor["_id"],
            desktop_avatar_img = self.get_avatar("html_desktop"),
            mobile_avatar_img = self.get_avatar("html_mobile"),
            name = self.survivor["name"],
            email = self.survivor["email"],
            courage = self.survivor["Courage"],
            understanding = self.survivor["Understanding"],
            sex = self.get_sex(),
            survival = survivor_survival_points,
            survival_limit = self.Settlement.get_attribute("survival_limit"),
            survival_max = self.Settlement.get_survivor_survival_max(),
            hunt_xp = self.survivor["hunt_xp"],
            survival_actions = self.get_survival_actions(return_as="html_checkboxes"),
            departure_buffs = self.Settlement.get_bonuses("departure_buff", return_type="html"),
            settlement_buffs = self.Settlement.get_bonuses("survivor_buff", return_type="html"),
            hunt_xp_3_event = self.Settlement.get_story_event("Bold"),
            courage_3_event = self.Settlement.get_story_event("Insight"),


            weapon_proficiency = self.survivor["Weapon Proficiency"],   # this is the score
            weapon_proficiency_options = WeaponProficiencies.render_as_html_toggle_dropdown(selected=self.survivor["weapon_proficiency_type"], expansions=exp),

            # controls
            epithet_controls = self.get_epithets("html_angular"),
            remove_survivor_controls = rm_controls,

            # checkbox status
            dead_checked = flags["dead"],
            favorite_checked = flags["favorite"],
            retired_checked = flags["retired"],
            public_checked = flags["public"],
            skip_next_hunt_checked = flags["skip_next_hunt"],
            cannot_spend_survival_checked = flags["cannot_spend_survival"],

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

            # affinities
            affinity_controls = self.get_affinities("survivor_sheet_controls"),
            red_affinities = self.get_affinities()["red"],
            blue_affinities = self.get_affinities()["blue"],
            green_affinities = self.get_affinities()["green"],


            cannot_use_fighting_arts_checked = flags["cannot_use_fighting_arts"],
            fighting_arts = self.get_fighting_arts("formatted_html"),
            add_fighting_arts = fighting_arts_picker,
            rm_fighting_arts = self.get_fighting_arts("html_select_remove"),

            disorders = self.get_disorders(return_as="formatted_html"),
            add_disorders = disorders_picker,
            rm_disorders = self.get_disorders(return_as="html_select_remove"),

            abilities_and_impairments = self.get_abilities_and_impairments("html_formatted"),
            add_abilities_and_impairments = Abilities.render_as_html_dropdown(
                excluded_type="curse",
                disable=Abilities.get_maxed_out_abilities(self.survivor["abilities_and_impairments"]),
                Settlement=self.Settlement,
                ),
            rm_abilities_and_impairments = self.get_abilities_and_impairments("html_select_remove"),

            # lineage
            parents = self.get_parents(return_type="html_select"),
            children = self.get_children(return_type="html"),
            siblings = self.get_siblings(return_type="html"),
            partners = self.get_intimacy_partners("html"),

            # controls of death
            death_button_class = death_button_class,
            custom_cause_of_death = custom_COD,

            # optional and/or campaign-specific controls and modals
            partner_controls = self.get_partner("html_controls"),
            expansion_attrib_controls = self.get_expansion_attribs("html_controls"),
            dragon_controls = self.render_dragon_controls(),

            # angularjs application controls
            survivor_notes = self.get_survivor_notes("angularjs"),
            survivor_attrib_controls = self.render_attribute_controls(),
        )
        return output



#
#   SETTLEMENT CLASS
#

class Settlement:


    def __repr__(self):
        return self.get_name_and_id()


    def __init__(self, settlement_id=False, name=False, campaign=False, session_object=None, update_mins=True, cgi_params=None):
        """ Initialize with a settlement from mdb. """
        self.logger = get_logger()
        self.cgi_params = cgi_params

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

        # 2016-12 timelines with None type events
        for ly in self.settlement["timeline"]:
            for ly_k in ly.keys():
                if ly_k in ["quarry_event","nemesis_encounter","story_event","settlement_event"]:
                    for i in ly[ly_k]:
                        if i is None:
                            self.logger.error("[%s] forbidden timeline event found: %s" % (self.User, i))
                            self.logger.debug("[%s] removing '%s' from LY %s" % (self.User, i, ly["year"]))
                            ly[ly_k].remove(i)


        # SUMMER 2016 bug: fix broken/incorrectly normalized innovations
        def normalize(settlement_attrib, incorrect, correct):
            if incorrect in self.settlement[settlement_attrib]:
                self.settlement[settlement_attrib].remove(incorrect)
                self.settlement[settlement_attrib].append(correct)
                self.logger.debug("Normalized '%s' (%s) to '%s' for %s." % (incorrect,settlement_attrib,correct,self.get_name_and_id()))

        mixed_case_tuples = [
            ("innovations", "Song Of The Brave", "Song of the Brave"),
            ("innovations", "Clan Of Death", "Clan of Death"),
            ("principles", "Survival Of The Fittest", "Survival of the Fittest"),
            ("principles", "Protect The Young", "Protect the Young"),
        ]
        for t in mixed_case_tuples:
            normalize(t[0],t[1],t[2])


        # keep innovations and principles separated
        for innovation_key in self.settlement["innovations"]:
            if innovation_key in Innovations.get_keys():
                innovation_dict = Innovations.get_asset(innovation_key)
                if "type" in innovation_dict.keys() and innovation_dict["type"] == "principle":
                    self.settlement["innovations"].remove(innovation_key)
                    self.logger.debug("Automatically removed principle '%s' from settlement '%s' (%s) innovations." % (innovation_key, self.settlement["name"], self.settlement["_id"]))

        # fix timelines without a zero year for prologue
        years = []
        for ly in self.settlement["timeline"]:
            years.append(ly["year"])
            if ly["year"] == 1:
                if "quarry_event" in ly:
                    try:
                        ly["quarry_event"].remove(u'White Lion (First Story)')
                        self.logger.debug("Removed 'White Lion (First Story) from LY 1 for %s" % self.get_name_and_id())
                    except:
                        pass
                    try:
                        ly["settlement_event"].remove(u'First Day')
                        self.logger.debug("Removed 'First Day' event from LY1 for %s" % self.get_name_and_id())
                    except:
                        pass
        if not 0 in years:
            year_zero = {"year": 0, "settlement_event": [u"First Day"], "quarry_event": [u'White Lion (First Story)']}
            self.settlement["timeline"].append(year_zero)
            self.logger.debug("Added errata LY 0 to %s" % self.get_name_and_id())



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

    def new(self):
        """ Creates a new settlement based on self.cgi_params. If you want to do
        this some other way, it's going to require a total rebuild of this
        method. Just FYI.

        This happens in two stages, presently. First, we process the CGI params
        that determine the fundamental characteristics of the settlement and
        save a basic settlement dictionary to the MDB.

        Next, we pull that settlement and set it as the 'settlement' attribute
        of the Settlement object (i.e self) and then start in on the rest of the
        CGI params, e.g. ones that require an initialized Settlement object.

        She might not look like much, but she's got it where it counts.
        """

        self.logger.debug("[%s] creating a new settlement..." % self.User)

        settlement = {
            "name": "Unknown",
            "campaign": "People of the Lantern",
            "created_on": datetime.now(),
            "created_by": self.User.user["_id"],
            "survival_limit": 1,
            "lantern_year": 0,
            "death_count": 0,
            "milestone_story_events": [],
            "innovations": [],
            "locations": [],
            "quarries": ["White Lion"],
            "nemesis_monsters": {"Butcher": [], },
            "defeated_monsters": [],
            "population": 0,
            "lost_settlements": 0,
            "principles": [],
            "expansions": [],
            "storage": [],
            "admins": [self.User.user["login"]],
            "timeline": game_assets.default_timeline,
        }

        # set the campaign
        if "campaign" in self.cgi_params:
            settlement["campaign"] = self.cgi_params["campaign"].value

        # set the name if the user wants
        if "settlement_name" in self.cgi_params:
            settlement["name"] = self.cgi_params["settlement_name"].value
        elif "settlement_name" not in self.cgi_params and self.User.get_preference("random_names_for_unnamed_assets"):
            name_list = settlement_names.core
            settlement["name"] = random.choice(name_list)

        # sometimes campaign assets have additional attribs
        c_dict = api.route_to_dict("/campaign", params={"name": settlement["campaign"]})
        for optional_attrib in ["storage","expansions","timeline","nemesis_monsters"]:
            if optional_attrib in c_dict.keys():
                settlement[optional_attrib] = c_dict[optional_attrib]

        # create the settlement and update the Settlement obj
        settlement_id = mdb.settlements.insert(settlement)
        self.settlement = mdb.settlements.find_one({"_id": settlement_id})
        self.Session.set_current_settlement(settlement_id)
        self.logger.debug("[%s] initialized a new settlement successfully!" % (self.User))

        # now, continue through the CGI params, operating on the 
        if "create_prologue_survivors" in self.cgi_params:
            self.first_story()

        # prefab survivors go here
        for s in self.cgi_params["survivors"]:
            if s.value != "None":
                s_dict = game_assets.survivors[s.value]
                n = Survivor(params=None, session_object=self.Session, suppress_event_logging=True)
                n.set_attrs({"name": s.value})
                n.set_attrs(s_dict["attribs"])

        self.save() # this is the LAST save
        self.logger.debug("[%s] legacy settlement creation method complete!" % (self.User))

        #
        #   settlement is initialized and saved; only API-based update methods
        #   may be called past this point! DO NOT save the settlement any more
        #   within this method, let ye overwrite any API-side changes!
        #

        if "expansions" in self.cgi_params:
            if type(self.cgi_params["expansions"]) == list:
                req_expansions = [e.value for e in self.cgi_params["expansions"]]
            else:
                req_expansions = [self.cgi_params["expansions"].value]
            response = api.post_JSON_to_route("/settlement/add_expansions/%s" % settlement_id, req_expansions)
            if response.status_code == 200:
                self.logger.debug("[%s] posted %s expansions to API successfully!" % (self.User, len(req_expansions)))
            else:
                self.logger.error("[%s] add_expansions API call returned %s!" % (self.User, response.status_code))


        # to play us out!? I don't know what means: to play us out!
        self.logger.info("[%s] created new settlement %s - (%s)." % (self.User, self, self.settlement["campaign"]))
        self.log_event("%s founded!" % self.settlement["name"])

        return settlement_id



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


    def bulk_add_survivors(self, male=0, female=0):
        """ Adds 'male' male survivors and 'female' female survivors the settlement. """

        for s in range(male):
            m = Survivor(params=None, session_object=self.Session, suppress_event_logging=True, update_mins=False)
            m.set_attrs({"public": "checked"})
        for s in range(female):
            f = Survivor(params={"sex": "F"}, session_object=self.Session, suppress_event_logging=True, update_mins=False)
            f.set_attrs({"public": "checked"})
        self.log_event("%s added %s male and %s female survivors to %s!" % (self.User, male, female, self.settlement["name"]))
        self.logger.debug("[%s] bulk-added %s male and %s female survivors to %s" % (self.User.user["login"], male, female, self))


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
    #   Settlement game asset management methods below
    #

    def add_expansions(self, e):
        """ Interim/legacy support method. Adds an expansion via API POST. """
        if type(e) != list:
            e = [e]
        response = api.post_JSON_to_route("/settlement/add_expansions/%s" % self.settlement["_id"], e)
        if response.status_code == 200:
            self.logger.debug("[%s] added %s expansions to %s via API call!" % (self.User, e, self))
        else:
            self.logger.error("[%s] add_expansions API call returned %s!" % (self.User, response.status_code))

    def rm_expansions(self, e):
        """ Interim/legacy support method. Adds an expansion via API POST. """
        if type(e) != list:
            e = [e]
        response = api.post_JSON_to_route("/settlement/rm_expansions/%s" % self.settlement["_id"], e)
        if response.status_code == 200:
            self.logger.debug("[%s] removed %s expansions from %s via API call!" % (self.User, e, self))
        else:
            self.logger.error("[%s] rm_expansions API call returned %s!" % (self.User, response.status_code))





    #
    #   Settlement reference, retrieval and look-up methods below
    #

    def get_survivor_survival_max(self):
        """ Gets the limit that the survivor can set the Survival to on the
        Sheet by checking epansion properties. """

        limit = self.get_attribute("survival_limit")

        for e in self.get_api_asset("sheet","expansions"):
            e_dict = self.get_api_asset("game_assets","expansions")[e]
            if "enforce_survival_limit" in e_dict.keys():
                if not e_dict["enforce_survival_limit"]:
                    return 666

        return limit


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



    def first_story(self):
        """ Adds "First Story" survivors, items and Hunting Party setup to the
        settlement. """

        self.add_game_asset("storage", "Founding Stone", 4)
        self.add_game_asset("storage", "Cloth", 4)

        for i in range(2):
            m = Survivor(params=None, session_object=self.Session, suppress_event_logging=True)
            m.set_attrs({"Waist": 1})
            m.join_departing_survivors()
            m.save()
        for i in range(2):
            f = Survivor(params={"sex":"F"}, session_object=self.Session, suppress_event_logging=True)
            f.set_attrs({"Waist": 1})
            f.join_departing_survivors()
            f.save()
        self.log_event("Added four new survivors and Starting Gear to settlement storage")

        # API operations
        q_json = json.dumps({"current_quarry": "White Lion (First Story)"})
        api.post_JSON_to_route("/settlement/set_current_Quarry/%s" % self.settlement["_id"], q_json)

        self.add_timeline_event({
            "ly": self.get_ly(),
            "user_login": self.User.user["login"],
            "type": "showdown_event",
            "name": "White Lion (First Story)",
            })

        self.logger.info("[%s] added 'First Story' assets to %s" % (self.User, self))



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

        milestones_dict = self.get_campaign("dict")["milestones"]
        for m_key in milestones_dict.keys():

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


    def get_available_weapon_masteries(self):
        """ Uses the settlement's API asset to return a list of available weapon
        mastery names. """

        available = []
        for k,v in self.get_api_asset("game_assets","weapon_masteries").iteritems():
            available.append(v["name"])
        return available


    def validate_weapon_masteries(self):
        """ Checks the possible weapon masteries the settlement might have and,
        if any of them are among the settlement["innovations"], makes sure that
        a survivor still has the mastery. If there are no survivors with the
        mastery, auto-remove the mastery from settlement["innovations"]. """

        survivor_weapon_masteries = []
        for weapon_mastery in self.get_available_weapon_masteries():
            for survivor in self.get_survivors():
                if weapon_mastery in survivor["abilities_and_impairments"]:
                    survivor_weapon_masteries.append(weapon_mastery)

        for weapon_mastery in self.get_available_weapon_masteries():
            if weapon_mastery in self.settlement["innovations"]:
                if weapon_mastery not in survivor_weapon_masteries:
                    self.logger.debug("""[%s] weapon mastery '%s' is in settlement["innovations"] for %s, but not present on any survivor's A&I attribute.. Updating settlement...""" % (self.User, weapon_mastery, self))
                    self.rm_game_asset("innovations", weapon_mastery)
                    self.log_event("Automatically removed '%s' weapon mastery from settlement Innovations, since no survivor possesses the mastery." % (weapon_mastery))


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


    def export(self, export_type):
        """ Dumps the settlement to a file, e.g. XLS or PDF. """

        self.logger.debug("[%s] Exporting campaign %s as '%s'..." % (self.User, self, export_type))

        if export_type == "XLS":
            book = export_to_file.xls(self.settlement, self.get_survivors(), self.Session)
            s = StringIO()
            book.save(s)
            length = s.tell()
            s.seek(0)
            self.logger.debug("[%s] Export successful. Returning XLS payload." % self.User)
            return s, length

        return "Invalid export type.", 0


    def add_weapon_mastery(self, master, mastery_string):
        """ Adds a weapon mastery to settlement innovations. Make sure that the
        'master' arg is a Survivor object. The 'mastery_string' can be whatever,
        so long as it follows the general naming conventions for masteries. """

        all_masteries = self.get_api_asset("game_assets","weapon_masteries")
        mastery_lookup = {}
        for m in all_masteries.keys():
            mastery_lookup[all_masteries[m]["name"]] = m

        m_handle = mastery_lookup[mastery_string]
        M = all_masteries[m_handle]

        if not M.get("add_to_innovations", True):
            self.logger.debug("[%s] Not adding '%s' to settlement innovations..." % (self.User, mastery_string))
            return True

        self.settlement["innovations"].append(M["handle"])
        self.log_event("%s has become a %s master!" % (master, M["weapon"]))
        self.log_event("'%s' added to settlement Innovations!" % mastery_string)
        self.logger.debug("[%s] added '%s' to %s Innovations! (Survivor: %s)" % (self.User, M["handle"], self, master))

        self.save()



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


    def get_survival_actions(self, return_as=False):
        """ Available survival actions depend on innovations. This func checks
        the settlement's innovations and returns a list of available survival
        actions for survivors to use during Showdowns. """

        survival_actions = []
        available = self.get_api_asset("game_assets","available_survival_actions")
        for sa in available:
            survival_actions.append(available[sa]["name"])

        return sorted(survival_actions)


    def get_bonuses(self, bonus_type, return_type=False, update_mins=True):
        """ Returns the buffs/bonuses that settlement gets. 'bonus_type' is
        required and can be 'departure_buff', 'settlement_buff' or
        'survivor_buff'.  """

        innovations = copy(self.get_game_asset("innovations", update_mins=update_mins))
        innovations.extend(self.settlement["principles"])

        buffs = {}

        for innovation_key in innovations:
            if innovation_key in Innovations.get_keys() and bonus_type in Innovations.get_asset(innovation_key).keys():
                buffs[innovation_key] = Innovations.get_asset(innovation_key)[bonus_type]

        # support for campaign settlement_buff
        campaign_dict = self.get_campaign("dict")
        if bonus_type in campaign_dict.keys():
            buffs[self.get_campaign()] = campaign_dict[bonus_type]

        if return_type == "html":
            output = ""
            for k in buffs.keys():
                output += '<p class="settlement_buff"><i>%s:</i> %s</p>\n' % (k, buffs[k])
            return output

        return buffs


    def get_endeavors(self, return_type=False):
        """ Returns available endeavors. This used to be in 'get_bonuses()', but
        it's such an insane coke-fest of business logic, it got promoted into
        it's own method. """

        # this is a list of locations and innovations together that will be used
        #  later to determine if the settlement meets the requirements for an
        #  endeavor
        prereq_assets = copy(self.settlement["innovations"])
        prereq_assets.extend(self.settlement["locations"])

        # now create our list of all possible sources: any game asset with an
        #  an endeavor should be in this
        sources = copy(self.get_game_asset("innovations", update_mins=False, handles_to_names=True))
        sources.extend(self.settlement["principles"])
        sources.extend(self.settlement["locations"])
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
            buffs[self.get_campaign()] = self.get_campaign("dict")["endeavors"]

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


    def get_nemeses(self, return_type=None):
        """ Use the 'return_type' arg to specify a special return type, or leave
        unspecified to get sorted list of nemesis monsters back. """

        nemesis_monster_keys = sorted(self.settlement["nemesis_monsters"].keys())

        if return_type == "comma-delimited":
            return ", ".join(nemesis_monster_keys)

        if return_type == "list_of_options":
            n_options = []


            def add_nemesis_to_options(nem, n_levels):
                """ Stupid DRYness func to update the option drop-down/list. """
                for i in range(1,n_levels+1):
                    if exp_key in self.settlement["nemesis_monsters"] and "Lvl %s" % i in self.settlement["nemesis_monsters"][nem]:
                        pass
                    else:
                        n_options.append("%s Lvl %s" % (nem,i))


            # check expansion content and add always available nems
            for exp_key in self.get_expansions():
                exp_dict = self.get_expansions("dict")[exp_key]
                if "always_available_nemesis" in exp_dict.keys():
                    n_key = exp_dict["always_available_nemesis"]
                    n_levels = Nemeses.get_levels(n_key)
                    add_nemesis_to_options(n_key, n_levels)

            # do the same check for the campaign
            c_dict = self.get_campaign("dict")
            if "always_available_nemesis" in c_dict.keys():
                n_key = c_dict["always_available_nemesis"]
                n_levels = Nemeses.get_levels(n_key)
                add_nemesis_to_options(n_key, n_levels)

            # now process settlement nem keys
            for k in nemesis_monster_keys:
                if k in Nemeses.get_keys() and "no_levels" in Nemeses.get_asset(k).keys():
                    n_options.append(k)
                else:
                    # support for nemeses with variable levels
                    if k in Nemeses.get_keys() and "levels" in Nemeses.get_asset(k).keys():
                        n_levels = (Nemeses.get_asset(k)["levels"] + 1)
                    else:
                        n_levels = 4

                    for i in range(1,n_levels):
                        if "Lvl %s" % i not in self.settlement["nemesis_monsters"][k]:
                            n_options.append("%s Lvl %s" % (k,i))

            # finally, check defeated monsters and remove those options
            for d_mon in self.settlement["defeated_monsters"]:
                if d_mon in n_options:
                    n_options.remove(d_mon)

            return n_options

        if return_type == "html_buttons":
            output = '<input class="hidden" type="submit" name="increment_nemesis" value="None"/>\n'
            for k in nemesis_monster_keys:
                output += '<p><b>%s</b> ' % k
                if k in Nemeses.get_keys() and "no_levels" in Nemeses.get_asset(k).keys():
                    levels = ["Lvl 1"]
                else:
                    levels = ["Lvl 1", "Lvl 2", "lvl 3"]
                for level in levels:
                    if level not in self.settlement["nemesis_monsters"][k]:
                        output += ' <button id="increment_nemesis" name="increment_nemesis" value="%s">%s</button> ' % (k,level)
                    else:
                        output += ' <button id="increment_nemesis" class="disabled" disabled>%s</button> ' % level
                output += '</p>\n'

            return output

        return self.settlement["nemesis_monsters"].keys()



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
                if "in_hunting_party" in survivor.keys():
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
                if S.is_savior():
                    annotation += '&ensp; <span class="survivor_annotation affinity_%s">%s Savior</span><br/>' % (S.is_savior(), S.is_savior().capitalize())
                user_owns_survivor = False
                disabled = "disabled"

                if survivor["email"] == user_login or current_user_is_settlement_creator or "public" in survivor.keys():
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
                if "in_hunting_party" in S.survivor.keys():
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
                    sex = S.get_sex("html"),
                    favorite = is_favorite,
                    hunt_xp = S.survivor["hunt_xp"],
                    survival = S.survivor["survival"],
                    insanity = S.survivor["Insanity"],
                    courage = S.survivor["Courage"],
                    understanding = S.survivor["Understanding"],
                )

                # finally, file our newly minted survivor in a group:
                if "in_hunting_party" in S.survivor.keys():
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

                    if group["name"] == "Departing" and group["survivors"] != []:
                        bonuses = self.get_bonuses("departure_buff")
                        if bonuses != {}:
                            output += '<hr class="invisible"><span class="tiny_break"></span>'
                        for b in sorted(bonuses.keys()):
                            output += "<p><b>%s:</b> %s</p>" % (b, bonuses[b])
                        if bonuses != {}:
                            output += '<span class="tiny_break"/></span>'


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
            if "in_hunting_party" in s.keys():
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
                self.add_kill(quarry_key)
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
            if self.get_endeavor_tokens() == 0:
                self.update_endeavor_tokens(len(returning_survivor_name_list))
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
        """ Returns the campaign of the settlement. Not to be confused with the
        User.get_campaigns() method, which returns campaigns a user is currently
        associated with. """

        if not "campaign" in self.settlement.keys():
            self.settlement["campaign"] = "People of the Lantern"

        if return_type == "dict":
            campaign_dict = game_assets.campaigns[self.settlement["campaign"]]
            if not "forbidden" in campaign_dict.keys():
                campaign_dict["forbidden"] = []
            return campaign_dict

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
        response = api.post_JSON_to_route("/settlement/add_timeline_event/%s" % self.settlement["_id"], event)
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
        response = api.post_JSON_to_route("/settlement/rm_timeline_event/%s" % self.settlement["_id"], event)
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


    def set_principle(self, principle=None, election=None):
        """ Better than the deprecated update_principles() method, but
        needs to know what principle you're setting in order to work. """

        if election in self.get_principles():
            self.logger.debug("[%s] is setting %s %s principle to its current value, '%s'." % (self.User, self, principle, election))
            return True

        if principle is None:
            return None

        # now that we've sanity checked, turn 'principle' and 'election' into
        #   dictionaries using the API
        available = self.get_api_asset("game_assets","principles_options")
        for p in available:
            if p["handle"] == principle:
                principle=p

        if election != "UNSET":
            election = principle["options"][election]
            if election["name"] in self.settlement["principles"]:
                self.logger.warn("[%s] attempting to set principle that is already set!" % self.User)
                return None

        # this is our UNSET logic
        for o_handle in principle["option_handles"]:
            o_dict = principle["options"][o_handle]
            if o_dict["name"] in self.get_principles():
                self.logger.debug("[%s] unset %s %s principle '%s'." % (self.User, self, principle["name"], o_dict["name"]))
                self.log_event("%s removed the settlement %s principle." % (self.User, principle["name"]))
                self.settlement["principles"].remove(o_dict["name"])
                if "current_survivor" in o_dict.keys():
                    self.increment_all_survivors(o_dict["current_survivor"], action="decrement")

        if election != "UNSET":
            self.logger.debug("[%s] set %s %s principle '%s'." % (self.User, self, principle["name"], election["name"]))
            self.log_event("Settlement %s principle is now set to '%s'" % (principle["name"], election["name"]))
            self.settlement["principles"].append(election["name"])
            if "current_survivor" in election.keys():
                self.increment_all_survivors(election["current_survivor"])


    def increment_all_survivors(self, d={}, action="increment"):
        """ d is a dictionary of attributes with numerical values. This method
        gets all survivors in the settlement and increments each attribute for
        each survivor. Set 'action' to decrement to do the reverse. """

        for s in self.get_survivors():
            for attrib in d.keys():
                self.logger.debug("Attrib: '%s' ; Value: %s (%s)" % (attrib, d[attrib], type(d[attrib])))
                if action == "increment":
                    s[attrib] = int(s[attrib]) + d[attrib]
                elif action == "decrement":
                    s[attrib] = int(s[attrib]) - d[attrib]
            self.logger.debug("[%s] automatically %sed %s: %s" % (self.User, action, s["name"], d))
            mdb.survivors.save(s)
        d_string = ["%s: %s" % (attrib, value) for attrib,value in d.iteritems()]
        self.log_event("Automatically %sed all survivors: %s" % (action, ", ".join(d_string)))


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


    def update_endeavor_tokens(self, value=0):
        """ Adds 'value' to self.settlement["endeavor_tokens"]. """

        cur_val = self.get_endeavor_tokens()
        new_val = cur_val + int(value)
        if new_val < 0:
            new_val = 0
        self.settlement["endeavor_tokens"] = new_val
        self.logger.debug("[%s] updated endeavor tokens for %s. New total %s" % (self.User, self, self.get_endeavor_tokens()))


    def update_lost_settlements(self, new_value=None):
        """ Updates the settlement's lost settlements attribs. """

        if new_value is None:
            return False

        if int(new_value) <= 0:
            self.settlement["lost_settlements"] = 0
        else:
            self.settlement["lost_settlements"] = int(new_value)
        self.logger.debug("[%s] set %s lost settlements for %s" % (self.User, self.settlement["lost_settlements"], self))

    def update_quarries(self, action, quarry_handle):
        """ Operates on self.settlement["quarries"]. """

        try:
            m = self.get_api_asset("game_assets","monsters")[quarry_handle]
        except Exception as e:
            self.logger.exception(e)
            self.logger.error("[%s] tried to work with quarry handle '%s', but that quarry handle could not be retrieved from API data!" % (self.User, quarry_handle))
            return False

        if action == "add":
            self.settlement["quarries"].append(quarry_handle)
            self.log_event("%s added '%s' to the settlement quarries list." % (self.User.user["login"], m["name"]))
        elif action == "rm":
            self.settlement["quarries"].remove(quarry_handle)
            self.log_event("%s removed '%s' from the settlement quarries list." % (self.User.user["login"], m["name"]))
        else:
            logger.warn("[%s] the update_quarries() method does not support the '%s' action!" % (self.User,action))
        self.logger.debug("[%s] updated settlement quarries (%s %s)" % (self.User, action, quarry_handle))



    def update_location_level(self, location_name, lvl):
        """ Changes 'location_name' level to 'lvl'. """
        self.logger.debug("[%s] Location '%s' level update initiated by %s..." % (self, location_name, self.User))

        if len(lvl.split(":"))==2:
            lvl = int(lvl.split(":")[1])
        else:
            lvl = int(lvl)
        if not "location_levels" in self.settlement.keys():
            self.settlement["location_levels"] = {location_name: lvl}
        else:
            self.settlement["location_levels"][location_name] = lvl
        self.logger.debug("[%s] Location '%s' level set to %s." % (self, location_name, lvl))


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


    def get_endeavor_tokens(self):
        """ Returns self.settlement["endeavor_tokens"] as an int. """

        if not "endeavor_tokens" in self.settlement.keys():
            self.settlement["endeavor_tokens"] = 0
        return self.settlement["endeavor_tokens"]


    def get_lost_settlements(self, return_type=None):
        """ Returns the settlement's lost settlements as an int, or as JS
        object (for use with angular controls). """

        lost = int(self.settlement["lost_settlements"])

        return lost



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


    def add_kill(self, monster_desc):
        """ Adds a kill to the settlement: appends it to the 'defeated_monsters'
        monsters and also to the settlement's kill_board. """

        kill_board_dict = {
            "settlement_id": self.settlement["_id"],
            "settlement_name": self.settlement["name"],
            "kill_ly": self.get_ly(),
            "name": monster_desc,
            "created_by": self.User.user["_id"],
            "created_on": datetime.now(),
            "handle": "other",
        }



        #
        #   V2 API call to try to get more monster info
        #

        try:
            api_asset = api.route_to_dict("monster", params={"name": monster_desc})
            if api_asset != {}:
                self.logger.debug("[%s] API call successful: monster asset retrieved." % self.User)
                kill_board_dict["name"] = api_asset["name"]
                kill_board_dict["raw_name"] = monster_desc
                kill_board_dict["handle"] = api_asset["handle"]
                kill_board_dict["type"] = api_asset["type"]
                for aux_attrib in ["level", "comment"]:
                    if aux_attrib in api_asset.keys():
                        kill_board_dict[aux_attrib] = api_asset[aux_attrib]
                self.logger.debug("[%s] Defeated monster dict updated with API data!" % self.User)
            else:
                self.logger.warn("[%s] API call failed. Skipping killboard update..." % (self.User))
        except Exception as e:
            self.logger.error("API call failed!")
            self.logger.exception(e)


        mdb.killboard.insert(kill_board_dict)
        self.logger.debug("[%s] Updated application killboard: %s" % (self.User, monster_desc))

        # update the settlement sheet and do a settlement event log
        self.settlement["defeated_monsters"].append(monster_desc)
        self.log_event("%s defeated!" % monster_desc)


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
            elif p == "lost_settlements":
                self.update_lost_settlements(game_asset_key)
            elif p == "endeavor_tokens":
                self.update_endeavor_tokens(game_asset_key)
            elif p == "name":
                self.update_settlement_name(game_asset_key)
            elif p == "add_defeated_monster":
                self.add_kill(game_asset_key)
            elif p == "rm_defeated_monster":
                self.rm_game_asset("defeated_monsters", game_asset_key)
            elif p == "add_quarry":
                self.update_quarries("add",game_asset_key)
            elif p == "rm_quarry":
                self.update_quarries("rm",game_asset_key)
            elif p == "add_nemesis":
                self.add_game_asset("nemesis_monsters",game_asset_key)
            elif p == "rm_nemesis":
                self.rm_game_asset("nemesis_monsters",game_asset_key)
            elif p == "increment_nemesis":
                self.increment_nemesis(game_asset_key)
            elif p == "toggle_admin_status":
                self.toggle_admin_status(game_asset_key)
            elif p == "toggle_milestone":
                self.update_milestones(game_asset_key)
            elif p in ["add_item","remove_item"]:
                self.update_settlement_storage("html_form", params)
            elif p == "add_location":
                self.add_game_asset("locations", game_asset_key)
            elif p == "rm_location":
                self.rm_game_asset("locations", game_asset_key)
            elif p == "abandon_settlement":
                self.log_event("Settlement abandoned!")
                self.settlement["abandoned"] = datetime.now()
            elif p == "hunting_party_operation":
                self.modify_departing_survivors(params)
            elif p.split("_")[:2] == ["set","principle"]:
                principle = "_".join(p.split("_")[2:])
                self.set_principle(principle, game_asset_key)
            elif p.split("_")[0] == "location" and p.split("_")[1] == "level":
                self.update_location_level(p.split("_")[2:][0], game_asset_key)
            else:
                self.settlement[p] = game_asset_key
                self.logger.debug("%s set '%s' = '%s' for %s" % (self.User.user["login"], p, game_asset_key, self.get_name_and_id()))
        #
        #   settlement post-processing starts here!
        #

        #   auto-add milestones for principles:
        for principle in self.settlement["principles"]:
            principle_dict = Innovations.get_asset(principle)
            if "type" in principle_dict.keys() and principle_dict["type"] == "principle" and "milestone" in principle_dict.keys():
                if principle_dict["milestone"] not in self.settlement["milestone_story_events"]:
                    self.settlement["milestone_story_events"].append(principle_dict["milestone"])
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
            departure_bonuses = self.get_bonuses('departure_buff', return_type="html", update_mins=False),
            settlement_bonuses = self.get_bonuses('settlement_buff', return_type="html", update_mins=False),
            survivor_bonuses = self.get_bonuses('survivor_buff', return_type="html", update_mins=False),
            survivors = self.get_survivors(return_type="html_campaign_summary", user_id=user_id),
            special_rules = self.get_special_rules("html_campaign_summary"),

            show_departing_survivors_management_button=self.User.can_manage_departing_survivors(),
            show_endeavor_controls = self.User.get_preference("show_endeavor_token_controls"),
            endeavor_tokens = self.get_endeavor_tokens(),

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
                campaign=self.get_campaign(),
                ly=self.get_ly(),
                pop=self.settlement["population"],
                players_block=players,
            )
        else:
            button_class = "kd_dying_lantern dashboard_settlement_list_settlement_button"
            link_text = "<b class='dashboard_settlement_list_settlement_name'>%s</b>" % self.settlement["name"]
            link_text += "<br/><i>%s</i>" % self.get_campaign()

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






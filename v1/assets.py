#!/usr/bin/env python

from bson.objectid import ObjectId
from bson import json_util
from copy import copy
from collections import defaultdict
from cStringIO import StringIO
from datetime import datetime
import gridfs
from hashlib import md5
from PIL import Image
import json
import operator
import os
import pickle
import random
from string import Template, capwords
import types

import admin
import export_to_file
import assets
import game_assets
import html
from models import Abilities, DefeatedMonsters, Disorders, Epithets, FightingArts, Locations, Items, Innovations, Nemeses, Resources, Quarries, WeaponProficiencies, userPreferences, mutually_exclusive_principles
from session import Session
from utils import mdb, get_logger, load_settings, get_user_agent, ymdhms, stack_list
import world

settings = load_settings()

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


    def is_admin(self):
        """ Returns True if the user is an admin, False if they are not. """

        if "admin" in self.user.keys() and type(self.user["admin"]) == datetime:
            return True
        else:
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
                    self.user["preferences"][p] = True
                elif p_value == "False":
                    self.user["preferences"][p] = False
                self.logger.debug("'%s' added '%s'->'%s' to preferences!" % (self.user["login"], p, p_value))
                user_admin_log_dict["msg"] += "'%s' -> %s; " % (p, p_value)

        user_admin_log_dict["msg"] = user_admin_log_dict["msg"].strip()
        mdb.user_admin.insert(user_admin_log_dict)


    def dump_assets(self, dump_type=None):
        """ Returns a dictionary representation of a user's complete assets. Due
        to the...kind of arbitrary design of things, this is a multi-stage sort
        of export: first we get the user info and the user's settlements and
        settlement events, then we get his survivors in a separate bit of logic.
        The last thing we do is get his GridFS stuff, e.g. avatars."""

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


    def get_settlements(self, return_as=False):
        """ Returns the user's settlements in a number of ways. Leave
        'return_as' unspecified if you want a mongo cursor back. """

        self.settlements = list(mdb.settlements.find({"created_by": self.user["_id"]}).sort("name"))

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
                S = assets.Settlement(settlement_id=settlement["_id"], session_object=self.Session)
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
            ]}
        ).sort("name"))

        # user version

        if return_type == "asset_links":
            output = ""
            for s in survivors:
                S = Survivor(survivor_id=s["_id"], session_object=self.Session)
                output += S.asset_link()
            return output

        return survivors


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
            S = assets.Settlement(settlement_id=settlement_id, session_object=self.Session)
            if S.settlement is not None:
                if not "abandoned" in S.settlement.keys():
                    game_dict[settlement_id] = S.settlement["name"]
            else:
                self.logger.error("Could not find settlement %s while loading campaigns for %s" % (settlement_id, self.get_name_and_id()))
        sorted_game_tuples = sorted(game_dict.items(), key=operator.itemgetter(1))

        for settlement_tuple in sorted_game_tuples:
            settlement_id = settlement_tuple[0]
            S = assets.Settlement(settlement_id=settlement_id, session_object=self.Session)
            if S.settlement is not None:
                output += S.asset_link(context="dashboard_campaign_list")
        return output


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
        """ Creates an HTML MoTD for the user. """

        formatted_log_msg = ""
        last_log_msg = self.get_last_n_user_admin_logs(1)
        if last_log_msg is not None:
            formatted_log_msg = "<p>&nbsp;Latest user admin activity:</p><p>&nbsp;<b>%s</b>:</b> %s</p>" % (last_log_msg["created_on"].strftime(ymdhms), last_log_msg["msg"])

        pref_html = ""
        pref_models = userPreferences()
        for p in pref_models.get_keys():
            d = pref_models.pref(self, p)
            pref_html += html.dashboard.preference_block.safe_substitute(desc=d["desc"], pref_key=p, pref_true_checked=d["affirmative_selected"], pref_false_checked=d["negative_selected"], affirmative=d["affirmative"], negative=d["negative"])

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

        return html.dashboard.world.safe_substitute(
            dead_survivors = mdb.the_dead.find().count(),
            defeated_monsters = world.kill_board("html_table_rows"),
            total_users = mdb.users.find().count(),
            active_settlements = mdb.settlements.find().count() - mdb.settlements.find({"abandoned": {"$exists": True}}).count(),
            abandoned_settlements = mdb.settlements.find({"abandoned": {"$exists": True}}).count(),
            total_sessions = mdb.sessions.find().count(),
            live_survivors = mdb.survivors.find({"dead": {"$exists": False}}).count(),
            latest_fatality = world.latest_fatality("html"),
            top_principles = world.top_principles("html_ul"),
            avg_pop = world.get_average("population"),
            avg_death = world.get_average("death_count"),
        )



#
#   SURVIVOR CLASS
#

class Survivor:

    def __init__(self, survivor_id=False, params=None, session_object=None, suppress_event_logging=False):
        """ Initialize this with a cgi.FieldStorage() as the 'params' kwarg
        to create a new survivor. Otherwise, use a mdb survivor _id value
        to initalize with survivor data from mongo. """

        self.suppress_event_logging = suppress_event_logging
        self.Session = session_object
        if self.Session is None or not self.Session:
            raise Exception("Survivor objects may not be initialized without a Session object!")
        self.User = self.Session.User
        self.Settlement = self.Session.Settlement

        self.logger = get_logger()
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

        if not survivor_id:
            survivor_id = self.new(params)

        self.survivor = mdb.survivors.find_one({"_id": ObjectId(survivor_id)})
        if not self.survivor:
            raise Exception("Invalid survivor ID: '%s'" % survivor_id)

        settlement_id = self.survivor["settlement"]
        self.Settlement = Settlement(settlement_id=settlement_id, session_object=self.Session)
        if self.Settlement is not None:
            self.normalize()


    def normalize(self):
        """ Run this when a Survivor object is initialized: it will enforce
        the data model and apply settlements defaults to the survivor. """

        # auto-apply epithets for Birth of a Savior
        for ability in ["Dormenatus", "Caratosis", "Lucernae"]:
            if ability in self.survivor["abilities_and_impairments"] and ability not in self.survivor["epithets"]:
                self.survivor["epithets"].append(ability)
        if "Twilight Sword" in self.survivor["abilities_and_impairments"] and "Twilight Sword" not in self.survivor["epithets"]:
            self.survivor["epithets"].append("Twilight Sword")

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
        for innovation_key in self.Settlement.settlement["innovations"]:
            if innovation_key in WeaponProficiencies.get_keys():
                prof_dict = WeaponProficiencies.get_asset(innovation_key)
                if prof_dict["all_survivors"] not in self.survivor["abilities_and_impairments"]:
                    if self.User.get_preference("apply_weapon_specialization"):
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
            self.logger.warn("%s has no 'born_in_ly' value!" % self.get_name_and_id())
            if "father" not in self.survivor.keys() and "mother" not in self.survivor.keys():
                self.logger.warn("Defaulting birth year to 1 for %s" % self.get_name_and_id())
                self.survivor["born_in_ly"] = 1
            parent_birth_years = [1]
            for p in ["father","mother"]:
                if p in self.survivor.keys():
                    P = assets.Survivor(survivor_id=self.survivor[p], session_object=self.Session)
                    if not "born_in_ly" in P.survivor.keys():
                        self.logger.warn("%s has no 'born_in_ly' value!" % P.get_name_and_id())
                    else:
                        self.logger.debug("%s %s was born in LY %s" % (p.capitalize(), P.get_name_and_id(), P.survivor["born_in_ly"]))
                        parent_birth_years.append(P.survivor["born_in_ly"])
            self.logger.debug("Highest parent birth year is %s for %s" % (max(parent_birth_years), self.get_name_and_id()))
            self.survivor["born_in_ly"] = max(parent_birth_years) + 1
            self.logger.warn("Defaulting birth year to %s for %s" % (self.survivor["born_in_ly"], self.get_name_and_id()))

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

        mdb.survivors.save(self.survivor)


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

        email = self.User.user["login"]

        # if we have a cgi.FieldStorage() as our first arg
        if params is not None:
            if "name" in params and params["name"].value != "":
                name = params["name"].value.strip()
            if "sex" in params:
                sex = params["sex"].value
            if "email" in params:
                email = params["email"].value.strip()

        survivor_dict = {
            "name": name,
            "email": email,
            "sex": sex,
            "born_in_ly": self.Settlement.settlement["lantern_year"],
            "created_on": datetime.now(),
            "created_by": self.User.user["_id"],
            "settlement": self.Settlement.settlement["_id"],
            "survival": 1,
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

        # set the public bit if it's supplied:
        if params is not None and "toggle_public" in params:
            survivor_dict["public"] = "checked"

        # add parents if they're specified
        parents = []
        for parent in ["father", "mother"]:
            if params is not None and parent in params:
                p_id = ObjectId(params[parent].value)
                parents.append(mdb.survivors.find_one({"_id": p_id})["name"])
                survivor_dict[parent] = ObjectId(p_id)
        if parents != []:
            if sex == "M":
                genitive_appellation = "Son"
            elif sex == "F":
                genitive_appellation = "Daughter"
            survivor_dict["epithets"].append("%s of %s" % (genitive_appellation, " and ".join(parents)))

        # insert the new survivor into mdb and use its newly minted id to set
        #   self.survivor with the info we just inserted
        survivor_id = mdb.survivors.insert(survivor_dict)
        self.survivor = mdb.survivors.find_one({"_id": survivor_id})

        # log the addition or birth of the new survivor
        name_pretty = self.get_name_and_id(include_sex=True, include_id=False)
        current_ly = self.Settlement.settlement["lantern_year"]
        if not self.suppress_event_logging:
            if parents != []:
                self.Settlement.log_event("%s born to %s!" % (name_pretty, " and ".join(parents)))
            else:
                self.Settlement.log_event("%s joined the settlement!" % (name_pretty))

        # apply settlement buffs to the new guy depending on preference
        if self.User.get_preference("apply_new_survivor_buffs"):
            new_survivor_buffs = self.Settlement.get_bonuses("new_survivor")
            self.logger.debug("Automatically applying %s 'new_survivor' buffs to new survivor '%s'" % (len(new_survivor_buffs), self.get_name_and_id()))
            for b in new_survivor_buffs.keys():
                buffs = new_survivor_buffs[b]
                for attrib in buffs.keys():
                    self.survivor[attrib] = self.survivor[attrib] + buffs[attrib]
                self.logger.debug("Applied buffs for '%s' successfully: %s" % (b, buffs))
                self.Settlement.log_event("Applied '%s' bonus to %s." % (b, name))
        else:
            self.Settlement.log_event("Settlement bonuses were not applied to %s." % (name))
            self.logger.debug("Skipping auto-application of new survivor buffs for %s." % self.get_name_and_id())

        # if we've got an avatar, do that AFTER we insert the survivor record
        if params is not None and "survivor_avatar" in params and params["survivor_avatar"].filename != "":
            self.update_avatar(params["survivor_avatar"])

        # save the survivor (in case it got changed above), update settlement
        #   mins and log our successful creation
        mdb.survivors.save(self.survivor)
        self.Settlement.update_mins()
        self.logger.info("User '%s' created new survivor %s successfully." % (self.User.user["login"], self.get_name_and_id(include_sex=True)))

        return survivor_id


    def delete(self, run_valkyrie=True):
        """ Retires the Survivor (in the Blade Runner sense) and then removes it
        from the mdb. """

        self.logger.debug("%s is removing survivor %s..." % (self.User.user["login"], self.get_name_and_id()))
        if not "cause_of_death" in self.survivor.keys():
            self.survivor["cause_of_death"] = "Forsaken."
        self.death()
        if run_valkyrie:
            admin.valkyrie()
        if "avatar" in self.survivor.keys():
            gridfs.GridFS(mdb).delete(self.survivor["avatar"])
            self.logger.debug("%s removed an avatar image (%s) from GridFS." % (self.User.user["login"], self.survivor["avatar"]))
        mdb.survivors.remove({"_id": self.survivor["_id"]})
        self.Settlement.log_event("%s has been Forsaken (and permanently deleted) by %s" % (self.get_name_and_id(include_id=False, include_sex=True), self.User.user["login"] ))
        self.logger.warn("%s removed survivor %s from mdb!" % (self.User.user["login"], self.get_name_and_id()))


    def get_name_and_id(self, include_id=True, include_sex=False):
        """ Laziness function to return a string of the Survivor's name, _id and
        sex values (i.e. so we can write DRYer log entries, etc.). """

        output = [self.survivor["name"]]
        if include_sex:
            output.append("[%s]" % self.get_sex())
        if include_id:
            output.append("(%s)" % self.survivor["_id"])
        return " ".join(output)


    def get_survival_actions(self, return_as=False):
        """ Creates a list of survival actions that the survivor can do. """
        possible_actions = game_assets.survival_actions

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

        if "cannot_spend_survival" in self.survivor.keys():
            available_actions = []

        if return_as == "html_checkboxes":
            html = ""
            for a in possible_actions:
                if a in available_actions:
                    checked = "checked"
                else:
                    checked = ""
                html += Template('<input disabled type="checkbox" id="$action" class="radio_principle" $checked/><label class="radio_principle_label" for="$action"> $action </label>').safe_substitute(checked=checked, action=a)
            return html

        return available_actions


    def add_ability_customization(self, attrib_key, attrib_customization):
        """ This basically creates a custom dict on the Survivor that is used
        when rendering attributes. Not super elegant, but it'll do for version
        one. """

        if not "ability_customizations" in self.survivor.keys():
            self.survivor["ability_customizations"] = {}

        if not attrib_key in self.survivor["ability_customizations"]:
            self.survivor["ability_customizations"][attrib_key] = ""

        self.survivor["ability_customizations"][attrib_key] = attrib_customization
        self.logger.debug("Custom ability description '%s' -> '%s' added to survivor '%s' by %s" % (attrib_key, attrib_customization, self.survivor["name"], self.Session.User.user["login"]))


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

            output = '<select name="customize_ability">'
            output += '<option selected disabled hidden value="">Customize Ability</option>'
            for ability in all_list:
                output += html.ui.game_asset_select_row.safe_substitute(asset=ability)
            output += html.ui.game_asset_select_bot
            output += html.ui.text_input.safe_substitute(name="custom_ability_description", placeholder_text="customize ability") 

            output += html.ui.game_asset_select_top.safe_substitute(
                operation = "remove_",
                operation_pretty = "Remove",
                name = "ability",
                name_pretty = "Ability",
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
                    pretty_list.append("<p><b>%s:</b> %s %s</p>" % (ability, desc, suffix))
                elif ability not in Abilities.get_keys() and suffix != "":
                    pretty_list.append("<p><b>%s:</b> %s" % (ability, suffix))
                else:
                    pretty_list.append("<p><b>%s:</b> custom ability or impairment (use fields below to add a description).</p>" % ability)
            return "\n".join(pretty_list)

        return all_list


    def get_fighting_arts(self, return_type=False, strikethrough=False):
        fighting_arts = self.survivor["fighting_arts"]

        if return_type == "formatted_html":
            html = ""
            for fa_key in fighting_arts:
                html += '<p><b>%s:</b> %s</p>\n' % (fa_key, FightingArts.get_asset(fa_key)["desc"])
                if strikethrough:
                    html = "<del>%s</del>\n" % html
            return html

        if return_type == "html_select_remove":
            html = ""
            html = '<select name="remove_fighting_art" onchange="this.form.submit()">'
            html += '<option selected disabled hidden value="">Remove Fighting Art</option>'
            for fa in fighting_arts:
                html += '<option>%s</option>' % fa
            html += '</select>'
            return html

        return disorders


    def get_disorders(self, return_as=False):
        disorders = self.survivor["disorders"]

        if return_as == "formatted_html":
            html = ""
            for disorder_key in disorders:
                html += '<p><b>%s:</b> %s</p>' % (disorder_key, Disorders.get_asset(disorder_key)["survivor_effect"])
            return html

        if return_as == "html_select_remove":
            html = ""
            html = '<select name="remove_disorder" onchange="this.form.submit()">'
            html += '<option selected disabled hidden value="">Remove Disorder</option>'
            for disorder in disorders:
                html += '<option>%s</option>' % disorder
            html += '</select>'
            return html

        return disorders


    def get_epithets(self, return_type=False):
        epithets = self.survivor["epithets"]

        if return_type == "comma-delimited":
            return ", ".join(epithets)

        if return_type == "html_formatted":
            if epithets == []:
                return ""
            else:
                styled_epithets = []
                for epithet in epithets:
                    if epithet in ["Lucernae", "Caratosis", "Dormenatus"]:
                        styled_epithets.append('<font id="%s">&#x02588;</font> %s' % (epithet, epithet))
                    else:
                        styled_epithets.append(epithet)
                return '<p class="subhead_p_block">%s</p>' % ", ".join(styled_epithets)

        if return_type == "html_remove":
            output = '<select name="remove_epithet" onchange="this.form.submit()">'
            output += '<option selected disabled hidden value="">Remove Epithet</option>'
            for epithet in self.survivor["epithets"]:
                output += '<option value="%s">%s</option>' % (epithet, epithet)
            output += '</select>'
            return output

        return epithets


    def heal(self, cmd, heal_armor=False, increment_hunt_xp=False):
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
            heal_armor=True
            increment_hunt_xp=1
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

        mdb.survivors.save(self.survivor)


    def add_game_asset(self, asset_type, asset_key, asset_desc=None):
        """ Our generic function for adding a game_asset to a survivor. Some biz
        logic/game rules happen here.

        The kwarg 'asset_type' should always be the self.name value of the
        game_asset model (see models.py for more details).

        Finally, if, for whatever reason, we can't add the asset, we return
        False.
        """

        self.logger.debug("%s is adding '%s' to survivor '%s' (%s)..." % (self.User.user["login"], asset_key, self.survivor["name"], self.survivor["_id"]))

        asset_key = asset_key.strip()

        if asset_type == "disorder":
            self.survivor["disorders"] = list(set([d for d in self.survivor["disorders"]])) # uniquify
            if len(self.survivor["disorders"]) >= 3:
                return False

            if asset_key == "RANDOM_DISORDER":
                disorder_deck = Disorders.get_keys()
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
                mdb.survivors.save(self.survivor)
                return True
            else:
                return False

        elif asset_type == "fighting_art":
            if asset_key == "RANDOM_FIGHTING_ART":
                fa_deck = FightingArts.get_keys(exclude_if_attrib_exists="secret")
                for fa in self.survivor["fighting_arts"]:
                    if fa in fa_deck:
                        fa_deck.remove(fa)
                self.survivor["fighting_arts"].append(random.choice(fa_deck))
            elif asset_key in FightingArts.get_keys():
                self.survivor["fighting_arts"].append(asset_key)
            else:
                return False

        elif asset_type == "abilities_and_impairments":
            if asset_key == "Twilight Sword":
                self.Settlement.log_event("%s got the Twilight Sword!" % self.get_name_and_id(include_id=False, include_sex=True))

            # birth of a savior stuff
            savior_abilities = ["Dream of the Beast", "Dream of the Crown", "Dream of the Lantern"]
            if asset_key in savior_abilities:
                self.Settlement.log_event("A savior was born! %s had the '%s'." % (self.get_name_and_id(include_id=False, include_sex=True), asset_key))

            if asset_key not in Abilities.get_keys():
                self.survivor["abilities_and_impairments"].append("%s" % asset_key)
                return True
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

                if "related" in asset_dict.keys():
                    for related_ability in asset_dict["related"]:
                        self.survivor["abilities_and_impairments"].append(related_ability)
                        self.logger.debug("%s is adding '%s' to '%s': automatically adding related '%s' ability." % (self.User.user["login"], asset_key, self.survivor["name"], related_ability))
                        if related_ability in savior_abilities:
                            self.Settlement.log_event("A savior was born! %s had the '%s'." % (self.get_name_and_id(include_id=False, include_sex=True), related_ability))
                return True
            else:
                return False
        else:
            self.logger.critical("Attempted to add unknown game_asset type '%s'. Doing nothing!" % asset_type)



    def rm_game_asset(self, asset_type, asset_key):
        """ This is the reverse of the above function: give it a type and a key
        to remove that key from that type of asset on the survivor. """

        asset_key = asset_key.strip()

        if asset_type == "abilities_and_impairments":
            if asset_key not in Abilities.get_keys():
                self.survivor["abilities_and_impairments"].remove(asset_key)
                return True
            elif asset_key in Abilities.get_keys():
                asset_dict = Abilities.get_asset(asset_key)
                self.survivor["abilities_and_impairments"].remove(asset_key)
                if "cannot_spend_survival" in asset_dict.keys() and "cannot_spend_survival" in self.survivor.keys():
                    del self.survivor["cannot_spend_survival"]
                mdb.survivors.save(self.survivor)
                return True
            else:
                return False

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
                return True

        if type(toggle_value) != list:
            try:
                del self.survivor[toggle_key]
                self.logger.debug("%s toggled '%s' OFF for survivor %s." % (self.User.user["login"], toggle_key, self.get_name_and_id()))
                if toggle_key == "dead":
                    if self.death(undo_death=True):
                        self.logger.debug("Survivor '%s' (%s) has not returned from death!" % (self.survivor["name"], self.survivor["_id"]))
            except Exception as e:
                pass
        else:
            self.survivor[toggle_key] = "checked"
            if toggle_key == "dead":
                if not self.death():
                    self.logger.error("Could not process death for survivor '%s' (%s)." % (self.survivor["name"], self.survivor["_id"]))
            if toggle_key == "retired":
                self.survivor["retired_in"] = self.Settlement.settlement["lantern_year"]


        mdb.survivors.save(self.survivor)


    def get_avatar(self, return_type=False):
        """ Returns the avatar's GridFS id AS A STRING if you don't specify a
        'return_type'. Use 'html' to get an img element back. """

        if not "avatar" in self.survivor.keys():
            if return_type == "html":
                return ""
            else:
                return None

        if return_type == "html":
            img_element = '<img class="survivor_avatar_image" src="/get_image?id=%s" alt="%s"/>' % (self.survivor["avatar"], self.survivor["name"])
            return '<a href="/get_image?id=%s">%s</a>' % (self.survivor["avatar"], img_element)
        if return_type == "html_campaign_summary":
            img_element = '<img class="survivor_avatar_image_campaign_summary" src="/get_image?id=%s"/>' % (self.survivor["avatar"])
            return img_element

        return self.survivor["avatar"]


    def update_avatar(self, file_instance):
        """ Changes the survivor's avatar. """

        if not type(file_instance) == types.InstanceType:
            self.logger.error("Avatar update failed! 'survivor_avatar' must be %s instead of %s." % (types.InstanceType, type(file_instance)))
            return None

        fs = gridfs.GridFS(mdb)

        if "avatar" in self.survivor.keys():
            fs.delete(self.survivor["avatar"])
            self.logger.debug("%s removed an avatar image (%s) from GridFS." % (self.User.user["login"], self.survivor["avatar"]))

        processed_image = StringIO()
        im = Image.open(file_instance.file)
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
                if Abilities.get_asset(a)["type"] == "impairment":
                    impairment_set.add(a)
        return list(impairment_set)


    def get_siblings(self, return_type=None):
        """ Gets a survivors siblings and returns it as a dictionary (by
        default). Our pretty/HTML return comes back as a list. """

        siblings = {}

        for s in self.Settlement.get_survivors():
            S = Survivor(survivor_id=s["_id"], session_object=self.Session)
            for p in self.get_parents():
                if p in S.get_parents():
                    siblings[S.survivor["_id"]] = "half"
            if S.get_parents() == self.get_parents():
                siblings[S.survivor["_id"]] = "full"

        del siblings[self.survivor["_id"]]   # remove yourself

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
        """ Uses assets.Settlement.get_ancestors() sort of like the new Survivor
        creation screen to allow parent changes. """

        parents = []
        for p in ["father","mother"]:
            if p in self.survivor.keys():
                parents.append(self.survivor[p])

        if return_type == "html_select":
            output = ""
            for role in [("father", "M"), ("mother", "F")]:
                output += html.survivor.change_ancestor_select_top.safe_substitute(parent_role=role[0], pretty_role=role[0].capitalize())
                for s in self.Settlement.get_survivors():
                    S = assets.Survivor(survivor_id=s["_id"], session_object=self.Session)
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
                            O = assets.Survivor(survivor_id=other_parent, session_object=self.Session)
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

    def death(self, undo_death=False):
        """ Call this method when a survivor dies. Call it with the 'undo_death'
        kwarg to undo the death.

        This returns a True or False that reflects the life/death status of the
        survivor (which is a little strange, but bear with me).

        We return True if the survivor is marked with the 'dead' attrib and we
        return False if the survivor is NOT marked with the 'dead' attrib.
        """

        self.Settlement.update_mins()

        population = int(self.Settlement.settlement["population"])
        death_count = int(self.Settlement.settlement["death_count"])

        if undo_death:
            self.logger.debug("Survivor '%s' is coming back from the dead..." % self.survivor["name"])
            for death_key in ["died_on","died_in","cause_of_death"]:
                try:
                    del self.survivor[death_key]
                except Exception as e:
                    self.logger.debug("Could not unset '%s'" % death_key)
                    pass

            mdb.the_dead.remove({"survivor_id": self.survivor["_id"]})
            self.logger.debug("Survivor '%s' removed from the_dead." % self.survivor["name"])
        else:
            self.logger.debug("Survivor '%s' (%s) has died!" % (self.survivor["name"], self.survivor["_id"]))
            death_dict = {
                "name": self.survivor["name"],
                "epithets": self.survivor["epithets"],
                "survivor_id": self.survivor["_id"],
                "created_by": self.survivor["created_by"],
                "settlement_id": self.Settlement.settlement["_id"],
                "created_on": datetime.now(),
                "lantern_year": self.Settlement.settlement["lantern_year"],
                "Courage": self.survivor["Courage"],
                "Understanding": self.survivor["Understanding"],
                "Insanity": self.survivor["Insanity"],
                "epithets": self.survivor["epithets"],
                "hunt_xp": self.survivor["hunt_xp"],
            }

            for optional_attrib in ["avatar","cause_of_death"]:
                if optional_attrib in self.survivor.keys():
                    death_dict[optional_attrib] = self.survivor[optional_attrib]

            if mdb.the_dead.find_one({"survivor_id": self.survivor["_id"]}) is None:
                mdb.the_dead.insert(death_dict)
                self.logger.debug("Survivor '%s' added to the The Dead." % self.survivor["name"])
                self.Settlement.settlement["population"] = int(self.Settlement.settlement["population"]) - 1
                self.Settlement.settlement["death_count"] = int(self.Settlement.settlement["death_count"]) + 1
                self.logger.debug("Settlement '%s' population and death count automatically adjusted!" % self.Settlement.settlement["name"])
                self.Settlement.log_event("%s died." % self.get_name_and_id(include_id=False, include_sex=True))
                self.Settlement.log_event("Population decreased to %s; death count increased to %s." % (self.Settlement.settlement["population"], self.Settlement.settlement["death_count"]))
            else:
                self.logger.debug("Survivor '%s' is already among The Dead." % self.survivor["name"])

            self.survivor["died_on"] = datetime.now()
            self.survivor["died_in"] = self.Settlement.settlement["lantern_year"]

        # save the survivor then update settlement mins: you have to do it in
        # this order, or else update_mins() doesn't know about the stiff and the
        # population decrement above won't work.
        mdb.survivors.save(self.survivor)
        self.Settlement.update_mins()

        if "dead" in self.survivor.keys():
            return True
        else:
            return False


    def modify_weapon_proficiency(self, target_lvl):
        """ Wherein we update the survivor's 'Weapon Proficiency' attrib. There
        is some biz logic here re: specializations and masteries. """

        # if we do nothing else, at least update the level
        self.survivor["Weapon Proficiency"] = target_lvl

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
            self.Settlement.settlement["innovations"].append(mastery_string)
            self.Settlement.log_event("%s has mastered %s!" % (self.get_name_and_id(include_sex=True, include_id=False), weapon))
            self.Settlement.log_event("'%s' added to settlement Innovations!" % mastery_string)
            mdb.settlements.save(self.Settlement.settlement)
            self.logger.debug("Survivor '%s' added '%s' to settlement %s's Innovations!" % (self.survivor["name"], mastery_string, self.Settlement.settlement["name"]))


    def join_hunting_party(self):
        """ Adds a survivor to his settlement's hunting party and saves. """
        self.survivor["in_hunting_party"] = "checked"
        mdb.survivors.save(self.survivor)
        self.Settlement.log_event("%s has joined the hunting party." % self.get_name_and_id(include_sex=True, include_id=False))


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


    def modify(self, params):
        """ Reads through a cgi.FieldStorage() (i.e. 'params') and modifies the
        survivor. """

        self.Settlement.update_mins()

        for p in params:

            if type(params[p]) != list:
                game_asset_key = params[p].value.strip()

            if p in ["asset_id", "heal_survivor", "form_id", "modify","view_game"]:
                pass
            elif p == "survivor_avatar":
                self.update_avatar(params[p])
            elif p == "add_epithet":
                self.survivor["epithets"].append(params[p].value.strip())
                self.survivor["epithets"] = sorted(list(set(self.survivor["epithets"])))
            elif p == "remove_epithet":
                self.survivor["epithets"].remove(params[p].value)
            elif p == "add_ability":
                self.add_game_asset("abilities_and_impairments", game_asset_key)
            elif p == "remove_ability":
                self.rm_game_asset("abilities_and_impairments", game_asset_key)
            elif p == "add_disorder":
                self.add_game_asset("disorder", game_asset_key)
            elif p == "remove_disorder":
                self.survivor["disorders"].remove(params[p].value)
            elif p == "add_fighting_art" and len(self.survivor["fighting_arts"]) < 3:
                self.add_game_asset("fighting_art", game_asset_key)
            elif p == "remove_fighting_art":
                self.survivor["fighting_arts"].remove(params[p].value)
            elif p.split("_")[0] == "toggle":
                toggle_attrib = "_".join(p.split("_")[1:])
                self.toggle(toggle_attrib, params[p])
            elif p == "name":
                if game_asset_key != self.survivor[p]:
                    self.Settlement.log_event("%s was renamed to '%s'" % (self.get_name_and_id(include_sex=True, include_id=False), game_asset_key))
                    self.survivor["name"] = game_asset_key
            elif p == "email":
                self.survivor["email"] = game_asset_key.lower().strip()
            elif p == "cause_of_death":
                self.survivor[p] = game_asset_key
                mdb.survivors.save(self.survivor)
                admin.valkyrie()
            elif game_asset_key == "None":
                del self.survivor[p]
                if p == "in_hunting_party":
                    self.Settlement.log_event("%s left the hunting party." % self.survivor["name"])
            elif p == "Weapon Proficiency":
                self.modify_weapon_proficiency(int(game_asset_key))
            elif p == "customize_ability" and "custom_ability_description" in params:
                self.add_ability_customization(params[p].value, params["custom_ability_description"].value)
            elif p == "custom_ability_description":
                pass
            elif p == "in_hunting_party":
                self.join_hunting_party()
            elif p == "sex":
                new_sex = game_asset_key.strip()[0].upper()
                if new_sex in ["M","F"]:
                    self.survivor["sex"] = new_sex
            else:
                self.survivor[p] = game_asset_key
#                self.logger.debug("%s set '%s' -> '%s' for survivor '%s' (%s)." % (self.User.user["login"], p, game_asset_key, self.survivor["name"], self.survivor["_id"]))


        # enforce ability and impairment maxes
        for asset_key in self.survivor["abilities_and_impairments"]:
            if asset_key not in Abilities.get_keys():
                pass
            else:
                asset_dict = Abilities.get_asset(asset_key)
                if "max" in asset_dict.keys():
                    asset_count = self.survivor["abilities_and_impairments"].count(asset_key)
                    while asset_count > asset_dict["max"]:
                        self.logger.warn("Survivor '%s' has '%s' x%s (max is %s)." % (self.survivor["name"], asset_key, asset_count, asset_dict["max"]))
                        self.survivor["abilities_and_impairments"].remove(asset_key)
                        self.logger.info("Removed '%s' from survivor '%s'." % (asset_key, self.survivor["name"]))
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
        mdb.survivors.save(self.survivor)


    def asset_link(self, view="survivor", button_class="green", link_text=False, include=["hunt_xp", "insanity", "sex", "dead", "retired"], disabled=False):
        """ Returns an asset link (i.e. html form with button) for the
        survivor. """

        if not link_text:
            link_text = "<b>%s</b>" % self.survivor["name"]
            if "sex" in include:
                link_text += " [%s]" % self.get_sex("html")
        if disabled:
            link_text += "<br />%s" % self.survivor["email"]

        if include != []:
            attribs = []
            if "dead" in include:
                if "dead" in self.survivor.keys():
                    button_class = "dark_green"
                    attribs.append("Dead")

            if "retired" in include:
                if "retired" in self.survivor.keys():
                    button_class = "warn"
                    attribs.append("Retired")

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


    def render_html_form(self):
        """ This is just like the render_html_form() method of the settlement
        class: a giant tangle-fuck of UI/UX logic that creates the form for
        modifying a survivor. """

        survivor_survival_points = int(self.survivor["survival"])
        if survivor_survival_points > int(self.Settlement.settlement["survival_limit"]):
            survivor_survival_points = int(self.Settlement.settlement["survival_limit"])

        flags = {}
        for flag in self.flags:
            flags[flag] = ""
            if flag in self.survivor.keys():
                flags[flag] = self.survivor[flag]

        insane = ""
        if int(self.survivor["Insanity"]) >= 3:
            insane = "#C60000"

        if int(self.survivor["hunt_xp"]) >= 16:
            flags["retired"] = "checked"

        COD_div_display_style = "none"
        if "dead" in self.survivor.keys():
            COD_div_display_style = "block"
        COD = ""
        if "cause_of_death" in self.survivor.keys():
            COD = self.survivor["cause_of_death"]

        # fighting arts widgets
        fighting_arts_picker = FightingArts.render_as_html_dropdown(exclude=self.survivor["fighting_arts"])
        if len(self.survivor["fighting_arts"]) >= 3:
            fighting_arts_picker = ""
        fighting_arts_remover = self.get_fighting_arts("html_select_remove")
        if self.survivor["fighting_arts"] == []:
            fighting_arts_remover = ""
        # disorders widgets
        disorders_picker = Disorders.render_as_html_dropdown(exclude=self.survivor["disorders"])
        if len(self.survivor["disorders"]) >= 3:
            disorders_picker = ""
        disorders_remover = self.get_disorders(return_as="html_select_remove")
        if self.survivor["disorders"] == []:
            disorders_remover = ""


        output = html.survivor.form.safe_substitute(
            MEDIA_URL = settings.get("application", "STATIC_URL"),
            avatar_img = self.get_avatar("html"),
            survivor_id = self.survivor["_id"],
            name = self.survivor["name"],
            add_epithets = Epithets.render_as_html_dropdown(exclude=self.survivor["epithets"]),
            rm_epithets =self.get_epithets("html_remove"),
            epithets = self.get_epithets("html_formatted"),
            sex = self.get_sex(),
            survival = survivor_survival_points,
            survival_limit = self.Settlement.get_attribute("survival_limit"),
            cannot_spend_survival_checked = flags["cannot_spend_survival"],
            hunt_xp = self.survivor["hunt_xp"],
            dead_checked = flags["dead"],
            favorite_checked = flags["favorite"],
            retired_checked = flags["retired"],
            public_checked = flags["public"],
            survival_actions = self.get_survival_actions(return_as="html_checkboxes"),
            movement = self.survivor["Movement"],
            accuracy = self.survivor["Accuracy"],
            strength = self.survivor["Strength"],
            evasion = self.survivor["Evasion"],
            luck = self.survivor["Luck"],
            speed = self.survivor["Speed"],
            departure_buffs = self.Settlement.get_bonuses("departure_buff", return_type="html"),
            settlement_buffs = self.Settlement.get_bonuses("survivor_buff", return_type="html"),

            insanity = self.survivor["Insanity"],
            insanity_number_style = insane,
            brain_damage_light_checked = flags["brain_damage_light"],
            head_damage_heavy_checked = flags["head_damage_heavy"],
            arms_damage_light_checked = flags["arms_damage_light"],
            arms_damage_heavy_checked = flags["arms_damage_heavy"],
            body_damage_light_checked = flags["body_damage_light"],
            body_damage_heavy_checked = flags["body_damage_heavy"],
            waist_damage_light_checked = flags["waist_damage_light"],
            waist_damage_heavy_checked = flags["waist_damage_heavy"],
            legs_damage_light_checked = flags["legs_damage_light"],
            legs_damage_heavy_checked = flags["legs_damage_heavy"],

            head = self.survivor["Head"],
            arms = self.survivor["Arms"],
            body = self.survivor["Body"],
            waist = self.survivor["Waist"],
            legs = self.survivor["Legs"],

            weapon_proficiency = self.survivor["Weapon Proficiency"],
            weapon_proficiency_type = self.survivor["weapon_proficiency_type"],

            courage = self.survivor["Courage"],
            understanding = self.survivor["Understanding"],

            cannot_use_fighting_arts_checked = flags["cannot_use_fighting_arts"],
            fighting_arts = self.get_fighting_arts("formatted_html", strikethrough=flags["cannot_use_fighting_arts"]),
            add_fighting_arts = fighting_arts_picker,
            rm_fighting_arts = fighting_arts_remover,

            disorders = self.get_disorders(return_as="formatted_html"),
            add_disorders = disorders_picker,
            rm_disorders = disorders_remover,

            skip_next_hunt_checked = flags["skip_next_hunt"],

            abilities_and_impairments = self.get_abilities_and_impairments("html_formatted"),
            add_abilities_and_impairments = Abilities.render_as_html_dropdown(
                disable=Abilities.get_maxed_out_abilities(self.survivor["abilities_and_impairments"]),
                ),
            remove_abilities_and_impairments = self.get_abilities_and_impairments("html_select_remove"),

            parents = self.get_parents(return_type="html_select"),
            children = self.get_children(return_type="html"),
            siblings = self.get_siblings(return_type="html"),
            cause_of_death = COD,
            show_COD = COD_div_display_style,

            email = self.survivor["email"],
            campaign_link = self.Settlement.asset_link(context="asset_management"),

        )
        return output



#
#   SETTLEMENT CLASS
#

class Settlement:

    def __init__(self, settlement_id=False, name=False, session_object=None):
        """ Initialize with a settlement from mdb. """
        self.logger = get_logger()

        # initialize session and user objects
        self.Session = session_object
        if self.Session is None or not self.Session:
            raise Exception("Settlements may not be initialized without a Session object!")
        self.User = self.Session.User

        # if we initialize a settlement without an ID, make a new one
        if not settlement_id:
            settlement_id = self.new(name)

        self.settlement = mdb.settlements.find_one({"_id": ObjectId(settlement_id)})
        if self.settlement is not None:
            self.update_mins()
#        else:
#            self.logger.error("Settlement '%s' could not be initialized!" % settlement_id)


    def log_event(self, msg):
        """ Logs a settlement event to mdb.settlement_events. """
        d = {
            "created_on": datetime.now(),
            "created_by": self.User.user["_id"],
            "settlement_id": self.settlement["_id"],
            "ly": self.settlement["lantern_year"],
            "event": msg,
        }
        mdb.settlement_events.insert(d)
        self.logger.debug("Settlement event logged for %s" % self.get_name_and_id())


    def new(self, name=None):
        """ Creates a new settlement. """

        self.logger.debug("User %s (%s) is creating a new settlement..." % (self.User.user["login"], self.User.user["_id"]))

        new_settlement_dict = {
            "nemesis_monsters": {"Butcher": [], },
            "created_on": datetime.now(),
            "created_by": self.User.user["_id"],
            "name": name,
            "survival_limit": 1,
            "lantern_year": 1,
            "death_count": 0,
            "milestone_story_events": [],
            "innovations": [],
            "principles": [],
            "locations": [],
            "quarries": ["White Lion"],
            "storage": [],
            "defeated_monsters": [],
            "population": 0,
            "lost_settlements": 0,
            "timeline": [
                {"year": 1, "story_event": "Returning Survivors", "settlement_event": ["First Day"], "quarry_event": ["White Lion (First Story)"]},
                {"year": 2, "story_event": "Endless Screams", },
                {"year": 3, },
                {"year": 4, "nemesis_encounter": "Nemesis Encounter: Butcher", },
                {"year": 5, "story_event": "Hands of Heat", },
                {"year": 6, "story_event": "Armored Strangers", },
                {"year": 7, "story_event": "Phoenix Feather", },
                {"year": 8, },
                {"year": 9, "nemesis_encounter": "Nemesis Encounter: King's Man", },
                {"year": 10, },
                {"year": 11, "story_event": "Regal Visit", },
                {"year": 12, "story_event": "Principle: Conviction (p. 141)", },
                {"year": 13, }, {"year": 14, }, {"year": 15, },
                {"year": 16, "nemesis_encounter": "Nemesis Encounter", },
                {"year": 17, }, {"year": 18, },
                {"year": 19, "nemesis_encounter": "Nemesis Encounter"},
                {"year": 20, "story_event": "Watched", },
                {"year": 21, }, {"year": 22, },
                {"year": 23, "nemesis_encounter": "Nemesis Encounter: Level 3"},
                {"year": 24, }, {"year": 25, },
                {"year": 26, "nemesis_encounter": "Nemesis Encounter: Watcher"},
                {"year": 27, }, {"year": 28, }, {"year": 29, }, {"year": 30, }, {"year": 31, },
                {"year": 32, }, {"year": 33, }, {"year": 34, }, {"year": 35, }, {"year": 36, },
                {"year": 37, }, {"year": 38, }, {"year": 39, }, {"year": 40, },
            ],
        }
        settlement_id = mdb.settlements.insert(new_settlement_dict)
        self.settlement = mdb.settlements.find_one({"_id": settlement_id})
        self.logger.info("New settlement '%s' ('%s') created by %s!" % (name, settlement_id, self.User.user["login"]))
        self.log_event("Settlement founded!")
        return settlement_id


    def delete(self):
        """ Retires and removes all survivors; runs the Valkyrie and removes the
        settlement from the mdb. """

        self.logger.debug("%s is removing settlement %s..." % (self.User.user["login"], self.get_name_and_id()))
        for survivor in self.get_survivors():
            S = Survivor(survivor_id=survivor["_id"], session_object=self.Session)
            S.delete(run_valkyrie=False)
        admin.valkyrie()
        mdb.settlements.remove({"_id": self.settlement["_id"]})
        self.logger.warn("%s removed settlement %s from mdb!" % (self.User.user["login"], self.get_name_and_id()))


    def update_mins(self):
        """ check 'population' and 'death_count' minimums and update the
        settlement's attribs if necessary.

        There's also some misc. house-keeping that happens here, e.g. changing
        lists to sets (since MDB doesn't support sets), etc.

        This one should be called FREQUENTLY, as it enforces the data model and
        sanitizes the settlement object's settlement dict.
        """

        self.enforce_data_model()

        for min_key in ["population", "death_count", "survival_limit"]:
            min_val = self.get_min(min_key)
            orig_val = int(self.settlement[min_key])
            if orig_val < min_val:
                self.settlement[min_key] = min_val
                self.logger.debug("Automatically updated settlement %s (%s) %s from %s to %s" % (self.settlement["name"], self.settlement["_id"], min_key, orig_val, min_val))
                self.log_event("Automatically changed %s from %s to %s" % (min_key, orig_val, min_val))

            # just a little idiot- and user-proofing against negative values
            if self.settlement[min_key] < 0:
                self.settlement[min_key] = 0

#        self.logger.debug("Updated minimum values for settlement %s (%s)" % (self.settlement["name"], self.settlement["_id"]))
        self.enforce_data_model()
        mdb.settlements.save(self.settlement)


    def enforce_data_model(self):
        """ mongo will FTFO if it sees a set(): uniquify our unique lists before
        saving them and exclude any non str/unicode objects that might have
        snuck in while iterating over the cgi.FieldStorage(). """

        set_attribs = ["milestone_story_events", "innovations", "locations", "principles", "quarries"]
        for a in set_attribs:
            self.settlement[a] = list(set([i.strip() for i in self.settlement[a] if type(i) in (str, unicode)]))

        uniq_attribs = ["locations","quarries"]
        for a in uniq_attribs:
            self.settlement[a] = [i.title().strip() for i in self.settlement[a]]

        # fix broken/incorrectly normalized innovations
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


    def get_name_and_id(self):
        """ Laziness function for DRYer log construction. """
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


    def export(self, export_type):
        """ Dumps the settlement to a file, e.g. XLS or PDF. """

        self.logger.debug("%s is exporting campaign %s as '%s'..." % (self.User.user["login"], self.get_name_and_id(), export_type))

        if export_type == "XLS":
            book = export_to_file.xls(self.settlement, self.get_survivors(), self.Session)
            s = StringIO()
            book.save(s)
            length = s.tell()
            s.seek(0)
            return s, length

        return "Invalid export type.", 0

    def get_ancestors(self, return_type=None, survivor_id=False):
        """ This is the settlement's version of this method and it is way
        different from the survivor """

        if survivor_id:
            return "NOT IMPLEMENTED YET"

        if return_type == "html_parent_select":
            male_parent = False
            female_parent = False
            for s in self.get_survivors():
                S = assets.Survivor(survivor_id=s["_id"], session_object=self.Session)
                if S.get_sex() == "M" and "dead" not in S.survivor.keys():
                    male_parent = True
                elif S.get_sex() == "F" and "dead" not in S.survivor.keys():
                    female_parent = True
        else:
            return False

        if not (male_parent and female_parent):
            return ""
        else:
            output = html.survivor.add_ancestor_top
            for role in [("father", "M"), ("mother", "F")]:
                output += html.survivor.add_ancestor_select_top.safe_substitute(parent_role=role[0], pretty_role=role[0].capitalize())
                for s in self.get_survivors():
                    S = assets.Survivor(survivor_id=s["_id"], session_object=self.Session)
                    if S.get_sex() == role[1] and "dead" not in S.survivor.keys():
                        output += html.survivor.add_ancestor_select_row.safe_substitute(parent_id=S.survivor["_id"], parent_name=S.survivor["name"])
                output += html.survivor.add_ancestor_select_bot
            output += html.survivor.add_ancestor_bot
            return output

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
            if s["_id"] in genealogy["has_no_parents"] and s["born_in_ly"] == 1:
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
#                        self.logger.debug("Unable to determine generation for %s after %s loops." % (s["name"], loops))
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
            output = html.settlement.genealogy_headline.safe_substitute(value="Undetermined Lineage")
            sorted_survivor_list = mdb.survivors.find({"_id": {"$in": list(genealogy["no_family"])}}).sort("created_on")
            for s in sorted_survivor_list:
                S = assets.Survivor(survivor_id=s["_id"], session_object=self.Session)
                output += survivor_to_span(S, display="block")
            return output
        if return_type == "html_tree":
            return genealogy["tree"]
        if return_type == "html_generations":
            return genealogy["summary"]

        return genealogy


    def get_locations(self, return_type=False):
        """ Returns a sorted list of locations. """
        final_list = sorted(self.settlement["locations"])

        if return_type == "comma-delimited":
            return ", ".join(final_list)

        if return_type == "html_select_remove":
            if final_list == []:
                return ""

            output = '<select name="remove_location" onchange="this.form.submit()">'
            output += '<option selected disabled hidden value="">Remove Location</option>'
            for location in final_list:
                output += '<option>%s</option>' % location
            output += '</select>'
            return output

        return final_list


    def get_storage(self, return_type=False):
        """ Returns the settlement's storage in a number of ways. """

        # first, normalize storage to try to fix case-sensitivity PEBKAC
        storage = [capwords(i) for i in self.settlement["storage"]]
        self.settlement["storage"] = storage
        mdb.settlements.save(self.settlement)

        if return_type == "html_buttons":
            custom_items = {}
            gear = {}
            resources = {}

            def add_to_gear_dict(item_key):
                item_dict = Items.get_asset(item_key)
                item_location = item_dict["location"]
                if item_location in Locations.get_keys():
                    target_item_dict = gear
                    item_color = Locations.get_asset(item_location)["color"]
                elif item_location in Resources.get_keys():
                    item_color = Resources.get_asset(item_location)["color"]
                    target_item_dict = resources
                if "type" in item_dict.keys():
                    if item_dict["type"] == "gear":
                        target_item_dict = gear
                    else:
                        target_item_dict = resources
                if not item_dict["location"] in target_item_dict.keys():
                    target_item_dict[item_location] = {}
                if not item_key in target_item_dict[item_location].keys():
                    target_item_dict[item_location][item_key] = {"count": 1, "color": item_color}
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

            output = ""
            for item_dict in [gear, resources]:
                for location in sorted(item_dict.keys()):
                    for item_key in sorted(item_dict[location].keys()):
                        quantity = item_dict[location][item_key]["count"]
                        color = item_dict[location][item_key]["color"]
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


    def get_nemeses(self, return_type=None):
        """ Use the 'return_type' arg to specify a special return type, or leave
        unspecified to get sorted list of nemesis monsters back. """

        nemesis_monster_keys = sorted(self.settlement["nemesis_monsters"].keys())

        if return_type == "comma-delimited":
            return ", ".join(nemesis_monster_keys)

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
            output += Nemeses.render_as_html_dropdown(exclude=self.settlement["nemesis_monsters"].keys()) 
            output += '\t<input onchange="this.form.submit()" type="text" class="full_width" name="add_nemesis" placeholder="add custom nemesis"/>'
            return output

        return self.settlement["nemesis_monsters"].keys()


    def increment_nemesis(self, nemesis_key):
        """ Increments a nemesis once if 'nemesis_key' is in the settlement's
        list of known nemesis monsters. """

        if nemesis_key not in self.settlement["nemesis_monsters"].keys():
            return False

        completed_levels = self.settlement["nemesis_monsters"][nemesis_key]
        if completed_levels == []:
            self.settlement["nemesis_monsters"][nemesis_key].append("Lvl 1")
        elif "Lvl 1" in completed_levels:
            self.settlement["nemesis_monsters"][nemesis_key].append("Lvl 2")
        elif "Lvl 2" in completed_levels:
            self.settlement["nemesis_monsters"][nemesis_key].append("Lvl 3")
        else:
            raise
        self.logger.debug("%s checked off nemesis '%s' %s for settlement '%s' (%s)." % (self.User.user["login"], nemesis_key, self.settlement["nemesis_monsters"][nemesis_key][-1], self.settlement["name"], self.settlement["_id"]))


    def get_timeline(self, return_type=False):
        """ Returns the settlement's timeline. """

        story_event_icon_url = os.path.join(settings.get("application","STATIC_URL"), "icons/trigger_story_event.png")
        story_event_icon = '<img class="icon" src="%s"/>' % story_event_icon_url
        nemesis_encounter_icon_url = os.path.join(settings.get("application", "STATIC_URL"), "icons/nemesis_encounter_event.jpg")
        nemesis_encounter_icon = '<img class="icon" src="%s"/>' % nemesis_encounter_icon_url
        settlement_event_icon_url = os.path.join(settings.get("application", "STATIC_URL"), "icons/settlement.png")
        settlement_event_icon = '<img class="icon" src="%s"/>' % settlement_event_icon_url
        quarry_event_icon_url = os.path.join(settings.get("application", "STATIC_URL"), "icons/quarry.png")
        quarry_event_icon = '<img class="icon" src="%s"/>' % quarry_event_icon_url

        current_lantern_year = int(self.settlement["lantern_year"])

        if return_type == "html":
            output = ""
            for year in range(1,41):
                strikethrough = ""
                disabled = ""
                hidden = "full_width"
                if year <= current_lantern_year - 1:
                    disabled = "disabled"
                    strikethrough = "strikethrough"
                    hidden = "hidden"
                output += '<p class="%s">' % strikethrough
                output += html.settlement.timeline_button.safe_substitute(LY=year, button_class=strikethrough, disabled=disabled, settlement_id=self.settlement["_id"],)

                target_year = {"year": year}
                for year_dict in self.settlement["timeline"]:
                    if year == year_dict["year"]:
                        target_year = year_dict

                event_type_tuples = [
                    ("nemesis_encounter", nemesis_encounter_icon),
                    ("story_event", story_event_icon),
                    ("settlement_event", settlement_event_icon),
                    ("quarry_event", quarry_event_icon),
                    ("custom", settlement_event_icon),
                ]

                this_year_events = []
                for event_type_tuple in event_type_tuples:
                    event_type, event_icon = event_type_tuple
                    if event_type in target_year.keys():
                        if target_year[event_type] != []:
                            if type(target_year[event_type]) in [str,unicode]:
                                event_text = target_year[event_type]
                                this_year_events.append(event_text)
                            elif type(target_year[event_type]) == list:
                                event_text = ", ".join(target_year[event_type])
                                this_year_events.extend(target_year[event_type])
                            else:
                                raise Exception("LY %s contains an event with an unsupported type! %s" % type(target_year[event_type]))
                            output += '\t<p class="%s">%s %s</p>\n' % (strikethrough, event_icon, event_text)

                # start the form for updating this year
                output+= html.settlement.timeline_form_top.safe_substitute(settlement_id=self.settlement["_id"], year=year)

                # add blanks for adding events
                output += html.settlement.timeline_add_event.safe_substitute(input_class=hidden, event_type="story_event", pretty_event_type="Story Event", LY="_%s" % year)
                output += html.settlement.timeline_add_event.safe_substitute(input_class=hidden, event_type="settlement_event", pretty_event_type="Settlement Event", LY="_%s" % year)

                # add nemesis picker
                output += html.ui.game_asset_select_top.safe_substitute(operation="add_", name="nemesis_event_%s" % year, operation_pretty="Add", name_pretty="Nemesis Encounter", select_class=hidden)
                for nemesis in self.settlement["nemesis_monsters"]:
                    output += html.ui.game_asset_select_row.safe_substitute(asset=nemesis)
                output += html.ui.game_asset_select_bot

                # add quarry picker
                output += html.ui.game_asset_select_top.safe_substitute(operation="add_", name="quarry_event_%s" % year, operation_pretty="Add", name_pretty="Quarry", select_class=hidden)
                for q in self.get_quarries("list_of_options"):
                    output += html.ui.game_asset_select_row.safe_substitute(asset=q)
                output += html.ui.game_asset_select_bot

                if this_year_events != []:
                    output += html.ui.game_asset_select_top.safe_substitute(operation="remove_", name="timeline_event_%s" % year, operation_pretty="Remove", name_pretty="Timeline Event", select_class=hidden)
                    for event in this_year_events:
                        output += html.ui.game_asset_select_row.safe_substitute(asset=event)
                    output += html.ui.game_asset_select_bot

                button_class = "full_width gradient_orange"
                if hidden == "hidden":
                    button_class = hidden
                output += '<button class="%s">Update Timeline</button>' % button_class

                output += html.settlement.timeline_year_break
            return output


        return "oops! not implemented yet"


    def get_principles(self, return_type=None, query=None):
        """ Returns the settlement's principles. Use the 'return_type' arg to
        specify one of the following, or leave it unspecified to get a sorted
        list back:

            'comma-delimited': a comma-delimited list wrapped in <p> tags.
            'checked': use this with kwarg 'query' to return an empty string if
                if the principle is not present or the string 'checked' if it is

        """

        principles = sorted(self.settlement["principles"])

        if return_type == "comma-delimited":
            if principles == []:
                return "<p>No principles</p>"
            else:
                return "<p>%s</p>" % ", ".join(principles)

        if return_type == "html_select_remove":

            if principles == []:    #bail if we've got nothing
                return ""

            output = html.ui.game_asset_select_top.safe_substitute(operation="remove_", name="principle", operation_pretty="Remove", name_pretty="Principle")
            for principle in principles:
                output += html.ui.game_asset_select_row.safe_substitute(asset=principle)
            output += html.ui.game_asset_select_bot
            return output

        if return_type == "checked" and query is not None:
            if query in self.settlement["principles"]:
                return "checked"
            else:
                return ""

        return principles


    def get_milestones(self, return_type=False, query=None):
        """ Returns the settlement's milestones as a list. If the 'return_type'
        kwarg is "checked" and the 'query' kwarg is a string, this returns an
        empty string if the 'query' is NOT in the settlement's milestones and
        the string 'checked' if it is present."""

        milestones = self.settlement["milestone_story_events"]

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

        innovations = self.get_game_asset("innovations")

        survival_actions = ["Dodge"]
        for innovation in innovations:
            if innovation in Innovations.get_keys() and "survival_action" in Innovations.get_asset(innovation).keys():
                survival_actions.append(Innovations.get_asset(innovation)["survival_action"])

        return list(set(survival_actions))


    def get_bonuses(self, bonus_type, return_type=False):
        """ Returns the buffs/bonuses that settlement gets. 'bonus_type' is
        required and can be 'departure_buff', 'settlement_buff' or
        'survivor_buff'.  """

        innovations = self.get_game_asset("innovations")
        innovations.extend(self.settlement["principles"])

        buffs = {}

        for innovation_key in innovations:
            if innovation_key in Innovations.get_keys() and bonus_type in Innovations.get_asset(innovation_key).keys():
                buffs[innovation_key] = Innovations.get_asset(innovation_key)[bonus_type]

#        self.logger.debug("Settlement %s has '%s' bonuses for %s." % (self.get_name_and_id(), bonus_type, ", ".join(buffs.keys())))

        if return_type == "html":
            output = ""
            if bonus_type == "endeavors":
                icon_url = os.path.join(settings.get("application","STATIC_URL"), "icons/endeavor.png")
                icon = '<img class="icon" src="%s"/> ' % icon_url
                for k in buffs.keys():
                    for endeavor,cost in buffs[k].iteritems():
                        output += '<p>%s <b>%s</b> (%s, %s)</p>' % (cost*icon, endeavor, k, Innovations.get_asset(k)["type"])
            else:
                for k in buffs.keys():
                    output += '<p><b>%s:</b> %s</p>\n' % (k, buffs[k])
            return output

        return buffs


    def get_quarries(self, return_type=None):
        """ Returns a list of the settlement's quarries. Leave the 'return_type'
        arg unspecified to get a sorted list. """
        quarries = sorted(self.settlement["quarries"])

        if return_type == "comma-delimited":
            return ", ".join(quarries)

        if return_type == "list_of_options":
            output_list = []
            for quarry in quarries:
                if quarry in Quarries.get_keys() and "no_levels" in Quarries.get_asset(quarry).keys():
                    output_list.append(quarry)
                else:
                    for i in range(1,4):
                        output_list.append("%s Lvl %s" % (quarry,i))
            return output_list

        return quarries


    def get_settlement_notes(self):
        """ Returns the settlement's notes. Assumes an HTML target. """

        if not "settlement_notes" in self.settlement:
            return ""
        else:
            return self.settlement["settlement_notes"]


    def get_survivors(self, return_type=False, user_id=None, exclude=[], exclude_dead=False):
        """ Returns the settlement's survivors. Leave 'return_type' unspecified
        if you want a mongo cursor object back. """

        query = {"settlement": self.settlement["_id"], "_id": {"$nin": exclude}}

        if exclude_dead:
            query["dead"] = {"$exists": False}

        survivors = mdb.survivors.find(query).sort("name")

        if self.User is not None:
            user_login = self.User.user["login"]
        elif self.User is None and user_id is not None:
            self.User = assets.User(user_id=user_id)
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
                S = assets.Survivor(survivor_id=survivor["_id"])
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
            # this is our big-boy, full-featured controls for survivor management
            if survivors.count() == 0:
                return html.survivor.no_survivors_error

            groups = {
                1: {"name": "Hunting Party", "survivors": [], },
                2: {"name": "Favorite", "survivors": [], },
                3: {"name": "Available", "survivors": [], },
                4: {"name": "Skipping Next Hunt", "survivors": [], },
                5: {"name": "Retired", "survivors": [], },
                6: {"name": "The Dead", "survivors": [], },
            }

            anonymous = []
            available = []
            for survivor in survivors:
                S = assets.Survivor(survivor_id=survivor["_id"], session_object=self.Session)
                annotation = ""
                user_owns_survivor = False
                disabled = "disabled"

                if survivor["email"] == user_login or current_user_is_settlement_creator or "public" in survivor.keys():
                    disabled = ""
                    user_owns_survivor = True

                button_class = ""
                if user_owns_survivor:
                    button_class = "green"

                if "skip_next_hunt" in S.survivor.keys():
                    annotation = "&ensp; <i>Skipping next hunt</i><br/>"
                    button_class = "dark_green"

                for t in [("retired", "retired_in", "tan"),("dead", "died_in", "silver")]:
                    attrib, event, color = t
                    if attrib in S.survivor.keys():
                        if event in S.survivor.keys():
                            annotation = "&ensp; <i>%s LY %s</i><br/>" % (event.replace("_"," ").capitalize(), S.survivor[event])
                        else:
                            annotation = "&ensp; <i>%s</i><br/>" % attrib.title()
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

                if group["name"] == "Hunting Party" and group["survivors"] == []:
                    output += "<p>Use [::] to add survivors to the hunting party.</p>"
                elif group["name"] == "Hunting Party" and group["survivors"] != [] and current_user_is_settlement_creator:
                    # settlement admin_controls; only show these if we've got
                    #   survivors and the current user is the admin
                    output += html.settlement.return_hunting_party.safe_substitute(settlement_id=self.settlement["_id"])
                    output += html.settlement.hunting_party_macros.safe_substitute(settlement_id=self.settlement["_id"])

            return output + html.settlement.campaign_summary_survivors_bot

        if return_type == "chronological_order":
            return mdb.survivors.find(query).sort("created_on")

        return survivors


    def return_hunting_party(self):
        """ Gets the hunting party, runs heal("Return from Hunt") on them."""
        healed_survivors = 0
        returning_survivor_id_list = []
        returning_survivor_name_list = []
        for survivor in self.get_survivors("hunting_party"):
            S = assets.Survivor(survivor_id=survivor["_id"], session_object=self.Session)
            returning_survivor_id_list.append(S.survivor["_id"])
            if "dead" not in S.survivor.keys():
                returning_survivor_name_list.append(S.survivor["name"])
            S.heal("Return from Hunt")
            healed_survivors += 1

            # Check for disorders with an "on_return" effect
            for d in S.survivor["disorders"]:
                if d in Disorders.get_keys() and "on_return" in Disorders.get_asset(d):
                    for k, v in Disorders.get_asset(d)["on_return"].iteritems():
                        S.survivor[k] = v
                    mdb.survivors.save(S.survivor)

        # remove "skip_next_hunt" from anyone who has it but didn't return
        for survivor in self.get_survivors(exclude=returning_survivor_id_list, exclude_dead=False):
            if "skip_next_hunt" in survivor.keys():
                del survivor["skip_next_hunt"]
                mdb.survivors.save(survivor)
        self.log_event("The hunting party (%s) returned." % ", ".join(returning_survivor_name_list))


    def modify_hunting_party(self, params):
        """ Modifies all hunters in the settlement's hunting party according to
        cgi.FieldStorage() params. """

        target_attrib = params["hunting_party_operation"].value
        target_action = params["operation"].value
        self.logger.debug("Hunting party operation by %s: %s %s..." % (self.User.user["login"], target_action, target_attrib))

        for s in self.get_survivors("hunting_party"):
            if target_action == "increment":
                s[target_attrib] = int(s[target_attrib]) + 1
            elif target_action == "decrement":
                s[target_attrib] = int(s[target_attrib]) - 1
            self.logger.debug("%s %sed Survivor '%s' %s by 1" % (self.User.user["login"], target_action, s["name"], target_attrib))

            # enforce settlement survival limit/min
            if target_attrib == "survival":
                if s[target_attrib] > int(self.settlement["survival_limit"]):
                    s[target_attrib] = self.settlement["survival_limit"]

            # enforce a minimum of zero for all attribs
            if s[target_attrib] < 0:
                s[target_attrib] = 0

            mdb.survivors.save(s)

    def get_recently_added_items(self):
        """ Returns the three items most recently appended to storage. """
        max_items = 3
        all_items = copy(self.settlement["storage"])
        return_list = set()
        while len(return_list) < max_items:
            if all_items == []:
                break
            return_list.add(all_items.pop())
        return sorted(list([capwords(i) for i in return_list]))



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
            results = mdb.survivors.find({"settlement": settlement_id, "dead": {"$exists": False}}).count()
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

        player_set = set()
        survivors = mdb.survivors.find({"settlement": self.settlement["_id"]})
        for s in survivors:
            player_set.add(s["email"])

        if count_only:
            return len(player_set)

        if return_type == "html":
            if len(player_set) == 1 and self.User.user["login"] in player_set:
                return html.settlement.player_controls_none.safe_substitute(name=self.settlement["name"])

            output = html.settlement.player_controls_table_top
            for player in sorted(list(player_set)):
                player_id = mdb.users.find_one({"login": player})["_id"]
                if player_id == self.settlement["created_by"]:
                    output += html.settlement.player_controls_table_row.safe_substitute(email=player, role="<i>Founder</i>")
                else:
                    if "admins" in self.settlement.keys() and player in self.settlement["admins"]:
                        controls = '<select name="player_role_%s"><option>Player</option><option selected>Admin</option></select>' % player
                    else:
                        controls = '<select name="player_role_%s"><option selected>Player</option><option>Admin</option></select>' % player
                    output += html.settlement.player_controls_table_row.safe_substitute(email=player, role=controls)
            output += html.settlement.player_controls_table_bot
            return output

        return player_set


    def update_timeline(self, new_lantern_year=None, increment=False, add_event=(), rm_event=()):
        """ This is where we manage the timeline, incrementing Lantern Year,
        adding/removing settlement events, etc.

        The 'add_event' and 'rm_event' kwargs should be two part tuples where
        the first part is the LY (as an int) and the second part is a str of the
        thing we're removing.
        """

        current_ly = int(self.settlement["lantern_year"])

        # increment LY if we're doing that
        if increment:
            self.log_event("Lantern year %s has ended." % current_ly)
            current_ly = current_ly + 1
            self.settlement["lantern_year"] = current_ly

        # handle arbitrary updates/changes to LY
        if new_lantern_year is not None and int(new_lantern_year) != current_ly:
            new_lantern_year= int(new_lantern_year)
            self.settlement["lantern_year"] = new_lantern_year
            self.log_event("It is now Lantern Year %s." % new_lantern_year)

        # add an event to the timeline if we're doing that
        if add_event != ():
            target_ly, event_type, new_event = add_event

            if event_type == "nemesis_event":
                event_type = "nemesis_encounter"
                new_event = "Nemesis Encounter: %s" % new_event

            self.logger.debug("Adding %s event '%s' to LY '%s' for %s" % (event_type, new_event, target_ly, self.get_name_and_id()))
            for year_dict in self.settlement["timeline"]:   # timeline is a list of dicts
                if year_dict["year"] == target_ly:
                    year_index = self.settlement["timeline"].index(year_dict)
                    self.settlement["timeline"].remove(year_dict)
                    if event_type not in year_dict:
                        year_dict[event_type] = []
                    if type(year_dict[event_type]) in [str,unicode]:
                        year_dict[event_type] = [year_dict[event_type]] # change strings into lists
                    year_dict[event_type].append(new_event)
                    if event_type == "quarry_event":
                        year_dict[event_type] = sorted(list(year_dict[event_type]))    # uniquify and sort
                    else:
                        year_dict[event_type] = sorted(list(set(year_dict[event_type])))    # uniquify and sort
                    self.settlement["timeline"].insert(year_index, year_dict)
                    self.log_event("'%s' %s added to LY %s" % (new_event, event_type.replace("_"," "), target_ly))

        if rm_event != ():
            target_ly, target_event_string = rm_event
            for year_dict in self.settlement["timeline"]:
                if year_dict["year"] == target_ly:
                    for event_type in year_dict.keys():
                        if event_type != "year" and target_event_string in year_dict[event_type]:
                            if type(year_dict[event_type]) in [str, unicode]:
                                del year_dict[event_type]
                            else:
                                year_dict[event_type].remove(target_event_string) 
                            #year_dict[event_type].remove(target_event_string)
                            self.log_event("Removed %s '%s' from LY %s." % (event_type.replace("_"," "), target_event_string, target_ly))
                            self.logger.debug("%s removed %s '%s' from LY %s for %s" % (self.User.user["login"], event_type.replace("_"," "), target_event_string, target_ly, self.get_name_and_id()))

    def update_admins(self, player_login, player_role):
        """ Adds or removes player emails from the admins list. """
        if not "admins" in self.settlement.keys():
            self.settlement["admins"] = []

        if player_role != "Admin" and player_login in self.settlement["admins"]:
            self.settlement["admins"].remove(player_login)
            self.logger.debug("%s is no longer an admin of %s" % (player_login, self.get_name_and_id()))

        if player_role == "Admin" and player_login not in self.settlement["admins"]:
            self.settlement["admins"].append(player_login)
            self.logger.debug("%s is now an admin of %s" % (player_login, self.get_name_and_id()))


    def update_principles(self, add_new_principle=False):
        """ Since certain principles are mutually exclusive, all of the biz
        logic for toggling one on and toggling off its opposite is here. """

        principles = set(self.settlement["principles"])
        if add_new_principle and not add_new_principle in self.settlement["principles"]:
            principles.add(add_new_principle)
            self.logger.debug("%s added principle '%s' to settlement '%s' (%s)." % (self.User.user["login"], add_new_principle, self.settlement["name"], self.settlement["_id"]))
            self.log_event("'%s' added to settlement Principles." % add_new_principle)

        for k in mutually_exclusive_principles.keys():
            tup = mutually_exclusive_principles[k]
            if tup[0] == add_new_principle:
                if tup[1] in principles:
                    principles.remove(tup[1])
            elif tup[1] == add_new_principle:
                if tup[0] in principles:
                    principles.remove(tup[0])


        self.settlement["principles"] = sorted(list(principles))
        self.update_mins()  # this is a save


    def get_game_asset_deck(self, asset_type, return_type=False, exclude_always_available=False):
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
            asset_deck = Asset.get_always_available()

        for asset_key in current_assets:
            if asset_key in Asset.get_keys() and "consequences" in Asset.get_asset(asset_key).keys():
                for c in Asset.get_asset(asset_key)["consequences"]:
                    asset_deck.add(c)

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
            asset_deck = Asset.build_asset_deck(self.settlement, self.get_quarries("list_of_options"))   # self here is the settlement object

        final_list = sorted(list(set(asset_deck)))

        if return_type == "comma-delimited":
            if final_list == []:
                return ""
            else:
                headline = "%s Deck" % Asset.get_pretty_name()
            return "<h3>%s</h3>\n<p>%s</p>" % (headline, ", ".join(final_list))

        return final_list


    def get_game_asset(self, asset_type=None, return_type=False, exclude=[]):
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
        self.update_mins()

        if asset_type == "defeated_monsters":   # our pseudo model
            Asset = DefeatedMonsters
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

        #   now do return types
        pretty_asset_name = asset_name.replace("_"," ").title()
        if return_type == "comma-delimited":
            if hasattr(Asset, "uniquify"):
                asset_keys = list(set(asset_keys))
            if hasattr(Asset, "sort_alpha"):
                asset_keys = sorted(asset_keys)
            if hasattr(Asset, "stack"):
                asset_keys = stack_list(asset_keys)
            output = ", ".join(asset_keys)
            return "<p>%s</p>" % output
        elif return_type == "html_add":
            op = "add"
            output = html.ui.game_asset_select_top.safe_substitute(
                operation="%s_" % op, operation_pretty=op.capitalize(),
                name=asset_name,
                name_pretty=pretty_asset_name,
            )

            for asset_key in self.get_game_asset_deck(asset_type):
                output += html.ui.game_asset_select_row.safe_substitute(asset=asset_key)
            output += html.ui.game_asset_select_bot
            output += html.ui.game_asset_add_custom.safe_substitute(asset_name=asset_name, asset_name_pretty=pretty_asset_name)
            return output
        elif return_type == "html_remove":
            if asset_keys == []:
                return ""
            op = "remove"
            output = html.ui.game_asset_select_top.safe_substitute(
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
        elif not return_type:
            return asset_keys

        self.logger.error("An error occurred while retrieving settlement game assets ('%s')!" % asset_type)


    def add_kill(self, monster_desc):
        """ Adds a kill to the settlement: appends it to the 'defeated_monsters'
        monsters and also to the settlement's kill_board. """

        if not "kill_board" in self.settlement.keys():
            self.settlement["kill_board"] = {}
        current_ly = "ly_%s" % self.settlement["lantern_year"]
        if not current_ly in self.settlement["kill_board"].keys():
            self.settlement["kill_board"][current_ly] = []
        self.settlement["kill_board"][current_ly].append(monster_desc)
        self.settlement["defeated_monsters"].append(monster_desc)
        self.log_event("%s defeated!" % monster_desc)
        mdb.settlements.save(self.settlement)


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

        # otherwise, if we've got a str, let's get busy
        if asset_class == "storage":
            game_asset_key = capwords(game_asset_key)
            for i in range(int(game_asset_quantity)):
                self.settlement[asset_class].append(game_asset_key)
            self.logger.info("'%s' appended '%s' x%s to settlement '%s' (%s) storage." % (self.User.user["login"], game_asset_key, game_asset_quantity, self.settlement["name"], self.settlement["_id"]))
            return True

        exec "Asset = %s" % asset_class.capitalize()

        self.logger.debug("'%s' is adding '%s' asset '%s' (%s) to settlement '%s' (%s)..." % (self.User.user["login"], asset_class, game_asset_key, type(game_asset_key), self.settlement["name"], self.settlement["_id"]))

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

#        exec "Asset = %s" % asset_class.capitalize()   # this isn't necessary yet

        self.settlement[asset_class].remove(game_asset_key)
        self.logger.debug("%s removed asset '%s' from settlement '%s' (%s) successfully!" % (self.User.user["login"], game_asset_key, self.settlement["name"], self.settlement["_id"]))
        mdb.settlements.save(self.settlement)


    def modify(self, params):
        """ Pulls a settlement from the mdb, updates it and saves it using a
        cgi.FieldStorage() object.

        All of the business logic lives here.
        """

        for p in params:

            game_asset_key = None
            if type(params[p]) != list:
                game_asset_key = params[p].value.strip()

            if p in ["asset_id", "modify", "add_item_quantity"]:
                pass
            elif p == "add_defeated_monster":
                self.add_kill(game_asset_key)
            elif p == "remove_defeated_monster":
                self.rm_game_asset("defeated_monsters", game_asset_key)
            elif p == "add_quarry":
                self.settlement["quarries"].append(game_asset_key)
                self.log_event("%s added to settlement Quarry List" % game_asset_key)
            elif p == "add_nemesis":
                self.settlement["nemesis_monsters"][params[p].value] = []
            elif p == "increment_nemesis":
                self.increment_nemesis(game_asset_key)
            elif p == "add_item" and not "remove_item" in params:
                self.add_game_asset("storage", game_asset_key, params["add_item_quantity"].value)
            elif p == "remove_item" and not "add_item" in params:
                self.settlement["storage"].remove(game_asset_key)
                self.logger.debug("%s removed %s from settlement %s storage" % (self.User.get_name_and_id(), game_asset_key, self.get_name_and_id()))
            elif p == "add_innovation":
                self.add_game_asset("innovations", game_asset_key)
            elif p == "remove_innovation":
                self.rm_game_asset("innovations", game_asset_key)
            elif p == "add_location":
                self.add_game_asset("locations", game_asset_key)
            elif p == "remove_location":
                self.settlement["locations"].remove(game_asset_key)
            elif p in ["new_life_principle", "death_principle", "society_principle", "conviction_principle"]:
                if "remove_principle" not in params:
                    new_principle = params[p].value
                    self.update_principles(new_principle)
            elif p == "remove_principle":
                self.rm_game_asset("principles", game_asset_key)
            elif p in [
                "First child is born",
                "First time death count is updated",
                "Population reaches 15",
                "Settlement has 5 innovations",
                "Population reaches 0",
            ]:
                self.settlement["milestone_story_events"].append(p)
            elif p == "abandon_settlement":
                self.log_event("Settlement abandoned!")
                self.settlement["abandoned"] = datetime.now()
            # timeline operations
            elif p == "increment_lantern_year":
                self.update_timeline(increment=True)
            elif p == "lantern_year":
                self.update_timeline(game_asset_key)
            elif p.split("_")[0] == 'add' and p.split("_")[2] == 'event':
                target_year = int(p.split("_")[-1])
                event_type = "_".join(p.split("_")[1:3])
                self.update_timeline(add_event=(target_year, event_type, game_asset_key))
            elif p.split("_")[0:3] == ["remove","timeline","event"]:
                target_year = int(p.split("_")[-1])
                self.update_timeline(rm_event=(target_year, game_asset_key))
            elif p == "hunting_party_operation":
                self.modify_hunting_party(params)
                break
            elif p.split("_")[0] == "player" and p.split("_")[1] == "role":
                player_login = "_".join(p.split("_")[2:])
                self.update_admins(player_login, game_asset_key)
            else:
                self.settlement[p] = game_asset_key
                self.logger.debug("%s set '%s' = '%s' for settlement '%s' (%s)." % (self.User.user["login"], p, game_asset_key, self.settlement["name"], self.settlement["_id"]))

        #
        #   settlement post-processing starts here!
        #

        #   add milestones for principles:
        for principle in self.settlement["principles"]:
            principle_dict = Innovations.get_asset(principle)
            if "type" in principle_dict.keys() and principle_dict["type"] == "principle" and "milestone" in principle_dict.keys():
                self.settlement["milestone_story_events"].append(principle_dict["milestone"])


        # update mins will call self.enforce_data_model() and save
        self.update_mins()


    def render_html_event_log(self):
        """ Renders the settlement's event log as HTMl. """

        event_log_entries = list(mdb.settlement_events.find({"settlement_id": self.settlement["_id"]}).sort("created_by",-1))
        if event_log_entries == []:
            event_log_entries.append({"ly":"-","event":"Nothing here yet!"})
        event_log = html.settlement.event_table_top
        zebra=False
        for e in reversed(event_log_entries):
            event_log += html.settlement.event_table_row.safe_substitute(ly=e["ly"], event=e["event"], zebra=zebra)
            if not zebra:
                zebra = True
            else:
                zebra = False
        event_log += html.settlement.event_table_bot

        output = html.settlement.event_log.safe_substitute(
            generations = self.get_genealogy("html_generations"),
            family_tree = self.get_genealogy("html_tree"),
            no_family = self.get_genealogy("html_no_family"),
            log_lines = event_log,
            settlement_name = self.settlement["name"],
        )
        return output


    def render_html_summary(self, user_id=False):
        """ This is the summary view we print at the top of the game view. It's
        not a form. """

        output = html.settlement.summary.safe_substitute(
            export_xls = html.settlement.export_button.safe_substitute(export_type="XLS", export_pretty_name="Export to XLS", asset_id=self.settlement["_id"]),
            settlement_notes = self.get_settlement_notes(),
            settlement_name=self.settlement["name"],
            principles = self.get_principles("comma-delimited"),
            population = self.settlement["population"],
            death_count = self.settlement["death_count"],
            sex_count = self.get_survivors(return_type="sex_count", exclude_dead=True),
            survivors = self.get_survivors(return_type="html_campaign_summary", user_id=user_id),
            lantern_year = self.settlement["lantern_year"],
            survival_limit = self.settlement["survival_limit"],
            innovations = self.get_game_asset("innovations", return_type="comma-delimited", exclude=self.settlement["principles"]),
            locations = self.get_locations(return_type="comma-delimited"),
            endeavors = self.get_bonuses('endeavors', return_type="html"),
            departure_bonuses = self.get_bonuses('departure_buff', return_type="html"),
            settlement_bonuses = self.get_bonuses('settlement_buff', return_type="html"),
            survivor_bonuses = self.get_bonuses('survivor_buff', return_type="html"),
            defeated_monsters = self.get_game_asset("defeated_monsters", return_type="comma-delimited"),
            quarries = self.get_quarries("comma-delimited"),
            nemesis_monsters = self.get_nemeses("comma-delimited"),
        )
        return output


    def render_html_form(self):
        """ This is where we create the Settlement Sheet, so there's a lot of
        presentation and business logic here. """

        self.update_mins()

        # dynamically create the 'p_controls' dict based on user preference re:
        #   hiding preference controls; use p_controls below to show/hide pref
        #   toggles dynamically
        p_keys = ["new_life", "death", "society", "conviction"]
        if self.User.get_preference("hide_principle_controls"):
            p_controls = {k:"hidden" for k in p_keys}
        else:
            p_controls = {k:"" for k in p_keys}

        mp_tuples = [
            ("First child is born","new_life"),
            ("First time death count is updated","death"),
            ("Population reaches 15","society"),
        ]
        for mp_tuple in mp_tuples:
            milestone_event, principle = mp_tuple
            if milestone_event in self.settlement["milestone_story_events"]:
                p_controls[principle] = ""

        # use thresholds to determine whether certain controls are visible
        threshold_tuples = [
            ("death_count", "death", 1),
            ("population", "society", 15),
            ("lantern_year", "conviction", 12),
        ]
        for t in threshold_tuples:
            attrib, p_control_key, min_val = t
            if self.get_attribute(attrib) >= min_val:
                p_controls[p_control_key] = ""

        # additional/custom logic for hide/show principle controls
        for s in self.get_survivors():
            if "father" in s.keys() or "mother" in s.keys():
                p_controls["new_life"] = ""


        # user preferences determine if the timeline controls are visible
        if self.User.get_preference("hide_timeline"):
            timeline_controls = "none"
        else:
            timeline_controls = ""

        # this is stupid: I need to refactor this out at some point
        abandoned = ""
        if "abandoned" in self.settlement.keys():
            abandoned = '<h1 class="alert">ABANDONED</h1>'
        all_hidden_warning = "<p>(Update settlement Milestones to show controls for adding Settlement Principles.)</p>"
        for k in p_controls.keys():
            if p_controls[k] != "hidden":
                all_hidden_warning = ""

        return html.settlement.form.safe_substitute(
            MEDIA_URL = settings.get("application","STATIC_URL"),
            settlement_id = self.settlement["_id"],
            game_link = self.asset_link(context="asset_management"),

            name = self.settlement["name"],
            abandoned = abandoned,

            population = self.get_attribute("population"),
            death_count = self.get_attribute("death_count"),

            survival_limit = self.get_attribute("survival_limit"),
            min_survival_limit = self.get_min("survival_limit"),
            lost_settlements = self.settlement["lost_settlements"],
            settlement_notes = self.get_settlement_notes(),

            survivors = self.get_survivors(return_type="html_campaign_summary"),

            endeavors = self.get_bonuses('endeavors', return_type="html"),
            departure_bonuses = self.get_bonuses('departure_buff', return_type="html"),
            settlement_bonuses = self.get_bonuses('settlement_buff', return_type="html"),

            items_options = Items.render_as_html_dropdown_with_divisions(recently_added=self.get_recently_added_items()),
            storage = self.get_storage("html_buttons"),

            new_life_principle_hidden = p_controls["new_life"],
            society_principle_hidden = p_controls["society"],
            death_principle_hidden = p_controls["death"],
            conviction_principle_hidden = p_controls["conviction"],
            all_hidden_warning = all_hidden_warning,

            cannibalize_checked = self.get_principles("checked", query="Cannibalize"),
            graves_checked = self.get_principles("checked", query="Graves"),
            protect_the_young_checked = self.get_principles("checked", query="Protect the Young"),
            survival_of_the_fittest_checked = self.get_principles("checked", query="Survival of the Fittest"),
            collective_toil_checked = self.get_principles("checked", query="Collective Toil"),
            accept_darkness_checked = self.get_principles("checked", query="Accept Darkness"),
            barbaric_checked = self.get_principles("checked", query="Barbaric"),
            romantic_checked = self.get_principles("checked", query="Romantic"),
            principles_rm = self.get_principles("html_select_remove"),

            lantern_year = self.settlement["lantern_year"],
            timeline = self.get_timeline("html"),
            display_timeline = timeline_controls,

            first_child_checked = self.get_milestones("checked", query="First child is born"),
            first_death_checked = self.get_milestones("checked", query="First time death count is updated"),
            pop_15_checked = self.get_milestones("checked", query="Population reaches 15"),
            five_innovations_checked = self.get_milestones("checked", query="Settlement has 5 innovations"),
            game_over_checked = self.get_milestones("checked", query="Population reaches 0"),

            nemesis_monsters = self.get_nemeses("html_buttons"),

            quarries = self.get_quarries("comma-delimited"),
            quarry_options = Quarries.render_as_html_dropdown(exclude=self.get_quarries()),

            innovations = self.get_game_asset("innovations", return_type="comma-delimited", exclude=self.settlement["principles"]),
            innovations_add = self.get_game_asset("innovations", return_type="html_add"),
            innovations_rm = self.get_game_asset("innovations", return_type="html_remove", exclude=self.settlement["principles"]),
            innovation_deck = self.get_game_asset_deck("innovations", return_type="comma-delimited", exclude_always_available=True),

            locations = self.get_game_asset("locations", return_type="comma-delimited"),
            locations_add = self.get_game_asset("locations", return_type="html_add"),
            locations_rm = self.get_game_asset("locations", return_type="html_remove"),

            defeated_monsters = self.get_game_asset("defeated_monsters", return_type="comma-delimited"),
            defeated_monsters_add = self.get_game_asset("defeated_monsters", return_type="html_add"),
            defeated_monsters_rm = self.get_game_asset("defeated_monsters", return_type="html_remove"),

            player_controls = self.get_players("html"),
        )


    def asset_link(self, context=None):
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

        self.update_mins()  # update settlement mins before we create any text

        if context == "campaign_summary":
            button_class = "gradient_yellow floating_asset_button"
            link_text = html.dashboard.settlement_flash
            desktop_text = "Edit %s" % self.settlement["name"]
            asset_type = "settlement"
        elif context == "asset_management":
            button_class = "gradient_purple floating_asset_button"
            link_text = html.dashboard.campaign_flash
            desktop_text = "%s Campaign Summary" % self.settlement["name"]
            asset_type = "campaign"
        elif context == "dashboard_campaign_list":
            button_class = "gradient_violet"
            link_text = html.dashboard.campaign_flash + "<b>%s</b><br/>LY %s. Survivors: %s Players: %s" % (self.settlement["name"], self.settlement["lantern_year"], self.settlement["population"], self.get_players(count_only=True))
            desktop_text = ""
            asset_type = "campaign"
        else:
            button_class = "gradient_yellow"
            link_text = html.dashboard.settlement_flash + "<b>%s</b>" % self.settlement["name"]
            if "abandoned" in self.settlement.keys():
                link_text += ' [ABANDONED]'
            desktop_text = ""
            asset_type = "settlement"

        return html.dashboard.view_asset_button.safe_substitute(
            button_class = button_class,
            asset_type = asset_type,
            asset_id = self.settlement["_id"],
            asset_name = link_text,
            desktop_text = desktop_text,
        )






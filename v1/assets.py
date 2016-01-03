#!/usr/bin/env python

from bson.objectid import ObjectId
from bson import json_util
from copy import copy
from datetime import datetime
from hashlib import md5
import json
import operator
import os
import pickle
import random
from string import Template

import admin
import assets
import game_assets
import html
from models import Abilities, Disorders, Epithets, FightingArts, Locations, Items, Innovations, Nemeses, Resources, Quarries, WeaponProficiencies
from session import Session
from utils import mdb, get_logger, load_settings, get_user_agent, ymdhms

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


    def is_admin(self):
        """ Returns True if the user is an admin, False if they are not. """

        if "admin" in self.user.keys() and type(self.user["admin"]) == datetime:
            return True
        else:
            return False

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


        if "confirm_on_remove_from_storage" in params:
            confirmation_preference = params["confirm_on_remove_from_storage"].value
            if confirmation_preference == "confirm":
                self.user["preferences"]["confirm_on_remove_from_storage"] = True
                self.logger.debug("'%s' added 'confirm_on_remove_from_storage' from user preferences!" % self.user["login"])
                user_admin_log_dict["msg"] += "Confirm on remove from storage set!"
            elif confirmation_preference == "do_not_confirm":
                try:
                    del self.user["preferences"]["confirm_on_remove_from_storage"]
                    self.logger.debug("'%s' removed 'confirm_on_remove_from_storage' from user preferences!" % self.user["login"])
                    user_admin_log_dict["msg"] += "Confirm on remove from storage unset!"
                except:
                    pass
            else:
                self.logger.warn("Illegal value '%s' rejected from user preferences!" % confirmation_preference)

        user_admin_log_dict["msg"] = user_admin_log_dict["msg"].strip()
        mdb.user_admin.insert(user_admin_log_dict)

    def dump_assets(self, dump_type=None):
        """ Returns a dictionary representation of a user's complete assets. """

        assets_dict = {
            "user": self.user,
            "survivors": [s for s in mdb.survivors.find({"created_by": self.user["_id"]})],
            "settlements": [s for s in mdb.settlements.find({"created_by": self.user["_id"]})],
        }

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
            game_dict[settlement_id] = S.settlement["name"]
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
            formatted_log_msg = "<p>Latest admin log:</p><p><b>%s</b>:</b> %s</p>" % (last_log_msg["created_on"].strftime(ymdhms), last_log_msg["msg"])

        pref_conf_rem = ""
        if "preferences" in self.user.keys():
            if "confirm_on_remove_from_storage" not in self.user["preferences"].keys():
                pref_conf_rem = "checked"
        else:
            pref_conf_rem = "checked"

        output = html.dashboard.motd.safe_substitute(
            preferences_confirm_on_remove = pref_conf_rem,
            session_id = self.Session.session["_id"],
            login = self.user["login"],
            last_sign_in = self.user["latest_sign_in"].strftime(ymdhms),
            version = settings.get("application", "version"),
            last_log_msg = formatted_log_msg,
        )
        return output


    def html_world(self):
        """ Creates the HTML world panel for the user. This is a method of the
        User object because it will do stuff with the user's friends. """

        latest_fatality = mdb.the_dead.find_one({"complete": {"$exists": True}}, sort=[("created_on", -1)])

        output = html.dashboard.world.safe_substitute(
            total_users = mdb.users.find().count(),
            total_settlements = mdb.settlements.find().count(),
            total_sessions = mdb.sessions.find().count(),
            live_survivors = mdb.survivors.find({"dead": {"$exists": False}}).count(),
            dead_survivors = mdb.the_dead.find().count(),
            dead_name = latest_fatality["name"],
            dead_settlement = latest_fatality["settlement_name"],
            cause_of_death = latest_fatality["cause_of_death"],
            dead_ly = latest_fatality["lantern_year"],
            dead_xp = latest_fatality["hunt_xp"],
            dead_courage = latest_fatality["Courage"],
            dead_understanding = latest_fatality["Understanding"],
        )

        return output



#
#   SURVIVOR CLASS
#

class Survivor:

    def __init__(self, survivor_id=False, params=False, session_object=None):
        """ Initialize this with a cgi.FieldStorage() as the 'params' kwarg
        to create a new survivor. Otherwise, use a mdb survivor _id value
        to initalize with survivor data from mongo. """

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
                    self.survivor["abilities_and_impairments"].append(prof_dict["all_survivors"])
                    self.logger.debug("Auto-applied settlement default '%s' to survivor '%s' of '%s'." % (prof_dict["all_survivors"], self.survivor["name"], self.Settlement.settlement["name"]))
            elif innovation_key.split("-")[0].strip() == "Mastery":
                custom_weapon = " ".join(innovation_key.split("-")[1:]).title().strip()
                spec_str = "Specialization - %s" % custom_weapon
                if spec_str not in self.survivor["abilities_and_impairments"]:
                    self.survivor["abilities_and_impairments"].append(spec_str)
                    self.logger.debug("Auto-applied settlement default '%s' to survivor '%s'." % (spec_str, self.survivor["name"]))


        mdb.survivors.save(self.survivor)

    def new(self, params):
        """ Create a new survivor from cgi.FieldStorage() params. """

        if "name" in params:
            survivor_name = params["name"].value
        else:
            survivor_name = "Anonymous"

        created_by = self.User.user["_id"]
        settlement_id = ObjectId(params["settlement_id"].value)
        survivor_email = params["email"].value.lower()
        survivor_sex = params["sex"].value[0].upper()

        survivor_dict = {
            "epithets": [],
            "created_on": datetime.now(),
            "created_by": created_by,
            "settlement": settlement_id,
            "survival": 1,
            "name": survivor_name,
            "email": survivor_email,
            "sex": survivor_sex,
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
            "born_in_ly": self.Settlement.settlement["lantern_year"],
        }

        # add parents if they're specified
        parents = []
        for parent in ["father", "mother"]:
            if parent in params:
                p_id = ObjectId(params[parent].value)
                parents.append(mdb.survivors.find_one({"_id": p_id})["name"])
                survivor_dict[parent] = ObjectId(p_id)
        if parents != []:
            if survivor_sex == "M":
                genitive_appellation = "Son"
            elif survivor_sex == "F":
                genitive_appellation = "Daughter"
            survivor_dict["epithets"].append("%s of %s" % (genitive_appellation, " and ".join(parents)))

        self.logger.debug("Automatically applying 'new_survivor' buffs to new survivor '%s' before inserting..." % survivor_name)
        new_survivor_buffs = self.Settlement.get_bonuses("new_survivor")
        for b in new_survivor_buffs.keys():
            buffs = new_survivor_buffs[b]
            for attrib in buffs.keys():
                survivor_dict[attrib] = survivor_dict[attrib] + buffs[attrib]
            self.logger.debug("Applied buffs for '%s' successfully: %s" % (b, buffs))

        survivor_id = mdb.survivors.insert(survivor_dict)
        self.logger.info("User '%s' created new survivor '%s [%s]' successfully." % (self.User.user["login"], survivor_name, survivor_sex))

        self.Settlement.update_mins()

        return survivor_id


    def get_ancestors(self, return_type=None):
        """ This is a stub for now. Don't use it. """

        if not "ancestors" in self.survivor.keys():
            ancestors = []
        else:
            ancestors = self.survivor["ancestors"]

        return ancestors


    def get_survival_actions(self, return_as=False):
        possible_actions = game_assets.survival_actions

        available_actions = []
        for a in possible_actions:
            if a in self.Settlement.get_survival_actions():
                available_actions.append(a)

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
            self.survivor["ability_customizations"][attrib_key] = []

        self.survivor["ability_customizations"][attrib_key].append(attrib_customization)
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
                    suffix = " ".join(self.survivor["ability_customizations"][ability])
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

    def toggle(self, toggle_key, toggle_value):
        """ Toggles an attribute on or off. The 'toggle_value' arg is either
        going to be a MiniFieldStorage list (from cgi.FieldStorage) or its going
        to be a single value, e.g. a string.

        If it's a list, assume we're toggling something on; if it's a single
        value, assume we're toggling it off.

        Review the hidden form inputs to see more about how this works.
        """

        if type(toggle_value) != list:
            try:
                del self.survivor[toggle_key]
                self.logger.debug("%s toggled off '%s' for survivor '%s' (%s)." % (self.User.user["login"], toggle_key, self.survivor["name"], self.survivor["_id"]))
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
            }
            if mdb.the_dead.find_one({"survivor_id": self.survivor["_id"]}) is None:
                mdb.the_dead.insert(death_dict)
                self.logger.debug("Survivor '%s' added to the The Dead." % self.survivor["name"])
                self.Settlement.settlement["population"] = int(self.Settlement.settlement["population"]) - 1
                self.logger.debug("Settlement '%s' population automatically decreased by 1." % self.Settlement.settlement["name"])
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

        if mastery_string in self.survivor["abilities_and_impairments"]:
            self.Settlement.settlement["innovations"].append(mastery_string)
            mdb.settlements.save(self.Settlement.settlement)
            self.logger.debug("Survivor '%s' added '%s' to settlement %s's Innovations!" % (self.survivor["name"], mastery_string, self.Settlement.settlement["name"]))

    def modify(self, params):
        """ Reads through a cgi.FieldStorage() (i.e. 'params') and modifies the
        survivor. """

        self.Settlement.update_mins()

        for p in params:

            if type(params[p]) != list:
                game_asset_key = params[p].value.strip()

            if p in ["asset_id", "heal_survivor", "form_id", "modify"]:
                pass
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
            elif p == "email":
                self.survivor["email"] = game_asset_key.lower()
            elif p == "cause_of_death":
                self.survivor[p] = game_asset_key
                mdb.survivors.save(self.survivor)
                admin.valkyrie()
            elif game_asset_key == "None":
                del self.survivor[p]
            elif p == "Weapon Proficiency":
                self.modify_weapon_proficiency(int(game_asset_key))
            elif p == "customize_ability" and "custom_ability_description" in params:
                self.add_ability_customization(params[p].value, params["custom_ability_description"].value)
            elif p == "custom_ability_description":
                pass
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
                link_text += " [%s]" % self.survivor["sex"]
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

            survivor_id = self.survivor["_id"],
            name = self.survivor["name"],
            add_epithets = Epithets.render_as_html_dropdown(exclude=self.survivor["epithets"]),
            rm_epithets =self.get_epithets("html_remove"),
            epithets = self.get_epithets("html_formatted"),
            sex = self.survivor["sex"],
            survival = survivor_survival_points,
            survival_limit = self.Settlement.get_attribute("survival_limit"),
            cannot_spend_survival_checked = flags["cannot_spend_survival"],
            hunt_xp = self.survivor["hunt_xp"],
            dead_checked = flags["dead"],
            favorite_checked = flags["favorite"],
            retired_checked = flags["retired"],
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
            "storage": ["Cloth", "Cloth", "Cloth", "Cloth", "Founding Stone", "Founding Stone", "Founding Stone", "Founding Stone"],
            "defeated_monsters": [],
            "population": 0,
            "lost_settlements": 0,
            "timeline": [
                {"year": 1, "story_event": "Returning Survivors", "custom": [], },
                {"year": 2, "story_event": "Endless Screams", "custom": [], },
                {"year": 3, "custom": [], },
                {"year": 4, "nemesis_encounter": "Nemesis Encounter: Butcher", "custom": [], },
                {"year": 5, "custom": [], "story_event": "Hands of Heat", },
                {"year": 6, "custom": [], "story_event": "Armored Strangers", },
                {"year": 7, "custom": [], "story_event": "Phoenix Feather", },
                {"year": 8, "custom": [], },
                {"year": 9, "custom": [], "nemesis_encounter": "Nemesis Encounter: King's Man", },
                {"year": 10, "custom": [], },
                {"year": 11, "custom": [], "story_event": "Regal Visit", },
                {"year": 12, "custom": [], "story_event": "Principle: Conviction (p. 141)", },
                {"year": 13, "custom": [], },
                {"year": 14, "custom": [], },
                {"year": 15, "custom": [], },
                {"year": 16, "custom": [], "nemesis_encounter": "Nemesis Encounter", },
                {"year": 17, "custom": [], },
                {"year": 18, "custom": [], },
                {"year": 19, "custom": [], "nemesis_encounter": "Nemesis Encounter"},
                {"year": 20, "custom": [], "story_event": "Watched", },
                {"year": 21, "custom": [], },
                {"year": 22, "custom": [], },
                {"year": 23, "custom": [], "nemesis_encounter": "Nemesis Encounter: Level 3"},
                {"year": 24, "custom": [], },
                {"year": 25, "custom": [], },
                {"year": 26, "custom": [], "nemesis_encounter": "Nemesis Encounter: Watcher"},
                {"year": 27, "custom": [], },
                {"year": 28, "custom": [], },
                {"year": 29, "custom": [], },
                {"year": 30, "custom": [], },
                {"year": 31, "custom": [], },
                {"year": 32, "custom": [], },
                {"year": 33, "custom": [], },
                {"year": 34, "custom": [], },
                {"year": 35, "custom": [], },
                {"year": 36, "custom": [], },
                {"year": 37, "custom": [], },
                {"year": 38, "custom": [], },
                {"year": 39, "custom": [], },
                {"year": 40, "custom": [], },
            ],
        }
        settlement_id = mdb.settlements.insert(new_settlement_dict)
        self.logger.info("New settlement '%s' ('%s') created by %s!" % (name, settlement_id, self.User.user["login"]))
        return settlement_id


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
            self.settlement[a] = list(set([i for i in self.settlement[a] if type(i) in (str, unicode)]))

        for innovation_key in self.settlement["innovations"]:
            if innovation_key in Innovations.get_keys():
                innovation_dict = Innovations.get_asset(innovation_key)
                if "type" in innovation_dict.keys() and innovation_dict["type"] == "principle":
                    self.settlement["innovations"].remove(innovation_key)
                    self.logger.debug("Automatically removed principle '%s' from settlement '%s' (%s) innovations." % (innovation_key, self.settlement["name"], self.settlement["_id"]))


    def get_ancestors(self, return_type=None, survivor_id=False):
        """ This is the settlement's version of this method and it is way
        different from the survivor """

        if survivor_id:
            return "NOT IMPLEMENTED YET"

        if return_type == "html_parent_select":
            male_parent = False
            female_parent = False
            for s in self.get_survivors():
                if s["sex"] == "M" and "dead" not in s.keys():
                    male_parent = True
                elif s["sex"] == "F" and "dead" not in s.keys():
                    female_parent = True

        if not (male_parent and female_parent):
            return ""
        else:
            output = html.survivor.add_ancestor_top
            for role in [("father", "M"), ("mother", "F")]:
                output += html.survivor.add_ancestor_select_top.safe_substitute(parent_role=role[0], pretty_role=role[0].capitalize())
                for s in self.get_survivors():
                    if s["sex"] == role[1] and "dead" not in s.keys():
                        output += html.survivor.add_ancestor_select_row.safe_substitute(parent_id=s["_id"], parent_name=s["name"])
                output += html.survivor.add_ancestor_select_bot
            output += html.survivor.add_ancestor_bot
            return output



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
        storage = [i.title() for i in sorted(self.settlement["storage"])]
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

                        # check preferences and include a pop-up
                        confirmation_pop_up = ""
                        if "preferences" in self.User.user.keys() and "confirm_on_remove_from_storage" in self.User.user["preferences"].keys():
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
                for level in ["Lvl 1", "Lvl 2", "Lvl 3"]:
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


    def get_timeline(self, return_as=False):
        """ Returns the settlement's timeline. """

        book_icon_url = os.path.join(settings.get("application","STATIC_URL"), "icons/trigger_story_event.png")
        book_icon = '<img class="icon" src="%s"/>' % book_icon_url
        nemesis_icon_url = os.path.join(settings.get("application", "STATIC_URL"), "icons/nemesis_encounter_event.jpg")
        nemesis_icon = '<img class="icon" src="%s"/>' % nemesis_icon_url

        current_lantern_year = int(self.settlement["lantern_year"])

        if return_as == "html":
            html = ""
            for year in range(1,41):
                strikethrough = ""
                disabled = ""
                if year <= current_lantern_year - 1:
                    disabled = "disabled"
                    strikethrough = "strikethrough"
                html += '<p class="%s">' % strikethrough
                html += '<button id="remove_item" name="increment_lantern_year" class="%s" value="1" %s> &nbsp; %s &nbsp; </button>' % (strikethrough, disabled, year)
                target_year = {"year": year}
                for year_dict in self.settlement["timeline"]:
                    if year == year_dict["year"]:
                        target_year = year_dict
                if "story_event" in target_year:
                    html += ' %s %s' % (book_icon, target_year["story_event"])
                if "nemesis_encounter" in target_year:
                    html += ' %s %s' % (nemesis_icon, target_year["nemesis_encounter"])
                if "custom" in target_year and target_year["custom"] != []:
                    for custom_event in target_year["custom"]:
                        html += ' %s %s ' % (book_icon, custom_event)
                html += ' <input onchange="this.form.submit()" type="text" name="update_timeline_year_%s" placeholder="add event"/> </p><hr/>\n' % year
            return html

        return "oops! not implemented yet"

    def get_principles(self, return_type=None):
        """ Returns the settlement's principles. Use the 'return_type' arg to
        specify one of the following, or leave it unspecified to get a sorted
        list back:

            'comma-delimited': a comma-delimited list wrapped in <p> tags.

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

        return principles


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

        if return_type == "html":
            output = ""
            for k in buffs.keys():
                output += '<p><b>%s:</b> %s</p>\n' % (k, buffs[k])
            return output

        return buffs

    def get_defeated_monsters(self, return_type=None):
        """ Returns a sorted self.settlement["defeated_monsters"], unless the
        'return_type' kwarg is comma-delimited, in which case you get a pretty,
        sorted, stacked comma-delimited string. """

        monsters = sorted(self.settlement["defeated_monsters"])

        if return_type == "comma-delimited":
            if monsters == []:
                return ""

            monster_count_dict = {}
            for monster in monsters:
                if not monster in monster_count_dict.keys():
                     monster_count_dict[monster] = 1
                else:
                     monster_count_dict[monster] += 1

            stacked_list = []
            for m in sorted(monster_count_dict.keys()):
                if monster_count_dict[m] == 1:
                    stacked_list.append(m)
                else:
                    stacked_list.append("%s (x%s)" % (m, monster_count_dict[m]))
            return "<p>%s</p>" % ", ".join(stacked_list)

        return monsters


    def get_quarries(self, return_type=None):
        """ Returns a list of the settlement's quarries. Leave the 'return_type'
        arg unspecified to get a sorted list. """
        quarries = sorted(self.settlement["quarries"])

        if return_type == "comma-delimited":
            return ", ".join(quarries)

        return quarries


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

            for survivor in survivors:
                S = assets.Survivor(survivor_id=survivor["_id"], session_object=self.Session)
                annotation = ""
                user_owns_survivor = False
                disabled = "disabled"

                if survivor["email"] == user_login or current_user_is_settlement_creator:
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

                survivor_html = html.survivor.campaign_asset.safe_substitute(
                    survivor_id = s_id,
                    settlement_id = self.settlement["_id"],
                    hunting_party_checked = in_hunting_party,
                    settlement_name = self.settlement["name"],
                    b_class = button_class,
                    able_to_hunt = can_hunt,
                    special_annotation = annotation,
                    disabled = disabled,
                    name = S.survivor["name"],
                    sex = S.survivor["sex"],
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
                    groups[3]["survivors"].append(survivor_html)

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

        return survivors


    def return_hunting_party(self):
        """ Gets the hunting party, runs heal("Return from Hunt") on them."""
        healed_survivors = 0
        returning_survivor_id_list = []
        for survivor in self.get_survivors("hunting_party"):
            S = assets.Survivor(survivor_id=survivor["_id"], session_object=self.Session)
            returning_survivor_id_list.append(S.survivor["_id"])
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
        return sorted(list([i.title() for i in return_list]))


    def get_attribute(self, attrib=None):
        """ Returns the settlement attribute associated with 'attrib'. Using this
        is preferable to going straight to self.settlement[attrib] because we do
        business logic on these returns. """

        if attrib == "survival_limit":
            srv_lmt_min = self.get_min("survival_limit")
            if self.settlement["survival_limit"] < srv_lmt_min:
                return srv_lmt_min

        return self.settlement[attrib]


    def get_min(self, value=None):
        """ Returns the settlement's minimum necessary values for the following:

            'population': the minimum number of survivors based on which have
                'dead' in their Survivor.survivor.keys().
            'deaths': the minimum number of dead survivors.
                -> 'death_count' also does this.
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


    def get_players(self, count_only=False):
        player_set = set()
        survivors = mdb.survivors.find({"settlement": self.settlement["_id"]})
        for s in survivors:
            player_set.add(s["email"])

        if count_only:
            return len(player_set)

        return player_set

    def update_principles(self, add_new_principle=False):
        """ Since certain principles are mutually exclusive, all of the biz
        logic for toggling one on and toggling off its opposite is here. """

        principles = set(self.settlement["principles"])
        if add_new_principle:
            principles.add(add_new_principle)
            self.logger.debug("%s added principle '%s' to settlement '%s' (%s)." % (self.User.user["login"], add_new_principle, self.settlement["name"], self.settlement["_id"]))

        mutually_exclusive_principles = [
            ("Graves", "Cannibalize"),
            ("Romantic", "Barbaric"),
            ("Protect the Young", "Survival of the Fittest"),
            ("Collective Toil", "Accept Darkness"),
            ]


        for tup in mutually_exclusive_principles:
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
        if return_type == "comma-delimited":
            if hasattr(Asset, "uniquify"):
                asset_keys = list(set(asset_keys))
            if hasattr(Asset, "sort_alpha"):
                asset_keys = sorted(asset_keys)
            output = ", ".join(asset_keys)
            return "<p>%s</p>" % output
        elif return_type == "html_add":
            op = "add"
            output = html.ui.game_asset_select_top.safe_substitute(
                operation="%s_" % op, operation_pretty=op.capitalize(),
                name=asset_name,
                name_pretty=asset_name.capitalize(),
            )

            for asset_key in self.get_game_asset_deck(asset_type):
                output += html.ui.game_asset_select_row.safe_substitute(asset=asset_key)
            output += html.ui.game_asset_select_bot
            output += html.ui.game_asset_add_custom.safe_substitute(asset_name=asset_name)
            return output
        elif return_type == "html_remove":
            if asset_keys == []:
                return ""
            op = "remove"
            output = html.ui.game_asset_select_top.safe_substitute(
                operation="%s_" % op, operation_pretty=op.capitalize(),
                name=asset_name,
                name_pretty=asset_name.capitalize(),
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


    def get_defeated_monsters_deck(self, return_type=False):
        """ Returns a list of the settlement's possible kills, based on the
        'quarries' and the keys of 'nemesis_monsters'. """

        possible_quarries = self.settlement["quarries"]

        deck = ["White Lion (First Story)"]
        for m in possible_quarries:
            for lv in range(1,4):
                deck.append("%s Lvl %s" % (m, lv))
        for n in self.settlement["nemesis_monsters"].keys():
            try:
                deck.append("%s %s" % (n, self.settlement["nemesis_monsters"][n][-1]))
            except IndexError:
                deck.append("%s Lvl 1" % n)

        if return_type == "html_add":
            output = html.ui.game_asset_select_top.safe_substitute(operation="add_", name="defeated_monster", operation_pretty="Add", name_pretty="Monster")
            for m in deck:
                output += html.ui.game_asset_select_row.safe_substitute(asset=m)
            output += html.ui.game_asset_select_bot
            return output

        return deck


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
        mdb.settlements.save(self.settlement)


    def add_game_asset(self, asset_class, game_asset_key=None):
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
            game_asset_key = game_asset_key.title()
            self.settlement[asset_class].append(game_asset_key)
            self.logger.info("'%s' appended '%s' to settlement '%s' (%s) storage." % (self.User.user["login"], game_asset_key, self.settlement["name"], self.settlement["_id"]))
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

            if p in ["asset_id", "modify"]:
                pass
            elif p == "add_defeated_monster":
                self.add_kill(game_asset_key)
            elif p == "add_quarry":
                self.settlement["quarries"].append(params[p].value)
            elif p == "add_nemesis":
                self.settlement["nemesis_monsters"][params[p].value] = []
            elif p == "increment_nemesis":
                self.increment_nemesis(game_asset_key)
            elif p == "add_item" and not "remove_item" in params:
                self.add_game_asset("storage", game_asset_key)
            elif p == "remove_item" and not "add_item" in params:
                self.settlement["storage"].remove(game_asset_key)
                self.logger.debug("Removing %s from settlement %s storage" % (game_asset_key, self.settlement["_id"]))
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
            elif p == "increment_lantern_year":
                self.settlement["lantern_year"] = int(self.settlement["lantern_year"]) + 1
            elif p.split("_")[:3] == ['update', 'timeline', 'year']:
                for year_dict in self.settlement["timeline"]:
                    if int(year_dict["year"]) == int(p.split("_")[-1]):
                        year_index = self.settlement["timeline"].index(year_dict)
                        self.settlement["timeline"].remove(year_dict)
                        year_dict["custom"].append(params[p].value)
                        self.settlement["timeline"].insert(year_index, year_dict)
                        break
            elif p == "hunting_party_operation":
                self.modify_hunting_party(params)
                break
            else:
                self.settlement[p] = game_asset_key
                self.logger.debug("%s set '%s' = '%s' for settlement '%s' (%s)." % (self.User.user["login"], p, game_asset_key, self.settlement["name"], self.settlement["_id"]))  # this is crazy noisy; only uncomment for serious CLI debugging

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


    def render_html_summary(self, user_id=False):
        """ This is the summary view we print at the top of the game view. It's
        not a form. """

        output = html.settlement.summary.safe_substitute(
            settlement_name=self.settlement["name"],
            principles = self.get_principles("comma-delimited"),
            population = self.settlement["population"],
            death_count = self.settlement["death_count"],
            sex_count = self.get_survivors(return_type="sex_count", exclude_dead=True),
            survivors = self.get_survivors(return_type="html_campaign_summary", user_id=user_id),
            survival_limit = self.settlement["survival_limit"],
            innovations = self.get_game_asset("innovations", return_type="comma-delimited", exclude=self.settlement["principles"]),
            locations = self.get_locations(return_type="comma-delimited"),
            departure_bonuses = self.get_bonuses('departure_buff', return_type="html"),
            settlement_bonuses = self.get_bonuses('settlement_buff', return_type="html"),
            survivor_bonuses = self.get_bonuses('survivor_buff', return_type="html"),
            defeated_monsters = self.get_defeated_monsters("comma-delimited"),
            quarries = self.get_quarries("comma-delimited"),
            nemesis_monsters = self.get_nemeses("comma-delimited"),
        )
        return output


    def render_html_form(self):
        """ This is the all-singing, all-dancing form creating function. Pretty
        much all of the UI/UX happens here. """

        self.update_mins()

        hide_new_life_principle = "hidden"
        first_child = ""
        if "First child is born" in self.settlement["milestone_story_events"]:
            hide_new_life_principle = ""
            first_child = "checked"

        hide_death_principle = "hidden"
        first_death = ""
        if "First time death count is updated" in self.settlement["milestone_story_events"]:
            hide_death_principle = ""
            first_death = "checked"
        if int(self.settlement["death_count"]) > 0:
            hide_death_principle = ""

        hide_society_principle = "hidden"
        pop_15 = ""
        if "Population reaches 15" in self.settlement["milestone_story_events"]:
            hide_society_principle = ""
            pop_15 = "checked"
        if int(self.settlement["population"]) > 14:
            hide_society_principle = ""

        hide_conviction_principle = "hidden"
        if int(self.settlement["lantern_year"]) >= 12:
            hide_conviction_principle = ""

        cannibalize = ""
        if "Cannibalize" in self.settlement["principles"]:
            cannibalize = "checked"
        graves = ""
        if "Graves" in self.settlement["principles"]:
            graves = "checked"

        protect_the_young = ""
        if "Protect the Young" in self.settlement["principles"]:
            protect_the_young = "checked"
        survival_of_the_fittest = ""
        if "Survival of the Fittest" in self.settlement["principles"]:
            survival_of_the_fittest = "checked"

        collective_toil = ""
        if "Collective Toil" in self.settlement["principles"]:
            collective_toil = "checked"
        accept_darkness = ""
        if "Accept Darkness" in self.settlement["principles"]:
            accept_darkness = "checked"

        barbaric = ""
        if "Barbaric" in self.settlement["principles"]:
            barbaric = "checked"
        romantic = ""
        if "Romantic" in self.settlement["principles"]:
            romantic = "checked"

        five_innovations = ""
        if "Settlement has 5 innovations" in self.settlement["milestone_story_events"]:
            five_innovations = "checked"
        game_over = ""
        if "Population reaches 0" in self.settlement["milestone_story_events"]:
            game_over = "checked"

        survival_limit = int(self.settlement["survival_limit"])
        if survival_limit < self.get_min("survival_limit"):
            survival_limit = self.get_min("survival_limit")

        deaths = int(self.settlement["death_count"])
        if deaths < self.get_min("deaths"):
            deaths = self.get_min("deaths")

        population = int(self.settlement["population"])
        if population < self.get_min("population"):
            population = self.get_min("population")

        return html.settlement.form.safe_substitute(
            MEDIA_URL = settings.get("application","STATIC_URL"),
            settlement_id = self.settlement["_id"],
            game_link = self.asset_link(context="asset_management"),

            population = population,
            name = self.settlement["name"],
            survival_limit = survival_limit,
            min_survival_limit = self.get_min("survival_limit"),
            death_count = deaths,
            lost_settlements = self.settlement["lost_settlements"],

            survivors = self.get_survivors(return_type="html_campaign_summary"),

            departure_bonuses = self.get_bonuses('departure_buff', return_type="html"),
            settlement_bonuses = self.get_bonuses('settlement_buff', return_type="html"),

            items_options = Items.render_as_html_dropdown_with_divisions(recently_added=self.get_recently_added_items()),
            storage = self.get_storage("html_buttons"),

            new_life_principle_hidden = hide_new_life_principle,
            society_principle_hidden = hide_society_principle,
            death_principle_hidden = hide_death_principle,
            conviction_principle_hidden = hide_conviction_principle,

            cannibalize_checked = cannibalize,
            graves_checked = graves,
            protect_the_young_checked = protect_the_young,
            survival_of_the_fittest_checked = survival_of_the_fittest,
            collective_toil_checked = collective_toil,
            accept_darkness_checked = accept_darkness,
            barbaric_checked = barbaric,
            romantic_checked = romantic,
            principles_rm = self.get_principles("html_select_remove"),

            lantern_year = self.settlement["lantern_year"],
            timeline = self.get_timeline(return_as="html"),

            first_child_checked = first_child,
            first_death_checked = first_death,
            pop_15_checked = pop_15,
            five_innovations_checked = five_innovations,
            game_over_checked = game_over,

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

            defeated_monsters = self.get_defeated_monsters("comma-delimited"),
            defeated_monsters_add = self.get_defeated_monsters_deck(return_type="html_add"),

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
            link_text = html.dashboard.campaign_flash + "<b>%s</b><br/>LY %s. Survivors: %s Players: %s" % (self.settlement["name"], self.settlement["lantern_year"], self.settlement["population"], len(self.get_players()))
            desktop_text = ""
            asset_type = "campaign"
        else:
            button_class = "gradient_yellow"
            link_text = html.dashboard.settlement_flash + "<b>%s</b>" % self.settlement["name"]
            desktop_text = ""
            asset_type = "settlement"

        return html.dashboard.view_asset_button.safe_substitute(
            button_class = button_class,
            asset_type = asset_type,
            asset_id = self.settlement["_id"],
            asset_name = link_text,
            desktop_text = desktop_text,
        )






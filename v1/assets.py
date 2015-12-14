#!/usr/bin/env python

from bson.objectid import ObjectId
from copy import copy
from datetime import datetime
import os
from string import Template

import admin
import assets
import game_assets
import html
from models import Abilities, Disorders, Epithets, FightingArts, Locations, Items, Innovations, Resources, Quarries
from utils import mdb, get_logger, load_settings, get_user_agent

settings = load_settings()

class User:

    def __init__(self, user_id):
        """ Initialize with a user's _id to create an object with his compelte
        user object and all settlements. """

        self.logger = get_logger()

        user_id = ObjectId(user_id)
        self.user = mdb.users.find_one({"_id": user_id})
        self.get_settlements()
        self.get_survivors()

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
                S = assets.Settlement(settlement_id=settlement["_id"])
                output += S.asset_link()
            return output

        return self.settlements

    def get_survivors(self, return_type=False):
        """ Returns all of the survivors that a user can access. Leave
        the 'return_as' kwarg unspecified/False if you want a mongo cursor
        back (instead of fruity HTML crap). """

        self.survivors = list(mdb.survivors.find({"$or": [
            {"email": self.user["login"]},
            {"created_by": self.user["_id"]},
            ]}
        ).sort("name"))

        # user version

        if return_type == "asset_links":
            output = ""
            for s in self.survivors:
                S = Survivor(survivor_id=s["_id"])
                output += S.asset_link()
            return output

        return self.survivors

    def get_games(self):
        self.get_settlements()
        game_list = set()

        if self.settlements is not None:
            for s in self.settlements:
                if s is not None:
                    game_list.add(s["_id"])

        for s in self.survivors:
            game_list.add(s["settlement"])

        output = ""
        for settlement_id in game_list:
            S = assets.Settlement(settlement_id=settlement_id)
            if S.settlement is not None:
                output += S.asset_link(view="game")
        return output

    def html_motd(self):
        """ Creates an HTML MoTD for the user. """

        d = admin.get_latest_casualty()
        if d is None:
            d = {"name": None, "settlement_name": None, "sex": None, "hunt_xp": None, "Courage": None, "Understanding": None}

        COD = "Unspecified cause of death."
        if "cause_of_death" in d.keys():
            COD = d["cause_of_death"]

        output = html.dashboard.motd.safe_substitute(
            login = self.user["login"],
            version = settings.get("application", "version"),
            users = mdb.users.find().count(),
            dead_survivors = mdb.survivors.find({"dead": {"$exists": True}}).count(),
            live_survivors = mdb.survivors.find().count() - mdb.survivors.find({"dead": {"$exists": True}}).count(),
            sessions = mdb.sessions.find().count(),
            settlements = mdb.settlements.find().count(),
            casualty_name = d["name"],
            casualty_sex = d["sex"],
            casualty_settlement = d["settlement_name"],
            casualty_xp = d["hunt_xp"],
            casualty_courage = d["Courage"],
            casualty_understanding = d["Understanding"],
            cause_of_death = COD,
        )
        return output


#
#   SURVIVOR CLASS
#

class Survivor:

    def __init__(self, survivor_id=False, params=False):
        """ Initialize this with a cgi.FieldStorage() as the 'params' kwarg
        to create a new survivor. Otherwise, use a mdb survivor _id value
        to initalize with survivor data from mongo. """

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
        ]
        self.flags = self.damage_locations + self.flag_attribs

        if not survivor_id:
            survivor_id = self.new(params)

        self.survivor = mdb.survivors.find_one({"_id": ObjectId(survivor_id)})
        if not self.survivor:
            raise Exception("Invalid survivor ID: '%s'" % survivor_id)
        self.Settlement = Settlement(settlement_id=self.survivor["settlement"])


    def new(self, params):
        """ Create a new survivor from cgi.FieldStorage() params. """

        created_by = ObjectId(params["created_by"].value)
        settlement_id = ObjectId(params["settlement_id"].value)
        survivor_name = params["name"].value
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
        }

        user = mdb.users.find_one({"_id": created_by})
        login = user["login"]

        survivor_id = mdb.survivors.insert(survivor_dict)
        self.logger.info("User '%s' created new survivor '%s [%s]' successfully." % (login, survivor_name, survivor_sex))
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


    def get_abilities_and_impairments(self, return_type=False):
        all_list = sorted(self.survivor["abilities_and_impairments"])

        if return_type == "comma-delimited":
            return ", ".join(all_list)

        if return_type == "html_select_remove":
            if all_list == []:
                return ""

            output = '<select name="remove_ability" onchange="this.form.submit()">'
            output += '<option selected disabled hidden value="">Remove Ability</option>'
            for ability in all_list:
                output += '<option>%s</option>' % ability
            output += '</select>'
            return output

        if return_type == "html_formatted":
            pretty_list = []
            for ability in all_list:
                if ability in Abilities.get_keys():
                    desc = Abilities.get_asset(ability)["desc"]
                    pretty_list.append("<p><b>%s:</b> %s</p>" % (ability, desc))
                else:
                    pretty_list.append(ability)
            return "\n".join(pretty_list)

        return all_list


    def get_fighting_arts(self, return_as=False, strikethrough=False):
        fighting_arts = self.survivor["fighting_arts"]

        if return_as == "formatted_html":
            html = ""
            for fa_key in fighting_arts:
                html += '<p><b>%s:</b> %s</p>\n' % (fa_key, FightingArts.get_asset(fa_key)["desc"])
                if strikethrough:
                    html = "<del>%s</del>\n" % html
            return html

        if return_as == "html_select_remove":
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

        if increment_hunt_xp:
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

        asset_key = asset_key.strip()

        if asset_type == "disorder":
            self.survivor["disorders"] = list(set([d for d in self.survivor["disorders"]])) # uniquify
            if len(self.survivor["disorders"]) >= 3:
                return False

            if asset_key not in Disorders.get_keys():
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
        elif asset_type == "abilities_and_impairments":
            if asset_key not in Abilities.get_keys():
                self.survivor["abilities_and_impairments"].append("%s" % asset_key)
                return True
            elif asset_key in Abilities.get_keys():
                asset_dict = Abilities.get_asset(asset_key)
                below_max = True
                if "max" in asset_dict.keys() and asset_key in self.survivor["abilities_and_impairments"]:
                    asset_count = self.survivor["abilities_and_impairments"].count(asset_key)
                    if asset_dict["max"] == asset_count:
                        self.logger.warn("Survivor '%s' has '%s' x%s. Max is %s." % (self.survivor["name"], asset_key, asset_count, asset_dict["max"]))
                        below_max = False
                if below_max:
                    self.survivor["abilities_and_impairments"].append(asset_key)
                    if "cannot_spend_survival" in asset_dict.keys():
                        self.survivor["cannot_spend_survival"] = "checked"
                    for attrib in game_assets.survivor_attributes:
                        if attrib in asset_dict and attrib in self.survivor.keys():
                            old_value = int(self.survivor[attrib])
                            new_value = old_value + asset_dict[attrib]
                            self.survivor[attrib] = new_value
                mdb.survivors.save(self.survivor)
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
            except:
                pass
        else:
            self.survivor[toggle_key] = "checked"
            if toggle_key == "dead":
                self.survivor["died_on"] = datetime.now()
                self.survivor["died_in"] = self.Settlement.settlement["lantern_year"]
            if toggle_key == "retired":
                self.survivor["retired_in"] = self.Settlement.settlement["lantern_year"]

        mdb.survivors.save(self.survivor)


    def modify(self, params):
        """ Reads through a cgi.FieldStorage() (i.e. 'params') and modifies the
        survivor. """


        for p in params:

            if type(params[p]) != list:
                game_asset_key = params[p].value.strip()

            if p in ["asset_id", "heal_survivor"]:
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
                self.survivor["fighting_arts"].append(params[p].value.strip())
            elif p == "remove_fighting_art":
                self.survivor["fighting_arts"].remove(params[p].value)
            elif p.split("_")[0] == "toggle":
                toggle_attrib = "_".join(p.split("_")[1:])
                self.toggle(toggle_attrib, params[p])
            elif p == "email":
                self.survivor["email"] = game_asset_key.lower()
            elif game_asset_key == "None":
                del self.survivor[p]
            else:
                self.survivor[p] = game_asset_key

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
        )

        return output


    def render_html_form(self):
        """ This is just like the render_html_form() method of the settlement
        class: a giant tangle-fuck of UI/UX logic that creates the form for
        modifying a surviro. """

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

        stalwart = ""
        prepared = ""
        matchmaker = ""
        if "courage_attribute" in self.survivor.keys():
            if self.survivor["courage_attribute"] == "Stalwart":
                stalwart = "checked"
            elif self.survivor["courage_attribute"] == "Prepared":
                prepared = "checked"
            elif self.survivor["courage_attribute"] == "Matchmaker":
                matchmaker = "checked"

        analyze = ""
        explore = ""
        tinker = ""
        if "understanding_attribute" in self.survivor.keys():
            if self.survivor["understanding_attribute"] == "Analyze":
                analyze = "checked"
            elif self.survivor["understanding_attribute"] == "Explore":
                explore = "checked"
            elif self.survivor["understanding_attribute"] == "Tinker":
                tinker = "checked"

        COD_div_display_style = "none"
        if "cause_of_death" in self.survivor.keys() and "dead" in self.survivor.keys():
            COD_div_display_style = "block"
        COD = ""
        if "cause_of_death" in self.survivor.keys():
            COD = self.survivor["cause_of_death"]

        # fighting arts widgets
        fighting_arts_picker = FightingArts.render_as_html_dropdown(exclude=self.survivor["fighting_arts"])
        if len(self.survivor["fighting_arts"]) >= 3:
            fighting_arts_picker = ""
        fighting_arts_remover = self.get_fighting_arts(return_as="html_select_remove")
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
            retired_checked = flags["retired"],
            survival_actions = self.get_survival_actions(return_as="html_checkboxes"),
            movement = self.survivor["Movement"],
            accuracy = self.survivor["Accuracy"],
            strength = self.survivor["Strength"],
            evasion = self.survivor["Evasion"],
            luck = self.survivor["Luck"],
            speed = self.survivor["Speed"],
            departure_buffs = self.Settlement.get_bonuses(bonus_type="departure_buff"),
            settlement_buffs = self.Settlement.get_bonuses(bonus_type="survivor_buff"),

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
            stalwart_checked = stalwart,
            prepared_checked = prepared,
            matchmaker_checked = matchmaker,
            understanding = self.survivor["Understanding"],
            analyze_checked = analyze,
            explore_checked = explore,
            tinker_checked = tinker,

            cannot_use_fighting_arts_checked = flags["cannot_use_fighting_arts"],
            fighting_arts = self.get_fighting_arts(return_as="formatted_html", strikethrough=flags["cannot_use_fighting_arts"]),
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
            campaign_link = self.Settlement.asset_link(view="game", fixed=True),
        )
        return output



#
#   SETTLEMENT CLASS
#

class Settlement:

    def __init__(self, settlement_id=False, name=False, created_by=False, user_object=None):
        """ Initialize with a settlement from mdb. """
        self.logger = get_logger()
        if not settlement_id:
            settlement_id = self.new(name, created_by)
        self.settlement = mdb.settlements.find_one({"_id": ObjectId(settlement_id)})
        self.survivors = mdb.survivors.find({"settlement": settlement_id})
        if self.settlement is not None:
            self.update_death_count()

        self.User = user_object

    def new(self, name=None, created_by=None):
        """ Creates a new settlement. 'name' is any string and 'created_by' has to
        be an ObjectId of a user. """
        new_settlement_dict = {
            "nemesis_monsters": {"Butcher": [], },
            "created_on": datetime.now(),
            "created_by": created_by,
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
                {"year": 12, "custom": [], "story_event": "Principle: Conviction", },
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
        creator = mdb.users.find_one({"_id": created_by})
        self.logger.info("New settlement '%s' ('%s') created by %s!" % (name, settlement_id, creator["login"]))
        return settlement_id


    def update_death_count(self):
        """ This runs whenever we initialize the settlement. It makes sure that
        our dead survivors are reflected in the death count. """

        min_death_count = 0
        for survivor in self.survivors:
            if "dead" in survivor.keys():
                min_death_count += 1

        if int(self.settlement["death_count"]) < min_death_count:
            self.settlement["death_count"] = min_death_count

        mdb.settlements.save(self.settlement)


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

        storage = sorted(self.settlement["storage"])


        if return_type == "html_buttons":
            resources = []
            gear = []
            other = []

            for item_key in storage:
                item_color = "D3AAAA"
                item_type = "other"

                if item_key in Items.get_keys():
                    item_asset_dict = Items.get_asset(item_key)
                    item_type = None
                    item_location = item_asset_dict["location"]
                    if item_location in Locations.get_keys():
                        item_type = "gear"
                        item_color = Locations.get_asset(item_location)["color"]
                    elif item_location in Resources.get_keys():
                        item_type = "resource"
                        item_color = Resources.get_asset(item_location)["color"]
                    else:
                        self.logger.warn("Item '%s' does not belong to a location or resource group!" % item_key)

                    # overwrite this default stuff if the item dict says so
                    if "type" in item_asset_dict:
                        item_type = item_asset_dict["type"]

                item_button_html = '\t<button id="remove_item" name="remove_item" value="%s" style="background-color: #%s; color: #000;"> %s</button>\n' % (item_key, item_color, item_key)
                if item_type == "gear":
                    gear.append(item_button_html)
                elif item_type == "resource":
                    resources.append(item_button_html)
                else:
                    other.append(item_button_html)

            output = ""
            for l in [gear, resources, other]:
                if l != []:
                    for item_html in l:
                        output += item_html
                    output += "\n<hr/>\n"

            return output

        if return_type == "drop_list":
            html = '<select name="remove_item" onchange="this.form.submit()">'
            html += '<option selected disabled hidden value="">Remove Item</option>'
            for item in storage:
                html += '<option value="%s">%s</option>' % (item, item)
            html += '</select>'
            return html

        if return_type == "comma-delimited":
            return ", ".join(storage)

        return storage


    def get_nemesis_monsters(self, return_type=None):
        """ Use the 'return_type' arg to specify a special return type, or leave
        unspecified to get sorted list of nemesis monsters back. """

        nemesis_monster_keys = sorted(self.settlement["nemesis_monsters"].keys())

        if return_type == "comma-delimited":
            return ", ".join(nemesis_monster_keys)

        if return_type == "html_select":
            html = ""
            for k in nemesis_monster_keys:
                html += '<p><b>%s</b> ' % k
                for level in ["Lvl 1", "Lvl 2", "Lvl 3"]:
                    if level not in self.settlement["nemesis_monsters"][k]:
                        html += ' <button id="increment_nemesis" name="increment_nemesis" value="%s">%s</button> ' % (k,level)
                    else:
                        html += ' <button id="increment_nemesis" class="disabled" disabled>%s</button> ' % level
                html += '</p>\n'
            return html

        return self.settlement["nemesis_monsters"].keys()


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


    def get_bonuses(self, bonus_type, return_as=False):
        """ Returns the buffs/bonuses that settlement gets. 'bonus_type' is
        required and can be 'departure_buff', 'settlement_buff' or
        'survivor_buff'.  """

        innovations = self.get_game_asset("innovations")
        innovations.append(self.settlement["principles"])

        buffs = {}

        for innovation_key in innovations:
            if innovation_key in Innovations.get_keys() and bonus_type in Innovations.get_asset(innovation_key).keys():
                buffs[innovation_key] = Innovations.get_asset(innovation_key)[bonus_type]

        html = ""
        for k in buffs.keys():
            html += '<p><b>%s:</b> %s</p>\n' % (k, buffs[k])
        return html

    def get_defeated_monsters(self, return_type=None):
        monsters = sorted(self.settlement["defeated_monsters"])

        if return_type == "comma-delimited":
            if monsters == []:
                return ""
            else:
                return ", ".join(monsters)

        return monsters

    def get_quarries(self, return_type=None):
        """ Returns a list of the settlement's quarries. Leave the 'return_type'
        arg unspecified to get a sorted list. """
        quarries = sorted(self.settlement["quarries"])

        if return_type == "comma-delimited":
            return ", ".join(quarries)

        return quarries

    def get_survivors(self, return_type=False, user_id=None):
        """ Returns the settlement's survivors. Leave 'return_typ' unspecified
        if you want a mongo cursor object back. """

        survivors = mdb.survivors.find({"settlement": self.settlement["_id"]}).sort("name")

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

        if return_type == "html_campaign_summary":

            groups = {
                1: {"name": "Hunting Party", "survivors": [], },
                2: {"name": "Available", "survivors": [], },
                3: {"name": "Skipping Next Hunt", "survivors": [], },
                4: {"name": "Retired", "survivors": [], },
                5: {"name": "The Dead", "survivors": [], },
            }

            for survivor in survivors:
                S = assets.Survivor(survivor_id=survivor["_id"])
                annotation = ""
                user_owns_survivor = False
                disabled = "disabled"

                if survivor["email"] == user_login or current_user_is_settlement_creator:
                    disabled = ""
                    user_owns_survivor = True

                button_class = ""
                if user_owns_survivor:
                    button_class = "green"
                if "dead" in S.survivor.keys():
                    if "died_in" in S.survivor.keys():
                        annotation = "&ensp; <i>Died in LY %s</i><br/>" % S.survivor["died_in"]
                    else:
                        annotation = "&ensp; <i>Dead</i><br/>"
                    button_class = "tan"

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
                    hunt_xp = S.survivor["hunt_xp"],
                    survival = S.survivor["survival"],
                    insanity = S.survivor["Insanity"],
                    courage = S.survivor["Courage"],
                    understanding = S.survivor["Understanding"],
                )

                # finally, file our newly minted survivor in a group:
                if "in_hunting_party" in S.survivor.keys():
                    groups[1]["survivors"].append(survivor_html)
                elif "skip_next_hunt" in S.survivor.keys():
                    groups[3]["survivors"].append(survivor_html)
                elif "retired" in S.survivor.keys():
                    groups[4]["survivors"].append(survivor_html)
                elif "dead" in S.survivor.keys():
                    groups[5]["survivors"].append(survivor_html)
                else:
                    groups[2]["survivors"].append(survivor_html)

            output = ""
            for g in sorted(groups.keys()):
                group = groups[g]
                output += "<h4>%s</h4>\n" % group["name"]
                for s in group["survivors"]:
                    output += "  %s\n" % s
                if group["name"] == "Hunting Party" and group["survivors"] == []:
                    output += "<p>Use [::] to add survivors to the hunting party.</p>"
                elif group["name"] == "Hunting Party" and group["survivors"] != [] and current_user_is_settlement_creator:
                    output += html.settlement.return_hunting_party.safe_substitute(settlement_id=self.settlement["_id"])
            return output

        return survivors


    def return_hunting_party(self):
        """ Gets the hunting party, runs heal("Return from Hunt") on them."""
        healed_survivors = 0
        for survivor in self.get_survivors("hunting_party"):
            S = assets.Survivor(survivor_id=survivor["_id"])
            S.heal("Return from Hunt")
            healed_survivors += 1


    def get_recently_added_items(self):
        """ Returns the three items most recently appended to storage. """
        max_items = 3
        all_items = copy(self.settlement["storage"])
        return_list = set()
        while len(return_list) < max_items:
            if all_items == []:
                break
            return_list.add(all_items.pop())
        return sorted(list(return_list))


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
            'survival_limit': the minimum survival limit, based on innovations.

        Returns an int. ALWAYS.
        """
        results = False
        settlement_id = ObjectId(self.settlement["_id"])

        if value == "population":
            results = mdb.survivors.find({"settlement": settlement_id, "dead": {"$exists": False}}).count()
        elif value == "deaths":
            results = mdb.survivors.find({"settlement": settlement_id, "dead": {"$exists": True}}).count()
        elif value == "survival_limit":
            min_survival = 0

            if self.settlement["name"] != "":
                min_survival +=1

            innovations = self.settlement["innovations"]
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
        principles = set(self.settlement["principles"])
        if add_new_principle:
            principles.add(add_new_principle)

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
        mdb.settlements.save(self.settlement)


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
            if asset_key in Asset.get_keys():
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
        exec "Asset = %s" % asset_type.capitalize() # if asset_type is 'innovations', initialize 'Innovations'
        asset_name = asset_type[:-1]                # if asset_type is 'locations', asset_name is 'location'
        asset_keys = self.settlement[asset_type]

        for asset_key in exclude:                   # process the exclude list
            while asset_key in asset_keys:
                asset_keys.remove(asset_key)

        for asset in asset_keys:
            if type(asset) != unicode:
                asset_keys.remove(asset)

        for asset_key in exclude:
            if asset_key in asset_keys:
                raise

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


    def add_game_asset(self, asset_class, game_asset_key=None):
        """ Generic function for adding game assets to a settlement.

        The 'asset_class' kwarg needs to be one of the game asset classes from
        models.py, e.g. Innovations, Locations, etc.

        This updates mdb and saves the update. Don't look for any semaphore on
        its returns (because there isn't any).
        """

        exec "Asset = %s" % asset_class.capitalize()

        if hasattr(Asset, "uniquify"):
            current_assets = set(self.settlement[asset_class])
            current_assets.add(game_asset_key)
            current_assets = list(current_assets)
        else:
            current_assets = self.settlement[asset_class]
            current_assets.append(game_asset_key)

        if hasattr(Asset, "sort_alpha"):
            current_assets = sorted(current_assets)

        self.settlement[asset_class] = current_assets
        mdb.settlements.save(self.settlement)


    def modify(self, params):
        """ Pulls a settlement from the mdb, updates it and saves it using a
        cgi.FieldStorage() object.

        All of the business logic lives here.
        """

        for p in params:

            game_asset_key = None
            if type(params[p]) != list:
                game_asset_key = params[p].value

            if p in ["asset_id", "modify"]:
                pass
            elif p == "add_defeated_monster":
                self.settlement["defeated_monsters"].append(params[p].value)
            elif p == "add_quarry":
                self.settlement["quarries"].append(params[p].value)
            elif p == "add_nemesis":
                self.settlement["nemesis_monsters"][params[p].value] = []
            elif p == "add_item":
                self.settlement["storage"].append(params[p].value)
            elif p == "remove_item":
                self.settlement["storage"].remove(params[p].value)
            elif p == "add_innovation":
                self.add_game_asset("innovations", game_asset_key)
            elif p == "remove_innovation":
                self.settlement["innovations"].remove(game_asset_key)
            elif p == "add_location":
                self.add_game_asset("locations", game_asset_key)
            elif p == "remove_location":
                self.settlement["locations"].remove(game_asset_key)
            elif p in ["new_life_principle", "death_principle", "society_principle", "conviction_principle"]:
                new_principle = params[p].value
                self.update_principles(new_principle)
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
            elif p == "increment_nemesis":
                nemesis_key = params[p].value
                completed_levels = self.settlement["nemesis_monsters"][nemesis_key]
                if completed_levels == []:
                    self.settlement["nemesis_monsters"][nemesis_key].append("Lvl 1")
                elif "Lvl 1" in completed_levels:
                    self.settlement["nemesis_monsters"][nemesis_key].append("Lvl 2")
                elif "Lvl 2" in completed_levels:
                    self.settlement["nemesis_monsters"][nemesis_key].append("Lvl 3")
            else:
                self.settlement[p] = params[p].value.strip()


        #   Turn lists into sets to prevent dupes; turn sets into lists to prevent
        #   mongo from FTFO if it sees a set(). File this under user-proofing
        for attrib in ["quarries", "innovations", "principles", "locations"]:
            self.settlement[attrib] = list(set(self.settlement[attrib]))

        mdb.settlements.save(self.settlement)


    def render_html_summary(self, user_id=False):
        """ This is the summary view we print at the top of the game view. It's
        not a form. """

        display_population = int(self.settlement["population"])
        if display_population < self.get_min(value="population"):
            display_population = self.get_min(value="population")

        display_death_count = int(self.settlement["death_count"])
        if display_death_count < self.get_min(value="death_count"):
            display_death_count = self.get_min(value="death_count")

        survivor_controls = self.get_survivors(return_type="html_campaign_summary", user_id=user_id)
        if self.get_survivors().count() == 0:
            survivor_controls = ""

        output = html.settlement.summary.safe_substitute(
            settlement_name=self.settlement["name"],
            principles = self.get_principles("comma-delimited"),
            population = display_population,
            death_count = display_death_count,
            survivors = survivor_controls,
            survival_limit = self.settlement["survival_limit"],
            innovations = self.get_game_asset("innovations", return_type="comma-delimited"),
            locations = self.get_locations(return_type="comma-delimited"),
            departure_bonuses = self.get_bonuses('departure_buff'),
            settlement_bonuses = self.get_bonuses('settlement_buff'),
            survivor_bonuses = self.get_bonuses('survivor_buff'),
            defeated_monsters = self.get_defeated_monsters("comma-delimited"),
            quarries = self.get_quarries("comma-delimited"),
            nemesis_monsters = self.get_nemesis_monsters("comma-delimited"),
        )
        return output


    def render_html_form(self):
        """ This is the all-singing, all-dancing form creating function. Pretty
        much all of the UI/UX happens here. """

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

        output = html.settlement.form.safe_substitute(
            MEDIA_URL = settings.get("application","STATIC_URL"),
            settlement_id = self.settlement["_id"],
            game_link = self.asset_link(view="game", fixed=True),

            population = population,
            name = self.settlement["name"],
            survival_limit = survival_limit,
            min_survival_limit = self.get_min("survival_limit"),
            death_count = deaths,
            lost_settlements = self.settlement["lost_settlements"],

            survivors = self.get_survivors(return_type="html_campaign_summary"),

            departure_bonuses = self.get_bonuses('departure_buff'),
            settlement_bonuses = self.get_bonuses('settlement_buff'),

            items_options = Items.render_as_html_dropdown_with_divisions(recently_added=self.get_recently_added_items()),
            items_remove = self.get_storage("drop_list"),
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

            lantern_year = self.settlement["lantern_year"],
            timeline = self.get_timeline(return_as="html"),

            first_child_checked = first_child,
            first_death_checked = first_death,
            pop_15_checked = pop_15,
            five_innovations_checked = five_innovations,
            game_over_checked = game_over,

            nemesis_monsters = self.get_nemesis_monsters("html_select"),

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

        )

        return output


    def asset_link(self, view="settlement", button_class="orange", link_text=False, fixed=False, use_flash=False):
        """ Returns an asset link (i.e. html form with button) for the
        settlement. """

        if use_flash:
            if use_flash == "settlement":
                link_text = html.dashboard.settlement_flash
                button_class = "orange"
            elif use_flash == "campaign":
                link_text = html.dashboard.campaign_flash
            else:
                link_text = None

        prefix = ""
        suffix = ""

        functional_pop = self.settlement["population"]
        if functional_pop < self.get_min("population"):
            functional_pop =  self.get_min("population")

        if view == "game":
            button_class = "purple"
            if not link_text and not fixed:
                prefix = html.dashboard.campaign_flash
                link_text = prefix + self.settlement["name"]
                suffix = " (LY %s, pop. %s)" % (self.settlement["lantern_year"], functional_pop)
                link_text += suffix
        elif not fixed:
            prefix = html.dashboard.settlement_flash
            link_text = prefix + self.settlement["name"]

        button_id = None
        if fixed:
            button_id = "floating_asset_button"
            if not link_text:
                link_text = html.dashboard.campaign_flash

        if not link_text:
            link_text = self.settlement["name"]

        output = html.dashboard.view_asset_button.safe_substitute(
            button_id = button_id,
            button_class = button_class,
            asset_type = view,
            asset_id = self.settlement["_id"],
            asset_name = link_text,
        )
        return output






#!/usr/bin/env python

from bson.objectid import ObjectId
from datetime import datetime
import os
from string import Template

import assets
import html
import models
from models import Epithets, Locations, Items, Innovations, Quarries
from utils import mdb, get_logger, load_settings

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

    def get_survivors(self, return_as=False):
        """ Returns all of the survivors that a user can access. Leave
        the 'return_as' kwarg unspecified/False if you want a mongo cursor
        back (instead of fruity HTML crap). """

        self.survivors = list(mdb.survivors.find({"$or": [
            {"email": self.user["login"]},
            {"created_by": self.user["_id"]},
            ]}
        ).sort("name"))

        # user version

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
            output += S.asset_link(view="game")
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
        self.settlement = Settlement(settlement_id=self.survivor["settlement"])


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


    def get_survival_actions(self, return_as=False):
        possible_actions = ["Dodge", "Encourage", "Surge", "Dash"]
        available_actions = []
        for a in possible_actions:
            if a in self.settlement.get_survival_actions():
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


    def get_abilities_and_impairments(self, return_as=False):
        all_list = self.survivor["abilities_and_impairments"]

        final_list = []
        for i in all_list:
            if i in models.abilities_and_impairments.keys():
                desc = models.abilities_and_impairments[i]["desc"]
                final_list.append("<b>%s:</b> %s" % (i, desc))
            else:
                final_list.append(i)

        if return_as == "html_select_remove":
            html = '<select name="remove_ability" onchange="this.form.submit()">'
            html += '<option selected disabled hidden value="">Remove Ability</option>'
            for ability in all_list:
                html += '<option>%s</option>' % ability
            html += '</select>'
            return html

        return "<br/>\n".join(final_list)


    def get_fighting_arts(self, return_as=False):
        fighting_arts = self.survivor["fighting_arts"]

        if return_as == "formatted_html":
            html = ""
            for fa_key in fighting_arts:
                html += '<b>%s:</b> %s<br />' % (fa_key, models.fighting_arts[fa_key]["desc"])
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
                html += '<b>%s:</b> %s<br />' % (disorder_key, models.disorders[disorder_key]["survivor_effect"])
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


    def heal(self, heal_armor=False, increment_hunt_xp=False):
        """ This removes the keys defined in self.damage_locations from the
        survivor's MDB object. It can also do some game logic, e.g. remove armor
        points and increment hunt XP.

            'heal_armor'        -> bool; use to zero out armor in addition to
                removing self.damage_location keys
            'increment_hunt_xp' -> int; increment hunt XP by whatever

        """

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

        self.logger.debug("Survivor '%s' healed!" % self.survivor["name"])
        mdb.survivors.save(self.survivor)


    def modify(self, params):
        """ Reads through a cgi.FieldStorage() (i.e. 'params') and modifies the
        survivor. """

        for p in params:
            if p == "asset_id":
                pass
            elif p == "heal_survivor":
                if params[p].value == "Heal Injuries Only":
                    self.heal()
                elif params[p].value == "Heal Injuries and Remove Armor":
                    self.heal(heal_armor=True)
                elif params[p].value == "Return from Hunt":
                    self.heal(heal_armor=True, increment_hunt_xp=1)
            elif p == "add_epithet":
                self.survivor["epithets"].append(params[p].value.strip())
                self.survivor["epithets"] = sorted(list(set(self.survivor["epithets"])))
            elif p == "remove_epithet":
                self.survivor["epithets"].remove(params[p].value)
            elif p == "add_ability":
                self.survivor["abilities_and_impairments"].append(params[p].value.strip())
                self.survivor["abilities_and_impairments"] = sorted(list(set(self.survivor["abilities_and_impairments"])))
            elif p == "remove_ability":
                self.survivor["abilities_and_impairments"].remove(params[p].value)
            elif p == "add_disorder" and len(self.survivor["disorders"]) < 3:
                self.survivor["disorders"].append(params[p].value.strip())
            elif p == "remove_disorder":
                self.survivor["disorders"].remove(params[p].value)
            elif p == "add_fighting_art" and len(self.survivor["fighting_arts"]) < 3:
                self.survivor["fighting_arts"].append(params[p].value.strip())
            elif p == "remove_fighting_art":
                self.survivor["fighting_arts"].remove(params[p].value)
            else:
                self.survivor[p] = params[p].value.strip()


        for flag in self.flag_attribs:
            if flag in params:
                self.survivor[flag] = "checked"
            elif flag not in params and flag in self.survivor.keys():
                del self.survivor[flag]
        for flag in self.damage_locations:
            if flag in params and not "heal_survivor" in params:
                self.survivor[flag] = "checked"
            elif flag not in params and flag in self.survivor.keys():
                del self.survivor[flag]

        # idiot-proof the hit boxes
        for hit_tuplet in [("arms_damage_light","arms_damage_heavy"), ("body_damage_light", "body_damage_heavy"), ("legs_damage_light", "legs_damage_heavy"), ("waist_damage_light", "waist_damage_heavy")]:
            light, heavy = hit_tuplet
            if heavy in self.survivor.keys() and not light in self.survivor.keys():
                self.survivor[light] = "checked"

        mdb.survivors.save(self.survivor)


    def asset_link(self, view="survivor", button_class="info", link_text=False, include=["hunt_xp", "insanity", "sex", "dead", "retired"], disabled=False):
        """ Returns an asset link (i.e. html form with button) for the
        survivor. """

        if not link_text:
            link_text = self.survivor["name"]
            if "sex" in include:
                link_text += " [%s]" % self.survivor["sex"]
        if disabled:
            link_text += "<br />%s" % self.survivor["email"]

        if include != []:
            attribs = []
            if "dead" in include:
                if "dead" in self.survivor.keys():
                    button_class = "warn"
                    attribs.append("Dead")

            if "retired" in include:
                if "retired" in self.survivor.keys():
                    button_class = "warn"
                    attribs.append("Retired")

            if "settlement_name" in include:
                attribs.append(self.settlement.settlement["name"])

            if "hunt_xp" in include:
                attribs.append("XP: %s" % self.survivor["hunt_xp"])

            if "insanity" in include:
                attribs.append("Insanity: %s" % self.survivor["Insanity"])

            if attribs != []:
                suffix = "<br /> ("
                suffix += ", ".join(attribs)
                suffix += ")"
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
        modifying a user. """

        survivor_survival_points = int(self.survivor["survival"])
        if survivor_survival_points > int(self.settlement.settlement["survival_limit"]):
            survivor_survival_points = int(self.settlement.settlement["survival_limit"])

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

        output = html.survivor.form.safe_substitute(
            MEDIA_URL = settings.get("application", "STATIC_URL"),

            survivor_id = self.survivor["_id"],
            name = self.survivor["name"],
            add_epithets = Epithets.render_as_html_dropdown(exclude=self.survivor["epithets"]),
            rm_epithets =self.get_epithets("html_remove"),
            epithets = self.get_epithets("html_formatted"),
            sex = self.survivor["sex"],
            survival = survivor_survival_points,
            survival_limit = int(self.settlement.settlement["survival_limit"]),
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
            departure_buffs = self.settlement.get_bonuses(bonus_type="departure_buff"),
            settlement_buffs = self.settlement.get_bonuses(bonus_type="survivor_buff"),

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

            fighting_arts = self.get_fighting_arts(return_as="formatted_html"),
            add_fighting_arts = models.render_fighting_arts_dict(return_as="html_select_add", exclude=self.survivor["fighting_arts"]),
            rm_fighting_arts = self.get_fighting_arts(return_as="html_select_remove"),

            disorders = self.get_disorders(return_as="formatted_html"),
            add_disorders = models.render_disorder_dict(return_as="html_select_add", exclude=self.survivor["disorders"]),
            rm_disorders = self.get_disorders(return_as="html_select_remove"),

            skip_next_hunt_checked = flags["skip_next_hunt"],
            abilities_and_impairments = self.get_abilities_and_impairments(),
            remove_abilities_and_impairments = self.get_abilities_and_impairments(return_as="html_select_remove"),

            email = self.survivor["email"],
            game_link = self.settlement.asset_link(view="game", fixed=True),
        )
        return output



#
#   SETTLEMENT CLASS
#

class Settlement:

    def __init__(self, settlement_id=False, name=False, created_by=False):
        """ Initialize with a settlement from mdb. """
        self.logger = get_logger()
        if not settlement_id:
            settlement_id = self.new(name, created_by)
        self.settlement = mdb.settlements.find_one({"_id": ObjectId(settlement_id)})
        self.survivors = mdb.survivors.find({"settlement": settlement_id})
        if self.settlement is not None:
            self.update_death_count()

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
        self.logger.info("New settlement '%s' ('%s') created!" % (name, settlement_id, creator["login"]))
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


    def get_min_survival_limit(self):
        """ Returns the settlement's minimum survival limit as an int."""

        min_survival = 0
        if self.settlement["name"] != "":
            min_survival +=1

        innovations = self.settlement["innovations"]
        innovations.extend(self.settlement["principles"])
        innovations = list(set(innovations))
        for innovation_key in innovations:
            if "survival_limit" in Innovations.get_asset(innovation_key).keys():
                min_survival += Innovations.get_asset(innovation_key)["survival_limit"]

        return min_survival

    def get_innovation_deck(self, return_as=False):
        """ Returns the settlement's Innovation Deck as a list of strings. """

        innovations = self.settlement["innovations"]

        innovation_deck = Innovations.get_always_available_innovations()

        for innovation_key in innovations:
            for c in Innovations.get_asset(innovation_key)["consequences"]:
                innovation_deck.add(c)

        for innovation_key in innovations:
            if innovation_key in innovation_deck:
                innovation_deck.discard(innovation_key)

        final_list = sorted(list(set(innovation_deck)))

        if return_as == "html_option":
            return "</option><option>".join(final_list)

        return final_list


        return final_list

    def get_locations(self, return_as=False):
        """ Returns a sorted list of locations. """
        final_list = sorted(self.settlement["locations"])

        if return_as == "comma-delimited":
            return ", ".join(final_list)
        return final_list

    def get_locations_deck(self, return_as=False):
        """ Returns a sorted list of available locations. """

        eligible_locations = Locations.get_keys()

        for location_key in eligible_locations:
            if "is_resource" in Locations.get_asset(location_key).keys():
                eligible_locations.remove(location_key)

        for l in self.settlement["locations"]:
            if l in eligible_locations:
                eligible_locations.remove(l)
        final_list = sorted(eligible_locations)
        if return_as == "html_option":
            return "</option><option>".join(final_list)
        return final_list

    def get_storage(self, return_type=False):
        """ Returns the settlement's storage in a number of ways. """

        storage = sorted(self.settlement["storage"])

        if return_type == "html_buttons":
            html = ""
            for item_key in storage:
                if item_key in Items.get_keys():
                    item_location = Items.get_asset(item_key)["location"]
                    item_color = Locations.get_asset(item_location)["color"]
                else:
                    item_color = "FFF"
                html += '<button id="remove_item" name="remove_item" value="%s" style="background-color: #%s; color: #000;"> %s</button>\n' % (item_key, item_color, item_key)
            return html

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
        list back. """

        principles = sorted(self.settlement["principles"])

        if return_type == "comma-delimited":
            if principles == []:
                return "No principles"
            else:
                return ", ".join(principles)

        return principles

    def get_innovations(self, include_principles=False, return_as=False):
        """ Get the settlement's innovations as a list. Use 'include_principles'
        if you want the list to include principles as well as plain Jane
        innovations. """

        innovations = self.settlement["innovations"]
        if include_principles:
            innovations.extend(self.settlement["principles"])

        innovations = list(set(innovations))

        if return_as == "comma-delimited":
            return ", ".join(innovations)

        return innovations

    def get_survival_actions(self, return_as=False):
        innovations = self.get_innovations()
        survival_actions = ["Dodge"]
        for innovation in innovations:
            if "survival_action" in Innovations.get_asset(innovation).keys():
                survival_actions.append(Innovations.get_asset(innovation)["survival_action"])
        return list(set(survival_actions))

    def get_bonuses(self, bonus_type, return_as=False):
        """ Returns the buffs/bonuses that settlement gets. 'bonus_type' is
        required and can be 'departure_buff', 'settlement_buff' or
        'survivor_buff'.  """

        innovations = self.get_innovations(include_principles=True)

        buffs = {}

        for innovation_key in innovations:
            if bonus_type in Innovations.get_asset(innovation_key).keys():
                buffs[innovation_key] = Innovations.get_asset(innovation_key)[bonus_type]

        html = ""
        for k in buffs.keys():
            html += '<p><b>%s:</b> %s</p>\n' % (k, buffs[k])
        return html

    def get_defeated_monsters(self, return_type=None):
        monsters = sorted(self.settlement["defeated_monsters"])

        if return_type == "comma-delimited":
            if monsters == []:
                return None
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

    def get_survivors(self, return_as=False, user_id=False):
        """ Returns the settlement's survivors. Leave 'return_as' unspecified
        if you want a mongo cursor object back. """

        survivors = mdb.survivors.find({"settlement": self.settlement["_id"]})

        user = None
        if user_id:
            user = mdb.users.find_one({"_id": user_id})
            user_login = user["login"]

        current_user_is_settlement_creator = False
        if user is not None and user["_id"] == self.settlement["created_by"]:
            current_user_is_settlement_creator = True

        if return_as == "html_buttons":
            output = ""
            for survivor in survivors:
                S = assets.Survivor(survivor_id=survivor["_id"])
                output += S.asset_link()
            return output

        if return_as == "game_view":
            output = ""
            for survivor in survivors:
                S = assets.Survivor(survivor_id=survivor["_id"])
                user_owns_survivor = False

                if survivor["email"] == user_login:
                    user_owns_survivor = True
                if current_user_is_settlement_creator:
                    user_owns_survivor = True

                if user_owns_survivor:
                    output += S.asset_link()
                else:
                    output += S.asset_link(disabled=True)
            return output

        return survivors


    def get_min(self, value="population"):
        """ Returns the settlement's minimum population as an int. """
        results = False
        settlement_id = ObjectId(self.settlement["_id"])
        if value == "population":
            results = mdb.survivors.find({"settlement": settlement_id, "dead": {"$exists": False}}).count()
        if value == "deaths":
            results = mdb.survivors.find({"settlement": settlement_id, "dead": {"$exists": True}}).count()
        return results


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

    def modify(self, params):
        """ Pulls a settlement from the mdb, updates it and saves it using a
        cgi.FieldStorage() object.

        All of the business logic lives here.
        """

        for p in params:
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
                self.settlement["innovations"].append(params[p].value)
            elif p == "add_location":
                self.settlement["locations"].append(params[p].value)
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
        output = html.settlement.summary.safe_substitute(
            settlement_name=self.settlement["name"],
            principles = self.get_principles("comma-delimited"),
            population=self.settlement["population"],
            death_count = self.settlement["death_count"],
            survivors = self.get_survivors(return_as="game_view", user_id=user_id),
            survival_limit = self.settlement["survival_limit"],
            innovations = self.get_innovations(return_as="comma-delimited", include_principles=True),
            departure_bonuses = self.get_bonuses('departure_buff'),
            settlement_bonuses = self.get_bonuses('settlement_buff'),
            survivor_bonuses = self.get_bonuses('survivor_buff'),
            defeated_monsters = self.get_defeated_monsters("comma-delimited"),
            quarries = self.get_quarries("comma-delimited"),
            nemesis_monsters = self.get_nemesis_monsters("comma-delimited"),
        )
        return output


    def render_html_form(self, read_only=False):
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
        if survival_limit < self.get_min_survival_limit():
            survival_limit = self.get_min_survival_limit()

        deaths = int(self.settlement["death_count"])
        if deaths < self.get_min(value="deaths"):
            deaths = self.get_min(value="deaths")

        population = int(self.settlement["population"])
        if population < self.get_min(value="population"):
            population = self.get_min(value="population")

        output = html.settlement.form.safe_substitute(
            MEDIA_URL = settings.get("application","STATIC_URL"),
            settlement_id = self.settlement["_id"],
            game_link = self.asset_link(view="game", fixed=True),

            population = population,
            name = self.settlement["name"],
            survival_limit = survival_limit,
            min_survival_limit = self.get_min_survival_limit(),
            death_count = deaths,
            lost_settlements = self.settlement["lost_settlements"],

            survivors = self.get_survivors(return_as="html_buttons"),

            departure_bonuses = self.get_bonuses('departure_buff'),
            settlement_bonuses = self.get_bonuses('settlement_buff'),

            items_options = Items.render_as_html_dropdown_with_divisions(),
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
            quarry_options = Quarries.render_as_html_dropdown(),
            innovations = self.get_innovations(return_as="comma-delimited"),
            innovation_options = self.get_innovation_deck(return_as="html_option"),
            locations = self.get_locations(return_as="comma-delimited"),
            locations_options = self.get_locations_deck(return_as="html_option"),

            defeated_monsters = self.get_defeated_monsters("comma-delimited"),

        )

        return output


    def asset_link(self, view="settlement", button_class="info", link_text=False, fixed=False):
        """ Returns an asset link (i.e. html form with button) for the
        settlement. """

        prefix = ""
        suffix = ""

        if view == "game":
            button_class = "purple"
            if not link_text and not fixed:
                prefix = html.dashboard.settlement_flash
                link_text = prefix + self.settlement["name"]
#                suffix = " (%s players, pop. %s)" % (self.get_players(count_only=True), self.settlement["population"])
                suffix = " (LY %s, pop. %s)" % (self.settlement["lantern_year"], self.settlement["population"])
                link_text += suffix

        button_id = None
        if fixed:
            button_id = "floating_asset_button"
            if not link_text:
                link_text = html.dashboard.settlement_flash

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






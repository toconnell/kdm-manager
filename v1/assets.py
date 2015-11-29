#!/usr/bin/env python

from bson.objectid import ObjectId
from datetime import datetime
import os
from string import Template

import html
import models
from utils import mdb, get_logger, load_settings

settings = load_settings()

class User:

    def __init__(self, user_id):
        """ Initialize with a user's _id to create an object with his compelte
        user object and all settlements. """

        self.logger = get_logger()

        user_id = ObjectId(user_id)
        self.user = mdb.users.find_one({"_id": user_id})
        self.settlements = mdb.settlements.find({"created_by": self.user["_id"]}).sort("name")
        self.survivors = mdb.survivors.find({"$or": [
            {"email": self.user["login"]},
            {"created_by": self.user["_id"]},
            ]}
        ).sort("name")

    def get_settlements(self, return_as=False):
        """ Returns the user's settlements in a number of ways. Leave
        'return_as' unspecified if you want a mongo cursor back. """

        if return_as == "html_option":
            html = ""
            for settlement in self.settlements:
                html += '<option value="%s">%s</option>' % (settlement["_id"], settlement["name"])
            return html

        return self.settlements

    def get_survivors(self, return_as=False):
        """ Returns all of the survivors that a user can access. Leave
        the 'return_as' kwarg unspecified/False if you want a mongo cursor
        back (instead of fruity HTML crap). """

        return self.survivors

class Survivor:

    def __init__(self, survivor_id=False, params=False):
        """ Initialize this with a cgi.FieldStorage() as the 'params' kwarg
        to create a new survivor. Otherwise, use a mdb survivor _id value
        to initalize with survivor data from mongo. """

        self.logger = get_logger()
        self.flags = [
            "cannot_spend_survival",
            "cannot_use_fighting_arts",
            "skip_next_hunt",
            "dead",
            "retired",
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
        survivor_email = params["email"].value
        survivor_sex = params["sex"].value[0].upper()

        survivor_dict = {
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
        }

        user = mdb.users.find_one({"_id": created_by})
        login = user["login"]

        survivor_id = mdb.survivors.insert(survivor_dict)
        self.logger.info("User '%s' created new survivor '%s [%s]' successfully." % (login, survivor_name, survivor_sex))
        return survivor_id

    def modify(self, params):
        """ Reads through a cgi.FieldStorage() (i.e. 'params') and modifies the
        survivor. """

        for p in params:
            if p == "asset_id":
                pass
            else:
                self.survivor[p] = params[p].value.strip()

        for flag in self.flags:
            if flag in params:
                self.survivor[flag] = "checked"
            elif flag not in params and flag in self.survivor.keys():
                del self.survivor[flag]

        mdb.survivors.save(self.survivor)

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


    def render_html_form(self):
        """ This is just like the render_html_form() method of the settlement
        class: a giant tangle-fuck of UI/UX logic that creates the form for
        modifying a user. """

        survivor_survival_points = int(self.survivor["survival"])
        if survivor_survival_points > int(self.settlement.settlement["survival_limit"]):
            survivor_survival_points = self.settlement.settlement["survival_limit"]

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

        output = html.survivor.form.safe_substitute(
            MEDIA_URL = settings.get("application", "STATIC_URL"),

            survivor_id = self.survivor["_id"],
            name = self.survivor["name"],
            sex = self.survivor["sex"],
            survival = survivor_survival_points,
            survival_limit = self.settlement.settlement["survival_limit"],
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

            settlement_link = self.settlement.asset_link(),
        )
        return output



class Settlement:

    def __init__(self, settlement_id=False, name=False, created_by=False):
        """ Initialize with a settlement from mdb. """
        self.logger = get_logger()

        if not settlement_id:
            settlement_id = self.new(name, created_by)

        self.settlement = mdb.settlements.find_one({"_id": settlement_id})
        self.logger.info("Initialized settlement '%s' successfully!" % settlement_id)

    def new(self, name=None, created_by=None):
        """ Creates a new settlement. 'name' is any string and 'created_by' has to
        be an ObjectId of a user. """
        new_settlement_dict = {
            "nemesis_monsters": {"Butcher": [], },
            "created_on": datetime.now(),
            "created_by": created_by,
            "name": name,
            "survival_limit": 0,
            "lantern_year": 0,
            "death_count": 0,
            "milestone_story_events": [],
            "innovations": ["Language"],
            "principles": [],
            "locations": ["Lantern Hoard"],
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
        self.logger.info("New settlement '%s' ('%s') created!" % (name, created_by))
        return settlement_id

    def get_min_survival_limit(self):
        """ Returns the settlement's minimum survival limit as an int."""

        min_survival = 0
        if self.settlement["name"] != "":
            min_survival +=1

        innovations = self.settlement["innovations"]
        innovations.extend(self.settlement["principles"])
        innovations = list(set(innovations))
        for i in innovations:
            if "survival_limit" in models.innovations[i].keys():
                min_survival += models.innovations[i]["survival_limit"]

        return min_survival

    def get_innovation_deck(self, return_as=False):
        """ Returns the settlement's Innovation Deck as a list of strings. """

        innovations = self.settlement["innovations"]
        innovation_deck = set()
        for i in innovations:
            for c in models.innovations[i]["consequences"]:
                innovation_deck.add(c)
        for i in innovations:
            if i in innovation_deck:
                innovation_deck.discard(i)

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
        eligible_locations = models.locations.keys()
        for location_key in eligible_locations:
            if "is_resource" in models.locations[location_key].keys():
                eligible_locations.remove(location_key)
        for l in self.settlement["locations"]:
            if l in eligible_locations:
                eligible_locations.remove(l)
        final_list = sorted(eligible_locations)
        if return_as == "html_option":
            return "</option><option>".join(final_list)
        return final_list

    def get_storage(self, return_as=False):
        """ Returns the settlement's storage in a number of ways. """

        storage = sorted(self.settlement["storage"])

        if return_as == "html_buttons":
            html = ""
            for item_key in storage:
                if item_key in models.items.keys():
                    item_location = models.items[item_key]["location"]
                    item_color = models.locations[item_location]["color"]
                else:
                    item_color = "FFF"
                html += '<button id="remove_item" style="background-color: #%s; color: #000;" disabled> %s</button>\n' % (item_color, item_key)
            return html

        if return_as == "drop_list":
            html = '<select name="remove_item" onchange="this.form.submit()">'
            html += '<option selected disabled hidden value="">Remove Item</option>'
            for item in storage:
                html += '<option value="%s">%s</option>' % (item, item)
            html += '</select>'
            return html

        if return_as == "comma-delimited":
            return ", ".join(storage)

        return storage


    def get_nemesis_monsters(self, return_as=False):
        nemesis_monster_keys = sorted(self.settlement["nemesis_monsters"].keys())

        if return_as == "html_select":
            html = ""
            for k in nemesis_monster_keys:
                html += '<p><b>%s</b> ' % k
                for level in ["Lvl 3", "Lvl 2", "Lvl 1"]:
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
                if year <= current_lantern_year:
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
            if "survival_action" in models.innovations[innovation].keys():
                survival_actions.append(models.innovations[innovation]["survival_action"])
        return list(set(survival_actions))

    def get_bonuses(self, bonus_type, return_as=False):
        """ Returns the buffs/bonuses that settlement gets. 'bonus_type' is
        required and can be 'departure_buff', 'settlement_buff' or
        'survivor_buff'.  """

        innovations = self.get_innovations(include_principles=True)

        buffs = {}

        for innovation_key in innovations:
            if bonus_type in models.innovations[innovation_key].keys():
                buffs[innovation_key] = models.innovations[innovation_key][bonus_type]

        html = ""
        for k in buffs.keys():
            html += '<p><b>%s:</b> %s</p>\n' % (k, buffs[k])
        return html

    def get_quarries(self, return_as=False):
        """ Returns a list of the settlement's quarries. """
        quarries = self.settlement["quarries"]

        if return_as == "comma-delimited":
            return ", ".join(quarries)

        return quarries

    def get_survivors(self, return_as=False):
        """ Returns the settlement's survivors. Leave 'return_as' unspecified
        if you want a mongo cursor object back. """

        survivors = mdb.survivors.find({"settlement": self.settlement["_id"]})

        if return_as == "html_buttons":
            output = ""
            for survivor in survivors:
                output += html.dashboard.view_asset_button.safe_substitute(
                    asset_type = "survivor",
                    asset_id = survivor["_id"],
                    asset_name = survivor["name"],
                )
            return output

        return survivors

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

        output = html.settlement.form.safe_substitute(
            MEDIA_URL = settings.get("application","STATIC_URL"),
            settlement_id = self.settlement["_id"],

            population = self.settlement["population"],
            name = self.settlement["name"],
            survival_limit = survival_limit,
            min_survival_limit = self.get_min_survival_limit(),
            death_count = self.settlement["death_count"],
            lost_settlements = self.settlement["lost_settlements"],

            survivors = self.get_survivors(return_as="html_buttons"),

            departure_bonuses = self.get_bonuses('departure_buff'),
            settlement_bonuses = self.get_bonuses('settlement_buff'),

            items_options = models.render_item_dict(return_as="html_select_box"),
            items_remove = self.get_storage(return_as="drop_list"),
            storage = self.get_storage(return_as="html_buttons"),

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

            nemesis_monsters = self.get_nemesis_monsters(return_as="html_select"),

            quarries = self.get_quarries(return_as="comma-delimited"),
            quarry_options = "</option><option>".join(sorted(models.quarries.keys())),
            innovations = self.get_innovations(return_as="comma-delimited"),
            innovation_options = self.get_innovation_deck(return_as="html_option"),
            locations = self.get_locations(return_as="comma-delimited"),
            locations_options = self.get_locations_deck(return_as="html_option"),

            defeated_monsters = ", ".join(sorted(self.settlement["defeated_monsters"])),

        )

        return output

    def asset_link(self):
        """ Returns an asset link (i.e. html form with button) for the
        settlement. """

        output = html.dashboard.view_asset_button.safe_substitute(
            asset_type="settlement",
            asset_id=self.settlement["_id"],
            asset_name=self.settlement["name"],
        )
        return output


def update_settlement(params):
    """ Pulls a settlement from the mdb, updates it and saves it.

    Needs to be moved up into the Settlement class. Leaving it here for now.
    """

    logger = get_logger()

    settlement = mdb.settlements.find_one({"_id": ObjectId(params["asset_id"].value)})

    settlement["principles"] = []
    settlement["milestone_story_events"] = []

    for p in params:
        if p == "asset_id":
            pass
        elif p == "add_defeated_monster":
            settlement["defeated_monsters"].append(params[p].value)
        elif p == "add_quarry":
            settlement["quarries"].append(params[p].value)
        elif p == "add_nemesis":
            settlement["nemesis_monsters"][params[p].value] = []
        elif p == "add_item":
            settlement["storage"].append(params[p].value)
        #    break   # don't process any params after this
        elif p == "remove_item":
            logger.info("remove request received")
            logger.info(params)
            settlement["storage"].remove(params[p].value)
        elif p == "add_innovation":
            settlement["innovations"].append(params[p].value)
        elif p == "add_location":
            settlement["locations"].append(params[p].value)
        elif p in ["new_life_principle", "death_principle", "society_principle", "conviction_principle"]:
            settlement["principles"].append(params[p].value)
        elif p in [
            "First child is born",
            "First time death count is updated",
            "Population reaches 15",
            "Settlement has 5 innovations",
            "Population reaches 0",
        ]:
            settlement["milestone_story_events"].append(p)
        elif p == "increment_lantern_year":
            settlement["lantern_year"] = int(settlement["lantern_year"]) + 1
            break
        elif p.split("_")[:3] == ['update', 'timeline', 'year']:
            for year_dict in settlement["timeline"]:
                if int(year_dict["year"]) == int(p.split("_")[-1]):
                    year_index = settlement["timeline"].index(year_dict)
                    settlement["timeline"].remove(year_dict)
                    year_dict["custom"].append(params[p].value)
                    settlement["timeline"].insert(year_index, year_dict)
                    break
        elif p == "increment_nemesis":
            nemesis_key = params[p].value
            completed_levels = settlement["nemesis_monsters"][nemesis_key]
            if completed_levels == []:
                settlement["nemesis_monsters"][nemesis_key].append("Lvl 1")
            elif "Lvl 1" in completed_levels:
                settlement["nemesis_monsters"][nemesis_key].append("Lvl 2")
            elif "Lvl 2" in completed_levels:
                settlement["nemesis_monsters"][nemesis_key].append("Lvl 3")
        else:
            settlement[p] = params[p].value.strip()

    #   Turn lists into sets to prevent dupes; turn sets into lists to prevent
    #   mongo from FTFO if it sees a set()
    for attrib in ["quarries", "innovations", "principles"]:
        settlement[attrib] = list(set(settlement[attrib]))

    mdb.settlements.save(settlement)



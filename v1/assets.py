#!/usr/bin/env python

from bson.objectid import ObjectId
from datetime import datetime
import os

import models
from utils import mdb, get_logger, load_settings

settings = load_settings()

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


    def get_innovations(self, return_as=False):
        """ Returns a sorted list of a innovations. """
        final_list = sorted(list(set(self.settlement["innovations"])))

        if return_as == "comma-delimited":
            return ", ".join(final_list)
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

    def get_bonuses(self, bonus_type, return_as=False):
        """ Returns the buffs/bonuses that settlement gets. 'bonus_type' is
        required and can be 'departure_buff' or 'settlement_buff'. """

        innovations = self.settlement["innovations"]
        innovations.extend(self.settlement["principles"])
        innovations = set(innovations)

        buffs = {}

        for innovation_key in innovations:
            if bonus_type in models.innovations[innovation_key].keys():
                buffs[innovation_key] = models.innovations[innovation_key][bonus_type]

        html = ""
        for k in buffs.keys():
            html += '<p><b>%s:</b> %s</p>\n' % (k, buffs[k])
        return html


def update_settlement(params):
    """ Pulls a settlement from the mdb, updates it and saves it. """

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



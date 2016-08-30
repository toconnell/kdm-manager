#!/usr/bin/env python

from bson.objectid import ObjectId
from datetime import datetime, timedelta
from optparse import OptionParser

import game_assets
import html
from utils import mdb, get_percentage, ymd
from models import Quarries, Nemeses, mutually_exclusive_principles

def latest_kill(return_type=False):
    """ Returns the latest defeated monster from mdb.killboard. """
    l = mdb.killboard.find_one({"settlement_name": {"$nin": ["Test", "Unknown"]}}, sort=[("created_on", -1)])
    if l is None:
        return None

    if return_type == "admin_panel":
        output = "%s: %s (%s)" % (l["created_on"].strftime(ymd), l["name"], l["settlement_name"])
    else:   # all other return_type values
        output = "<li><b>%s</b></li>" % l["name"]
        ly = l["kill_ly"].split("_")[1]
        output += "<li>Defeated by the survivors of <b>%s</b> in LY %s on %s at %s (CT).</li>" % (l["settlement_name"], ly, l["created_on"].strftime(ymd), l["created_on"].strftime("%H:%M:%S"))

    return output

def latest_fatality(return_type=False):
    """ Returns the latest fatality from mdb.the_dead. """
    latest_fatality = mdb.the_dead.find_one(
        {
            "complete": {"$exists": True},
            "name": {"$ne": "Anonymous"},
            "cause_of_death": {"$ne": "Forsaken."},
        },
        sort=[("created_on", -1)],
        )

    if return_type == "html":

        avatar_img = ""
        if "avatar" in latest_fatality.keys():
            avatar_img = '<img class="latest_fatality" src="/get_image?id=%s" alt="%s"/>' % (latest_fatality["avatar"], latest_fatality["name"])

        html_epithets = ""
        if "epithets" in latest_fatality.keys() and latest_fatality["epithets"] != []:
            epithets = ", ".join(latest_fatality["epithets"])
            html_epithets = "<li><i>%s</i></li>" % epithets

        output = '<p>Latest survivor fatality: %s<br/><ul>' % avatar_img
        output += '<li><b>%s</b> of <b>%s</b></li>' % (latest_fatality["name"], latest_fatality["settlement_name"])
        output += html_epithets
        output += '<li>Cause of death: %s<br/>&ensp; Died in LY %s, XP: %s</li>' % (latest_fatality["cause_of_death"], latest_fatality["lantern_year"], latest_fatality["hunt_xp"]) 
        output += '<li>Courage: %s, Understanding: %s</li>' % (latest_fatality["Courage"], latest_fatality["Insanity"])
        output += '</ul></p>'
        return output

    return latest_fatality

def kill_board(return_type=None, admin=False):
    """ Creates a dictionary showing kills by monster type. """
    kill_list = []
    all_settlements = mdb.settlements.find()
    for settlement in all_settlements:
        for m in settlement["defeated_monsters"]:
            kill_list.append(m)

    monsters = {"Other": {"sort_order": 99, "tokens": ["OTHER"], }}
    others = []
    for model in [Quarries, Nemeses]:
        monsters.update(model.game_assets)
    for m in monsters:
        monsters[m]["kills"] = 0
        monsters[m]["name"] = m

    for kill in kill_list:
        categorized = False
        k_tokenized = kill.upper().split()
        for monster in monsters.keys():
            if kill.upper() in monsters[monster]["tokens"]:
                categorized = True
                monsters[monster]["kills"] += 1
            if not categorized:
                for k_token in k_tokenized:
                    if k_token in monsters[monster]["tokens"]:
                        categorized = True
                        monsters[monster]["kills"] += 1
        if not categorized:
            others.append(kill)
            monsters["Other"]["kills"] += 1

    sorted_monsters = {}
    for m in monsters:
        sorted_monsters[monsters[m]["sort_order"]] = monsters[m]

    if return_type == "html_table_rows":
        output = ""
        for numerical_key in sorted(sorted_monsters.keys()):
            monst_dict = sorted_monsters[numerical_key]
            monst_html = html.dashboard.kill_board_row.safe_substitute(monster = monst_dict["name"], kills = monst_dict["kills"])
            output += monst_html
        if admin:
            output += html.dashboard.kill_board_foot.safe_substitute(other_list = ", ".join(sorted(others)))
        return output

    return sorted_monsters


def top_principles(return_type=None):
    """ Determines which principles are most popular. """

    popularity_contest = {}
    for principle in mutually_exclusive_principles.keys():
        tup = mutually_exclusive_principles[principle]
        sample_set = mdb.settlements.find({"principles": {"$in": tup} }).count()
        popularity_contest[principle] = {"sample_size": sample_set, "options": tup}
        for option in tup:
            total = mdb.settlements.find({"principles": {"$in": [option]}}).count()
            popularity_contest[principle][option] = {
                "total": total,
                "percentage": int(get_percentage(total, sample_set)),
            }

    if return_type == "html_ul":
        output = "<ul>\n"
        for k in popularity_contest.keys():
            output += "<li>%s Principle:\n\t<ul>\n" % k
            for principle in popularity_contest[k]["options"]:
                output += "<li>%s%% - %s</li>\n" % (popularity_contest[k][principle]["percentage"], principle) 
            output += "\t</ul>\n</li>"
        output += '</ul>\n\n'
        return output

    return popularity_contest

def expansion_popularity_contest():
    """ Creates a dict of expansion use across all settlements. """
    exp_dict = {}
    for expansion in game_assets.expansions.keys():
        exp_dict[expansion] = mdb.settlements.find({"expansions": {"$in": [expansion]}}).count()
    output = ""
    for k in sorted(exp_dict.keys()):
        v = exp_dict[k]
        output += "<li>%s: %s</li>" % (k, v)
    return output

def current_hunt():
    try:
        settlement = mdb.settlements.find({"name": {"$nin": ["Test", "Unknown"]}, "current_quarry": {"$exists": True}, "hunt_started": {"$gte": datetime.now() - timedelta(minutes=180)}}).sort("hunt_started", -1)[0]
    except:
        return "No settlements are currently hunting monsters."
    if settlement is None:
        return "No settlements are currently hunting monsters."
    hunters = mdb.survivors.find({"settlement": settlement["_id"], "in_hunting_party": {"$exists": True}}).sort("name")
    if hunters.count() == 0:
        return "No settlements are currently hunting monsters."
    elif hunters.count() == 1:
        hunter = mdb.survivors.find_one({"settlement": settlement["_id"], "in_hunting_party": {"$exists": True}})
        return "%s of <b>%s</b> is currently out hunting! Quarry: %s" % (hunter["name"], settlement["name"], settlement["current_quarry"])
    elif hunters.count() >= 2:
        hunter_names = []
        for h in hunters:
            hunter_names.append(h["name"])
        hunter_string = ", ".join(hunter_names[:-1])
        hunter_string += " and %s of <b>%s</b>" % (hunter_names[-1], settlement["name"])
        hunter_string += " are currently out hunting! Quarry: %s" % (settlement["current_quarry"])
        return hunter_string
    else:
        return "An error occurred while gathering information about the latest monster hunt."

def get_minmax(attrib="population"):
    data_points = []
    sample_set = mdb.settlements.find({"population": {"$gt": 4}, "death_count": {"$gt": 0}})
    for sample in sample_set:
        data_points.append(int(sample[attrib]))
    return min(data_points), max(data_points)

def get_average(attrib="population"):
    data_points = []
    sample_set = mdb.settlements.find({"population": {"$gt": 4}, "death_count": {"$gt": 0}, "lantern_year": {"$gte": 1},})
    for sample in sample_set:
        data_points.append(int(sample[attrib]))
    return reduce(lambda x, y: x + y, data_points) / len(data_points)

def get_survivor_average(attrib="hunt_xp"):
    data_points = []
    survivors = mdb.survivors.find({"dead": {"$exists": False}})
    for s in survivors:
        data_points.append(int(s[attrib]))
    return reduce(lambda x, y: x + y, data_points) / len(data_points)



if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-a", dest="average", help="Returns an average for the specified value", metavar="population", default=False)
    parser.add_option("-m", dest="minmax", help="Returns min/max numbers the specified value", metavar="death_count", default=False)
    parser.add_option("-k", dest="kill_board", help="Run the kill_board func and print its contents.", default=False, action="store_true")
    parser.add_option("-p", dest="top_principles", help="Run the top_principles func and print its contents.", default=False, action="store_true")
    (options, args) = parser.parse_args()

    if options.kill_board:
        print kill_board()
    if options.top_principles:
        print top_principles()
    if options.average:
        print get_average(options.average)
    if options.minmax:
        print get_minmax(options.minmax)

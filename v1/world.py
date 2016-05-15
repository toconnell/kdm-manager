#!/usr/bin/env python

from bson.objectid import ObjectId
from datetime import datetime, timedelta
from optparse import OptionParser

import html
from utils import mdb, get_percentage
from models import Quarries, Nemeses, mutually_exclusive_principles


def latest_fatality(return_type=False):
    """ Returns the latest fatality from mdb.the_dead. """
    latest_fatality = mdb.the_dead.find_one({"complete": {"$exists": True}, "name": {"$ne": ["Anonymous","Test"]}}, sort=[("created_on", -1)])

    if return_type == "html":

        avatar_img = ""
        if "avatar" in latest_fatality.keys():
            avatar_img = '<img class="latest_fatality" src="/get_image?id=%s" alt="%s"/>' % (latest_fatality["avatar"], latest_fatality["name"])

        html_epithets = ""
        if "epithets" in latest_fatality.keys() and latest_fatality["epithets"] != []:
            epithets = ", ".join(latest_fatality["epithets"])
            html_epithets = "&ensp; <i>%s</i><br/>" % epithets

        output = '<p>Latest fatality: %s<br/><br/>' % avatar_img
        output += '&ensp; <b>%s</b> of <b>%s</b> <br/>' % (latest_fatality["name"], latest_fatality["settlement_name"])
        output += html_epithets
        output += '&ensp; &nbsp; %s<br/>&ensp; Died in LY %s, XP: %s<br/>' % (latest_fatality["cause_of_death"], latest_fatality["lantern_year"], latest_fatality["hunt_xp"]) 
        output += '&ensp; Courage: %s, Understanding: %s</p>' % (latest_fatality["Courage"], latest_fatality["Insanity"])
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

def current_hunt():
    try:
        settlement = mdb.settlements.find({"current_quarry": {"$exists": True}, "hunt_started": {"$gte": datetime.now() - timedelta(minutes=120)}}).sort("hunt_started", -1)[0]
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
    sample_set = mdb.settlements.find({"population": {"$gt": 4}, "death_count": {"$gt": 0}})
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

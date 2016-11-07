#!/usr/bin/env python

import json
from datetime import datetime, timedelta
from optparse import OptionParser

import assets
import game_assets
import html
import os
import requests
from utils import mdb, get_percentage, ymd, admin_session, load_settings, get_logger, thirty_days_ago, recent_session_cutoff, forbidden_names


def survivor_html(s, item=False):
    """ Helper function that returns survivor HTML for dashboard/panel use. """
    output = ""

    if item == "avatar":
        if "avatar" in s.keys():
            output = html.dashboard.avatar_image.safe_substitute(name=s["name"], avatar_id=s["avatar"])
    elif item == "epithets":
        if "epithets" in s.keys() and s["epithets"] != []:
            epithets = ", ".join(s["epithets"])
            output = "<li><i>%s</i></li>" % epithets

    return output


#
#   World data comes from a call to the production API; the Warehouse object is
#   deprecated, as are any one-off data retrieval functions in this module.
#
#   What follows are all methods for working with API data
#

def api_world():
    """ This method, which can be run in the clear from anywhere, retrieves JSON
    from the API /world route and turns it into a dict. """

    settings = load_settings()
    w_url = settings.get("application","api_url") + "world"
    r = requests.get(w_url)
    if r.status_code == 200:
       return dict(r.json())
    else:
        logger = get_logger()
        logger.warn("API call failed. Response status code: %s" % (r.status_code))
        return None

def api_top_principles(p):
    """ Custom function to render top principles as html. """
    if p is None:
        return "<p>Data unavailable.</p>"

    data = p["value"]

    output = '<p><table class="dashboard_table" title="%s">' % p["comment"]
    for k in sorted(data.keys()):
        output += '<tr title="%s settlements polled"><th colspan="2">%s</th></tr>' % (data[k]["sample_size"], k)
        for option in data[k]["options"]:
            output += '<tr><td>&ensp; &ensp; &ensp; %s</td><td>%s%%</td></tr>' % (option, data[k][option]["percentage"])
    output += "</table></p>"

    return output

def api_pop_con_to_html(p):
    """ Turns a standard popularity contest into a table. Doesn't work for the
    killboard or for top principles. """

    if p is None:
        return "<p>Data unavailable.</p>"

    table = p["value"]

    output = '<p><table class="dashboard_table" title="%s">' % p["comment"]
    for k in sorted(table.keys()):
        output += '<tr><td>%s</td><td class="value">%s</td></tr>' % (k,table[k])
    output += "</table></p>"

    return output

def api_killboard_to_html(k):
    """ Makes a few tables representing kills across the various monster
    type groups. Only reasons mdb.killboard (doesn't read settlement objects).
    """

    if k is None:
        return "<p>Data unavailable.</p>"

    killboard = k["value"]

    output = ""
    list_tup = [("quarry","Quarries"), ("nemesis", "Nemeses")]
    for tup in list_tup:
        group_key = tup[0]
        group_title = tup[1]
        output += '<p><table class="dashboard_table killboard" title="%s">' % k["comment"]
        output += '<tr><th colspan="2">%s:</th></tr>' % group_title
        for monster in killboard[group_key]:
            output += '<tr><td>%s</td><td class="value">%s</td>' % (monster["name"], monster["count"])
        output += "</table>"

    output += "</p>"
    return output

def api_top_five_list(l):
    """ Takes a top-five-type list and returns it as an html <ol> element. """

    if l is None:
        return "<p>Data unavailable.</p>"

    items = l["value"]

    output = "<ol>"
    for i in items:
        output += "<li>%s (%s)</li>" % (i["value"],i["count"])
    output += "</ol>"

    return output


def api_survivor_to_html(s, supplemental_info=["birth","death"]):
    """ Meant to be at least a little bit extensible, this one can show latest
    birth/death without too much fiddling (and a lot of user friendliness). """

    if s is None:
        return "<p>No data available.</p>"

    survivor = s["value"]

    output = ""
    if "avatar" in survivor.keys():
        output = html.dashboard.avatar_image.safe_substitute(name=survivor["name"], avatar_id=survivor["avatar"]["$oid"])

    try:
        output += "<p><ul><li><b>%s</b> of <b>%s</b></li>" % (survivor["name"], survivor["settlement"]["name"])
    except Exception as e:
        raise Exception("survivor missing name")

    output += survivor_html(survivor, item="epithets")

    if "death" in supplemental_info:
        output += '<li>Died in LY %s on %s</li>' % (survivor["died_in"], datetime.fromtimestamp(survivor["died_on"]["$date"]/1000).strftime(ymd))
        if "cause_of_death" in survivor.keys():
            output += '<li>Cause of death: %s</li>' % (survivor["cause_of_death"])

    if "birth" in supplemental_info:
        if "mother" in survivor.keys() or "father" in survivor.keys():
            output += "<li>Born in LY %s</li>" % survivor["born_in_ly"]
        else:
            output += "<li>Joined the settlement in LY %s</li>" % survivor["born_in_ly"]

    output += '<li>XP: %s, Insanity: %s</li>' % (survivor["hunt_xp"], survivor["Insanity"])
    output += '<li>Courage: %s, Understanding: %s</li>' % (survivor["Courage"], survivor["Understanding"])

    output += "</ul></p>"

    return output


def api_current_hunt(h):
    """ Formats a current/latest hunt block. Total one-off. """

    if h is None:
        return "<p>Data is unavailable.</p>"
    elif h["value"] is None:
        return "<p>No settlements are currently hunting monsters.</p>"

    settlement = h["value"]["settlement"]
    hunters = h["value"]["survivors"]

    output = "ERROR"
    if len(hunters) == 1:
        hunter = hunters[0]
        output = "%s of <b>%s</b> is currently out hunting!<br/>Monster: %s" % (hunter["name"], settlement["name"], settlement["current_quarry"])
    elif len(hunters) >= 2:
        hunter_names = []
        for h in hunters:
            hunter_names.append(h["name"])
        output = ", ".join(hunter_names[:-1])
        output += " and %s of <b>%s</b>" % (hunter_names[-1], settlement["name"])
        output += " are currently out hunting!<br/>Monster: %s" % (settlement["current_quarry"])

    return output


def api_monster_to_html(m):
    """ Generic method for returning simple HTML of a monst. The monster's level
    and 'comment' keys are sometimes absent from mdb.killboard documents, so we
    handle for that. """

    if m is None:
        return "<p>No data available.</p>"

    monster = m["value"]

    comment = ""
    if "comment" in monster.keys():
        comment = monster["comment"]

    output = "<li><b>%s</b> %s</li>" % (monster["name"], comment)

    if "level" in monster.keys():
        output += "<li>Level: %s</li>" % monster["level"]

    output += "<li>Defeated by the survivors of <b>%s</b></li><li>Killed in LY %s on %s at %s (UTC).</li>" % (
        monster["settlement_name"],
        monster["kill_ly"],
        datetime.fromtimestamp(monster["created_on"]["$date"]/1000).strftime(ymd),
        datetime.fromtimestamp(monster["created_on"]["$date"]/1000).strftime("%H:%M:%S"),
    )

    return output


def api_settlement_to_html(s):
    """ Used for the 'latest_settlement' results. If we can think of some other
    context in which we want to represent a settlement...maybe latest nemesis
    kill or something, this could work for that as well. """

    if s is None:
        return "<p>No data available.</p>"

    settlement = s["value"]

    output = '<ul title="%s"><li><b>%s</b></li>' % (s["comment"], settlement["name"])
    output += "<li><i>%s</i></li>" % settlement["campaign"]
    output += "<li>Expansions: %s</li>" % settlement["expansions"]
    output += "<li>Players: %s</li>" % settlement["player_count"]
    output += "<li>Created on: %s</li>" % datetime.fromtimestamp(settlement["created_on"]["$date"]/1000).strftime(ymd)
    output += "<li>Population: %s</li>" % settlement["population"]
    output += "</ul>"

    return output

#
#   -fin
#


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-q", dest="query", help="Query a specific world value", default=False, metavar="avg_courage")
    (options, args) = parser.parse_args()

    w = api_world()

    if options.query:
        print w["world"][options.query]
    else:
        print json.dumps(w, indent=4)

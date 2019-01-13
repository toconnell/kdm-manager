#!/usr/bin/python2.7

# standard
from bson import json_util
from bson.objectid import ObjectId
from copy import copy
from datetime import datetime, timedelta
import json
import os
import sys

# project
import utils
from models import users, settlements

logger = utils.get_logger(log_name="server")

def get_settlement_data():
    """ Returns JSON about recently updated settlements. Also serializes those
    settlements and gets their event_log. """

    recent_cutoff = datetime.now() - timedelta(hours=utils.settings.get("application","recent_user_horizon"))

    ids = utils.mdb.settlements.find({'last_accessed': {'$gte': recent_cutoff}}).distinct('_id')

    sorting_hat = {}
    for s_id in ids:
        last_updated = utils.mdb.settlement_events.find({'settlement_id': s_id}).limit(1).sort("created_on",-1)[0]['created_on']
        sorting_hat[last_updated] = s_id

    sorted_ids = []
    for timestamp in sorted(sorting_hat.keys(), reverse=True):
        sorted_ids.append(sorting_hat[timestamp])

    recent_settlements = []
    for s in utils.mdb.settlements.find({"_id": {"$in": sorted_ids}}):
        s['creator_email'] = utils.mdb.users.find_one({'_id': s['created_by']})['login']
        s['age'] = utils.get_time_elapsed_since(s['created_on'], 'age')
        s['players'] = utils.mdb.survivors.find({"settlement": s['_id']}).distinct('email')
        recent_settlements.append(s)

    return json.dumps(recent_settlements, default=json_util.default)



def get_user_data():
    """ Returns JSON about active and recently active users, as well as info
    about user agents, etc. """

    # first, do the user agent popularity contest, since that's simple
    results = utils.mdb.users.group(
        ['latest_user_agent'],
        {'latest_user_agent': {'$exists': True}},
        {"count": 0},
        "function(o, p){p.count++}"
    )
    sorted_list = sorted(results, key=lambda k: k["count"], reverse=True)
    for i in sorted_list:
        i["value"] = i['latest_user_agent']
        i["count"] = int(i["count"])
    ua_data = sorted_list[:25]


    # next, get active/recent users
    recent_user_cutoff = datetime.now() - timedelta(hours=utils.settings.get("application","recent_user_horizon"))
    recent_users = utils.mdb.users.find(
        {"latest_activity": {"$gte": recent_user_cutoff}}
    ).sort("latest_activity", -1)

    active_user_count = 0
    recent_user_count = 0
    final_user_output = []
    for u in recent_users:
        u['age'] = utils.get_time_elapsed_since(u['created_on'], 'age')
        u['latest_activity_age'] = utils.get_time_elapsed_since(u['latest_activity'], 'age')
        if u["latest_activity"] > (datetime.now() - timedelta(minutes=utils.settings.get('application','active_user_horizon'))):
            active_user_count += 1
            u['is_active'] = True
        else:
            recent_user_count += 1
            u['is_active'] = False
        final_user_output.append(u)

    # create the final output dictionary
    d = {
        "meta": {
            "active_user_horizon": utils.settings.get("application","active_user_horizon"),
            "active_user_count": active_user_count,
            "recent_user_horizon": utils.settings.get("application","recent_user_horizon"),
            "recent_user_count": recent_user_count,
        },
        "user_agent_stats": ua_data,
        "user_info": final_user_output,
    }
    # and return it as json
    return json.dumps(d, default=json_util.default)


def serialize_system_logs():
    """ Returns JSON represent application/system log output. """

    d = {}

    log_root = utils.settings.get("application","log_root_dir")

    for l in ["world","api","server","world_daemon","gunicorn"]:
        log_file_name = os.path.join(log_root, "%s.log" % l)
        if os.path.isfile(log_file_name):
            fh = file(log_file_name, "r")
            log_lines = fh.readlines()
            log_limit = utils.settings.get("application","log_summary_length")
            d[l] = [line for line in reversed(log_lines[-log_limit:])]
        else:
            d[l] = ["'%s' does not exist!" % log_file_name]


    return json.dumps(d, default=json_util.default)



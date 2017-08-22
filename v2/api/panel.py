#!/usr/bin/python2.7

# standard
from bson import json_util
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import json
import os
import settings
import sys

# project
import utils
from models import users

logger = utils.get_logger(log_name="server")

def active_users():
    """ Returns a bit of JSON about active and recently active users. """

    active_users = utils.mdb.users.find(
        {"latest_activity": {"$gte": utils.active_user_cutoff}}
    ).sort("latest_activity")

    enhanced_user_info = []
    for u in active_users:
        U = users.User(_id=u["_id"])
        u["age_days"] = U.get_age('days')
        u["age_years"] = U.get_age('years')
        u["has_session"] = U.has_session()
        u["is_active"] = U.is_active()
        u["friend_count"] = U.get_friends(int)
        u["friend_list"] = U.get_friends(list)
        u["current_session"] = utils.mdb.sessions.find_one({"_id": u["current_session"]})
        enhanced_user_info.append(u)

    d = {
        "meta": {
            "active_user_cutoff": utils.active_user_cutoff,
            "active_user_count": active_users.count(),
        },
        "users": enhanced_user_info,
    }


    return json.dumps(d, default=json_util.default)


def serialize_system_logs():
    """ Returns JSON represent application/system log output. """

    d = {}

    log_root = settings.get("application","log_root_dir")

    for l in ["world","api","server","world_daemon"]:
        log_file_name = os.path.join(log_root, "%s.log" % l)
        fh = file(log_file_name, "r")
        log_lines = fh.readlines()
        log_limit = settings.get("application","log_summary_length")
        d[l] = [line for line in reversed(log_lines[-log_limit:])]


    return json.dumps(d, default=json_util.default)

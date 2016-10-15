#!/usr/bin/python2.7

# general imports

# local imports
import utils

models = {
    "dead_survivors": {
        "name": "Dead survivors",
        "max_age": 5,
        "comment": "worldwide count of all dead survivors",
    },
    "live_survivors": {
        "max_age": 5,
        "name": "Live survivors",
        "comment": "worldwide count of all living survivors",
    },
    "total_survivors": {
        "name": "Total survivors",
        "comment": "worldwide count of all survivors, living and dead",
    },
    "abandoned_settlements": {
        "name": "Abandoned settlements",
        "comment": "worldwide count of all abandoned and removed settlements",
    },
    "active_settlements": {
        "name": "Active settlements",
        "comment": "worldwide count of all settlements that have not been abandoned or removed"
    },
    "total_users": {
        "name": "Total users",
        "comment": "total of all registered users"
    },
    "total_users_last_30": {
        "max_age": 60,
        "name": "Total users in the last 30 days",
        "comment": "total of all users who have signed in during the last 30 days"
    },
    "new_settlements_last_30": {
        "name": "Total settlements created in the last 30 days",
        "comment": "total of all settlements with a 'created_on' date within the last 30 days"
    },
    "recent_sessions": {
        "max_age": 30,
        "name": "Recent sessions",
        "comment": "total of all sessions within the 'recent_session' horizon"
    },
}

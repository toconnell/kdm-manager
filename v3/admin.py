"""

    Totally deprecated in v4. This goes away completely when we 86 login.py
    and the rest of the legacy webapp's login/authentication scaffolding.

"""


from bson.objectid import ObjectId
from bson.son import SON
from datetime import datetime, timedelta
import gridfs
from hashlib import md5
import operator
from optparse import OptionParser
import os
import cPickle as pickle
import pymongo
import socket
import time
from werkzeug.security import safe_str_cmp, check_password_hash

import api
import assets
import html
import session
import utils
from utils import (
    email,
    mdb,
    get_logger,
    get_user_agent,
    load_settings,
    ymdhms,
    hms,
    days_hours_minutes,
    ymd,
    admin_session,
    thirty_days_ago,
    get_latest_change_log
)

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


logger = get_logger()
settings = load_settings()

#
#   Maintenance and administrative functions
#

@utils.deprecated
def get_response_times():
    """ Hits the MDB with an aggregate query re: response times. """
    return mdb.response_times.aggregate([
        {"$group": {
                "_id": "$view",
                "avg_time": { "$avg": "$time" },
                "max_time": { "$max": "$time" },
                "count": {"$sum": 1 },
            },
        },
        {"$sort": SON([("_id", 1)])},
    ])


def prune_sessions():
    """ Removes sessions older than 24 hours. """
    yesterday = datetime.now() - timedelta(days=1)
#    logger.debug("Searching for sessions older than %s to prune..." % yesterday)
    old_sessions = mdb.sessions.find({"created_on": {"$lt": yesterday}}).sort("created_on")
#    logger.debug("%s sessions found." % old_sessions.count())

    pruned_sessions = 0
    preserved_sessions = 0
    for s in old_sessions:

        # set some user and session details
        user = mdb.users.find_one({"login": s["login"]})
        preserve = user['preferences'].get('preserve_sessions', False)
        session_age = datetime.now() - s['created_on']

#        logger.debug("preserve_sessions: %s; session age: %s days" % (preserve, session_age.days))

        # now preserve or prune
        if user.get('admin', False):
            preserved_sessions += 1
        elif preserve and session_age.days < 30:
            preserved_sessions += 1
        else:
            s_id = s["_id"]
#            logger.debug("Pruning old session '%s' (%s; age: %s)." % (s_id, s["login"], session_age.days))
            remove_session(s_id, "admin")
            pruned_sessions += 1

    if pruned_sessions > 0:
        logger.info("Pruned %s old sessions." % pruned_sessions)
    if preserved_sessions > 0:
        logger.info("Preserved %s sessions due to user preference." % preserved_sessions)

#
#   administrative helper functions for user-land
#

def authenticate(login, password):
    """ Tries to authenticate a user and log him in. Returns None if the user's
    login cannot be found. Returns False if he enters a bad password.

    Logs him in and returns True, otherwise. The session gets created later.

    email addresses are always normalized using .lower()
    """

    user = mdb.users.find_one({"login": login})

    if user is None:
        logger.error("User login '%s' not found in MDB!" % login)
        return None

    authenticated = False

    if safe_str_cmp(md5(password).hexdigest(), user["password"]):   # legacy
        authenticated = True
    elif check_password_hash(user["password"], password):   # werkzeug
        authenticated = True

    if authenticated:
        user["latest_sign_in"] = datetime.now()
        mdb.users.save(user)
        prune_sessions()
    else:
        logger.warn("User '%s' FAILED to authenticate successfully." % login)

    return authenticated


def remove_session(session_id, login):
    """ If you have a session_id (as a string or an ObjectId) and a login, you
    can remove a session from anywhere. """

    s = ObjectId(session_id)
    mdb.sessions.remove({"_id": s})
    logger.debug("User '%s' removed session '%s' successfully." % (login, session_id))



#
#   Interactive CLI admin stuff; not to be used in user-land
#



@utils.deprecated
def ls_documents(collection, sort_on="created_on"):
    """ Dumps a list- or ls-style rendering of a collection's contents. """

    if collection == "users":
        sort_on = "latest_activity"

    if collection == "response_times":
        print("\n\t  View\t\t    Avg. response time\t    Max response time\n")
        for a in get_response_times():
            print "\t%s\t\t%s\t\t%s" % (a["_id"],a["avg_time"],a["max_time"])
        print("")
        return True

    for d in mdb[collection].find().sort(sort_on):
        output = " "
        if sort_on in d.keys():
            output += d[sort_on].strftime("%Y-%m-%d %H:%M:%S")
            output += " "
        output += str(d["_id"])
        output += " - "
        if collection == "users" or collection == "sessions":
            output += d["login"]
        elif collection == "settlement_events":
            creator = assets.User(user_id=d["created_by"], session_object={"_id": 0})
            output += creator.user["login"]
        else:
            output += d["name"]
            try:
                output += " <%s> " % mdb.users.find_one({"_id": d["created_by"]})["login"]
            except TypeError:
                output += " <USER NOT FOUND> "
        try:
            output += " (%s)" % d["created_on"]
        except Exception as e:
            print d
            raise
        print output



@utils.deprecated
def dump_document(collection, doc_id):
    """ Prints an object to stdout in a semi-pretty way, e.g. for review or
    analysis, etc. """

    key_length = 31
    document = mdb[collection].find_one({"_id": ObjectId(doc_id)})
    print("")
    for a in sorted(document.keys()):
#        print(" %s%s%s%s %s" % (a, " " * (key_length - len(a)), document[a], " " * (key_length - len(str(document[a]))), type(document[a])))
        print(" %s%s%s%s|%s|" % (a, " "*(key_length - len(a)), type(document[a]), " "*(key_length+7 - len(str(type(document[a])))), document[a]))
    print("")


@utils.deprecated
def export_data(u_id):
    """ Writes a pickle of the user and his assets. """
    U = assets.User(user_id=u_id, session_object=admin_session)
    filename = "%s.%s.admin_export.pickle" % (datetime.now().strftime(ymd), U.user["login"])
    fh = file(filename, "w")
    fh.write(U.dump_assets("pickle"))
    fh.close()
    print("Export successful!\n -> %s" % filename)


@utils.deprecated
def import_data(data_pickle_path, force=False):
    """ Takes a pickle of User and asset data and imports it into the local MDB.
    This will absolutely overwrite/clobber any documents whose _id values match
    those in the pickled data. YHBW. """

    try:
        data = pickle.loads(data_pickle_path)
    except:
        if not os.path.isfile(data_pickle_path):
            raise Exception("Path '%s' looks bogus!" % data_pickle_path)
        else:
            data = pickle.load(file(data_pickle_path, "rb"))

    print("\n Importing user %s (%s)" % (data["user"]["login"], data["user"]["_id"]))
    if "current_session" in data["user"].keys():
        del data["user"]["current_session"]
    try:
        mdb.users.save(data["user"])
    except pymongo.errors.DuplicateKeyError:
        print(" User login '%s' exists under a different user ID!\n Cannot import user data in %s.\n Exiting...\n" % (data["user"]["login"], data_pickle_path))
        sys.exit(255)

    def import_assets(asset_name):
        """ Helper function to import assets generically.

        The 'asset_name' arg should be something like "settlement_events" or
        "survivors" or "settlements", i.e. one of the keys in the incoming
        'assets_dict' dictionary (called 'data' here). """

        imported_assets = 0
        print(" Importing %s assets..." % asset_name)
        for asset in data[asset_name]:
            imported_assets += 1
            mdb[asset_name].save(asset)
        print(" %s %s assets imported." % (imported_assets, asset_name))

    import_assets("settlements")
    import_assets("settlement_events")
    import_assets("survivors")

    # sanity check survivor imports here
    for s in mdb.survivors.find():
        if mdb.settlements.find_one({"_id": s["settlement"]}) is None:
            print(" Survivor %s belongs to a non-existent settlement (%s).\n  Removing survivor %s from mdb..." % (s["_id"], s["settlement"], s["_id"]))
            mdb.survivors.remove({"_id": s["_id"]})

    # import avatars here
    imported_avatars = 0
    for avatar in data["avatars"]:
        if gridfs.GridFS(mdb).exists(avatar["_id"]):
            gridfs.GridFS(mdb).delete(avatar["_id"])
            print("  Removed object %s from local GridFS." % avatar["_id"])
        gridfs.GridFS(mdb).put(avatar["blob"], _id=avatar["_id"], content_type=avatar["content_type"], created_by=avatar["created_by"], created_on=avatar["created_on"])
        imported_avatars += 1
    print(" Imported %s avatars!" % imported_avatars)

    mdb.sessions.remove({"login": data["user"]["login"]})
    print(" Removed session(s) belonging to incoming user.")

    if force:
        manual_approve = "YES"
    else:
        manual_approve = raw_input(' Reset password for %s? Type "YES" to reset: ' % data["user"]["login"])

    if manual_approve == "YES":
        U = assets.User(user_id=data["user"]["_id"], session_object=admin_session)
        U.update_password("password")
        print(" Updated password to 'password'. ")
    else:
        print(" Password has NOT been reset.")

    print(" Import complete!")

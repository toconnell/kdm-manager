#!/usr/bin/env python

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
from validate_email import validate_email
from werkzeug.security import safe_str_cmp

import api
import assets
import html
import session
from utils import email, mdb, get_logger, get_user_agent, load_settings, ymdhms, hms, days_hours_minutes, ymd, admin_session, thirty_days_ago, get_latest_change_log
import world

import sys
reload(sys)
sys.setdefaultencoding("utf-8")


logger = get_logger()
settings = load_settings()

#
#   Maintenance and administrative functions
#

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
    logger.debug("Searching for sessions older than %s to prune..." % yesterday)
    old_sessions = mdb.sessions.find({"created_on": {"$lt": yesterday}}).sort("created_on")
    logger.debug("%s sessions found." % old_sessions.count())

    pruned_sessions = 0
    preserved_sessions = 0
    for s in old_sessions:
        user = mdb.users.find_one({"login": s["login"]})
        U = assets.User(user["_id"], session_object=admin_session)
        if U.is_admin():
#            logger.debug("Preserving session for admin user '%s'" % user["login"])
            preserved_sessions += 1
        elif U.get_preference("preserve_sessions") and s["created_on"] > thirty_days_ago:   # if it's older than 30 days, ignore the preference
#            logger.debug("Preserving session for user '%s' because of user preference." % user["login"])
            preserved_sessions += 1
        else:
            s_id = s["_id"]
            logger.debug("Pruning old session '%s' (%s)" % (s_id, s["login"]))
            remove_session(s_id, "admin")
            pruned_sessions += 1

    if pruned_sessions > 0:
        logger.info("Pruned %s old sessions." % pruned_sessions)
    if preserved_sessions > 0:
        logger.info("Preserved %s sessions due to user preference." % preserved_sessions)

#
#   administrative helper functions for user-land
#

def create_new_user(login, password, password_again, params):
    """ Creates a new user. Returns False if the passwords don't match;
    returns None if the email address is bogus. Returns True and logs a user in
    if we create a new user successfully. """

    login = login.lower()   # normalize email address on creation

    if password != password_again:
        logger.error("New user creation failed! %s %s %s" % (login, password, password_again))
        return False
    else:
        logger.debug("Creating user '%s' from %s" % (login, get_user_agent()))

        # email validation
        if settings.getboolean("application", "validate_email"):
            validated = validate_email(login, verify=True)
            if validated is None:
                logger.critical("Unable to validate email address '%s'." % login)
                logger.error(validated)
                return None
        else:
            logger.debug("Skipping email validation...")

        prefs = {}
        if "keep_me_logged_in" in params:
            prefs = {"preserve_sessions": True}

        # create the user and update mdb
        user_dict = {
            "created_on": datetime.now(),
            "login": login,
            "password": md5(password).hexdigest(),
            "preferences": prefs,
        }
        try:
            mdb.users.insert(user_dict)
        except Exception as e:
            logger.error("An error occurred while registering a new user!")
            logger.exception(e)
            return False
        mdb.users.create_index("login", unique=True)
        logger.info("New user '%s' created successfully!" % login)
        return True



def authenticate(login, password):
    """ Tries to authenticate a user and log him in. Returns None if the user's
    login cannot be found. Returns False if he enters a bad password.

    Logs him in and returns True, otherwise. The session gets created later.

    email addresses are always normalized using .lower()
    """

    user = mdb.users.find_one({"login": login})

    if user is None:
        return None

    if safe_str_cmp(md5(password).hexdigest(), user["password"]):
        user["latest_sign_in"] = datetime.now()
        mdb.users.save(user)
        logger.debug("User '%s' authenticated successfully (%s)." % (login, get_user_agent()))
        prune_sessions()
        return True
    else:
        logger.debug("User '%s' FAILED to authenticate successfully." % login)
        return False


def remove_session(session_id, login):
    """ If you have a session_id (as a string or an ObjectId) and a login, you
    can remove a session from anywhere. """

    s = ObjectId(session_id)
    mdb.sessions.remove({"_id": s})
    logger.debug("User '%s' removed session '%s' successfully." % (login, session_id))



#
#   Interactive CLI admin stuff; not to be used in user-land
#



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


def rm_collection(collection):
    """ Drops an entire collection from mdb. Serious business. """

    mdb[collection].remove()


def random_doc(collection):
    return dir(mdb[collection])
#    return mdb[collection].random_one()


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


def update_survivor(operation, s_id=None, attrib=False, attrib_value=False, survivor_key=False):
    """ """
    print("Searching for survivor _id '%s'..." % s_id)
    survivor = mdb.survivors.find_one({"_id": ObjectId(s_id)})
    if survivor is None:
        print("Could not retrieve survivor! Exiting...\n")
        return None

    print("\n\tSurvivor found!\n")
    dump_document("survivors", survivor["_id"])

    # attribute updates

    if operation in ["add","remove"]:
        print(" Target attrib is '%s'" % attrib)
        print(" survivor['%s'] -> %s" % (attrib, survivor[attrib]))
        print(" Tarvet value is '%s'" % attrib_value)

    if operation == "add":
        survivor[attrib] = attrib_value
        print(" survivor['%s'] = %s" % (attrib, attrib_value))

    if operation == "remove":
        if attrib_value not in survivor[attrib]:
            print(" Target value '%s' not in attribute! Exiting...\n" % attrib_value)
            return None
        else:
            manual_approve = raw_input("\n    Remove '%s' from %s?\n\tType YES to proceed: " % (attrib_value, survivor[attrib]))
            if manual_approve == "YES":
                survivor[attrib].remove(attrib_value)
                mdb.survivors.save(survivor)
            else:
                print("    Aborting...\n")
                return False


    # key updates

    if operation == "del":
        if survivor_key not in survivor.keys():
            print("Key '%s' not found!\n" % survivor_key)
            return None
        else:
            del(survivor[survivor_key])
            print("Key '%s' deleted!\n" % survivor_key)
            mdb.survivors.save(survivor)


    print("\n  Survivor updated successfully!\n")


def remove_document(collection, doc_id):
    """ Removes a single document (by _id) from the specified collection."""

    doc_id = ObjectId(doc_id)
    if collection == "settlements":
        settlement = mdb.settlements.find_one({"_id": doc_id})
        survivors = mdb.survivors.find({"settlement": doc_id})
        death_count = 0
        for s in survivors:
            mdb.survivors.remove({"_id": s["_id"]})
            death_count += 1
        logger.info("[ADMIN] Removed %s survivors." % death_count)
    mdb[collection].remove({"_id": doc_id})
    logger.info("[ADMIN] Removed '%s' from mdb.%s" % (doc_id, collection))


def pretty_view_user(u_id):
    """ Prints a pretty summary of the user and his assets to STDOUT. """

    User = assets.User(u_id, session_object=admin_session)

    if User.user is None:
        print("Could not retrieve user info from mdb.")
        return None

    print("\n\tUser Summary!\n\n _id: %s\n login: %s\n created: %s\n" % (User.user["_id"], User.user["login"], User.user["created_on"]))
    for u_key in sorted(User.user.keys()):
        if u_key not in ["_id", "login", "created_on", "activity_log"]:
            print(" %s: %s" % (u_key, User.user[u_key]))
    print("")


    def asset_repr(a, type=False):
        if type == "settlement":
            return " %s - %s - LY: %s (%s/%s)" % (a["_id"], a["name"], a["lantern_year"], a["population"], a["death_count"])
        if type == "survivor":
            return " %s - %s [%s] %s" % (a["_id"], a["name"], a["sex"], a["email"])

    if User.settlements == []:
        print(" No settlements.\n")
    else:
        print("\t%s settlements:\n" % len(User.settlements))
        for settlement in User.settlements:
            print asset_repr(settlement, "settlement")
            settlement_survivors = mdb.survivors.find({"settlement": settlement["_id"]})
            if settlement_survivors.count() > 0:
                for survivor in settlement_survivors:
                    print("  %s" % asset_repr(survivor, "survivor"))
            else:
                print("  -> No survivors in mdb.")
            print("")

    if User.get_survivors() is None:
        print(" No survivors.\n")
    else:
        print("\t%s survivors:\n" % len(User.get_survivors()))
        for survivor in User.get_survivors():
            print asset_repr(survivor, "survivor")
    print("")

    if "activity_log" in User.user.keys():
        print(" Last 10 Actions:")
        for entry in User.user["activity_log"]:
            dt, action = entry
            print("   %s | %s" % (dt.strftime(ymdhms), action))
    print("")


def initialize():
    """ Completely initializes the application. Scorched earth. """
    avatars = 0
    for survivor in mdb.survivors.find():
        if "avatar" in survivor.keys():
            gridfs.GridFS(mdb).delete(survivor["avatar"])
            avatars += 1
    print("\nRemoved %s avatars from GridFS!" % avatars)
    for collection in ["users", "sessions", "survivors", "settlements", "the_dead", "user_admin"]:
        mdb[collection].remove()


def toggle_admin_status(user_id):
    """ Makes a user an admin or, if they're already an admin, strips them of
    the attribute. """
    u_id = ObjectId(user_id)
    user = mdb.users.find_one({"_id": u_id})
    login = user["login"]
    if "admin" in user.keys():
        del user["admin"]
        print("Admin permission removed from '%s'." % login)
    else:
        user["admin"] = datetime.now()
        print("Admin permission added for '%s'." % login)
    mdb.users.save(user)


def update_user_password(user_id, password):
    u_id = ObjectId(user_id)
    User = assets.User(user_id=u_id)
    User.update_password(password)


def motd():
    """ Creates a CLI MoTD. """
    users = mdb.users.find()
    sessions = mdb.sessions.find()
    settlements = mdb.settlements.find()
    survivors = mdb.survivors.find()

    print("\n %s users (%s sessions)\n %s settlements\n %s survivors" % (users.count(), sessions.count(), settlements.count(), survivors.count()))

    recent_user_agents = {}
    for u in users:
        if "latest_user_agent" in u.keys():
            ua = u["latest_user_agent"].split("/")[1]
        else:
            ua = "UNKNOWN"
        if ua not in recent_user_agents.keys():
            recent_user_agents[ua] = 1
        else:
            recent_user_agents[ua] += 1
    print("\n Recent user OS round-up (top 5):")
    sorted_ua_dict = sorted(recent_user_agents.items(), key=operator.itemgetter(1), reverse=True)
    for ua in sorted_ua_dict[:6]:
        ua_string, ua_count = ua
        if ua_string != "UNKNOWN":
            print("   %s --> %s" % (ua_string, ua_count))
    print("")


def play_summary():
    """ Summarizes play sessions. """

    print("\n\t\tRecent Activity:\n")
    users = mdb.users.find({"latest_sign_in": {"$exists": True}, "latest_activity": {"$exists": True}}).sort("latest_activity", -1)
    for u in users[:5]:
        output = " "
        output += "%s - %s (%s):\n " % (u["login"], u["_id"], u["latest_user_agent"])
        duration = u["latest_activity"] - u["latest_sign_in"]
        dur_minutes = duration // 60
        output += "    %s - %s (%s)\n" % (u["latest_sign_in"].strftime(ymdhms), u["latest_activity"].strftime(ymdhms), dur_minutes)
        output += "     Latest Action: '%s' (%s minutes ago)\n" % (u["latest_action"], (datetime.now() - u["latest_activity"]).seconds // 60)
        print(output)


def tail(settlement_id, interval=5, last=20):
    settlement = mdb.settlements.find_one({"_id": ObjectId(settlement_id)})
    if settlement is None:
        print("\n\tSettlement '%s' does not exist. Exiting...\n" % settlement_id)
        sys.exit(255)

    try:
        while True:
            print(chr(27) + "[2J")
            log_lines = mdb.settlement_events.find({"settlement_id": settlement["_id"]}).sort("created_on",-1).limit(last)
            for l in reversed(list(log_lines)):
                creator = mdb.users.find_one({"_id": l["created_by"]})
                print "  [%s] %s (LY:%s) - %s" % (l["created_on"].strftime(ymdhms), creator["login"], l["ly"], l["event"])
            print("\nTailing settlement '%s' (%s)..." % (settlement["name"], settlement["_id"]))
            time.sleep(interval)
    except KeyboardInterrupt:
        print("")
        sys.exit(1)


def render_about_panel():
    """ Random method to render the HTML for the Dashboard "about" panel. """
    lcl = ""
    lcd = "ERROR"
    try:
        log = get_latest_change_log()
        lcl = log["url"]
        lcd = log["published"]
    except:
        self.logger.exception("An error occurred while trying to retrieve blog info!")

    output = html.dashboard.about.safe_substitute(
        version = settings.get("application","version"),
        latest_change_date = lcd,
        latest_change_link = lcl,
    )
    return output

    #
    #   Admin Panel!
    #

class Panel:
    def __init__(self, admin_login):
        self.admin_login = admin_login
        self.Session = session.Session()
        self.logger = get_logger()
        self.recent_users = self.get_recent_users()

    def get_recent_users(self):
        """ Gets users from mdb who have done stuff within our time horizon for
        'recent' sessions and returns them. """
        hours_ago = settings.getint("application", "session_horizon")
        recent_cut_off = datetime.now() - timedelta(hours=hours_ago)
        return mdb.users.find({"latest_activity": {"$gte": recent_cut_off}, "login": {"$ne": self.admin_login}}).sort("latest_activity", -1)

    def get_last_n_log_lines(self, lines):
        log_path = os.path.join(settings.get("application", "log_dir"), "index.log")
        index_log = file(log_path, "r")
        return index_log.readlines()[-lines:]

    def render_html(self):
        """ Renders the whole panel. """

        try:
            World = api.route_to_dict("world")
            W = World["world"]
        except Exception as e:
            return "World could not be loaded! %s" % e

        daemon_block = '<table id="admin_panel_world_daemon_table">'
        daemon_block += '<tr><th colspan="2">World Daemon</th></tr>'
        for k, v in World["world_daemon"].iteritems():
            if type(v) == dict:
                raw = v["$date"]
                dt = datetime.fromtimestamp(raw/1000)
                daemon_block += '<tr><td>%s</td><td>%s</td></tr>' %  (k,dt)
            else:
                daemon_block += '<tr><td>%s</td><td>%s</td></tr>' % (k,v)
        daemon_block += "</table>"

        response_block = '<table class="admin_panel_response_block">'
        response_block += '<tr><th colspan="4">Response Times</th></tr>'
        response_block += '<tr><th>View</th><th>#</th><th>Avg.</th><th>Max</th></tr>'
        for r in get_response_times():
            response_block += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (r["_id"],r["count"],r["avg_time"],r["max_time"])
        response_block += "</table>"

        output = html.panel.headline.safe_substitute(
            version = settings.get("application","version"),
            api_url = api.get_api_url(),
            hostname = socket.getfqdn(),
            response_times = response_block,
            world_daemon = daemon_block,
            killboard = world.api_killboard_to_html(W["killboard"]),
            recent_users_count = self.recent_users.count(),
            users = W["total_users"]["value"],
            sessions = mdb.sessions.find().count(),
            settlements = mdb.settlements.find().count(),
            total_survivors = W["total_survivors"]["value"],
            live_survivors = W["live_survivors"]["value"],
            dead_survivors = W["dead_survivors"]["value"],
            complete_death_records = mdb.the_dead.find({"complete": {"$exists": True}}).count(),
            latest_fatality = world.api_survivor_to_html(W["latest_fatality"]),
            latest_settlement = world.api_settlement_to_html(W["latest_settlement"]),
            latest_kill = world.api_monster_to_html(W["latest_kill"]),
            current_hunt = world.api_current_hunt(W["current_hunt"]),
        )


        for user in self.recent_users:
            User = assets.User(user_id=user["_id"], session_object=self.Session)

            # create settlement summaries
            settlements = mdb.settlements.find({"created_by": User.user["_id"]}).sort("name")
            settlement_strings = []
            for s in settlements:
                S = assets.Settlement(settlement_id=s["_id"], session_object=self.Session, update_mins=False)
                settlement_strings.append(S.render_admin_panel_html())

            output += html.panel.user_status_summary.safe_substitute(
                user_name = User.user["login"],
                u_id = User.user["_id"],
                ua = User.user["latest_user_agent"],
                latest_sign_in = User.user["latest_sign_in"].strftime(ymdhms),
                latest_sign_in_mins = (datetime.now() - User.user["latest_sign_in"]).seconds // 60,
                session_length = (User.user["latest_activity"] - User.user["latest_sign_in"]).seconds // 60,
                latest_activity = User.user["latest_activity"].strftime(ymdhms),
                latest_activity_mins = (datetime.now() - User.user["latest_activity"]).seconds // 60,
                latest_action = User.user["latest_action"],
                settlements = "<br/>".join(settlement_strings),
                survivor_count = mdb.survivors.find({"created_by": User.user["_id"]}).count(),
                user_created_on = User.user["created_on"].strftime(ymd),
                user_created_on_days = (datetime.now() - User.user["created_on"]).days
            )

        output += "<hr/><h1>index.log</h1>"

        log_lines = self.get_last_n_log_lines(50)
        zebra = False
        for l in reversed(log_lines):
            if zebra:
                output += html.panel.log_line.safe_substitute(line=l, zebra=zebra)
                zebra = False
            else:
                output += html.panel.log_line.safe_substitute(line=l)
                zebra = "grey"

        return output


def dashboard_alert():
    """ Renders a fixed element on the dashboard if we're alerting the users
    about something. """

    if settings.get("application", "dashboard_alert") == "None":
        return ""
    else:
        return html.meta.dashboard_alert.safe_substitute(msg=settings.get("application", "dashboard_alert"))


def export_data(u_id):
    """ Writes a pickle of the user and his assets. """
    U = assets.User(user_id=u_id, session_object=admin_session)
    filename = "%s.%s.admin_export.pickle" % (datetime.now().strftime(ymd), U.user["login"])
    fh = file(filename, "w")
    fh.write(U.dump_assets("pickle"))
    fh.close()
    print("Export successful!\n -> %s" % filename)


def import_data(data_pickle_path):
    """ Takes a pickle of User and asset data and imports it into the local MDB.
    This will absolutely overwrite/clobber any documents whose _id values match
    those in the pickled data. YHBW. """

    if not os.path.isfile(data_pickle_path):
        raise Exception("Path '%s' looks bogus!" % data_pickle_path)
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

    manual_approve = raw_input(' Reset password for %s? Type "YES" to reset: ' % data["user"]["login"])
    if manual_approve == "YES":
        U = assets.User(user_id=data["user"]["_id"], session_object=admin_session)
        U.update_password("password")
        print(" Updated password to 'password'. ")
    else:
        print(" Password has NOT been reset.")

    print(" Import complete!")



if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option("-s", dest="survivor", help="Specify a survivor to work with.", metavar="566e228654922d30c47b8704", default=False)
    parser.add_option("--survivor_attrib", dest="survivor_attrib", help="Specify a survivor attrib to modify.", metavar="attributes_and_impairments", default=False)
    parser.add_option("--add_attrib", dest="add_attrib", help="Add attrib to survivor", metavar="user-specified string", default=False)
    parser.add_option("--remove_attrib", dest="remove_attrib", help="Remove attrib from survivor", metavar="<b>Cancer:</b> No description.", default=False)
    parser.add_option("--remove_key", dest="remove_key", help="Remove key from survivor record", metavar="born_in_ly", default=False)

    parser.add_option("-l", dest="list_documents", help="List documents in a collection", metavar="survivors", default=False)
    parser.add_option("-c", dest="collection", help="Specify a collection to work with", metavar="settlements", default=False)
    parser.add_option("-v", dest="view_document", help="View/dump a document to stdout (requires -c)", metavar="565a1829421aa96b33d1c8bb", default=False)
    parser.add_option("--RANDOM", dest="random_doc", help="Choose a random record from 'collection'", metavar="settlements", default=False, action="store_true")
    parser.add_option("-r", dest="remove_document", help="Remove a single document (requires -c)", metavar="29433d1c8b56581ab21aa96b", default=False)
    parser.add_option("-R", dest="drop_collection", help="Drop all docs in a collection.", metavar="users", default=False)

    parser.add_option("--play_summary", dest="play_summary", help="Summarize play sessions for users.", action="store_true", default=False)

    parser.add_option("-u", dest="user_id", help="Specify a user to work with.", default=False)
    parser.add_option("-p", dest="user_pass", help="Update a user's password (requires -u).", default=False)

    parser.add_option("-e", dest="export_data", help="export data to a pickle. needs a user _id", metavar="5681f9e7421aa93924b6d013", default=False)
    parser.add_option("-i", dest="import_data", help="import data from a pickle", metavar="/home/toconnell/data.pickle", default=False)
    parser.add_option("--user", dest="pretty_view_user", help="Print a pretty summary of a user", metavar="5665026954922d076285bdec", default=False)
    parser.add_option("--tail", dest="tail_settlement", help="tail -f a settlement's log", metavar="5665123bfhas90213bdhs85b123", default=False)
    parser.add_option("--user_repr", dest="user_repr", help="Dump a user's repr", metavar="5665026954922d076285bdec", default=False)
    parser.add_option("--admin", dest="toggle_admin", help="toggle admin status for a user _id", default=False)
    parser.add_option("--email", dest="email", help="Send a test email to an address", metavar="toconnell@tyrannybelle.com", default=False)

    parser.add_option("--initialize", dest="initialize", help="Burn it down.", action="store_true", default=False)
    (options, args) = parser.parse_args()

#    if args == []:
#        motd()

    if options.tail_settlement:
        tail(options.tail_settlement)

    if options.export_data:
        export_data(options.export_data)

    if options.import_data:
        import_data(options.import_data)

    if options.user_repr:
        User = assets.User(user_id=options.user_repr, session_object=admin_session)
        print User.dump_assets()

    if options.user_id and options.user_pass:
        update_user_password(options.user_id, options.user_pass)

    if options.toggle_admin:
        toggle_admin_status(options.toggle_admin)

    if options.initialize:
        print(" hostname: %s" % socket.gethostname())
        if socket.gethostname() not in ["paula.local", "mona"]:
            print("This isn't the dev machine!")
            sys.exit(1)
        manual_approve = raw_input('Initialize the project and remove all data? Type "YES" to proceed: ')
        if manual_approve == "YES":
            initialize()
        print("Project initialized! ALL DATA REMOVED!!\nExiting...\n")

    if options.list_documents:
        ls_documents(options.list_documents)
    if options.drop_collection:
        rm_collection(options.drop_collection)

    if options.collection:
        if options.view_document:
            dump_document(options.collection, options.view_document)
        if options.remove_document:
            remove_document(options.collection, options.remove_document)
        if options.random_doc:
            print random_doc(options.collection)

    if options.pretty_view_user:
        pretty_view_user(options.pretty_view_user)

    if options.survivor:
        if options.survivor_attrib:
            if options.add_attrib:
                update_survivor("add", s_id=options.survivor, attrib=options.survivor_attrib, attrib_value=options.add_attrib)
            if options.remove_attrib:
                update_survivor("remove", s_id=options.survivor, attrib=options.survivor_attrib, attrib_value=options.remove_attrib)
        if options.remove_key:
            update_survivor("del", s_id=options.survivor, survivor_key=options.remove_key)

    if options.email:
        email(recipients=options.email.split(), msg="This is a test message!\nGood!")
        print("Test email sent!")

    if options.play_summary:
        motd()
        play_summary()

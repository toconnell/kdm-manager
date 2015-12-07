#!/usr/bin/env python

from bson.objectid import ObjectId
from datetime import datetime
from hashlib import md5
from optparse import OptionParser
import os
from validate_email import validate_email

import assets
from utils import mdb, get_logger, get_user_agent, load_settings


logger = get_logger()
settings = load_settings()

#
#   administrative helper functions for user-land
#

def create_new_user(login, password, password_again):
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
        if settings.getboolean("users", "validate_email"):
            validated = validate_email(login, verify=True)
            if validated is None:
                logger.critical("Unable to validate email address '%s'." % login)
                logger.error(validated)
                return None
        else:
            logger.debug("Skipping email validation...")

        # create the user and update mdb
        user_dict = {
            "created_on": datetime.now(),
            "login": login,
            "password": md5(password).hexdigest(),
        }
        mdb.users.insert(user_dict)
        mdb.users.create_index("login", unique=True)
        logger.info("New user '%s' created successfully!" % login)
        return True


def authenticate(login, password):
    """ Tries to authenticate a user and log him in. Returns None if the user's
    login cannot be found. Returns False if he enters a bad password.

    Logs him in and creates a session, otherwise.

    email addresses are always normalized using .lower()
    """

    user = mdb.users.find_one({"login": login})

    if user is None:
        return None

    if md5(password).hexdigest() == user["password"]:
        user["latest_sign_in"] = datetime.now()
        mdb.users.save(user)
        logger.debug("User '%s' authenticated successfully." % login)
        return True
    else:
        logger.debug("User '%s' FAILED to authenticate successfully." % login)
        return False


def remove_session(session_id):
    s = ObjectId(session_id)
    mdb.sessions.remove({"_id": s})
    logger.debug("Removed session '%s' successfully." % session_id)


#
#   Interactive CLI admin stuff; not to be used in user-land
#

def ls_documents(collection):
    """ Dumps a list- or ls-style rendering of a collection's contents. """

    for d in mdb[collection].find().sort("created_on"):
        output = " "
        output += str(d["_id"])
        output += " - "
        if collection == "users" or collection == "sessions":
            output += d["login"]
        else:
            output += d["name"]
            output += " <%s> " % mdb.users.find_one({"_id": d["created_by"]})["login"]
        output += " (%s)" % d["created_on"]
        print output


def rm_collection(collection):
    """ Drops an entire collection from mdb. Serious business. """

    mdb[collection].remove()


def dump_document(collection, doc_id):
    """ Prints an object to stdout in a semi-pretty way, e.g. for review or
    analysis, etc. """

    key_length = 31
    document = mdb[collection].find_one({"_id": ObjectId(doc_id)})
    print("")
    for a in sorted(document.keys()):
        print(" %s%s%s" % (a, " " * (key_length - len(a)), document[a]))
    print("")


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

    User = assets.User(u_id)

    if User.user is None:
        print("Could not retrieve user info from mdb.")
        return None

    print("\n\tUser Summary!\n\n _id: %s\n login: %s\n created: %s\n" % (User.user["_id"], User.user["login"], User.user["created_on"]))
    for u_key in sorted(User.user.keys()):
        if u_key not in ["_id", "login", "created_on"]:
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
            for survivor in mdb.survivors.find({"settlement": settlement["_id"]}):
                print "  %s" % asset_repr(survivor, "survivor")
            print("")

    if User.survivors == []:
        print(" No survivors.\n")
    else:
        print("\t%s survivors:\n" % len(User.survivors))
        for survivor in User.survivors:
            print asset_repr(survivor, "survivor")
    print("")

def initialize():
    """ Completely initializes the application. Scorched earth. """
    for collection in ["users", "sessions", "survivors", "settlements"]:
        mdb[collection].remove()



if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-c", dest="collection", help="Specify a collection to work with", metavar="settlements", default=False)

    parser.add_option("-l", dest="list_documents", help="List documents in a collection", metavar="survivors", default=False)
    parser.add_option("-v", dest="view_document", help="View/dump a document to stdout (requires -c)", metavar="565a1829421aa96b33d1c8bb", default=False)
    parser.add_option("-r", dest="remove_document", help="Remove a single document (requires -c)", metavar="29433d1c8b56581ab21aa96b", default=False)
    parser.add_option("-R", dest="drop_collection", help="Drop all docs in a collection.", metavar="users", default=False)

    parser.add_option("--user", dest="pretty_view_user", help="Print a pretty summary of a user", metavar="5665026954922d076285bdec", default=False)
    parser.add_option("--initialize", dest="initialize", help="Burn it down.", action="store_true", default=False)
    (options, args) = parser.parse_args()


    if options.initialize:
        manual_approve = raw_input('Initialize the project and remove all data? Type "YES" to proceed: ')
        if manual_approve == "YES":
            initialize()
        print("Project initialized! ALL DATA REMOVED!!")

    if options.list_documents:
        ls_documents(options.list_documents)
    if options.drop_collection:
        rm_collection(options.drop_collection)

    if options.collection:
        if options.view_document:
            dump_document(options.collection, options.view_document)
        if options.remove_document:
            remove_document(options.collection, options.remove_document)

    if options.pretty_view_user:
        pretty_view_user(options.pretty_view_user)

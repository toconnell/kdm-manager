#!/usr/bin/env python

from bson.objectid import ObjectId
from datetime import datetime
from hashlib import md5
from optparse import OptionParser
import os
from validate_email import validate_email

from utils import mdb, get_logger, get_user_agent


logger = get_logger()

#
#   administrative helper functions for user-land
#

def create_new_user(login, password, password_again):
    """ Creates a new user. Returns False if the passwords don't match;
    returns None if the email address is bogus. Returns True and logs a user in
    if we create a new user successfully. """

    if password != password_again:
        logger.info("creation fail! %s %s %s" % (login, password, password_again))
        return False
    else:
        if not validate_email(login, verify=True):
            return None
        logger.info("Creating user '%s' from %s" % (login, get_user_agent()))
        user_dict = {
            "created_on": datetime.now(),
            "login": login,
            "password": md5(password).hexdigest(),
        }
        mdb.users.insert(user_dict)
        mdb.users.create_index("login", unique=True)
        return "user created"


def authenticate(login, password):
    """ Tries to authenticate a user and log him in. Returns None if the user's
    login cannot be found. Returns False if he enters a bad password.

    Logs him in and creates a session, otherwise. """

    user = mdb.users.find_one({"login": login})

    if user is None:
        return None

    if md5(password).hexdigest() == user["password"]:
        return True
    else:
        logger.info("User '%s' FAILED to authenticate successfully." % login)
        return False



#
#   Interactive CLI admin stuff; not to be used in user-land
#

def ls_documents(collection):
    """ Dumps a list- or ls-style rendering of a collection's contents. """

    for d in mdb[collection].find().sort("created_on"):
        output = " "
        output += str(d["_id"])
        output += " - "
        if collection == "users":
            output += d["login"]
        else:
            output += d["name"]
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



if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-c", dest="collection", help="Specify a collection to work with", metavar="settlements", default=False)

    parser.add_option("-l", dest="list_documents", help="List documents in a collection", metavar="survivors", default=False)
    parser.add_option("-v", dest="view_document", help="View/dump a document to stdout (requires -c)", metavar="565a1829421aa96b33d1c8bb", default=False)
    parser.add_option("-r", dest="remove_document", help="Remove a single document (requires -c)", metavar="29433d1c8b56581ab21aa96b", default=False)
    parser.add_option("-R", dest="drop_collection", help="Drop all docs in a collection.", metavar="users", default=False)
    (options, args) = parser.parse_args()


    if options.list_documents:
        ls_documents(options.list_documents)
    if options.drop_collection:
        rm_collection(options.drop_collection)

    if options.collection:
        if options.view_document:
            dump_document(options.collection, options.view_document)
        if options.remove_document:
            remove_document(options.collection, options.remove_document)

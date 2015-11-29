#!/usr/bin/env python

from bson.objectid import ObjectId
from datetime import datetime
from hashlib import md5
from optparse import OptionParser
import os
from validate_email import validate_email

from utils import mdb, get_logger, get_user_agent


logger = get_logger()


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
#   Interactive CLI admin stuff
#

def ls_documents(collection):
    for d in mdb[collection].find():
        print d

def rm_collection(collection):
    mdb[collection].remove()

def dump_document(collection, doc_id):
    key_length = 31
    document = mdb[collection].find_one({"_id": ObjectId(doc_id)})
    print("")
    for a in document:
        print(" %s%s%s" % (a, " " * (key_length - len(a)), document[a]))
    print("")

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-c", "--collection", dest="collection", help="Specify a collection to work with", metavar="settlements", default=False)

    parser.add_option("-l", "--list", dest="list_documents", help="List documents in a collection", metavar="users", default=False)
    parser.add_option("-v", "--view", dest="view_document", help="View/dump a document to stdout (requires -c)", metavar="565a1829421aa96b33d1c8bb", default=False)
    parser.add_option("-R", "--remove_collection", dest="drop_collection", help="Drop all docs in a collection.", metavar="users", default=False)
    (options, args) = parser.parse_args()

    if options.list_documents:
        ls_documents(options.list_documents)
    if options.drop_collection:
        rm_collection(options.drop_collection)
    if options.collection and options.view_document:
        dump_document(options.collection, options.view_document)

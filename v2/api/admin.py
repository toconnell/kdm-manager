#!/usr/bin/env python

from bson.objectid import ObjectId
from bson import json_util
import json
from optparse import OptionParser
import os
import socket
from string import Template
import sys

from api_config import settings
from user import User


#
#   Misc. helper and convenience functions
#

def input_password(username):
    """ Helper function. Collects a password from STDIN. """
    return raw_input("\n Enter password for '%s': " % username)


def version():
    """ Returns a json object of API config and meta info. """
    d = {
        "version":      settings.get("meta","version"),
        "mdb":          {
            "name":     settings.mdb.name,
        },
        "users":        {
            "total":    settings.mdb.users.find().count(),
        },
        "sessions":     {
            "total":    settings.mdb.sessions.find().count(),
        },
    }
    return json.dumps(d, indent=2, sort_keys=True, default=json_util.default)




#
#   User administration functions
#

def add_user(login, password):
    """ Creates a new user. Returns True if it succeeds, False if it fails and
    None if the user's login already exists. """

    try:
        U = User()
        return U.new(login, password, password_is_hashed=False)
    except Exception as e:
        settings.default_logger.exception(e)
        return False

def auth_test(login, password):
    """ Tests authentication. Mostly for dev/debug purposes. """
    U = User()
    return U.authenticate(login, password, password_is_hashed=False)



#
#   database administration
#

def initialize():
    """ Completely initializes the application. Scorched earth. """
    for collection in ["users"]:
        settings.mdb[collection].remove()
    settings.default_logger.critical("Project initialized by %s" % os.environ["USER"])


def view_document(collection, _id, return_type=None):
    """ Dumps a single document from the specified collection. Returns None if
    the document doesn't exist.

    Returns a mdb object by default, but the 'return_type' kwarg can be used to
    return either 'json' or 'cli' (which is CLI friendly text).
    """

    try:
        _id = ObjectId(_id)
        document = settings.mdb[collection].find_one({"_id": _id})
    except:
        document = settings.mdb[collection].find_one({"login": _id})

    if document is None:
        return None

    if return_type == "json":
        return json.dumps(document, default=json_util.default)
    elif return_type == "cli":
        key_length = 31
        output = "\n"
        for a in sorted(document.keys()):
            t = Template(" $key$key_spacer$value_type$value_type_spacer$value\n")
            output += t.safe_substitute(
                key = a,
                key_spacer = " "*(key_length - len(a)),
                value_type = type(document[a]),
                value_type_spacer = " "*(key_length+7 - len(str(type(document[a])))), 
                value = document[a]
            )
        output += "\n"
        return output
    else:
        return document


def what():
    pass


if __name__ == "__main__":

    parser = OptionParser()

    # project admin
    parser.add_option("--version", dest="version", help="Return a JSON object of config and meta data and then exit.", default=False, action="store_true")
    parser.add_option("--initialize", dest="initialize", help="Removes all mdb collections.", default=False, action="store_true")

    # db admin
    parser.add_option("-c", dest="collection", help="Specify a collection to work with", metavar="settlements")
    parser.add_option("-v", dest="view_document", help="View/dump a document to stdout (requires -c)", metavar="565a1829421aa96b33d1c8bb")

    # user admin
    parser.add_option("--add_user", dest="add_user", help="Interactively create a new user.", metavar="username")
    parser.add_option("--auth_test", dest="auth_user", help="Interactively test credentials.", metavar="username")

    options, args = parser.parse_args()

    if options.version:
        print version()
        sys.exit(1)

    if options.initialize:
        print(" hostname: %s" % socket.gethostname())
        if socket.gethostname() != "paula.local":
            print("This isn't the dev machine!")
            sys.exit(1)
        manual_approve = raw_input('Initialize the project and remove all data? Type "YES" to proceed: ')
        if manual_approve == "YES":
            initialize()
        print("Project initialized! ALL DATA REMOVED!!\nExiting...\n")

    # db admin
    if options.collection:
        if options.view_document:
            print view_document(options.collection, options.view_document, return_type="cli")

    # user admin
    if options.add_user:
        print "  > %s\n" % add_user(options.add_user.strip(), input_password(options.add_user))
    if options.auth_user:
        print "  > %s\n" % auth_test(options.auth_user.strip(), input_password(options.auth_user))



#!/usr/bin/env python

#curl kdm-manager.com/get_user?admin_key=rydlF0jcDaySU123\&u_id=573ad0b8421aa9157ca214eb > 2016i6-12_machine.pickle

from bson.objectid import ObjectId
import cPickle as pickle
import cStringIO
from datetime import datetime, timedelta
from optparse import OptionParser
import admin
import api
import os
import requests
import utils
import socket
import sys
from urlparse import urljoin

settings = utils.load_settings()

def clone_one(prod_url, admin_key, uid, force=False):
    """ Checks the token on the sesh: returns True if it's still good, returns
    False if it's expired/whatever else. """

    print("\n Webapp URL: %s" % prod_url)
    print(" Admin Key:  %s" % admin_key)
    print(" User OID:   %s" % uid)

    # do the web request
    start = datetime.now()
    sys.stderr.write("\n Initiating request...")
    req_url = urljoin(prod_url, "get_user")
    r = requests.get(req_url, params={"admin_key": admin_key, "u_id": uid})
    if r.status_code != 200:
        print(" Request failed!\n Status: %s\n Reason: %s" % (r.status_code, r.reason))
        sys.exit(1)
    stop = datetime.now()
    dur = stop - start
    sys.stderr.write("user data pickle retrieved in %s.%s seconds!\n" % (dur.seconds, dur.microseconds))

    # assuming we're still here, load the data
    admin.import_data(str(r.text).strip(), force)


def clone_many(admin_key):
    """ Gets recent users from the API and clones them down, forcing password
    reset. """

    users = get_user_data_from_api()
    for u in users:
        oid = u['_id']['$oid']
        clone_one(settings.get('application','prod_url'), admin_key, oid, force=True)
        print("\n")

    for u in users:
        print("  %s - %s " % (u['_id']['$oid'], u['login']))
    print("\n")


def get_user_data_from_api():
    start = datetime.now()
    api_url = settings.get("api","prod_url") + "admin/get/user_data"
    print("\n API Endpoint: %s\n Initiating request..." % api_url)
    r = requests.get(api_url)

    print(" Request response: %s %s" % (r.status_code, r.reason))
    stop = datetime.now()
    dur = stop - start
    if r.status_code == 200:
        output = r.json()
        print(" Response in %s.%s seconds.\n %s recent users retrieved.\n" % (dur.seconds, dur.microseconds, len(output['user_info'])))
        return output['user_info']
    else:
        raise Exception(r.reason)


def get_recent():
    """ Gets recent users from the API. """

    for u in get_user_data_from_api():
        active = "inactive"
        if u['is_active']:
            active = "active"
        print("  [%s] %s - %s (SL: %s)" % (active, u['_id']['$oid'], u['login'], u['patron']['level']))

    print("\n")



if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-u", dest="uid", help="OID of the user to clone.", metavar="566e22865492...", default=None)
    parser.add_option("-R", dest="clone_recent_users", help="Clone all recent production users to local.", default=False, action="store_true")
    parser.add_option("--get_recent", dest="get_recent", help="Summarize recent user activity (API).", default=False, action="store_true")
    (options, args) = parser.parse_args()

    # load default params
    S = utils.load_settings("private")
    try:
        admin_key=S.get("admin","admin_key")
    except:
        print("Webapp 'admin_key' not found in '%s'. Exiting..." % S.file_path)
        sys.exit(1)
    prod_url = utils.settings.get("application","prod_url")


    # sanity and pre-flight/user-friendliness checks
    if options.uid is None and get_recent is False and clone_recent_users is False:
        parser.print_help()
        sys.exit(1)

    if options.uid is not None:
        try:
            ObjectId(options.uid)
        except:
            print("User ID '%s' does not appear to be an valid BSON OID! Exiting..." % options.uid)
            sys.exit(1)

        # confirm params and do it
        clone_one(prod_url, admin_key, options.uid)

    if options.get_recent:
        get_recent()

    if options.clone_recent_users:
        local_fqdn = socket.getfqdn()
        if local_fqdn == settings.get('api','prod_fqdn'):
            raise Exception('Cannot clone production data to production!')
        print("\n Local FQDN is '%s'" % local_fqdn)
        clone_many(admin_key)




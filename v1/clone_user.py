#!/usr/bin/env python

#curl kdm-manager.com/get_user?admin_key=rydlF0jcDaySU123\&u_id=573ad0b8421aa9157ca214eb > 2016i6-12_machine.pickle

from bson.objectid import ObjectId
import cPickle as pickle
import cStringIO
from datetime import datetime, timedelta
from optparse import OptionParser
import admin
import os
import requests
import utils
import sys
from urlparse import urljoin

def do_request(prod_url, admin_key, uid):
    """ Checks the token on the sesh: returns True if it's still good, returns
    False if it's expired/whatever else. """

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
    admin.import_data(str(r.text).strip())


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-u", dest="uid", help="OID of the user to clone.", metavar="566e22865492...", default=None)
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
    if options.uid is None:
        parser.print_help()
        sys.exit(1)

    try:
        ObjectId(options.uid)
    except:
        print("User ID '%s' does not appear to be an valid BSON OID! Exiting..." % options.uid)
        sys.exit(1)


    # confirm params and do it
    print("\n Webapp URL: %s" % prod_url)
    print(" Admin Key:  %s" % admin_key)
    print(" User OID:   %s" % options.uid)

    do_request(prod_url, admin_key, options.uid)

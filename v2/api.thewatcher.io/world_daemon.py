#!/usr/bin/python2.7


from optparse import OptionParser
import os
import pwd
import sys

from api import settings, Models
from world import World, WorldDaemon
import utils

if __name__ == "__main__":

    # never ever do anything in this file as root. 
    if os.getuid() == 0:
        sys.stderr.write("The API World Daemon may not be operated as root!\n")
        daemon_user = pwd.getpwnam(settings.get("world","daemon_user"))
        uid = daemon_user.pw_uid
        gid = daemon_user.pw_gid
        sys.stderr.write("Changing UID to %s\n" % (uid))
        try:
            os.setuid(uid)
        except Exception as e:
            sys.stderr.write("Could not set UID!")
            raise

    # optparse
    parser = OptionParser()
    parser.add_option("-l", dest="list", action="store_true", default=False, help="List warehoused asset handles")
    parser.add_option("-j", dest="list_JSON", action="store_true", default=False, help="Dump 'world' JSON")
    parser.add_option("-u", dest="update", default=False, help="Update one asset's warehouse value", metavar="top_principles")
    parser.add_option("-r", dest="refresh", action="store_true", default=False, help="Force a warehouse refresh")
    parser.add_option("-a", dest="asset", default=False, help="Retrieve an mdb world asset (print a summary)", metavar="latest_survivor")
    parser.add_option("-q", dest="query", default=False, help="Execute a query method (print results)", metavar="avg_pop")
    parser.add_option("-R", dest="remove_one", default=None, help="Remove an object _id from the warehouse", metavar="57f010ec4...")
    parser.add_option("-d", dest="daemon_cmd", help="Daemon controls: status|start|stop|restart", default=None, metavar="restart")
    (options, args) = parser.parse_args()

    # process specific/manual world operations first
    W = World()
    if options.remove_one is not None:
        W.remove(options.remove_one)
    if options.refresh:
        W.logger.debug("Beginning forced asset refresh...")
        W.refresh_all_assets(force=True)
    if options.asset:
        print(W.dump(options.asset))
    if options.update:
        W.refresh_asset(asset_key=options.update, force=True, dump=True)
    if options.query:
        W.query_debug=True
        W.logger.info("Manually executing query '%s' from CLI..." % (options.query))
        print(W.do_query(options.query))
        print("\n\tSee '%s' for complete query debug info!\n" % (W.logger.handlers[0].baseFilename))
    if options.list:
        print(W.list("keys_cli"))
    if options.list_JSON:
        print(W.list(dict)["world"])

    # now process daemon commands
    if options.daemon_cmd is not None:
        if options.daemon_cmd in ["status","start","stop","restart"]:
            D = WorldDaemon()
            D.command(options.daemon_cmd)
        else:
            print("\nInvalid daemon command. Use -h for help. Exiting...\n")
            sys.exit(255)


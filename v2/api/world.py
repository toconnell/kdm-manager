#!/usr/bin/python2.7


# general imports
from bson import json_util
from bson.objectid import ObjectId
import daemon
from datetime import datetime, timedelta
import json
from lockfile.pidlockfile import PIDLockFile
from optparse import OptionParser
import os
from pwd import getpwuid
import shutil
import subprocess
import stat
import sys
import time

# local imports
from assets import world as world_assets
import settings
import utils

class World:

    def __init__(self):
        self.logger = utils.get_logger()
        self.assets = world_assets.models


    def refresh_all_assets(self, force=False):
        """ Updates all assets. Set 'force' to True to ignore 'max_age' and
        'asset_max_age'. A wrapper for self.refresh_asset(). """

        self.logger.info("Refreshing all warehouse assets...")
        for asset_key in self.assets.keys():
            self.refresh_asset(asset_key, force=force)


    def refresh_asset(self, asset_key=None, force=False):
        """ Updates a single asset. Checks the 'max_age' of the asset and falls
        back to settings.world.asset_max_age if it can't find one.

        Set 'force' to True if you want to force a refresh, regardless of the
        asset's age. """


        max_age = settings.get("world", "asset_max_age") * 60

        asset_dict = self.assets[asset_key]
        if "max_age" in asset_dict.keys():
            max_age = asset_dict["max_age"] * 60

        # now determine whether we want to refresh it
        do_refresh = False
        current_age = None


        mdb_asset = utils.mdb.world.find_one({"handle": asset_key})
        if mdb_asset is None:
            self.logger.debug("Asset handle '%s' not found in mdb!" % asset_key)
            do_refresh = True
        else:
            current_age = datetime.now() - mdb_asset["created_on"]
        if current_age is None:
            do_refresh = True
        elif current_age.seconds > max_age:
            self.logger.debug("Asset '%s' has a current age of %s seconds (max age is %s seconds)." % (asset_key, current_age.seconds, max_age))
            do_refresh = True
        if force:
            do_refresh = True

        # now do the refresh, if necessary
        if do_refresh:
            self.logger.debug("Refreshing '%s' asset..." % asset_key)
            try:
                exec "value = self.%s()" % asset_key
                asset_dict.update({"handle": asset_key})
                asset_dict.update({"created_on": datetime.now()})
                asset_dict.update({"value": value})
                self.update_mdb(asset_dict)
                self.logger.debug("Updated '%s' asset in mdb." % asset_key)
            except AttributeError:
                self.logger.error("Could not refresh '%s' asset: no method available." % asset_key)
            except Exception as e:
                self.logger.error("Exception caught while refreshing asset!")
                self.logger.exception(e)


    def update_mdb(self, asset_dict):
        """ Creates a new document in mdb.world OR, if this handle already
        exists, updates an existing one. """

        existing_asset = utils.mdb.world.find_one({"handle": asset_dict["handle"]})
        if existing_asset is not None:
            asset_dict["_id"] = existing_asset["_id"]
        utils.mdb.world.save(asset_dict)
        utils.mdb.world.create_index("handle", unique=True)


    def remove(self, asset_id):
        """ Removes a single asset _id from mdb.world. """
        _id = ObjectId(asset_id)
        if utils.mdb.world.find_one({"_id": _id}) is not None:
            utils.mdb.world.remove(_id)
            self.logger.warn("Removed asset _id '%s'" % asset_id )
        else:
            self.logger.warn("Object _id '%s' was not found!" % asset_id)


    def list(self, output_type="JSON"):
        """ Dump world data in a few different formats."""

        if output_type == "CLI":
            output = ""
            for asset in utils.mdb.world.find():
                output += str(asset)
            return output
        elif output_type == "JSON":
            d = {"world": {}}
            for asset in utils.mdb.world.find():
                d["world"][asset["handle"]] = asset
            return json.dumps(d, default=json_util.default)


    # refresh methods from here down
    def dead_survivors(self):
        return utils.mdb.the_dead.find().count()

    def live_survivors(self):
        return utils.mdb.survivors.find({"dead": {"$exists": False}}).count()

    def total_survivors(self):
        return utils.mdb.survivors.find().count()

    def total_settlements(self):
        return utils.mdb.settlements.find().count()

    def total_users(self):
        return utils.mdb.users.find().count()

    def total_users_last_30(self):
        return utils.mdb.users.find({"latest_sign_in": {"$gte": utils.thirty_days_ago}}).count()

    def abandoned_settlements(self):
        return utils.mdb.settlements.find(
            {"$or": [
                {"removed": {"$exists": True}},
                {"abandoned": {"$exists": True}}
            ]
        }).count()

    def active_settlements(self):
        return self.total_settlements() - self.abandoned_settlements()

    def new_settlements_last_30(self):
        return utils.mdb.settlements.find({"created_on": {"$gte": utils.thirty_days_ago}}).count()

    def recent_sessions(self):
        return utils.mdb.users.find({"latest_activity": {"$gte": utils.recent_session_cutoff}}).count()





#
#   daemon code here
#

class worldDaemon:

    def __init__(self):

        self.logger = utils.get_logger(log_name="world_daemon")

        self.pid_file_path = os.path.abspath(settings.get("world","daemon_pid_file"))
        self.pid_dir = os.path.dirname(self.pid_file_path)
        self.set_pid()

        self.kill_command = "/bin/kill"


    def check_pid_dir(self):
        """ Checks to see if the pid directory exists and is writable. Creates a
        a new dir if it needs to do so. Also logs a WARN if the user requesting
        the check is not the owner of the pid dir. """

        if not os.path.isdir(self.pid_dir):
            self.logger.error("PID dir '%s' does not exist!" % self.pid_dir)
            try:
                shutil.os.mkdir(self.pid_dir)
                self.logger.critical("Created PID dir '%s'!" % self.pid_dir)
            except Exception as e:
                self.logger.error("Could not create PID dir '%s'!" % self.pid_dir)
                self.logger.exception(e)
                sys.exit(255)

        pid_dir_owner = getpwuid(os.stat(self.pid_dir).st_uid).pw_name
        self.logger.debug("PID dir '%s' is owned by '%s'." % (self.pid_dir, pid_dir_owner))
        if pid_dir_owner != os.environ["USER"]:
            self.logger.warn("PID dir owner is not the current user!")


    def set_pid(self):
        """ Updates 'self.pid' with the int in the daemon pid file. Returns None
        if there is no file or the file cannot be parsed. """
        self.pid = None
        if os.path.isfile(self.pid_file_path):
            try:
                self.pid = int(file(self.pid_file_path, "rb").read().strip())
            except Exception as e:
                self.logger.exception(e)


    def command(self, command=None):
        """ Executes a daemon command. Think of this as the router for incoming
        daemon commands/operations. Register all commands here. """

        if command == "start":
            self.start()
        elif command == "stop":
            self.stop()
        elif command == "restart":
            self.stop()
            time.sleep(1)
            self.start()
        elif command == "status":
            self.dump_status()

    def start(self):
        """ Starts the daemon. """
        self.logger.info("Starting World Daemon...")

        # pre-flight sanity checks and initialization tasks
        self.check_pid_dir()

        if os.getuid() == 0:
            self.logger.error("The World Daemon may not be started as root!")
            sys.exit(255)

        context = daemon.DaemonContext(
            working_directory = (settings.get("api","cwd")),
            detach_process = True,
            umask=0o002, pidfile=PIDLockFile(self.pid_file_path),
            files_preserve = [self.logger.handlers[0].stream],
        )

        with context:
            while True:
                try:
                    self.run()
                except Exception as e:
                    self.logger.error("An exception occured during daemonization!")
                    self.logger.exception(e)
                    raise

    def run(self):
        """ A run involves checking all warehouse assets and, if they're older
        than their 'max_age' attrib (default to the world.asset_max_age value),
        it refreshes them.

        Once finished, it sleeps for world.refresh_interval, which is measured
        in minutes. """

        W = World()
        W.refresh_all_assets()
        self.logger.debug("World Daemon is sleeping...")
        time.sleep(settings.get("world","refresh_interval") * 60)


    def stop(self):
        """ Stops the daemon. """
        self.set_pid()

        if self.pid is not None:
            self.logger.warn("Preparing to kill PID %s" % self.pid)
            p = subprocess.Popen([self.kill_command, str(self.pid)], stdout=subprocess.PIPE)
            out, err = p.communicate()
            self.logger.warn("Process killed.")
        else:
            self.logger.debug("Daemon is not running. Ignoring stop command...")

    def get_uptime(self):
        """ Uses the pid file to determine how long the daemon has been active.
        Returns None if the daemon isn't active. Otherwise, this returns a raw
        timedelta. """

        if os.path.isfile(self.pid_file_path):
            pid_file_age = time.time() - os.stat(self.pid_file_path)[stat.ST_MTIME]
            return timedelta(seconds=pid_file_age)
        else:
            return None


    def dump_status(self):
        """ Prints daemon status to stdout. """
        spacer = 15

        active = False
        if self.pid is not None:
            active = True

        print("\n\tWorld Daemon stats:\n")
        utils.cli_dump("Active", spacer, active)
        utils.cli_dump("Uptime", spacer, self.get_uptime())
        utils.cli_dump("PID", spacer, self.pid)
        utils.cli_dump("PID file", spacer, self.pid_file_path)
        utils.cli_dump("Assets", spacer, utils.mdb.world.find().count())
        print("\n")



if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-r", dest="refresh", action="store_true", default=False, help="Force a warehouse refresh")
    parser.add_option("-l", dest="list", default=False, help="List warehoused data")
    parser.add_option("-R", dest="remove_one", default=None, help="Remove an object _id from the warehouse")
    parser.add_option("-d", dest="daemon_cmd", help="Daemon controls: status|start|stop|restart", default=None)
    (options, args) = parser.parse_args()

    # process specific/manual world operations first
    W = World()
    if options.remove_one is not None:
        W.remove(options.remove_one)
    if options.refresh:
        W.logger.debug("Beginning forced asset refresh...")
        W.refresh_all_assets(force=True)
    if options.list:
        print(W.list(options.list))

    # now process daemon commands
    if options.daemon_cmd is not None:
        if options.daemon_cmd in ["status","start","stop","restart"]:
            D = worldDaemon()
            D.command(options.daemon_cmd)
        else:
            print("\nInvalid daemon command. Use -h for help. Exiting...\n")
            sys.exit(255)


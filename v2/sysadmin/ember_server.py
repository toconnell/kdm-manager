#!/usr/bin/env python

# general
import os
from optparse import OptionParser
import psutil
import subprocess
import sys
import time

# custom
import logger
import settings


class emberController():
    def __init__(self):
        self.logger = logger.load()
        self.set_pid_dir()
        self.set_pid()

    def set_pid_dir(self):
        """ Checks the 'pid_dir' setting from our cfg file. If it's not there,
        tries to create it. """

        self.pid_dir = settings.get("ember","pid_dir")
        if not os.path.isdir(self.pid_dir):
            try:
                os.makedirs(pid_dir)
                self.logger.warn("Created PID dir '%s'" % pid_dir)
            except Exception as e:
                self.logger.exception("Could not create PID dir '%s'" % pid_dir)
                raise e
        self.logger.debug("Verified PID dir")


    def set_pid(self):
        """ Checks to see if a pid file exists and if the pid in the file is
        active. Automatically removes files whose PID is dead. """

        self.pid_file_path = os.path.join(settings.get("ember","pid_dir"), "%s.pid" % settings.profile)
        self.pid = None
        if os.path.exists(self.pid_file_path):
            self.pid = int(file(self.pid_file_path,"rb").read())
            if psutil.pid_exists(self.pid):
                self.logger.debug("Ember is running (PID: %s)." % self.pid)
            else:
                self.logger.warn("PID %s does not exist! PID file '%s' will be removed." % (self.pid, self.pid_file_path))
                os.remove(self.pid_file_path)
                self.pid = None


    def start(self):
        """ Forks a process to start Ember. """
        if self.pid is not None:
            err = "PID file '%s' exists (Ember is running). Aborting start command..." % self.pid_file_path
            self.logger.error(err)
            print(err)
            sys.exit()
        newpid = os.fork()
        if newpid == 0:
            self.ember()


    def stop(self):
        """ If we've got a self.pid, kill it. """
        if self.pid is not None:
            os.kill(self.pid,14)
            self.logger.warn("PID %s has been killed!" % self.pid)
            self.pid = None
        else:
            self.logger.info("Ember is not running.")


    def ember(self):
        """ Start an ember child. """
        cmd_list = ["ember","server","--port",settings.get("ember","port")]
        cmd = " ".join(cmd_list)
        self.logger.debug(cmd)
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,cwd=settings.get("ember","cwd"))
        self.logger.debug("Parent process ID: %s" % p.pid)
        parent_pid = psutil.Process(p.pid)
        time.sleep(5)   # give ember time to start
        self.pid = str(parent_pid.children(recursive=True)[0].pid)
        self.logger.debug("Ember process ID: %s" % self.pid)
        pid_fh = file(self.pid_file_path,"w")
        pid_fh.write(self.pid)
        pid_fh.close()
        self.logger.debug("Wrote PID file to '%s' successfully" % self.pid_file_path)
        stdout_value, stderr_value = p.communicate()



if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-s", dest="settings_profile", help="Which settings profile to use", metavar="production", default="production")
    parser.add_option("--start", dest="start", help="Start Ember", action="store_true", default=False)
    parser.add_option("--stop", dest="stop", help="Stop Ember", action="store_true", default=False)
    parser.add_option("--restart", dest="restart", help="Restart Ember (brutally)", action="store_true", default=False)
    options, args = parser.parse_args()

    settings = settings.load(options.settings_profile)
    E = emberController()
    if options.start:
        E.start()
    elif options.restart:
        E.logger.critical("Restarting Ember!")
        E.stop()
        time.sleep(6)
        E.start()
    elif options.stop:
        E.stop()
    else:
        raise Exception ("Unknown Action!")

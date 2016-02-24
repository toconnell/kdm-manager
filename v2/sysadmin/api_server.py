#!/usr/bin/env python

#   standard lib imports
import CGIHTTPServer
import BaseHTTPServer
import daemon
import logging
from lockfile.pidlockfile import PIDLockFile
import os
from pwd import getpwuid
import shutil
import psutil
import SimpleHTTPServer
import SocketServer
import subprocess
import sys
import time

# custom
import logger
import settings; settings = settings.load()
sys.path.append(settings.get("application","project_root"))
from api import server


def start_server():
    """ Starts a server. If you do this outside of a forked/daemonized process,
    you can watch it and manually Ctrl-C it. """

    check_pid_dir()

    logger.info("Starting API Server...")
    new_pid = os.fork()
    if new_pid == 0:
        context = daemon.DaemonContext(
            detach_process = True,
            umask=0o002, pidfile=PIDLockFile(settings.get("api", "pid_file")),
            files_preserve = [logger.handlers[0].stream],
            )
        with context:
            logger.info("PID file location is '%s'" % settings.get("api", "pid_file"))
            try:
                os.chdir(settings.get("api","cwd"))
                sys.path.append(settings.get("api","cwd"))
                server.run()
            except Exception as e:
                logger.error("Could not start server!")
                logger.exception(e)

    time.sleep(3)
    logger.debug("Server process forked.")



def stop_server():
    """ Kills a pid. """
    pid = get_pid()
    logger.warn("Preparing to kill PID %s" % pid)
    which_kill = "/bin/kill"
    p = subprocess.Popen([which_kill, str(pid)], stdout=subprocess.PIPE)
    out, err = p.communicate()
    logger.critical("Process killed.")


def get_pid():
    """ Gets the current PID associated with the daemon. """
    try:
        return int(file(settings.get("api","pid_file"), "rb").read().strip())
    except:
        return False


def check_pid_dir():
    """ Checks to see if the PID dir in the settings file exists and
    raises a generic Exception if it doesn't. """

    pid_dir = os.path.dirname(settings.get("api","pid_file"))
    if not os.path.isdir(pid_dir):
        err = "PID dir '%s' does not exist!" % pid_dir
        logger.critical(err)
        raise Exception(err)
    else:
        logger.info("PID dir '%s' exists." % pid_dir)

    pid_dir_owner = getpwuid(os.stat(pid_dir).st_uid).pw_name
    logger.info("PID dir '%s' is owned by '%s'." % (pid_dir, pid_dir_owner))
    if pid_dir_owner != os.environ["USER"]:
        logger.warn("PID dir owner is not the current user!")


if __name__ == "__main__":

    logger = logger.load()

    if not os.path.isfile(settings.get("api","pid_file")):
        start_server()
    else:
        logger.info("PID found. Attempting to stop server...")
        pid = get_pid()
        if psutil.pid_exists(pid):
            stop_server()
        else:
            logger.warn("pid file '%s' exists, but PID '%s' does not!" % (settings.get("api","pid_file"), pid))
            shutil.os.remove(settings.get("api","pid_file"))
            start_server()

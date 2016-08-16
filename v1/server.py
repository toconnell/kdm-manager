#!/usr/bin/env python

#   standard lib imports
import CGIHTTPServer
import BaseHTTPServer
import daemon
import logging
from lockfile.pidlockfile import PIDLockFile
from optparse import OptionParser
import os
from pwd import getpwuid
import shutil
import psutil
import SimpleHTTPServer
import SocketServer
import subprocess
import sys

#   custom imports
from utils import get_logger, load_settings

class StreamToLogger(object):
   """ Fake file-like stream object that redirects writes to a logger instance.
   """

   def __init__(self):
      self.linebuf = ''

   def write(self, buf):
      for line in buf.rstrip().splitlines():
         logger.log(logger.level, line.rstrip())


class ThreadingSimpleServer(SocketServer.ThreadingMixIn,BaseHTTPServer.HTTPServer):
    """ Initializes a vanilla server with threading by subclassing the above and
    overwriting literally nothing. """

    pass


class customRequestHandler(CGIHTTPServer.CGIHTTPRequestHandler):
    """ We need to make a custom request handler so that we can overwrite the
    log_message func in CGIHTTPRequestHandler (if you don't overwrite it, it
    prints to STDERR and, if you're a daemon, this just goes into the bit
    bucket. """

    def log_message(self, format, *args):
        logger.log(logger.level, "%s" % (format%args))


def start_server(port=None):
    """ Starts a server. If you do this outside of a forked/daemonized process,
    you can watch it and manually Ctrl-C it. """

    logger.info("Starting server...")

    server_port = settings.getint("server","port")
    if port is not None:
        server_port = int(port)

    logger.info("Server will listen on port %s..." % server_port)

    handler = customRequestHandler  # see above
    handler.cgi_directories.extend(["/"])
    server = ThreadingSimpleServer(('', server_port), handler)
    app_cwd = os.path.join(os.environ["HOME"], settings.get("server", "cwd"))
    os.chdir(app_cwd)

    logger.info("Server CWD is '%s'..." % app_cwd)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
        logger.critical("Caught manual interrupt! Exiting.")
        sys.exit()


def start_daemon():
    """ Uses DaemonContext to fork (i.e. daemonize) the start_server()
    function which, obviously, makes the server immune to Ctrl-C.

    Run this script with no arguments again to toggle it off.
    """
    logger.info("Preparing to daemonize...")
    check_pid_dir()

    context = daemon.DaemonContext(
        detach_process = True,
        umask=0o002, pidfile=PIDLockFile(settings.get("server", "pid_file")),
        files_preserve = [logger.handlers[0].stream],
        )

    with context:
        logger.info("PID file location is '%s'" % settings.get("server", "pid_file"))
        start_server()


def stop_daemon():
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
        return int(file(settings.get("server","pid_file"), "rb").read().strip())
    except:
        return False


def check_pid_dir():
    """ Checks to see if the PID dir in the settings file exists and
    raises a generic Exception if it doesn't. """

    pid_dir = os.path.dirname(settings.get("server","pid_file"))
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

    logger = get_logger()
    settings = load_settings()

    parser = OptionParser()
    parser.add_option("-i", dest="interactive", help="Run the server in 'interactive' mode (print output to STDOUT)", default=False, action="store_true")
    parser.add_option("-p", dest="port", help="Force the server to run on the specified port", default=None, metavar="9999")
    (options, args) = parser.parse_args()

    if options.interactive:
        logger.info("Starting server in interactive mode!")
        start_server(options.port)

    if not os.path.isfile(settings.get("server","pid_file")):
        start_daemon()
    else:
        logger.info("PID found. Attempting to stop server...")
        pid = get_pid()
        if psutil.pid_exists(pid):
            stop_daemon()
        else:
            logger.warn("pid file '%s' exists, but PID '%s' does not!" % (settings.server_pidfile, pid))
            shutil.os.remove(settings.server_pidfile)
            start_daemon()

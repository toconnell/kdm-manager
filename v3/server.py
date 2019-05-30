#!/usr/bin/python2.7

#   standard lib imports
import CGIHTTPServer
import BaseHTTPServer
from optparse import OptionParser
import os
from pwd import getpwuid
import SimpleHTTPServer
import SocketServer
import sys

#   custom imports
import utils


# lazy-ass
settings = utils.load_settings()
logger = utils.get_logger()

#
#   Server operations here
#

class ThreadingSimpleServer(
    SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer
    ):
    """ Initializes a vanilla server with threading by subclassing the above and
    overwriting literally nothing. """

    pass


def start_server(port=None):
    """ Starts a server. If you do this outside of a forked/daemonized process,
    you can watch it and manually Ctrl-C it. """

    logger.info('Starting kdm-manager server...')

    if os.getuid() == 0:
        logger.error("The server cannot be started as root.")
        logger.info("Aborting operation!")
        sys.exit()

    removed = utils.mdb.sessions.remove()
    logger.warn("Removed %s user sessions!" % removed["n"])

    server_port = settings.getint("server", "port")
    if port is not None:
        server_port = int(port)

    # 1.) create the handler and the server object
    try:
        handler = CGIHTTPServer.CGIHTTPRequestHandler
        handler.cgi_directories.extend(["/"])
        server = ThreadingSimpleServer(('', server_port), handler)
        logger.info("Server initialized to run on http://%s:%s/" % (
            server.server_address)
        )
    except Exception as e:
        logger.error("Server could not be initialized!")
        logger.exception(e)
        raise

    # 2.) set the working directory and change to it
    try:
        app_cwd = os.path.dirname(os.path.abspath(sys.argv[0]))
        os.chdir(app_cwd)
        logger.info("Set server CWD to %s" % app_cwd)
    except Exception as e:
        logger.error("Server working drectory could not be set!")
        logger.exception(e)
        raise

    # 3.) launch!
    try:
        logger.info("Server listening...")
        server.serve_forever()
    except KeyboardInterrupt:
        logger.critical("Shutting down server %s:%s" % (server.server_address))
        server.shutdown()
        sys.exit()
    finally:
        logger.critical("Server is no longer active!")



#
#   Misc. and helper/laziness functions here
#

def get_pid():
    """ Gets the current PID associated with the daemon. """
    try:
        return int(
            file(
                settings.get("server", "pid_file"), "rb"
            ).read().strip()
        )
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


    parser = OptionParser()
    parser.add_option("-p", dest="port", default=settings.get('server', 'port'),
                      help="Force the server to run on the specified port",
                      metavar="9999", type=int)
    (options, args) = parser.parse_args()

    start_server(options.port)

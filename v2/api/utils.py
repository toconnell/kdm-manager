#!/usr/bin/python2.7


# general imports
from datetime import datetime, timedelta
import logging
import os
import sys
from pymongo import MongoClient

# project-specific imports
import settings



class Utilities:
    """ Initialize one of these anywhere in the app to get access to basic
    handles, helpers, methods, etc. """

    def __init__(self):
        self.settings = settings.Settings()
        self.mdb = MongoClient()[self.settings.get("api","mdb")]
        self.ymd = "%Y-%m-%d"
        self.hms = "%H:%M:%S"
        self.ymdhms = "%Y-%m-%d %H:%M:%S"
        self.thirty_days_ago = datetime.now() - timedelta(days=30)
        self.recent_session_cutoff = datetime.now() - timedelta(hours=12)


    def get_logger(self, log_level=None, log_name=None):
        """ Initialize a logger, specifying a new file if necessary. """
        logger = logging.getLogger(__name__)

        if not len(logger.handlers):    # if it's not already open, open it

            # set the file name or default to the script asking for the logger
            log_file_name = log_name
            if log_name is None:
                log_file_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
            log_handler_level = log_level

            # do the same for log level, defaulting to the server's 'log_level'
            if log_handler_level is None:
                logger.setLevel(self.settings.get("server","log_level"))
            elif type(log_handler_level) == str:
                exec 'log_level_obj = logging.%s' % log_level
                logger.setLevel(log_level_obj)
            else:
                logger.setLevel(log_handler_level)

            # now check the logging root, just as a precaution
            log_root_dir = self.settings.get("api","log_dir")
            if not os.path.isdir(log_root_dir):
                e = Exception("Logging root dir '%s' does not exist!" % log_root_dir)
                raise e

            # create the path and add it to the handler
            log_path = os.path.join(log_root_dir, log_file_name + ".log")
            logger_fh = logging.FileHandler(log_path)

            #   set the formatter and add it via addHandler()
            formatter =  logging.Formatter('[%(asctime)s] %(levelname)s:\t%(message)s', self.ymdhms)
            logger_fh.setFormatter(formatter)
            logger.addHandler(logger_fh)

        return logger


if __name__ == "__main__":
    print("Don't execute this file.")


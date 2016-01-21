#!/usr/bin/env python

# generic
import getpass
import logging
import os
import sys

# custom
import settings; settings = settings.load()

def load(log_level="INFO", log_name=False):
    """ Creates a generic logger at the specified log level."""

    if settings.getboolean("application","debug"):
        log_level="DEBUG"

    #   initialize a generic logger
    logger = logging.getLogger(__name__)

    if not len(logger.handlers):    # if it's not already open, open it
        exec 'log_level_obj = logging.%s' % log_level
        logger.setLevel(log_level_obj)

        #   set the logger's name and path
        log_file_name = log_name
        if not log_file_name:
            log_file_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]

        log_root_dir = settings.get("application","log_dir")
        if not os.path.isdir(log_root_dir):
            print(" Logging root dir '%s' does not exist!" % log_root_dir)
            try:
                os.makedirs(log_root_dir)
            except Exception as e:
                print(" Could not create '%s' as user '%s' (uid: %s)" % (log_root_dir,getpass.getuser(),os.geteuid()))
                print(" Exiting...\n")
                raise e

        log_path = os.path.join(log_root_dir, log_file_name + ".log")
        logger_fh = logging.FileHandler(log_path)

        #   set the formatter and add it via addHandler()
        formatter =  logging.Formatter('[%(asctime)s] %(levelname)s:\t%(message)s',"%Y-%m-%d %H:%M:%S")
        logger_fh.setFormatter(formatter)
        logger.addHandler(logger_fh)

    return logger

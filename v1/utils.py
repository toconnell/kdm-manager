#!/usr/bin/env python

#   standard
import ConfigParser
import logging
import os
import sys

#
#   General purpose helpers and references
#

ymd = "%Y-%m-%d"

#   helper functions

def load_settings():
    config = ConfigParser.ConfigParser()
    config.readfp(open("settings.cfg"))
    config.file_path = os.path.abspath("settings.cfg")
    return config


def get_logger(log_level="INFO", log_name=False):
    """ Creates a generic logger at the specified log level."""

    settings = load_settings()
    print settings

    #   initialize a generic logger
    logger = logging.getLogger(__name__)
    exec 'log_level_obj = logging.%s' % log_level
    logger.setLevel(log_level_obj)

    #   set the logger's name and path
    log_file_name = log_name
    if not log_file_name:
        log_file_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    if not os.path.isdir(settings.log_root_dir):
        e = Exception("Logging root dir '%s' does not exist!" % settings.log_root_dir)
        raise e

    log_path = os.path.join(settings.log_root_dir, log_file_name + ".log")
    logger_fh = logging.FileHandler(log_path)

    #   set the formatter and add it via addHandler()
    formatter =  logging.Formatter('[%(asctime)s] %(levelname)s:\t%(message)s',"%Y-%m-%d %H:%M:%S")
    logger_fh.setFormatter(formatter)
    logger.addHandler(logger_fh)

    return logger


if __name__ == "__main__":
    print("Starting unit tests...")
    settings = load_settings()
    if not settings:
        raise Exception("Settings file could not be loaded!")
    else:
        print(" Settings file '%s' loaded!" % settings.file_path)

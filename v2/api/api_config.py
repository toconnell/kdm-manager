#!/usr/bin/env python

import logging
import os
from ConfigParser import SafeConfigParser
from pymongo import MongoClient

settings = SafeConfigParser()
settings.readfp(open("settings.cfg"))
settings.file_path = os.path.abspath("settings.cfg")

settings.mdb_name = "%s_%s" % (settings.get("data","mdb"), os.environ["USER"])
settings.mdb = MongoClient()[settings.mdb_name]

logger = logging.getLogger(__name__)
if not len(logger.handlers):    # if it's not already open, open it
    exec 'log_level_obj = logging.%s' % settings.get("meta","log_level")
    logger.setLevel(log_level_obj)
    logger_fh = logging.FileHandler("api.log")

    formatter =  logging.Formatter('[%(asctime)s] %(levelname)s:\t%(message)s',"%Y-%m-%d %H:%M:%S")
    logger_fh.setFormatter(formatter)
    logger.addHandler(logger_fh)
settings.default_logger = logger

if __name__ == "__main__":
    print("Don't execute this file.")

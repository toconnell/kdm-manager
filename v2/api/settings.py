#!/usr/bin/env python

# http://python-eve.org/config.html#global

import os
import logging
from pymongo import MongoClient

import models

API_VERSION = '0.2.0'
SERVER_NAME = "api.thewatcher.io"
LOG_LEVEL   = "DEBUG"
LOG_FILE    = "api.log"

# database
MONGO_DBNAME = "kdm-manager_v2_%s" % os.environ["USER"]
MDB = MongoClient()[MONGO_DBNAME]   # for admin.py

# api domain

DOMAIN = {
    "users": models.users,
}





#
# logging - this is non-eve stuff: it gets messy
#

logger = logging.getLogger(__name__)
if not len(logger.handlers):    # if it's not already open, open it
    exec 'log_level_obj = logging.%s' % LOG_LEVEL
    logger.setLevel(log_level_obj)
    logger_fh = logging.FileHandler(LOG_FILE)
    formatter =  logging.Formatter('[%(asctime)s] %(levelname)s:\t%(message)s',"%Y-%m-%d %H:%M:%S")
    logger_fh.setFormatter(formatter)
    logger.addHandler(logger_fh)
default_logger = logger

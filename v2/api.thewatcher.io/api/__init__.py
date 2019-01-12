#!/usr/bin/python2.7

# general imports
from bson.objectid import ObjectId
from bson import json_util
from celery import Celery
from datetime import datetime

from flask import Flask, send_file, render_template, request, Response, send_from_directory, jsonify
from flask_httpauth import HTTPBasicAuth
basicAuth = HTTPBasicAuth()
import flask_jwt
import flask_jwt_extended

import json
import os
from pprint import pprint
import socket

# application-specific imports
import docs
import request_broker
import settings
import world
import utils

# models
from models import users, settlements, names
from utils.route_decorators import crossdomain

# create the flask app with settings/utils info
application = Flask(__name__)

# fudge some private settings in
application.config.update(
    DEBUG = settings.get("server","DEBUG"),
    TESTING = settings.get("server","DEBUG"),
)
application.logger.addHandler(utils.get_logger(log_name="server"))
application.config['SECRET_KEY'] = settings.get("api","secret_key","private")


#   Javascript Web Token! DO NOT import jwt (i.e. pyjwt) here!
jwt = flask_jwt_extended.JWTManager(application)

from api import routes

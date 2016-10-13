#!/usr/bin/python2.7
#test
# general imports
from flask import Flask, send_file, request

# application-specific imports
import settings

application = Flask(__name__)

# default route - landing page, vanity URL stuff
@application.route("/")
def index():
    return send_file("templates/index.html")


# file-spoofing
@application.route("/settings.json")
def settings_json():
    S = settings.Settings()
    return send_file(S.json_file(), attachment_filename="settings.json", as_attachment=True)


# API routing starts here
#@api.route("/auth")
#def user():
#    output = ""
#    for k in request.headers.keys():
#        output += "%s: %s<br/>" % (k, request.headers[k])
#    return output



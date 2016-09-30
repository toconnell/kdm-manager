#!/usr/bin/python2.7

from flask import Flask, send_file, request
import settings

app = Flask(__name__)

@app.route("/")
def index():
    return send_file("templates/index.html")

@app.route("/user")
def user():
    output = ""
    for k in request.headers.keys():
        output += "%s: %s<br/>" % (k, request.headers[k])
    return output

if __name__ == "__main__":
    S = settings.Settings()
    app.run(host='0.0.0.0', port=S.get("application","port"))

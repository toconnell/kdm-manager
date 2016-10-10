#!/usr/bin/env python

import sys

#
#   This script renders a JS app file on demand
#

if __name__ == "__main__":
    print("Content-type: text/css\n\n")
    raw_file = file("media/app.js", "rb").read()
    print raw_file
    sys.exit()

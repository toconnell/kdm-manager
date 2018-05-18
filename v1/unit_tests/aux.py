#!/usr/bin/env python

import glob
import os

#
#   project stuff
#

project_root = "/home/toconnell/kdm-manager/v1"

#   
#   methods
#

def get_CSS_files():
    # this will be programmatic one day. For now, it's just a list, while
    # we get things sorted out and organized.
    return ['media/style.css','media/color.css','media/z-index.css']

def get_JS_files():
    """ Creates a set of JS module paths. """

    modules = set()
    glob_str = os.path.join(project_root, "js/*")
    for mod in glob.glob(glob_str):
        modules.add(mod)
    return modules

def get_HTML_templates():
    """ Creates a set of HTML template paths. """

    templates = set()
    glob_str = os.path.join(project_root, "templates/*.html")
    for template in glob.glob(glob_str):
        templates.add(template)
    templates.add(os.path.join(project_root,'html.py')) # remove this when templates project is finished
    return templates

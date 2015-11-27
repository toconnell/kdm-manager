#!/usr/bin/env python

#   standard
import Cookie
from datetime import datetime, timedelta
from string import Template
import sys

#   custom
import admin
from session import initialize
from utils import load_settings, mdb

settings = load_settings()

user_error_msg = Template('<div id="user_error_msg" class="$err_class">$err_msg</div>')

class settlement:
    form = Template("""\n\
    $name

    \n""")

class dashboard:
    home_button = '<form method="POST"><input type="hidden" name="change_view" value="dashboard"/><button> &lt- Return to Dashboard</button></form>\n'
    headline = Template('<h2 class="full_width">$title</h2>\n')
    new_settlement_button = '<form method="POST"><input type="hidden" name="change_view" value="new_settlement" /><button class="success">+ New Settlement</button></form>\n'
    new_settlement_form = """\n\
    <form method="POST">
    <input type="hidden" name="new" value="settlement" />
    <input type="text" name="settlement_name" placeholder="Settlement Name"/ class="full_width">
    <button class="success">SAVE</button>
    </form>
    \n"""
    view_asset_button = Template("""\n\
    <form method="POST">
    <input type="hidden" name="view_$asset_type" value="$asset_id" />
    <button class="info">$asset_name</button>
    </form>
    \n""")

class login:
    """ """
    form = """\n\
    <form method="POST">
    <input class="full_width" type="text" name="login" placeholder="email"/>
    <input class="full_width" type="password" name="password" placeholder="password"/>
    <button>Go</button>
    </form>
    \n"""
    new_user = Template("""\n\
    <form method="POST">
    <input class="full_width" type="text" name="login" value="$login"/>
    <input class="full_width" type="password" name="password" placeholder="password"/>
    <input class="full_width" type="password" name="password_again" placeholder="password (again)"/>
    <button>Create New User</button>
    </form>
    \n""")

class meta:
    """ This is for HTML that doesn't really fit anywhere else, in terms of
    views, etc. Use this for helpers/containers/administrivia/etc. """
    start_head = '<!DOCTYPE html>\n<html>\n<head>\n<meta charset="UTF-8">\n<title>%s</title>\n' % settings.get("application","title")
    stylesheet = Template('<link rel="stylesheet" type="text/css" href="$url">\n')
    close_head = '</head>\n<body>\n <div id="container">\n'
    close_body = '\n </div><!-- container -->\n</body>\n</html>'
    log_out_button = Template('\n\t<form method="POST"><input type="hidden" name="remove_session" value="$session_id"/><button class="error">LOG OUT</button>\n\t</form>')

#
#   application helper functions for HTML interfacing
#

def set_cookie_js(session_id):
    """ This returns a snippet of javascript that, if inserted into the html
    head will set the cookie to have the session_id given as the first/only
    argument to this function.

    Note that the cookie will not appear to have the correct session ID until
    the NEXT page load after the one where the cookie is set.    """
    expiration = datetime.now() + timedelta(days=1)
    cookie = Cookie.SimpleCookie()
    cookie["session"] = session_id
    cookie["session"]["expires"] = expiration.strftime("%a, %d-%b-%Y %H:%M:%S PST")
    return cookie.js_output()


def authenticate_by_form(params):
    """ Pass this a cgi.FieldStorage() to try to manually authenticate a user"""
    if "password_again" in params:
        if "login" in params and "password" in params:
            create_new = admin.create_new_user(params["login"].value, params["password"].value, params["password_again"].value)
            if create_new == False:
                output = user_error_msg.safe_substitute(err_class="warn", err_msg="Passwords did not match! Please re-enter.")
            elif create_new is None:
                output = user_error_msg.safe_substitute(err_class="warn", err_msg="Email address could not be verified! Please re-enter.")
            else:
                pass
    if "login" in params and "password" in params:
        auth = admin.authenticate(params["login"].value, params["password"].value)
        if auth == False:
            output = user_error_msg.safe_substitute(err_class="error", err_msg="Invalid password! Please re-enter.")
            output += login.form
        elif auth is None:
            output = login.new_user.safe_substitute(login=params["login"].value)
        elif auth == True:
            S = initialize()
            session_id = S.create_new(params["login"].value)
            render(S.current_view_html(), head=[set_cookie_js(session_id)])
    else:
        output = login.form
    return output



#
#   render() func is the only thing that goes below here.
#

def render(html, head=[], http_headers=False):
    """ This is our basic render: feed it HTML to change what gets rendered. """

    output = http_headers
    if not http_headers:
        output = "Content-type: text/html\n\n"

    output += meta.start_head
    output += '<script type="text/javascript" src="http://code.jquery.com/jquery-latest.min.js"></script>'
    output += meta.stylesheet.safe_substitute(url=settings.get("application", "stylesheet"))

    for element in head:
        output += element

    output += meta.close_head
    output += html
    output += meta.close_body

    print(output)
    sys.exit(0)     # this seems redundant, but it's necessary in case we want
                    #   to call a render() in the middle of a load, e.g. to just
                    #   finish whatever we're doing and show a page.

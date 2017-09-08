#!/usr/bin/env python

#   standard
import Cookie
from datetime import datetime, timedelta
import os
from string import Template
import sys

#   custom
import admin
import api
import html
import session
import utils


class AuthObject:
    """ Initialize one of these in session.py (or wherever) to attempt to
    authenticate incoming credentials and, if successful, render a view for
    the newly authenticated user (by calling the authenticate_and_render_view()
    method).

    Raises an exception if authentication fails.
    """

    def __init__(self, params={}):
        self.logger = utils.get_logger('server')
        self.params = params
        self.username = params["login"].value.strip().lower()
        self.password = params["password"].value.strip()


    def authenticate_and_render_view(self, skip_auth=False):
        """ Uses attributes in self to attempt to authenticate a user and render
        an HTML view for them. """

        auth = admin.authenticate(self.username, self.password)

        if auth == False:
            msg = "Failed to authenticate user '%s' and render HTML view!" % (self.username)
            self.logger.error(msg)
            raise Exception(msg)
        elif auth == True:
            s = session.Session()
            session_id = s.new(self.username, self.password)
            new_sesh = utils.mdb.sessions.find_one({"_id": session_id})
            s.User.mark_usage("authenticated successfully")

            # handle preserve sessions checkbox on the sign in view
            if "keep_me_signed_in" in self.params:
                if "preferences" not in s.User.user:
                    s.User.user["preferences"] = {}
                s.User.user["preferences"]["preserve_sessions"] = True
                utils.mdb.users.save(s.User.user)

            output, body = s.current_view_html()
            html.render(
                output,
                body_class=body,
                head = [self.set_cookie_js(new_sesh["_id"], new_sesh["access_token"])],
                )


    def set_cookie_js(self, session_id, token):
        """ This returns a snippet of javascript that, if inserted into the html
        head will set the cookie to have the session_id given as the first/only
        argument to this function.

        Note that the cookie will not appear to have the correct session ID until
        the NEXT page load after the one where the cookie is set.    """

        expiration = datetime.now() + timedelta(days=30)
        cookie = Cookie.SimpleCookie()
        cookie["session"] = session_id
        cookie["session"]["expires"] = expiration.strftime("%a, %d-%b-%Y %H:%M:%S PST")
        cookie["jwt_token"] = token
        return cookie.js_output()


def render(view_type=None, login=None, code=None):
    """ Renders the login HTML. Exits. """

    # init the settings object
    settings = utils.load_settings()

    template_file_path = "templates/login.html"
    if view_type == 'reset':
        template_file_path = 'templates/reset_password.html'

    # grab up the template
    html_raw = file(template_file_path, "rb").read()
    html_tmp = Template(html_raw)

    # create the output
    output = html.meta.basic_http_header
    output += html_tmp.safe_substitute(
        version = settings.get('application', 'version'),
        title = settings.get('application', 'title'),
        api_url = api.get_api_url(),
        prod_url = settings.get('application', 'tld'),
        released = utils.get_latest_update_string(),
        login = login,
        code = code,
    )

    # render and exit
    print(output)
    sys.exit()


if __name__ == "__main__":
    print("This is a module. Do not execute it.")

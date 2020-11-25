"""

    This module is deprecated in v4. It will go away compelte when we move to
    Flask for the session/cookie handling.

"""


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


    def authenticate(self, skip_auth=False):
        """ Uses params set during __init__() to authenticate.

        Returns a tuple containing a user object and a session dict. """

        auth = admin.authenticate(self.username, self.password)

        if auth == False:
            msg = "Failed to authenticate user '%s' and render HTML view!"
            self.logger.error(msg % self.username)
            raise Exception(msg)
        elif auth == True:
            s = session.Session()
            session_id = s.new(self.username, self.password)
            s.User.mark_usage("authenticated successfully")
            return s.User, s.session

        self.logger.error('Unable to authenticate user: %s' % self.username)
        self.logger.error(
            'admin.authenticate() returned non-Boolean: %s' % auth
        )


    def set_cookie_js(self, session_id, token):
        """ This returns a snippet of javascript that, if inserted into the html
        head will set the cookie to have the session_id given as the first/only
        argument to this function.

        Note that the cookie will not appear to have the correct session ID
        until the NEXT page load after the one where the cookie is set."""

        expiration = datetime.now() + timedelta(days=30)
        cookie = Cookie.SimpleCookie()
        cookie["session"] = session_id
        cookie["session"]["expires"] = expiration.strftime(
            "%a, %d-%b-%Y %H:%M:%S PST"
        )
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
        login = login,
        code = code,
    )
    logger = utils.get_logger()
    # render; don't exit (in case we're metering performance)
    print(output)

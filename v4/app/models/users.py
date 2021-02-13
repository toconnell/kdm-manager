"""

    We initialize users as objects that are partially composed of Flask stuff
    and informationa about the actual user assets stored in the KDM API.

"""

# standard library
import json

# second party imports
from bson.objectid import ObjectId
import flask
import flask_login
import requests
import werkzeug

# kdm-manager imports
from app import app, login, utils


@login.user_loader
def load_user(_id):
    """ Used by flask_login when intializing the app. """
    if utils.api_preflight():
        return User(_id=_id)


class User(flask_login.UserMixin):

    def __init__(self, *args, **kwargs):
        """ Initializing a user requires a username and password. Upon init,
        the self.login() method is called, which sets self.token and the rest
        of the user object's attribs, etc.
        """

        self.logger = utils.get_logger()

        # set kwargs to self.whatever
        vars(self).update(kwargs)

        # go no further if we're logging the user out
        if flask.request.endpoint == 'logout':
            return None # __init__ needs to return None, not boolean

        if hasattr(self, '_id'):
            self.load()


    def __repr__(self):
        return "[%s (%s)]" % (getattr(self, 'login', 'user'), self._id)


    def new(self):
        """ Creates a new user via API call. Always returns TWO things:
            - a boolean of whether the job was successful
            - the server's response
        """

        endpoint = app.config['API']['url'] + 'new/user'
        response = requests.post(
            endpoint,
            verify = app.config['API']['verify_ssl'],
            json= {
                'username': self.username,
                'password': self.password
            }
        )

        if response.status_code != 200:
            return False, response.text
        else:
            return True, response.text


    def load(self):
        """ Assumes an authenticated user! Make sure you log into flask
        (see self.login_to_flask) before calling this.

        Goes to the API, gets the user JSON from there, and uses it to
        enrich our 'current_user' object, so we have access to more user
        data in the templates, etc. """

        self.refresh_token()

        endpoint = app.config['API']['url'] + 'user/get/' + self._id
        response = requests.get(
            endpoint,
            verify = app.config['API']['verify_ssl'],
            headers = {
                'Authorization': self.token,
                'API-Key': app.config['API_KEY']
            },
        )

        if response.status_code != 200:
            self.logger.error('[%s] %s' % (
                response.status_code, response.reason)
            )
            err = "Could not retrieve user %s from KDM API @ %s"
            raise utils.Logout(err % (self._id, app.config['API']['url']))

        user_attribs = utils.convert_json_dict(response.json()['user'])
        for attrib in user_attribs.keys():
            if attrib not in ['_id', 'password']:
                setattr(self, attrib, user_attribs[attrib])


    def login_to_api(self):
        """ Part one of our two-part login deal.

        This first part hits the /login endpoint of the API and sets the
        self._id and self.token attribute, which is currently a JWT token.
        """

        # set the API endpoint and POST the username/password to it
        endpoint = app.config['API']['url'] + 'login'
        response = requests.post(
            endpoint,
            verify = app.config['API']['verify_ssl'],
            json = {
                'username': self.username,
                'password': self.password
            }
        )

        # if the response is good, return True
        if response.status_code == 200:
            user = response.json()
            self._id = ObjectId(user['_id'])
            self.token = user['access_token']
            return True


    def login_to_flask(self, form):
        """
        Second part of our two-step login.

        This part authenticates the user to flask_login and actually returns
        a flask response to the browser.
        """

        flask_login.login_user(self, remember=form.remember_me.data)

        # handle 'next' page if we're stopping them en route
        next_page = flask.request.args.get('next')
        if not next_page or werkzeug.urls.url_parse(next_page).netloc != '':
            next_page = flask.url_for('dashboard')

        # create a response, inject the token into the cookie and return
        redirect = flask.redirect(next_page)
        response = app.make_response(redirect)
        response.set_cookie('kdm-manager_token', self.token)
        return response


    def refresh_token(self):
        """ Contacts the API to refresh the token. Updates the user
        as well as the all-important flask-login cookie. """

        self.token = flask.request.cookies.get('kdm-manager_token')

        if self.token is None or self.token == 'None':
            err = 'Could not retrieve JWT from cookies!'
            self.logger.error(err)
            self.logger.error(flask.request.cookies)
            flask.abort(500, err)

        # set the API endpoint and post the Authorization header to it
        endpoint = app.config['API']['url'] + 'authorization/refresh'
        response = requests.post(
            endpoint,
            verify = app.config['API']['verify_ssl'],
            headers = {
                'Authorization': self.token,
                'API-Key': app.config['API_KEY']
            },
        )

        if response.status_code == 200:
            self.token = response.json()['access_token']
            return True
        else:
            self.logger.error('%s Could not refresh token!' % self)
            self.logger.error('%s - %s' % (response.status_code, response.text))
            raise utils.Logout('Could not refresh JWT!')


    def reset_password(self, new_password=None, recovery_code=None):
        """ Dials the API using 'recovery_code' and resets the user's password
        to 'new_password'. If successful, we then log the user in to the API
        with their new password, so we have a fresh/accurate token. """

        endpoint = app.config['API']['url'] + 'reset_password/reset'
        response = requests.post(
            endpoint,
            verify = app.config['API']['verify_ssl'],
            json = {
                'username': self.username,
                'password': new_password,
                'recovery_code': recovery_code
            }
        )

        if response.status_code == 200:
            self.password = new_password
            self.login_to_api()
        else:
            self.logger.error(response)
            return response.text



    #
    #   helpers
    #

    def get_id(self):
        """ Required for Flask-Login; also just a good idea. """
        return str(self._id)


    def has_token(self):
        """ Returns a bool representing whether the user currently has a JWT
        from the API. """
        user_id = getattr(self, '_id', None)
        user_token = getattr(self, 'token', None)
        if user_id is not None and user_token is not None:
            return True
        return False



class Preferences:
    """ Preferences for the webapp are an object: this makes them easier to work
    with in routes.py, etc. since we can sweep more of the business logic under
    the rug of methods here, etc. """

    DEFAULTS = {
        'default': True,
        'subscriber_level': 0,
        'type': 'general',
    }

    OPTIONS = {
        "beta": {
            "desc": "Enable Beta (&beta;) features of the Manager?",
            "affirmative": "Enable",
            "negative": "Disable",
            "subscriber_level": 2,
            'default': False,
        },

        # new assets
        "random_names_for_unnamed_assets": {
            "type": "general",
            "desc": (
                "Let the Manager choose random names for Settlements/Survivors "
                "without names?"
            ),
            "affirmative": "Choose randomly",
            "negative": "Use 'Unknown' and 'Anonymous'",
        },

        # new survivors
        "apply_new_survivor_buffs": {
            "type": "new_survivor_creation",
            "desc": (
                "Automatically apply settlement bonuses to new, newborn and "
                "current survivors where appropriate?"
            ),
            "affirmative": "Automatically apply",
            "negative": "Do not apply",
        },
        "apply_weapon_specialization": {
            "type": "new_survivor_creation",
            "desc": (
                "Automatically add weapon specialization ability to living "
                "survivors if settlement Innovations list includes that weapon "
                "mastery?"
            ),
            "affirmative": "Add",
            "negative": "Do Not Add",
        },

        # interface - campaign summary
        "show_endeavor_token_controls": {
            "type": "campaign_summary",
            "desc": "Show Endeavor Token controls on Campaign Summary view?",
            "affirmative": "Show controls",
            "negative": "Hide controls",
        },

        # interface - survivor sheet
        "show_epithet_controls": {
            "type": "survivor_sheet",
            "desc": "Use survivor epithets (tags)?",
            "affirmative": "Show controls on Survivor Sheets",
            "negative": "Hide controls and tags on Survivor Sheets",
        },

        # interface
        "show_remove_button": {
            "type": "ui",
            "desc": "Show controls for removing Settlements and Survivors?",
            "affirmative": "Show the Delete button",
            "negative": "Hide the Delete button",
            'default': False,
        },
        "show_ui_tips": {
            "type": "ui",
            "desc": "Display in-line help and user interface tips?",
            "affirmative": "Show UI tips",
            "negative": "Hide UI tips",
            "subscriber_level": 2,
        },
        "show_dashboard_alerts": {
            "type": "ui",
            "desc": "Display webapp alerts on the Dashboard?",
            "affirmative": "Show alerts",
            "negative": "Hide alerts",
            "subscriber_level": 2,
        },
    }

    TYPES = {
        'general': {
            'name': 'General Preferences',
            'sort': 0,
        },
        'ui': {
            'name': 'Interface',
            'sort': 1,
        },
        'campaign_summary': {
            'name': 'Campaign Summary',
            'sort': 2,
        },
        'survivor_sheet': {
            'name': 'Survivor Sheet',
            'sort': 3,
        },
        'new_survivor_creation': {
            'name': 'New Survivor Creation',
            'sort': 4,
        },
    }



    def __init__(self):
        self.logger = utils.get_logger()
        pass


    def dump(self, return_type=None):
        """ Returns a representation of the prefrences object. Returns as JSON
        by default; set 'return_type' to a type (e.g. dict) to get that type
        back instead. """

        # apply defaults
        for option, option_dict in self.OPTIONS.items():
            option_dict['handle'] = option
            for key, value in self.DEFAULTS.items():
                if option_dict.get(key, None) is None:
                    option_dict[key] = value

        # add options to types
        for type_handle, type_dict in self.TYPES.items():
            type_dict['options'] = []
            for option, option_dict in self.OPTIONS.items():
                if option_dict['type'] == type_handle:
                    type_dict['options'].append(self.OPTIONS[option])

        # finally, create a list of groups
        output = []
        for type_handle in self.TYPES.keys():
            output.append(self.TYPES[type_handle])

        return output

#!/usr/bin/env python

from bson.objectid import ObjectId
import cgi
import Cookie
from datetime import datetime
import json
import jwt
import os
import random
import socket
import string
import sys
import traceback

import admin
import api
import assets
import html
import login
import models
import game_assets
from utils import mdb, get_logger, get_user_agent, load_settings, ymd, ymdhms, mailSession

settings = load_settings()


#
#   decorators for Session() methods to help users report exceptions
#

def current_view_failure(func):
    """ Decorates the Session.current_view() method below, handling render
    failures according to our usability design. """

    def wrapper(self=None, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            err_msg = "Caught exception while rendering current view for %s!" % self.User
            self.logger.error(err_msg)
            self.logger.exception(e)
            tb = traceback.format_exc().replace("    ","&ensp;").replace("\n","<br/>")
            print html.meta.error_500.safe_substitute(msg=err_msg, exception=tb)

            if not self.User.is_admin():
                self.logger.warn("[%s] user is not an application admin. Ending session!" % (self.User))
                self.log_out()
                self.email_render_error(traceback=tb)
            else:
                self.logger.warn("[%s] user is an application admin. Preserving session." % self.User)

            sys.exit(255)

    return wrapper


def process_params_failure(func):
    """ Decorates the Session.process_params() method below, handling parameter
    processing errors in a way that encourages users to report. """

    def wrapper(self=None, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            err_msg = "Caught exception while processing parameters for %s!" % self.User
            self.logger.error(err_msg)
            self.logger.exception(e)
            tb = traceback.format_exc().replace("    ","&ensp;").replace("\n","<br/>")
            print html.meta.error_500.safe_substitute(msg=err_msg, exception=tb, params=str(self.params))

            if not self.User.is_admin():
                self.log_out()
                self.email_render_error(traceback=tb)
            else:
                self.logger.warn("[%s] user is an application admin. Preserving session." % self.User)
            sys.exit(255)

    return wrapper


class Session:
    """ The properties of a Session object are these:

        self.params     -> a cgi.FieldStorage() object
        self.session    -> a mdb session object
        self.Settlement -> an assets.Settlement object
        self.User       -> an assets.User object

    """

    def __repr__(self):
        return str(self.session["_id"])


    def __init__(self, params={}):
        """ Initialize a new Session object."""
        self.logger = get_logger()

        # these are our session attributes. Declare them all here
        self.params = params
        self.session = None
        self.Settlement = None
        self.User = None

        # we're not processing params yet, but if we have a log out request, we
        #   do it here, while we're initializing a new session object.
        if "remove_session" in self.params:
            user = mdb.users.find_one({"current_session": ObjectId(self.params["remove_session"].value)})

            if user is not None:
                self.User = assets.User(user_id=user["_id"], session_object={"_id": 0})
                self.User.mark_usage("signed out")

            if 'login' in self.params:
                admin.remove_session(self.params["remove_session"].value, self.params["login"].value)
            else:
                admin.remove_session(self.params["remove_session"].value, "webapp_error")

        # ok, if this is a recovery request, let's try to do that
        if 'recovery_code' in self.params:
            self.logger.info("Password Recovery Code sign-in initiated!")
            user = mdb.users.find_one({'recovery_code': self.params["recovery_code"].value})
            if user is None:
                self.logger.info("Password Recovery Code not found (possibly expired). Aborting attempt.")
            else:
                self.logger.info("Rendering Password Recovery controls for '%s'" % user["login"])
                login.render("reset", user["login"], self.params['recovery_code'].value)

        # try to retrieve a session and other session attributes from mdb using
        #   the browser cookie
        self.cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE"))

        creds_present = False
        if 'login' in self.params and 'password' in self.params:
            creds_present = True

        def sign_in(creds=()):
            """ Private DRYness method for quickly logging in with params. """
            if 'login' in self.params and 'password' in self.params:
                A = login.AuthObject(self.params)
                A.authenticate_and_render_view()

        if self.cookie is None and creds_present:
            sign_in()
        elif self.cookie is not None and "session" in self.cookie.keys():
            session_id = ObjectId(self.cookie["session"].value)
            self.session = mdb.sessions.find_one({"_id": session_id})
            if self.session is not None:
                user_object = mdb.users.find_one({"current_session": session_id})
                self.User = assets.User(user_object["_id"], session_object=self)
            elif self.session is None:
                sign_in()
        elif self.cookie is not None and 'Session' not in self.cookie.keys() and creds_present:
            sign_in()
        else:
            self.logger.error("Error attempting to process cookie!")
            self.logger.error(self.cookie)

        if self.session is not None:
            if not api.check_token(self):
#                self.logger.debug("JWT Token expired! Attempting to refresh...")
                r = api.refresh_jwt_token(self)
                if r.status_code == 401:
                    self.log_out()
                    self.session = None


    def save(self, verbose=True):
        """ Generic save method. """
        mdb.sessions.save(self.session)
        if verbose:
            self.logger.debug("[%s] saved changes to session in mdb!" % (self.User))


    def log_out(self):
        """ For when the session needs to kill itself. """
        self.logger.debug("Ending session for '%s' via admin.remove_session()." % self.User.user["login"])
        admin.remove_session(self.session["_id"], "admin")


    def new(self, login, password):
        """ Creates a new session. Needs a valid user login and password..

        Updates the session with a User object ('self.User') and a new Session
        object ('self.session'). """

        user = mdb.users.find_one({"login": login})
        mdb.sessions.remove({"login": user["login"]})

        # new! get a JWT token and add it to your sesh so that your sesh can be
        # used to add it to your cookie

        token = api.get_jwt_token(login, password)

        if token:
            self.logger.debug("[%s (%s)] JWT token retrieved!" % (user["login"], user["_id"]))

        session_dict = {
            "login": login,
            "created_on": datetime.now(),
            "created_by": user["_id"],
            "current_view": "dashboard",
            "user_agent": {"is_mobile": get_user_agent().is_mobile, "browser": get_user_agent().browser },
            "access_token": token,
        }

        session_id = mdb.sessions.insert(session_dict)
        self.session = mdb.sessions.find_one({"_id": session_id})

        # update the user with the session ID
        user["current_session"] = session_id
        mdb.users.save(user)

        self.User = assets.User(user["_id"], session_object=self)

        return session_id   # passes this back to the html.create_cookie_js()


    def get_current_view(self):
        """ Returns current view as a string. Also sets the attribute. """

        if self.session is None:
            return "sign-in / none"

        if "current_view" in self.session.keys():
            self.current_view = self.session["current_view"]
            return self.current_view
        elif hasattr(self, "current_view"):
            return self.current_view
        else:
            return None



    def set_current_settlement(self, settlement_id=None):
        """ Tries (hard) to set the following attributes of a sesh:

            - self.current_settlement
            - self.session["current_settlement"]
            - self.Settlement

        The best way is to use the 'settlement_id' kwarg and feed an ObjectId
        object. If you haven't got one of those, this func will back off to the
        current session's mdb object and try to set it from there.

        The API asset for the current settlement is also retrieved here prior to
        initializing self.Settlement (which requires an API asset, obvi).
        """

        # first, if our mdb session document is None, don't do this at all
        if self.session is None:
            self.logger.error("[%s] 'session' attribute is None! Cannot set current settlement!" % (self.User))
            return None
        elif self.get_current_view() in ["dashboard","panel"]:
            self.logger.warn("[%s] session tried to set a 'current_settlement' and doesn't need one! Current view: '%s'. Returning None..." % (self.User, self.get_current_view()))
            return None

        # next, if we're doing this manually, i.e. forcing a new current
        #   settlement for a view change or whatever, do it now:
        if settlement_id is not None:
            self.session["current_settlement"] = settlement_id

        # now, if we've got a 'current_settlement' key, normalize it to ObjectId
        #   to prevent funny business. back off to the session object attrib and
        #   the session["current_asset"] (in that order).
        if "current_settlement" in self.session.keys():
            self.session["current_settlement"] = ObjectId(self.session["current_settlement"])
        elif hasattr(self, "current_settlement"):
            self.session["current_settlement"] = ObjectId(self.current_settlement)
        elif "current_asset" in self.session.keys() and "current_settlement" not in self.session.keys():
            self.session["current_settlement"] = ObjectId(self.session["current_asset"])
            self.logger.warn("[%s] set 'current_settlement' from 'current_asset' key!")
        else:
            self.logger.critical("[%s] unable to set 'current_settlement' for session!" % (self.User))

        # now do the attrib if we've managed to get a settlement object set
        if "current_settlement" in self.session.keys():
            self.current_settlement = self.session["current_settlement"]

        # now, fucking finally, set self.Settlement
        if "current_settlement" in self.session.keys() and hasattr(self, "current_settlement"):
            s_id = self.session["current_settlement"]
            self.Settlement = assets.Settlement(settlement_id=s_id, session_object=self)
        else:
            raise Exception("[%s] session could not set current settlement!" % (self.User))


        user_current_settlement = self.User.user.get("current_settlement", None)
        if user_current_settlement != self.session["current_settlement"]:
            self.logger.info("[%s] changing current settlement to %s" % (self.User, self.session["current_settlement"]))
            self.User.user["current_settlement"] = self.session["current_settlement"]
            self.User.save()

        mdb.sessions.save(self.session)


    def change_current_view(self, target_view, asset_id=False):
        """ Convenience function to update a session with a new current_view.

        'asset_id' is only mandatory if using 'view_survivor' or
        'view_settlement' as the 'target_view'.

        Otherwise, if you're just changing the view to 'dashbaord' or whatever,
        'asset_id' isn't mandatory.
        """

        self.session["current_view"] = target_view

        if target_view == "dashboard":
            self.session["current_settlement"] = None

        if asset_id:
            asset = ObjectId(asset_id)
            self.session["current_asset"] = asset
            if target_view == "view_campaign":
                self.session["current_settlement"] = asset
                self.set_current_settlement(settlement_id = asset)

        mdb.sessions.save(self.session)
        self.session = mdb.sessions.find_one(self.session["_id"])

        return "changed view to '%s'" % target_view


    def change_current_view_to_asset(self, view):
        """ Changes the current view to a view of a user asset. Returns a
        string meant to be logged as a user action. """

        a = self.params[view].value

        if view == "view_survivor":
            asset = mdb.survivors.find_one({"_id": ObjectId(a)})
            asset_sum = "%s [%s]" % (asset["name"], asset["sex"])
        elif view in ["view_campaign", "view_settlement"]:
            asset = mdb.settlements.find_one({"_id": ObjectId(a)})
            asset_sum = "%s" % (asset["name"])
        else:
            self.logger.error("[%s] view could not be changed to asset '%s'" % (self.User,a))

        self.change_current_view(view, asset_id=a)

        return "changed view to '%s' | %s | %s" % (view, a, asset_sum)



    def report_error(self):
        """ Uses attributes of the session, including self.params, to create an
        error report email. """

        self.logger.debug("[%s] is entering an error report!" % self.User)
        admins = settings.get("application","admin_email").split(",")

        M = mailSession()
        email_msg = html.meta.error_report_email.safe_substitute(
            user_email=self.User.user["login"],
            user_id=self.User.user["_id"],
            body=self.params["body"].value.replace("\n","<br/>")
        )
        M.send(
            recipients=admins,
            html_msg=email_msg,
            subject="KDM-Manager Error Report",
            reply_to=self.User.user["login"],
        )
        self.logger.warn("[%s] Error report email sent!" % self.User)


    def email_render_error(self, traceback=None):
        """ Uses the attributes of the session to send an email when a user's
        current view fails to render. """

        admins = settings.get("application","admin_email").split(",")


        session_as_html = "<br/>".join(["&ensp; %s -> %s" % (k,v) for k,v in self.session.iteritems()])

        M = mailSession()
        email_msg = html.meta.view_render_fail_email.safe_substitute(
            user_email=self.User.user["login"],
            user_id=self.User.user["_id"],
            exception=traceback,
            hostname=socket.gethostname(),
            error_time=datetime.now(),
            session_obj=session_as_html,
        )
        M.send(
            recipients=admins,
            html_msg=email_msg,
            subject="KDM-Manager Render Failure! [%s]" % socket.gethostname(),
#            reply_to=self.User.user["login"],
        )
        self.logger.warn("[%s] Current view render failure email sent!" % self.User)


    @process_params_failure
    def process_params(self, user_action=None):
        """ All cgi.FieldStorage() params passed to this object on init
        need to be processed. This does ALL OF THEM at once. """

        #
        #   dashboard-based, user operation params
        #

        # do error reporting
        if "error_report" in self.params and "body" in self.params:
            self.report_error()

        #
        #   change view operations, incl. with/without an asset
        #

        # change to a generic view without an asset
        if "change_view" in self.params:
            target_view = self.params["change_view"].value
            user_action = self.change_current_view(target_view)

        # change to a view of an asset
        for p in ["view_campaign", "view_settlement", "view_survivor"]:
            if p in self.params:
                user_action = self.change_current_view_to_asset(p)

        # these are our two asset removal methods: this is as DRY as I think we
        #   can get with this stuff, since both require unique handling
        if "remove_settlement" in self.params:
            s_id = ObjectId(self.params["remove_settlement"].value)
            self.set_current_settlement(s_id)
            S = assets.Settlement(settlement_id=s_id, session_object=self)
            S.remove()
            user_action = "removed settlement %s" % S
            self.change_current_view("dashboard")

        if "remove_survivor" in self.params:
            # we actually have to get the survivor from the MDB to set the
            # current settlement before we can initialize the survivor and
            # use its remove() method.
            s_id = ObjectId(self.params["remove_survivor"].value)
            s_doc = mdb.survivors.find_one({"_id": s_id})
            self.set_current_settlement(s_doc["settlement"])
            S = assets.Survivor(survivor_id=s_id, session_object=self)
            S.remove()
            user_action = "removed survivor %s from %s" % (S, S.Settlement)
            self.change_current_view("view_campaign", asset_id=S.survivor["settlement"])


        # user and campaign exports
        if "export_user_data" in self.params:
            export_type = self.params["export_user_data"].value
            if "asset_id" in self.params and self.User.is_admin():
                user_object = assets.User(user_id=self.params["asset_id"].value, session_object=self)
                filename = "%s_%s.kdm-manager_export.%s" % (datetime.now().strftime(ymd), user_object.user["login"], export_type.lower())
                payload = user_object.dump_assets(dump_type=export_type)
            else:
                payload = self.User.dump_assets(dump_type=export_type)
                filename = "%s_%s.kdm-manager_export.%s" % (datetime.now().strftime(ymd), self.User.user["login"], export_type.lower())
            self.User.mark_usage("exported user data (%s)" % export_type)
            self.logger.debug("[%s] '%s' export complete. Rendering export via HTTP..." % (self.User, export_type))
            html.render(str(payload), http_headers="Content-Disposition: attachment; filename=%s\n" % (filename))
        if "export_campaign" in self.params:
            export_type = self.params["export_campaign"].value
            C = assets.Settlement(settlement_id=ObjectId(self.params["asset_id"].value), session_object=self)
            payload, length = C.export(export_type)
            filename = "%s_-_%s.%s" % (datetime.now().strftime(ymd), C.settlement["name"], export_type.lower())
            self.User.mark_usage("exported campaign data as %s" % export_type)
            self.logger.debug("[%s] '%s' export complete. Rendering export via HTTP..." % (self.User, export_type))
            html.render(payload, http_headers="Content-type: application/octet-stream;\r\nContent-Disposition: attachment; filename=%s\r\nContent-Title: %s\r\nContent-Length: %i\r\n" % (filename, filename, length))


        #
        #   settlement operations - everything below uses user_asset_id
        #       which is to say that all forms that submit these params use
        #       the asset_id=mdb_id convention.

        user_asset_id = None
        if "asset_id" in self.params:
            user_asset_id = ObjectId(self.params["asset_id"].value)


        #
        #   we support new settlement creation in the legacy webapp.
        #

        if "new" in self.params:

            params = {}
            params["campaign"] = self.params["campaign"].value

            # try to get a name or default to None
            if "name" in self.params:
                params["name"] = self.params["name"].value
            else:
                params["name"] = None

            # try to get expansions/survivors params or default to []
            for p in ["expansions", "survivors", "specials"]:
                if p not in self.params:
                    params[p] = []
                elif p in self.params and isinstance(self.params[p], cgi.MiniFieldStorage):
                    params[p] = [self.params[p].value]
                elif p in self.params and type(self.params[p]) == list:
                    params[p] = [i.value for i in self.params[p]]
                else:
                    msg = "Invalid form parameter! '%s' is unknown type: '%s'" % (p, type(self.params[p]).__name__)
                    self.logger.error("[%s] invalid param key '%s' was %s. Params: %s" % (self.User, p, type(self.params[p]), self.params))
                    raise AttributeError(msg)

            # hit the route; check the response
            response = api.post_JSON_to_route("/new/settlement", payload=params, Session=self)
            if response.status_code == 200:
                s_id = ObjectId(response.json()["sheet"]["_id"]["$oid"])
                self.set_current_settlement(s_id)
                S = assets.Settlement(s_id, session_object=self)
                user_action = "created settlement %s" % self.Settlement
                self.change_current_view("view_campaign", S.settlement["_id"])
                S.save()
            elif response.status_code == 405:
                self.change_current_view('dashboard')
            else:
                msg = "An API error caused settlement creation to fail! API response was: %s - %s" % (response.status_code, response.reason)
                self.logger.error("[%s] new settlement creation failed!" % self.User)
                self.logger.error("[%s] %s" % (self.User, msg))
                raise RuntimeError(msg)

        #
        #   modify - still supported in the legacy webapp, pending deprecation
        #

        if "modify" in self.params:
            if self.params["modify"].value == "settlement":
                self.logger.error("%s Attempt to call modify() method from params!" % (self.Settlement))

            if self.params["modify"].value == "survivor":
                s = mdb.survivors.find_one({"_id": ObjectId(user_asset_id)})
                self.set_current_settlement(s["settlement"])
                S = assets.Survivor(survivor_id=s["_id"], session_object=self)
                S.modify(self.params)
                user_action = "modified survivor %s of %s" % (S, self.Settlement)

        self.User.mark_usage(user_action)



    def render_user_asset_sheet(self, collection=None):
        """ Uses session attributes to render the sheet for the user asset
        currently set to be session["current_asset"].


        Only works for Survivor Sheets and Settlement Sheets so far. """

        output = "ERROR!"

        user_asset = mdb[collection].find_one({"_id": self.session["current_asset"]})
        if user_asset is not None:
            if collection == "settlements":
                self.set_current_settlement(user_asset["_id"])
                return self.Settlement.render_html_form()
            elif collection == "survivors":
                self.set_current_settlement(user_asset["settlement"])
                S = assets.Survivor(survivor_id=user_asset['_id'], session_object=self)
                return S.render_html_form()
            else:
                msg = "[%s] user assets from '%s' colletion don't have Sheets!" % (self.User,collection)
                self.logger.error(msg)
                raise Exception(msg)



    def render_dashboard(self):
        """ Renders the user's dashboard. Leans heavily on the AngularJS app
        calling on the API for data, etc."""

        output = html.dashboard.angular_app.safe_substitute(
            application_version = settings.get("application","version"),
            api_url = api.get_api_url(),
            user_id = self.User.user["_id"],
        )

        return output


    @current_view_failure
    def current_view_html(self):
        """ This func uses session's 'current_view' attribute to render the html
        for that view.

        In a best case, we want this function to initialize a class (e.g. a
        Settlement or a Survivor or a User, etc.) and then use one of the render
        methods of that class to get html and return it.

        The whole thing is decorated in a function that captures failures and
        asks users to report them (and kills their session, logging them out, so
        they don't get stuck in a state where they can't stop re-creating the
        error, etc.
        """

        output = html.meta.saved_dialog
        output += html.meta.corner_loader
        self.get_current_view() # sets self.current_view

        body = None

        output += html.meta.full_page_loader

        if self.current_view == "dashboard":
            body = "dashboard"
            output += self.render_dashboard()
            output += admin.dashboard_alert()
            if get_user_agent().browser.family == "Safari":
                output += html.meta.safari_warning.safe_substitute(vers=get_user_agent().browser.version_string)

        elif self.current_view == "view_campaign":
            if not hasattr(self, "Settlement") or self.Settlement is None:
                self.set_current_settlement()
            output += self.Settlement.render_html_summary(user_id=self.User.user["_id"])

        elif self.current_view == "new_settlement":
            output += html.settlement.new.safe_substitute(
                user_id=self.User.user['_id'],
            )

        elif self.current_view == "view_settlement":
            output += self.render_user_asset_sheet("settlements")

        elif self.current_view == "view_survivor":
            output += self.render_user_asset_sheet("survivors")

        elif self.current_view == "panel":
            if self.User.is_admin():
                P = admin.Panel(self.User.user["login"])
                body = "helvetica"
                output += P.render_html()
            else:
                self.logger.warn("[%s] attempted to view admin panel and is not an admin!" % self.User)
                raise Exception("Authorization failure!")

        else:
            self.logger.error("[%s] requested unhandled view '%s'" % (self.User, self.current_view))
            raise Exception("Unknown View!")


        return output, body




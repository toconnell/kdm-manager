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
            admin.remove_session(self.params["remove_session"].value, self.params["login"].value)

        # try to retrieve a session and other session attributes from mdb using
        #   the browser cookie
        self.cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE"))

        if self.cookie is not None and "session" in self.cookie.keys():
            session_id = ObjectId(self.cookie["session"].value)
            self.session = mdb.sessions.find_one({"_id": session_id})
            if self.session is not None:
                user_object = mdb.users.find_one({"current_session": session_id})
                self.User = assets.User(user_object["_id"], session_object=self)

        if self.session is not None:
            if not api.check_token(self):
                self.logger.debug("JWT Token expired! Attempting to refresh...")
                r = api.refresh_jwt_token(self)
                if r.status_code == 401:
                    self.log_out()
                    self.session = None


    def save(self):
        """ Generic save method. """
        mdb.sessions.save(self.session)
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


    def recover_password(self):
        """ Call this method to process params related to password recovery and
        return text that will be rendered by the index. """

        if "login" not in self.params and "recovery_code" not in self.params:
            return html.login.recover_password

        if "recovery_code" not in self.params:
            user = mdb.users.find_one({"login": self.params["login"].value.lower().strip()})
        elif "recovery_code" in self.params:
            user = mdb.users.find_one({"recovery_code": self.params["recovery_code"].value})

        if user is None:
            if "recovery_code" in self.params:
                err = "Your recovery code appears to have expired! Please check your email and try again."
            else:
                err = "The login '%s' does not exist! Notification email NOT sent." % self.params["login"].value
            msg = html.user_error_msg.safe_substitute(err_class="error", err_msg=err)
            return html.login.form + msg

        self.User = assets.User(user_id=user["_id"], session_object=self)
        login = self.User.user["login"]

        if "recovery_code" in self.params:
            msg = ""
            recovery_code = self.params["recovery_code"].value
            self.logger.debug("%s is activating password recovery code '%s'" % (login, recovery_code))
            if "password" in self.params and "password_again" in self.params:
                reset_successful = self.User.update_password(self.params["password"].value, self.params["password_again"].value)
                if not reset_successful:
                    self.logger.debug("%s failed to reset password" % login)
                    msg = html.user_error_msg.safe_substitute(err_class="error", err_msg="Passwords did not match! Please try again.")
                    return html.login.reset_pw.safe_substitute(login=login, recovery_code=recovery_code) + msg
                else:
                    del self.User.user["recovery_code"]
                    mdb.users.save(self.User.user)
                    self.logger.debug("Removed recovery code from user %s" % login)
                    msg = html.user_error_msg.safe_substitute(err_class="success", err_msg="Password reset successful!")
                    return html.login.form + msg
            else:
                return html.login.reset_pw.safe_substitute(login=login, recovery_code=recovery_code)

        self.logger.debug("New password recovery request initiated by %s" % login)
        if not "@" in list(login):
            err = "Unable to validate email address '%s'. Notification email NOT sent." % login
            msg = html.user_error_msg.safe_substitute(err_class="error", err_msg=err)
            self.logger.critical(err)
        else:
            recovery_code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(30))
            self.logger.debug("Recovery code for %s is '%s'" % (login, recovery_code))
            self.User.user["recovery_code"] = recovery_code
            mdb.users.save(self.User.user)
            email_msg = html.login.pw_recovery_email.safe_substitute(login=login, recovery_code=recovery_code)
            M = mailSession()
            M.send(recipients=[login], html_msg=email_msg, subject="KDM-Manager Password Recovery!")
            msg = html.user_error_msg.safe_substitute(err_class="success", err_msg="Password recovery instructions sent to %s" % login)
        return html.login.form + msg


    def set_current_settlement(self, settlement_id=None, update_mins=True):
        """ Tries (hard) to set the following attributes of a sesh:

            - self.current_settlement
            - self.session["current_settlement"]
            - self.Settlement.

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
            self.set_api_assets()
            s_id = self.session["current_settlement"]
            self.Settlement = assets.Settlement(settlement_id=s_id, session_object=self, update_mins=update_mins)
        else:
            raise Exception("[%s] session could not set current settlement!" % (self.User))


        user_current_settlement = self.User.user.get("current_settlement", None)
        if user_current_settlement != self.session["current_settlement"]:
            self.logger.info("[%s] changing current settlement to %s" % (self.User, self.session["current_settlement"]))
            self.User.user["current_settlement"] = self.session["current_settlement"]
            self.User.save()

        mdb.sessions.save(self.session)


    def set_api_assets(self, settlement_id=None):
        """ Sets self.api dictionaries required by the current session. There's
        a lot of sensitivity to order of operations and back-offs and nested
        try/except stuff here, so read it carefully before you start hacking.
        Odds are good that if there's something odd, I did it for a reason."""

        # don't get data from the API unless we need to.
        if self.get_current_view() in ["dashboard","panel"]:
            return None

        # try to set the self.current_settlement attrib to be a valid ObjectId
        if self.get_current_view() is None:
            self.logger.debug("[%s] session has no 'current_view'. Returning API as None." % (self.User))
            return None

        # bail if we haven't set the current settlement
        if not hasattr(self, "current_settlement"):
            self.logger.warn("[%s] session has no 'current_settlement'" % self.User)

        if settlement_id is not None:
            self.current_settlement=settlement_id

        # now dial the API; fail noisily if we can't get it
        self.api_settlement = api.route_to_dict(
            "settlement/get/%s" % self.current_settlement,
#            access_token = self.session["access_token"],
        )
        if self.api_settlement == {}:
            self.logger.error("[%s] could not retrieve settlement from API server!" % self.User)
            return False

        # now, assuming we're still here, initialize the survivor assets
        self.api_survivors = {}
        for s in self.api_settlement["user_assets"]["survivors"]:
            _id = ObjectId(s["sheet"]["_id"]["$oid"])
            self.api_survivors[_id] = s



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

        if "update_user_preferences" in self.params:
            self.User.update_preferences(self.params)
            user_action = "updated user preferences"

        if "change_password" in self.params:
            if "password" in self.params and "password_again" in self.params:
                self.User.update_password(self.params["password"].value, self.params["password_again"].value)
                user_action = "updated password"
            else:
                user_action = "failed to update password"

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


        #   create new user assets

        if "new" in self.params:

            #
            #   new survivor creation via legacy app methods
            #

            if self.params["new"].value == "survivor":
                self.set_current_settlement(user_asset_id)
                S = assets.Survivor(params=self.params, session_object=self)
                self.change_current_view("view_survivor", asset_id=S.survivor["_id"])
                user_action = "created survivor %s in %s" % (S, self.Settlement)

            #
            #   new settlement creation via API call
            #

            if self.params["new"].value == "settlement":

                params = {}
                params["campaign"] = self.params["campaign"].value

                # try to get a name or default to None
                if "name" in self.params:
                    params["name"] = self.params["name"].value
                else:
                    params["name"] = None

                # try to get expansions/survivors params or default to []
                for p in ["expansions", "survivors", "special"]:
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
                    S.new(params)
                    user_action = "created settlement %s" % self.Settlement
                    self.change_current_view("view_campaign", S.settlement["_id"])
                else:
                    msg = "An API error caused settlement creation to fail! API response was: %s - %s" % (response.status_code, response.reason)
                    self.logger.error("[%s] new settlement creation failed!" % self.User)
                    self.logger.error("[%s] %s" % (self.User, msg))
                    raise RuntimeError(msg)


        #   bulk add

        if "bulk_add_survivors" in self.params:

            self.set_current_settlement(user_asset_id)
            S = assets.Settlement(settlement_id=user_asset_id, session_object=self)
            male = int(self.params["male_survivors"].value)
            female = int(self.params["female_survivors"].value)
            S.bulk_add_survivors(male,female)
            self.change_current_view("view_campaign", user_asset_id)


        #   modify

        if "modify" in self.params:

            if self.params["modify"].value == "settlement":
                s = mdb.settlements.find_one({"_id": ObjectId(user_asset_id)})
                self.set_current_settlement(s["_id"])
                S = assets.Settlement(settlement_id=s["_id"], session_object=self)
                S.modify(self.params)
                user_action = "modified settlement %s" % self.Settlement

            if self.params["modify"].value == "survivor":

                update_mins = True
                if "norefresh" in self.params:
                    update_mins = False

                s = mdb.survivors.find_one({"_id": ObjectId(user_asset_id)})
                self.set_current_settlement(s["settlement"], update_mins)
                S = assets.Survivor(survivor_id=s["_id"], session_object=self)
                S.modify(self.params)
                user_action = "modified survivor %s of %s" % (S, self.Settlement)

        #   hunting party return
        if "return_departing_survivors" in self.params:
            self.set_current_settlement(user_asset_id)
            S = assets.Settlement(settlement_id=user_asset_id, session_object=self)
            S.return_departing_survivors(self.params["return_departing_survivors"].value)
            S.save()
            user_action = "returned departing survivors to settlement %s" % self.Settlement

        self.User.mark_usage(user_action)

        #   exit now if we're doing a 'norefresh' request
#        if "norefresh" in self.params:
#            self.logger.debug("[%s] all 'norefresh' form parameters processed. Exiting." % self.User)
#            sys.exit(0)
#       # index handles this now!!


    def render_user_asset_sheet(self, collection=None):
        """ Uses session attributes to render the sheet for the user asset
        currently set to be session["current_asset"].


        Only works for Survivor Sheets and Settlement Sheets so far. """

        output = "ERROR!"

        user_asset = mdb[collection].find_one({"_id": self.session["current_asset"]})
        if user_asset is not None:
            if collection == "settlements":
                self.set_current_settlement(user_asset["_id"])
                S = assets.Settlement(settlement_id = user_asset["_id"], session_object=self)
            elif collection == "survivors":
                self.set_current_settlement(user_asset["settlement"])
                S = assets.Survivor(survivor_id = user_asset["_id"], session_object=self)
            else:
                self.logger.error("[%s] user assets from '%s' colletion don't have Sheets!" % (self.User,collection))
            output = S.render_html_form()

        return output


    def render_dashboard(self):
        """ Renders the user's dashboard. """

        output = self.User.html_motd()

        display_settlements = "none"
        display_campaigns = ""

        if self.User.get_campaigns() == "":
            display_settlements = ""
            display_campaigns = "none"


        # render campaigns, settlements and survivors lists for the dashboard.
        #   all of this goes away when we can get a user from the API

        output += html.dashboard.campaign_summary.safe_substitute(
            campaigns=self.User.get_campaigns(),
            display=display_campaigns
        )
        output += html.dashboard.settlement_summary.safe_substitute(
            settlements=self.User.get_settlements(return_as="asset_links"),
            display=display_settlements
        )
#        output += html.dashboard.survivor_summary.safe_substitute(
#            survivors=self.User.get_survivors("asset_links")
#        )

        # due to volatility, the html_world() call is wrapped for silent
        #   failure. No plans to change this at present.
        try:
            output += self.User.html_world()
        except Exception as e:
            self.logger.exception(e)
            output += '<!-- ERROR! World Menu could not be created! -->'

        output += admin.render_about_panel()

        if self.User.is_admin():
            output += html.dashboard.panel_button

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
        self.get_current_view() # sets self.current_view

        body = None

        # tack on the full-page spinner if we're doing a view that has
        #   to initialize with API data
        if self.current_view in ["view_campaign", "view_settlement", "view_survivor","new_settlement"]:
            output += html.meta.full_page_loader

        if self.current_view == "dashboard":
            body = "dashboard"
            output += self.render_dashboard()
            output += admin.dashboard_alert()
            if get_user_agent().browser.family == "Safari":
                output += html.meta.safari_warning.safe_substitute(vers=get_user_agent().browser.version_string)

        elif self.current_view == "view_campaign":
            output += html.dashboard.refresh_button
            self.set_current_settlement()
            output += self.Settlement.render_html_summary(user_id=self.User.user["_id"])

        elif self.current_view == "new_settlement":
            output += html.settlement.new

        elif self.current_view == "view_settlement":
            output += html.dashboard.refresh_button
            output += self.render_user_asset_sheet("settlements")

        elif self.current_view == "view_survivor":
            output += html.dashboard.refresh_button
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




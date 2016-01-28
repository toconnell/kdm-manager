#!/usr/bin/env python

from bson.objectid import ObjectId
import Cookie
from datetime import datetime
import os
import random
import string
import sys
import traceback

import admin
import assets
import html
import models
from utils import mdb, get_logger, get_user_agent, load_settings, ymd, ymdhms, mailSession

settings = load_settings()

class Session:
    """ The properties of a Session object are these:

        self.params     -> a cgi.FieldStorage() object
        self.session    -> a mdb session object
        self.Settlement -> an assets.Settlement object
        self.User       -> an assets.User object

    """

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
                self.set_current_settlement()


    def new(self, login):
        """ Creates a new session. Only needs a valid user login.

        Updates the session with a User object ('self.User') and a new Session
        object ('self.session'). """

        user = mdb.users.find_one({"login": login})
        mdb.sessions.remove({"login": user["login"]})

        session_dict = {
            "login": login,
            "created_on": datetime.now(),
            "current_view": "dashboard",
            "user_agent": {"is_mobile": get_user_agent().is_mobile, "browser": get_user_agent().browser },
        }
        session_id = mdb.sessions.insert(session_dict)
        self.session = mdb.sessions.find_one({"_id": ObjectId(session_id)})

        # update the user with the session ID
        user["current_session"] = session_id
        mdb.users.save(user)

        self.User = assets.User(user["_id"], session_object=self)

        return session_id   # passes this back to the html.create_cookie_js()


    def recover_password(self):
        """ Call this method to process params related to password recovery and
        return text that will be rendered by the index. """

        if "login" not in self.params and "recovery_code" not in self.params:
            return html.login.recover_password

        if "recovery_code" not in self.params:
            user = mdb.users.find_one({"login": self.params["login"].value})
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


    def set_current_settlement(self, settlement_id=False):
        """ Tries (hard) to set the current settlement.

        The best way is to use the 'settlement_id' kwarg and feed an ObjectId
        object. If you haven't got one of those, this func will back off to the
        current session's mdb object and try to set it from there.
        """
        if settlement_id:
            self.session["current_settlement"] = settlement_id

        if self.session is not None:
            if "current_settlement" in self.session.keys():
                s_id = ObjectId(self.session["current_settlement"])
                self.Settlement = assets.Settlement(settlement_id=s_id, session_object=self)

            # back off to current_asset if we haven't got current_settlement
            if self.Settlement is None:
                if "current_asset" in self.session.keys():
                    self.logger.info("set settlement from current_asset %s" % self.session["current_asset"])
                    s_id = ObjectId(self.session["current_asset"])
                    self.Settlement = assets.Settlement(settlement_id=s_id, session_object=self)

#        if self.Settlement is None:
#            self.logger.debug("Unable to set 'current_settlement' for session '%s'." % self.session["_id"])
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
            self.session["current_settlement"] = None
        if asset_id:
            asset = ObjectId(asset_id)
            self.session["current_asset"] = asset
            if target_view == "view_campaign":
                self.session["current_settlement"] = asset
                self.set_current_settlement(settlement_id = asset)
        mdb.sessions.save(self.session)
        self.session = mdb.sessions.find_one(self.session["_id"])


    def process_params(self, user_action=None):
        """ All cgi.FieldStorage() params passed to this object on init
        need to be processed. This does ALL OF THEM at once. """

        if "update_user_preferences" in self.params:
            self.User.update_preferences(self.params)
            user_action = "updated user preferences"

        if "change_password" in self.params:
            if "password" in self.params and "password_again" in self.params:
                self.User.update_password(self.params["password"].value, self.params["password_again"].value)
                user_action = "updated password"
            else:
                user_action = "failed to update password"

        if "change_view" in self.params:
            target_view = self.params["change_view"].value
            self.change_current_view(target_view)
            user_action = "changed view to %s" % target_view

        if "view_campaign" in self.params:
            self.change_current_view("view_campaign", asset_id=self.params["view_campaign"].value)
            user_action = "viewed campaign summary"
        if "view_settlement" in self.params:
            self.change_current_view("view_settlement", asset_id=self.params["view_settlement"].value)
            user_action = "viewed settlement form"
        if "view_survivor" in self.params:
            self.change_current_view("view_survivor", asset_id=self.params["view_survivor"].value)
            user_action = "viewed survivor form"

        # these are our two asset removal methods: this is as DRY as I think we
        #   can get with this stuff, since both require unique handling
        if "remove_settlement" in self.params:
            self.change_current_view("dashboard")
            s_id = ObjectId(self.params["remove_settlement"].value)
            S = assets.Settlement(settlement_id=s_id, session_object=self)
            S.delete()
            user_action = "removed settlement %s" % s_id
        if "remove_survivor" in self.params:
            survivor_id = ObjectId(self.params["remove_survivor"].value)
            S = assets.Survivor(survivor_id=survivor_id, session_object=self)
            S.delete()
            self.change_current_view("view_campaign", asset_id=S.survivor["settlement"])
            user_action = "removed survivor %s" % survivor_id

        # this is where we handle requests to create new assets
        if "bulk_add_survivors" in self.params:
            S = assets.Settlement(settlement_id=self.params["asset_id"].value, session_object=self)
            male = int(self.params["male_survivors"].value)
            female = int(self.params["female_survivors"].value)
            for s in range(male):
                m = assets.Survivor(params=None, session_object=self, suppress_event_logging=True)
                m.set_attrs({"public": "checked"})
            for s in range(female):
                f = assets.Survivor(params=None, session_object=self, suppress_event_logging=True)
                f.set_attrs({"public": "checked", "sex": "F"})
            S.log_event("%s male and %s female survivors joined the settlement!" % (male, female))
        if "new" in self.params:
            if self.params["new"].value == "settlement":
                if "settlement_name" in self.params:
                    settlement_name = self.params["settlement_name"].value
                else:
                    settlement_name = "Unknown"
                S = assets.Settlement(name=settlement_name, session_object=self)
                self.set_current_settlement(S.settlement["_id"])
                self.change_current_view("view_campaign", asset_id=S.settlement["_id"])
                if "create_survivors" in self.params:   # this could use a refactor, but it's functional so FIWE
                    self.Settlement.log_event("Added four new survivors and Starting Gear to settlement storage")
                    self.Settlement.add_game_asset("storage", "Founding Stone", 4)
                    self.Settlement.add_game_asset("storage", "Cloth", 4)
                    for i in range(2):
                        m = assets.Survivor(params=None, session_object=self, suppress_event_logging=True)
                        m.set_attrs({"Waist": 1})
                        m.join_hunting_party()
                    for i in range(2):
                        f = assets.Survivor(params=None, session_object=self, suppress_event_logging=True)
                        f.set_attrs({"sex": "F", "Waist": 1})
                        f.join_hunting_party()
                    user_action = "created settlement %s with First Story survivors" % S.get_name_and_id()
                else:
                    user_action = "created vanilla settlement %s" % S.get_name_and_id()
            if self.params["new"].value == "survivor":
                S = assets.Survivor(params=self.params, session_object=self)
                self.change_current_view("view_survivor", asset_id=S.survivor["_id"])
                user_action = "created survivor %s" % S.survivor["_id"]

        if "modify" in self.params:
            s_id = self.params["asset_id"].value
            if self.params["modify"].value == "settlement":
                S = assets.Settlement(settlement_id=s_id, session_object=self)
                S.modify(self.params)
                user_action = "modified settlement %s" % s_id
            if self.params["modify"].value == "survivor":
                S = assets.Survivor(survivor_id=s_id, session_object=self)
                S.modify(self.params)
                user_action = "modified survivor %s" % s_id

        if "return_hunting_party" in self.params:
            s_id = self.params["return_hunting_party"].value
            S = assets.Settlement(settlement_id=s_id, session_object=self)
            S.return_hunting_party()
            user_action = "returned hunting party to settlement %s" % s_id

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
            html.render(str(payload), http_headers="Content-Disposition: attachment; filename=%s\n" % (filename))
            user_action = "exported user data (%s)" % export_type
        if "export_campaign" in self.params:
            export_type = self.params["export_campaign"].value
            C = assets.Settlement(settlement_id=ObjectId(self.params["asset_id"].value), session_object=self)
            payload, length = C.export(export_type)
            filename = "%s_-_%s.%s" % (datetime.now().strftime(ymd), C.settlement["name"], export_type.lower())
            html.render(payload, http_headers="Content-type: application/octet-stream;\r\nContent-Disposition: attachment; filename=%s\r\nContent-Title: %s\r\nContent-Length: %i\r\n" % (filename, filename, length))
            user_action = "exported campaign data as %s" % export_type

        self.User.mark_usage(user_action)


    def log_out(self):
        """ For when the session needs to kill itself. """
        self.logger.debug("Ending session for '%s' via admin.remove_session()." % self.User.user["login"])
        admin.remove_session(self.session["_id"], "admin")


    def current_view_html(self):
        """ This func uses session's 'current_view' attribute to render the html
        for that view.

        The whole thing is wrapped in a gigantic try/except so that if we cannot
        create the HTML for whatever reason, we log it, end the user's session
        and return False. From there, html.render() will receive the False and
        print a generic message for the user.

        In a best case, we want this function to initialize a class (e.g. a
        Settlement or a Survivor or a User, etc.) and then use one of the render
        methods of that class to get html.

        Generally speaking, however, we're not above calling one of the methods
        of the html module to summon some html.

        Ideally, we will be able to refactor that kind of stuff out at some
        point, and use this function as a function that simply initalizes a
        class and uses that class's methods to get html.
        """
        try:
            body = None
            output = html.meta.saved_dialog

            if self.session["current_view"] != "dashboard":
                output += html.dashboard.home_button

            if self.session["current_view"] == "dashboard":
                body = "dashboard"
                output += self.User.html_motd()

                display_settlements = "none"
                display_campaigns = ""
                if self.User.get_campaigns() == "":
                    display_settlements = ""
                    display_campaigns = "none"
                output += html.dashboard.campaign_summary.safe_substitute(campaigns=self.User.get_campaigns(), display=display_campaigns)
                output += html.dashboard.settlement_summary.safe_substitute(settlements=self.User.get_settlements(return_as="asset_links"), display=display_settlements)
                output += html.dashboard.survivor_summary.safe_substitute(survivors=self.User.get_survivors("asset_links"))

                if mdb.the_dead.find({"complete": {"$exists": True}}).count() > 0:
                    output += self.User.html_world()

                if self.User.is_admin():
                    output += html.dashboard.panel_button
            elif self.session["current_view"] == "event_log":
                settlement = mdb.settlements.find_one({"_id": self.session["current_asset"]})
                self.set_current_settlement(ObjectId(settlement["_id"]))
                output += html.dashboard.refresh_button
                output += self.Settlement.asset_link(context="asset_management")
                S = assets.Settlement(settlement_id = settlement["_id"], session_object=self)
                output += S.render_html_event_log()
            elif self.session["current_view"] == "view_campaign":
                output += html.dashboard.refresh_button
                if mdb.settlement_events.find({"settlement_id": self.Settlement.settlement["_id"]}).count() != 0:
                    output += html.dashboard.event_log_button.safe_substitute(name=self.Settlement.settlement["name"])
                if self.Settlement.settlement is not None and self.Settlement.settlement["created_by"] == self.User.user["_id"]:
                    output += self.Settlement.asset_link(context="campaign_summary")
                output += self.Settlement.render_html_summary(user_id=self.User.user["_id"])
            elif self.session["current_view"] == "new_settlement":
                output += html.settlement.new
            elif self.session["current_view"] == "new_survivor":
                output += self.Settlement.asset_link(context="asset_management")
                options = self.User.get_settlements(return_as="html_option")
                output += html.survivor.new.safe_substitute(home_settlement=self.session["current_settlement"], user_email=self.User.user["login"], created_by=self.User.user["_id"], add_ancestors=self.Settlement.get_ancestors("html_parent_select"))
            elif self.session["current_view"] == "view_settlement":
                output += html.dashboard.refresh_button
                settlement = mdb.settlements.find_one({"_id": self.session["current_asset"]})
                self.set_current_settlement(ObjectId(settlement["_id"]))
                S = assets.Settlement(settlement_id = settlement["_id"], session_object=self)
                output += S.render_html_form()
            elif self.session["current_view"] == "view_survivor":
                output += html.dashboard.refresh_button
                survivor = mdb.survivors.find_one({"_id": self.session["current_asset"]})
                S = assets.Survivor(survivor_id = survivor["_id"], session_object=self)
                output += S.render_html_form()
            elif self.session["current_view"] == "panel":
                if self.User.is_admin():
                    P = admin.Panel(self.User.user["login"])
                    output += P.render_html()
                else:
                    output += "Nope"
            else:
                output += "UNKNOWN VIEW!!!"

            output += html.meta.log_out_button.safe_substitute(session_id=self.session["_id"], login=self.User.user["login"])

            if self.session["current_view"] == "dashboard":
                output += admin.dashboard_alert()

            return output, body

        except Exception as e:
            err_msg = "Caught exception while rendering current view for %s!" % self.User.get_name_and_id()
            self.logger.error(err_msg)
            self.logger.exception(e)
            self.log_out()
            tb = traceback.format_exc().replace("    ","&ensp;").replace("\n","<br/>")
            print html.meta.error_500.safe_substitute(msg=err_msg, exception=tb)
            sys.exit(255)

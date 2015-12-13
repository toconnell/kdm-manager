#!/usr/bin/env python

from bson.objectid import ObjectId
import Cookie
from datetime import datetime
import os

import admin
import assets
import html
import models
from utils import mdb, get_logger, get_user_agent, load_settings

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
            admin.remove_session(self.params["remove_session"].value)

        # try to retrieve a session and other session attributes from mdb using
        #   the browser cookie
        self.cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE"))

        if self.cookie is not None and "session" in self.cookie.keys():
            session_id = ObjectId(self.cookie["session"].value)
            self.session = mdb.sessions.find_one({"_id": session_id})
            if self.session is not None:
                user_object = mdb.users.find_one({"current_session": session_id})
                self.User = assets.User(user_object["_id"])
                self.set_current_settlement()


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
                self.Settlement = assets.Settlement(settlement_id=s_id)

            # back off to current_asset if we haven't got current_settlement
            if self.Settlement is None:
                if "current_asset" in self.session.keys():
                    self.logger.info("set settlement from current_asset %s" % self.session["current_asset"])
                    s_id = ObjectId(self.session["current_asset"])
                    self.Settlement = assets.Settlement(settlement_id=s_id)

        if self.Settlement is None:
            self.logger.debug("Unable to set 'current_settlement' for session '%s'." % self.session["_id"])
        mdb.sessions.save(self.session)


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

        self.User = assets.User(user["_id"])

        return session_id   # passes this back to the html.create_cookie_js()


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
            if target_view == "view_game":
                self.session["current_settlement"] = asset
                self.set_current_settlement(settlement_id = asset)
        mdb.sessions.save(self.session)
        self.session = mdb.sessions.find_one(self.session["_id"])


    def process_params(self):
        """ All cgi.FieldStorage() params passed to this object on init
        need to be processed. This does ALL OF THEM at once. """

        user_action = None  # we're going to log this below

        if "change_view" in self.params:
            target_view = self.params["change_view"].value
            self.change_current_view(target_view)
            user_action = "changed view to %s" % target_view

        if "view_game" in self.params:
            self.change_current_view("view_game", asset_id=self.params["view_game"].value)
            user_action = "viewed campaign summary"
        if "view_settlement" in self.params:
            self.change_current_view("view_settlement", asset_id=self.params["view_settlement"].value)
            user_action = "viewed settlement form"
        if "view_survivor" in self.params:
            self.change_current_view("view_survivor", asset_id=self.params["view_survivor"].value)
            user_action = "viewed survivor form"

        if "remove_settlement" in self.params:
            self.change_current_view("dashboard")
            settlement_id = ObjectId(self.params["remove_settlement"].value)
            survivors = mdb.survivors.find({"settlement": settlement_id})
            for survivor in survivors:
                mdb.survivors.remove({"_id": survivor["_id"]})
                self.logger.info("User '%s' removed survivor '%s'" % (self.User.user["login"], survivor["name"]))
            self.User.get_settlements()
            mdb.settlements.remove({"_id": settlement_id})
            self.logger.info("User '%s' removed settlement '%s'" % (self.User.user["login"], settlement_id))
            user_action = "removed settlement %s" % settlement_id

        if "remove_survivor" in self.params:
            self.change_current_view("dashboard")
            survivor_id = ObjectId(self.params["remove_survivor"].value)
            mdb.survivors.remove({"_id": survivor_id})
            user_action = "removed survivor %s" % survivor_id

        if "new" in self.params:
            if self.params["new"].value == "settlement":
                settlement_name = self.params["settlement_name"].value
                s = assets.Settlement(name=settlement_name, created_by=ObjectId(self.User.user["_id"]))
                self.set_current_settlement(s.settlement["_id"])
                self.change_current_view("view_game", asset_id=s.settlement["_id"])
                user_action = "created settlement %s" % s.settlement["_id"]
            if self.params["new"].value == "survivor":
                s = assets.Survivor(params=self.params)
                self.change_current_view("view_survivor", asset_id=s.survivor["_id"])
                user_action = "created survivor %s" % s.survivor["_id"]

        if "modify" in self.params:
            s_id = self.params["asset_id"].value
            if self.params["modify"].value == "settlement":
                S = assets.Settlement(settlement_id=s_id)
                S.modify(self.params)
                user_action = "modified settlement %s" % s_id
            if self.params["modify"].value == "survivor":
                S = assets.Survivor(survivor_id=s_id)
                S.modify(self.params)
                user_action = "modified survivor %s" % s_id

        if "return_hunting_party" in self.params:
            s_id = self.params["return_hunting_party"].value
            S = assets.Settlement(settlement_id=s_id)
            S.return_hunting_party()
            user_action = "returned hunting party to settlement %s" % s_id

        self.User.mark_usage(user_action)


    def log_out(self):
        """ For when the session needs to kill itself. """
        self.logger.debug("Ending session for '%s' via admin.remove_session()." % self.User.user["login"])
        admin.remove_session(self.session["_id"])


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
            output = html.meta.saved_dialog

            if self.session["current_view"] != "dashboard":
                output += html.dashboard.home_button

            if self.session["current_view"] == "dashboard":
                output += self.User.html_motd()

                display_settlements = "none"
                display_campaigns = ""
                if self.User.get_games() == "":
                    display_settlements = ""
                    display_campaigns = "none"
                output += html.dashboard.campaign_summary.safe_substitute(campaigns=self.User.get_games(), display=display_campaigns)
                output += html.dashboard.settlement_summary.safe_substitute(settlements=self.User.get_settlements(return_as="asset_links"), display=display_settlements)
                output += html.dashboard.survivor_summary.safe_substitute(survivors=self.User.get_survivors("asset_links"))
            elif self.session["current_view"] == "view_game":
                if self.Settlement.settlement["created_by"] == self.User.user["_id"]:
                    output += self.Settlement.asset_link(fixed=True, use_flash="settlement")
                output += self.Settlement.render_html_summary(user_id=self.User.user["_id"])
                # if session user owns the settlement, let him edit it
            elif self.session["current_view"] == "new_settlement":
                output += html.dashboard.new_settlement_form
            elif self.session["current_view"] == "new_survivor":
                options = self.User.get_settlements(return_as="html_option")
                output += html.survivor.new.safe_substitute(home_settlement=self.session["current_settlement"], user_email=self.User.user["login"], created_by=self.User.user["_id"])
            elif self.session["current_view"] == "view_settlement":
                settlement = mdb.settlements.find_one({"_id": self.session["current_asset"]})
                self.set_current_settlement(ObjectId(settlement["_id"]))
                S = assets.Settlement(settlement_id = settlement["_id"], user_object=self.User)
                output += S.render_html_form()
            elif self.session["current_view"] == "view_survivor":
                survivor = mdb.survivors.find_one({"_id": self.session["current_asset"]})
                S = assets.Survivor(survivor_id = survivor["_id"])
                output += S.render_html_form()
            else:
                output += "UNKNOWN VIEW!!!"


            output += html.meta.log_out_button.safe_substitute(session_id=self.session["_id"])
            return output

        except Exception as e:
            self.logger.critical("Caught exception while rendering current view!")
            self.logger.exception(e)
            self.log_out()
            return False

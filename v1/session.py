#!/usr/bin/env python

from bson.objectid import ObjectId
import Cookie
from datetime import datetime
import os

import assets
import html
import models
from utils import mdb, get_logger, get_user_agent, load_settings

settings = load_settings()

class Session:
    def __init__(self, params={}):
        self.params = params
        self.logger = get_logger()

        # we're not processing params yet, but if we have a log out request, we
        #   do it here, while we're initializing a new session object.
        if "remove_session" in self.params:
            mdb.sessions.remove({"_id": ObjectId(self.params["remove_session"].value)})
            self.logger.info(params)
            self.logger.info('Removed session %s' % self.params["remove_session"].value)

        self.session = None
        self.user = None

        try:
            self.cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
            if "session" in self.cookie.keys():
                try:
                    user_object = mdb.users.find_one({"current_session": ObjectId(self.cookie["session"].value)})
                    self.user = assets.User(user_object["_id"])
                    self.session = mdb.sessions.find_one({"_id": ObjectId(self.cookie["session"].value)})
                except:
                    pass
        except:
            pass


    def new(self, login):
        """ Creates a new session. Only needs a valid user login.

        Updates the session with a User object ('self.user') and a new Session
        object ('self.session'). """

        user = mdb.users.find_one({"login": login})
        mdb.sessions.remove({"login": user["login"]})

        session_dict = {
            "login": login,
            "created_on": datetime.now(),
            "current_view": "dashboard",
            "current_asset": None,
            "user_agent": {"is_mobile": get_user_agent().is_mobile, "browser": get_user_agent().browser },
        }
        session_id = mdb.sessions.insert(session_dict)
        self.session = mdb.sessions.find_one({"_id": ObjectId(session_id)})

        # update the user with the session ID
        user["current_session"] = session_id
        mdb.users.save(user)

        self.user = assets.User(user["_id"])

        return session_id   # passes this back to the html.create_cookie_js()


    def change_current_view(self, target_view, asset_id=False):
        """ Convenience function to update a session with a new current_view.

        'asset_id' is only mandatory if using 'view_survivor' or
        'view_settlement' as the 'target_view'.

        Otherwise, if you're just changing the view to 'dashbaord' or whatever,
        'asset_id' isn't mandatory.
        """
        self.session["current_view"] = target_view
        if asset_id:
            self.session["current_asset"] = ObjectId(asset_id)
        mdb.sessions.save(self.session)

    def set_current_settlement(self, settlement_id):
        self.session["current_settlement"] = settlement_id
        mdb.sessions.save(self.session)

    def process_params(self):
        """ All cgi.FieldStorage() params passed to this object on init
        need to be processed. This does ALL OF THEM at once. """

        if "change_view" in self.params:
            self.change_current_view(self.params["change_view"].value)

        if "view_settlement" in self.params:
            self.change_current_view("view_settlement", asset_id=self.params["view_settlement"].value)
        if "view_survivor" in self.params:
            self.change_current_view("view_survivor", asset_id=self.params["view_survivor"].value)

        if "remove_settlement" in self.params:
            self.change_current_view("dashboard")
            settlement_id = ObjectId(self.params["remove_settlement"].value)
            survivors = mdb.survivors.find({"settlement": settlement_id})
            for survivor in survivors:
                mdb.survivors.remove({"_id": survivor["_id"]})
                self.logger.info("User '%s' removed survivor '%s'" % (self.user.user["login"], survivor["name"]))
            mdb.settlements.remove({"_id": settlement_id})
            self.logger.info("User '%s' removed settlement '%s'" % (self.user.user["login"], settlement_id))

        if "remove_survivor" in self.params:
            self.change_current_view("dashboard")
            mdb.survivors.remove({"_id": ObjectId(self.params["remove_survivor"].value)})

        if "new" in self.params:
            if self.params["new"].value == "settlement":
                settlement_name = self.params["settlement_name"].value
                assets.Settlement(name=settlement_name, created_by=ObjectId(self.user.user["_id"]))
                self.change_current_view("dashboard")
            if self.params["new"].value == "survivor":
                s = assets.Survivor(params=self.params)
                self.change_current_view("view_survivor", asset_id=s.survivor["_id"])

        if "modify" in self.params:
            if self.params["modify"].value == "settlement":
                assets.update_settlement(self.params)
            if self.params["modify"].value == "survivor":
                S = assets.Survivor(survivor_id=self.params["asset_id"].value)
                S.modify(self.params)

    def current_view_html(self):
        """ This func uses session's 'current_view' attribute to render the html
        for that view.

        In a best case, we want this function to initialize a class (e.g. a
        Settlement or a Survivor or a User, etc.) and then use one of the render
        methods of that class to get html.

        Generally speaking, however, we're not above calling one of the methods
        of the html module to summon some html.

        Ideally, we will be able to refactor that kind of stuff out at some
        point, and use this function as a function that simply initalizes a
        class and uses that class's methods to get html.
        """

        output = ""

        if self.session["current_view"] != "dashboard":
            output = html.dashboard.home_button

        if self.session["current_view"] == "dashboard":
            output += html.dashboard.headline.safe_substitute(title="Settlements", desc="Manage settlements created by you.")
            settlements = self.user.get_settlements()
            for s in settlements:
                output += html.dashboard.view_asset_button.safe_substitute(asset_type="settlement", asset_id=s["_id"], asset_name=s["name"])
            output += html.dashboard.new_settlement_button
            output += html.dashboard.headline.safe_substitute(title="Survivors", desc="Manage survivors created by you or shared with you. New survivors are created from the Settlement Menu.")
            survivors = self.user.get_survivors()
            for s in survivors:
                survivor_settlement = mdb.settlements.find_one({"_id": s["settlement"]})
                survivor_name = "%s (%s)" % (s["name"], survivor_settlement["name"])
                output += html.dashboard.view_asset_button.safe_substitute(asset_type="survivor", asset_id=s["_id"], asset_name=survivor_name)
            output += html.dashboard.headline.safe_substitute(title="Notes", desc="KD:M Manager! Version %s" % settings.get("application","version"))
        elif self.session["current_view"] == "new_settlement":
            output += html.dashboard.new_settlement_form
        elif self.session["current_view"] == "new_survivor":
            options = self.user.get_settlements(return_as="html_option")
            output += html.dashboard.new_survivor_form.safe_substitute(home_settlement=self.session["current_settlement"], user_email=self.user.user["login"], created_by=self.user.user["_id"])
        elif self.session["current_view"] == "view_settlement":
            #
            #   logic for read-only settlement views will go here
            #
            settlement = mdb.settlements.find_one({"_id": self.session["current_asset"]})
            self.set_current_settlement(ObjectId(settlement["_id"]))
            S = assets.Settlement(settlement_id = settlement["_id"])
            output += S.render_html_form()
        elif self.session["current_view"] == "view_survivor":
            survivor = mdb.survivors.find_one({"_id": self.session["current_asset"]})
            S = assets.Survivor(survivor_id = survivor["_id"])
            output += S.render_html_form()
        else:
            output += "UNKNOWN VIEW!!!"

        output += html.meta.log_out_button.safe_substitute(session_id=self.session["_id"])
        return output

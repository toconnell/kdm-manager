#!/usr/bin/env python

from bson.objectid import ObjectId
import Cookie
from datetime import datetime
import os

from utils import mdb, get_logger, get_user_agent
import html

class initialize:
    def __init__(self, params={}):
        self.params = params
        self.logger = get_logger()

        # we're not processing params yet, but if we have a log out request, we
        #   do it here, while we're initializing a new session object.
        if "remove_session" in self.params:
            mdb.sessions.remove({"_id": ObjectId(self.params["remove_session"].value)})

        self.session = None
        self.user = None

        try:
            self.cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
            if "session" in self.cookie.keys():
                try:
                    self.user = mdb.users.find_one({"current_session": ObjectId(self.cookie["session"].value)})
                    self.session = mdb.sessions.find_one({"_id": ObjectId(self.cookie["session"].value)})
                except:
                    pass
        except:
            pass

    def create_new(self, login):
        """ """
        self.user = mdb.users.find_one({"login": login})
        mdb.sessions.remove({"login": self.user["login"]})

        session_dict = {
            "login": login,
            "created_on": datetime.now(),
            "current_view": "dashboard",
            "user_agent": {"is_mobile": get_user_agent().is_mobile, "browser": get_user_agent().browser },
        }
        session_id = mdb.sessions.insert(session_dict)
        self.session = mdb.sessions.find_one({"_id": ObjectId(session_id)})

        # update the user with the session ID
        self.user["current_session"] = session_id
        mdb.users.save(self.user)

        return session_id   # passes this back to the html.create_cookie_js()

    def change_current_view(self, target_view):
        self.session["current_view"] = target_view
        mdb.sessions.save(self.session)

    def process_params(self):
        """ All cgi.FieldStorage() params passed to this object on init
        need to be processed. This does ALL OF THEM at once. """

        if "change_view" in self.params:
            self.change_current_view(self.params["change_view"].value)

        if "view_settlement" in self.params:
            self.change_current_view("view_settlement")
            self.session["current_asset"] = ObjectId(self.params["view_settlement"].value)
            mdb.sessions.save(self.session)

        if "new" in self.params:
            if self.params["new"].value == "settlement":
                settlement_name = self.params["settlement_name"].value
                new_settlement_dict = {
                    "created_on": datetime.now(),
                    "created_by": ObjectId(self.user["_id"]),
                    "name": settlement_name,
                    "survival_limit": 1,
                    "lantern_year": 1,
                    "death_count": 0,
                    "milestone_story_events": [],
                    "innovations": ["Language"],
                    "principles": [],
                    "locations": ["Lantern Hoard"],
                    "quarries": ["White Lion"],
                    "storage": [],
                    "defeated_monsters": [],
                    "population": 0,
                    "lost_settlements": 0,
                }
                mdb.settlements.save(new_settlement_dict)
                self.logger.info("User '%s' created the settlement '%s'" % (self.user["login"], settlement_name))
                self.change_current_view("dashboard")

    def current_view_html(self):
        output = html.dashboard.home_button

        if self.session["current_view"] == "dashboard":
            output += html.dashboard.headline.safe_substitute(title="Settlements")
            settlements = mdb.settlements.find({"created_by": self.user["_id"]})
            for s in settlements:
                output += html.dashboard.view_asset_button.safe_substitute(asset_type="settlement", asset_id=s["_id"], asset_name=s["name"])
            output += html.dashboard.new_settlement_button
            output += html.dashboard.headline.safe_substitute(title="Survivors")
            output += html.dashboard.headline.safe_substitute(title="Notes")
        elif self.session["current_view"] == "new_settlement":
            output += html.dashboard.new_settlement_form
        elif self.session["current_view"] == "view_settlement":
            settlement = mdb.settlements.find_one({"_id": self.session["current_asset"]})
            output += html.settlement.form.safe_substitute(name=settlement["name"])
        else:
            output += "UNKNOWN VIEW!!!"

        output += html.meta.log_out_button.safe_substitute(session_id=self.session["_id"])
        return output

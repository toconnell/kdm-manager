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

        if "remove_settlement" in self.params:
            self.change_current_view("dashboard")
            mdb.settlements.remove({"_id": ObjectId(self.params["remove_settlement"].value)})

        if "new" in self.params:
            if self.params["new"].value == "settlement":
                settlement_name = self.params["settlement_name"].value
                assets.Settlement(name=settlement_name, created_by=ObjectId(self.user["_id"]))
                self.change_current_view("dashboard")

        if "modify" in self.params:
            if self.params["modify"].value == "settlement":
                assets.update_settlement(self.params)

    def current_view_html(self):
        output = ""
        if self.session["current_view"] != "dashboard":
            output = html.dashboard.home_button

        if self.session["current_view"] == "dashboard":
            output += html.dashboard.headline.safe_substitute(title="Settlements")
            settlements = mdb.settlements.find({"created_by": self.user["_id"]}).sort("name")
            for s in settlements:
                output += html.dashboard.view_asset_button.safe_substitute(asset_type="settlement", asset_id=s["_id"], asset_name=s["name"])
            output += html.dashboard.new_settlement_button
            output += html.dashboard.headline.safe_substitute(title="Survivors")
            output += html.dashboard.headline.safe_substitute(title="Notes")
        elif self.session["current_view"] == "new_settlement":
            output += html.dashboard.new_settlement_form
        elif self.session["current_view"] == "view_settlement":
            settlement = mdb.settlements.find_one({"_id": self.session["current_asset"]})

            S = assets.Settlement(settlement_id = settlement["_id"])

            hide_new_life_principle = "hidden"
            first_child = ""
            if "First child is born" in settlement["milestone_story_events"]:
                hide_new_life_principle = ""
                first_child = "checked"

            hide_death_principle = "hidden"
            first_death = ""
            if "First time death count is updated" in settlement["milestone_story_events"]:
                hide_death_principle = ""
                first_death = "checked"
            if int(settlement["death_count"]) > 0:
                hide_death_principle = ""

            hide_society_principle = "hidden"
            pop_15 = ""
            if "Population reaches 15" in settlement["milestone_story_events"]:
                hide_society_principle = ""
                pop_15 = "checked"
            if int(settlement["population"]) > 14:
                hide_society_principle = ""

            hide_conviction_principle = "hidden"
            if int(settlement["lantern_year"]) >= 12:
                hide_conviction_principle = ""

            cannibalize = ""
            if "Cannibalize" in settlement["principles"]:
                cannibalize = "checked"
            graves = ""
            if "Graves" in settlement["principles"]:
                graves = "checked"

            protect_the_young = ""
            if "Protect the Young" in settlement["principles"]:
                protect_the_young = "checked"
            survival_of_the_fittest = ""
            if "Survival of the Fittest" in settlement["principles"]:
                survival_of_the_fittest = "checked"

            collective_toil = ""
            if "Collective Toil" in settlement["principles"]:
                collective_toil = "checked"
            accept_darkness = ""
            if "Accept Darkness" in settlement["principles"]:
                accept_darkness = "checked"

            barbaric = ""
            if "Barbaric" in settlement["principles"]:
                barbaric = "checked"
            romantic = ""
            if "Romantic" in settlement["principles"]:
                romantic = "checked"


            five_innovations = ""
            if "Settlement has 5 innovations" in settlement["milestone_story_events"]:
                five_innovations = "checked"
            game_over = ""
            if "Population reaches 0" in settlement["milestone_story_events"]:
                game_over = "checked"

            survival_limit = int(settlement["survival_limit"])
            if survival_limit < S.get_min_survival_limit():
                survival_limit = S.get_min_survival_limit()

            output += html.settlement.form.safe_substitute(
                MEDIA_URL = settings.get("application","STATIC_URL"),
                settlement_id = settlement["_id"],

                population = settlement["population"],
                name = settlement["name"],
                survival_limit = survival_limit,
                min_survival_limit = S.get_min_survival_limit(),
                death_count = settlement["death_count"],
                lost_settlements = settlement["lost_settlements"],

                departure_bonuses = S.get_bonuses('departure_buff'),
                settlement_bonuses = S.get_bonuses('settlement_buff'),

                items_options = models.render_item_dict(return_as="html_select_box"),
                items_remove = S.get_storage(return_as="drop_list"),
                storage = S.get_storage(return_as="html_buttons"),

                new_life_principle_hidden = hide_new_life_principle,
                society_principle_hidden = hide_society_principle,
                death_principle_hidden = hide_death_principle,
                conviction_principle_hidden = hide_conviction_principle,

                cannibalize_checked = cannibalize,
                graves_checked = graves,
                protect_the_young_checked = protect_the_young,
                survival_of_the_fittest_checked = survival_of_the_fittest,
                collective_toil_checked = collective_toil,
                accept_darkness_checked = accept_darkness,
                barbaric_checked = barbaric,
                romantic_checked = romantic,

                lantern_year = settlement["lantern_year"],
                timeline = S.get_timeline(return_as="html"),

                first_child_checked = first_child,
                first_death_checked = first_death,
                pop_15_checked = pop_15,
                five_innovations_checked = five_innovations,
                game_over_checked = game_over,

                nemesis_monsters = S.get_nemesis_monsters(return_as="html_select"),

                quarries = ", ".join(settlement["quarries"]),
                quarry_options = "</option><option>".join(sorted(models.quarries.keys())),
                innovations = S.get_innovations(return_as="comma-delimited"),
                innovation_options = S.get_innovation_deck(return_as="html_option"),
                locations = S.get_locations(return_as="comma-delimited"),
                locations_options = S.get_locations_deck(return_as="html_option"),

                defeated_monsters = ", ".join(sorted(settlement["defeated_monsters"])),

            )
        else:
            output += "UNKNOWN VIEW!!!"

        output += html.meta.log_out_button.safe_substitute(session_id=self.session["_id"])
        return output

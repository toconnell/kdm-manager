#!/usr/bin/env python

from bson.objectid import ObjectId
from bson import json_util
from copy import copy
from collections import defaultdict
from cStringIO import StringIO
from datetime import datetime, timedelta
import gridfs
from hashlib import md5
from PIL import Image
import inspect
import json
import operator
import os
import pickle
import random
from string import Template, capwords, punctuation
import time
import types

import api
import admin
from modular_assets import survivor_attrib_controls
import html
from session import Session
from utils import mdb, get_logger, load_settings, get_user_agent, ymdhms, stack_list, to_handle, thirty_days_ago, recent_session_cutoff, ymd, u_to_str

settings = load_settings()


def ua_decorator(render_func=None):
    """ Decorate User Asset render methods with this guy to get some additional
    template variables and header/footer HTML. The 'render_func' kwarg must be
    a User Asset HTML-rendering method.

    We do a few things here:

        - take the output of the render method (as a string), turn it back
        into a template and then plug in some additional variables from the
        self.User object, etc.
        - tack on some additional HTML to the literal bottom of the second
        rendering pass (i.e. the one that happens in the previous bullet)

    """

    if render_func is None:
        raise Exception("This decorator must wrap a User Asset HTML rendering method!")

    def wrapper(self, *args, **kwargs):

        view_html = Template(render_func(self, *args, **kwargs))

        return view_html.safe_substitute(

            application_version = settings.get("application", "version"),

            # angularjs appRoot and other app stuff
            MEDIA_URL = settings.get("application", "STATIC_URL"),
            user_login = self.User.user["login"],
            user_id = self.User.user["_id"],
            settlement_id = self.Session.Settlement.settlement["_id"],

        ) + html.angularJS.settlement_notes + html.angularJS.hunt_phase

    return wrapper



class User:

    def __init__(self, user_id, session_object=None):
        """ Initialize with a user's _id to create an object with his complete
        user object and all settlements. Like all asset classes, you cannot
        initialize this one without a valid session object. """

        self.logger = get_logger()
        user_id = ObjectId(user_id)
        self.user = mdb.users.find_one({"_id": user_id})

        # 2017-11-13 - sign-in bug - https://github.com/toconnell/kdm-manager/issues/401
        if not 'preferences' in self.user.keys():
            self.user['preferences'] = {}
            self.logger.warn("%s Adding 'preferences' attribute to user!" % self)
            self.save()

        self.Session = session_object
        if self.Session is None:
            raise Exception("User Objects may not be initialized without a session object!")



    def __repr__(self):
        return self.get_name_and_id()


    def save(self):
        """ Save method for user objects. """

        mdb.users.save(self.user)
        self.logger.info("[%s] saved changes to %s" % (self, self))


    def mark_usage(self, action=None):
        """ Updates the user's mdb object with some data. """
        self.user["latest_action"] = action
        self.user["latest_activity"] = datetime.now()
        self.user["latest_user_agent"] = str(get_user_agent())
        mdb.users.save(self.user)


    def update_password(self, password, password_again=False):
        """ Leave the 'password_again' kwarg blank if you're not checking two
        passwords to see if they match, e.g. if you're doing this from the CLI.
        """

        user_admin_log_dict = {
            "created_on": datetime.now(),
            "u_id": self.user["_id"],
        }

        if password_again:
            if password != password_again:
                err_msg = "Could not change password for '%s' (passwords did not match)!" % self.user["login"]
                self.logger.error(err_msg)
                user_admin_log_dict["msg"] = err_msg
                mdb.user_admin.insert(user_admin_log_dict)
                return False
        self.user["password"] = md5(password).hexdigest()
        self.logger.info("Password update for '%s' was successful!" % self.user["login"])
        mdb.users.save(self.user)
        user_admin_log_dict["msg"] = "Password Updated!"
        mdb.user_admin.insert(user_admin_log_dict)
        return True



    def is_admin(self):
        """ Returns True if the user is an application admin. This only returns
        python bools because it should only be used for internal application
        logic and so on.

        Check out the is_settlement_admin() method if you're
        working in user-space."""

        if "admin" in self.user.keys() and type(self.user["admin"]) == datetime:
            return True
        else:
            return False


    def is_settlement_admin(self, return_type=None):
        """ Checks self.Session.Settlement.settlement admins to see if the user
        is a settlement admin. Returns a python bool by default, but can also
        return JS-friendly 'truthy/falsy' strings if required. """

        is_settlement_admin = False

        if self.user["_id"] == self.Session.Settlement.settlement["created_by"]:
            is_settlement_admin = True
        elif "admins" in self.Session.Settlement.settlement.keys():
            if self.user["login"] in self.Session.Settlement.settlement["admins"]:
                is_settlement_admin = True

        if return_type == "truthy":
            return str(is_settlement_admin).lower()

        return is_settlement_admin


    def get_name_and_id(self):
        """ Returns a string of the user login and _id value. """
        return "%s (%s)" % (self.user["login"], self.user["_id"])


    def dump_assets(self, dump_type=None):
        """ Returns a dictionary representation of a user's complete assets. Due
        to the...kind of arbitrary design of things, this is a multi-stage sort
        of export: first we get the user info and the user's settlements and
        settlement events, then we get his survivors in a separate bit of logic.
        The last thing we do is get his GridFS stuff, e.g. avatars."""

        self.logger.debug("Beginning '%s' dump for %s" % (dump_type, self))

        assets_dict = {
            "user": self.user,
            "settlements": list(mdb.settlements.find({"created_by": self.user["_id"]})),
            "settlement_events": list(mdb.settlement_events.find({"created_by": self.user["_id"]})),
            "survivors": [],
            "avatars": [],
        }

        # get all survivors (including those created by other users) for the
        #   user's settlements; then get all survivors created by the user.
        for s in assets_dict["settlements"]:
            assets_dict["settlement_events"].extend(mdb.settlement_events.find({"settlement_id": s["_id"]}))
            survivors = mdb.survivors.find({"settlement": s["_id"]})
            assets_dict["survivors"].extend(survivors)
        other_survivors = mdb.survivors.find({"created_by": self.user["_id"]})
        for s in other_survivors:
            if s not in assets_dict["survivors"]:
                assets_dict["survivors"].append(s)
        self.logger.debug("Dumping %s survivors for %s" % (len(assets_dict["survivors"]), self.get_name_and_id()))

        # now we have to go to GridFS to get avatars
        for s in assets_dict["survivors"]:
            if "avatar" in s.keys():
                try:
                    img = gridfs.GridFS(mdb).get(ObjectId(s["avatar"]))
                    img_dict = {
                        "blob": img.read(),
                        "_id": ObjectId(s["avatar"]),
                        "content_type": img.content_type,
                        "created_by": img.created_by,
                        "created_on": img.created_on,
                    }
                    assets_dict["avatars"].append(img_dict)
                except gridfs.errors.NoFile:
                    self.logger.error("Could not retrieve avatar for survivor %s during asset dump!" % s["_id"])

        # some quick debug tallies
        for a in ["settlements","survivors","avatars"]:
            self.logger.debug("Added %s %s to asset dump for %s." % (len(assets_dict[a]), a, self.get_name_and_id()))

        # now we (finally) do returns:
        if dump_type == "pickle":
            return pickle.dumps(assets_dict)
        elif dump_type == "json":
            return json.dumps(assets_dict, default=json_util.default)

        return assets_dict



    def get_survivors(self, return_type=False):
        """ Returns all of the survivors that a user can access. Leave
        the 'return_type' kwarg unspecified/False if you want a mongo cursor
        back (instead of fruity HTML crap). """

        survivors = list(mdb.survivors.find({"$or": [
            {"email": self.user["login"]},
            {"created_by": self.user["_id"]},
            ], "removed": {"$exists": False}}
        ).sort("name"))

        # user version

        if return_type == "asset_links":
            output = ""
            for s in survivors:
                S = Survivor(survivor_id=s["_id"], session_object=self.Session)
                output += S.asset_link()
            return output

        return survivors



    def mark_auth(self, auth_dt=None):
        self.mark_usage("successful sign-in")
        self.user["latest_succesful_authentication"] = auth_dt
        mdb.users.save(self.user)






#
#   SURVIVOR CLASS
#

class Survivor:


    def __repr__(self):
        return self.get_name_and_id(include_id=False, include_sex=True)


    def __init__(self, survivor_id=None, params=None, session_object=None, suppress_event_logging=False, update_mins=True):
        """ Initialize this with a cgi.FieldStorage() as the 'params' kwarg
        to create a new survivor. Otherwise, use a mdb survivor _id value
        to initalize with survivor data from mongo. """

        self.logger = get_logger()

        self.suppress_event_logging = suppress_event_logging
        self.update_mins = update_mins
        self.damage_locations = [
            "brain_damage_light",
            "head_damage_heavy",
            "arms_damage_light",
            "arms_damage_heavy",
            "body_damage_light",
            "body_damage_heavy",
            "waist_damage_light",
            "waist_damage_heavy",
            "legs_damage_light",
            "legs_damage_heavy",
        ]
        self.flag_attribs = [
            "cannot_spend_survival",
            "cannot_use_fighting_arts",
            "skip_next_hunt",
            "dead",
            "retired",
            "favorite",
            "public",
        ]
        self.flags = self.damage_locations + self.flag_attribs


        #
        #   Now start initializing and setting object attribs
        #

        self.survivor = None
        if survivor_id is not None:
            self.survivor = mdb.survivors.find_one({"_id": ObjectId(survivor_id)})

        # whether we've got a survivor from MDB or not, set the attribs of the 
        #   survivor object, because we'll need them for everything below here
        self.set_objects_from_session(session_object)

        # make a new survivor if we haven't retrieved one
        if self.survivor is None:
            survivor_id = self.new(params)


        if self.Settlement is not None:
            self.normalize()


    #
    #   Survivor meta and manager-only methods below
    #


    def set_objects_from_session(self, session_object=None):
        """ Tries (hard) to set the current self.Session, .User and .Settlement.
        Makes a ton of noise if it can't. """

        self.Session = session_object

        if self.Session is None or not self.Session:
            err_msg = "Survivor objects may not be initialized without a Session object!"
            self.logger.error(err_msg)
            raise Exception(err_msg)

        self.User = session_object.User
        if self.User is None or not self.User:
            self.logger.error("Survivor objects should not be initialized without a User object!")
            self.logger.critical("Initializing without a User obejct...")

        self.Settlement = session_object.Settlement
        if self.Settlement is None or not self.Settlement:
            if self.survivor is not None:
                self.Settlement = Settlement(settlement_id=self.survivor["settlement"], session_object=self.Session)
            else:
                self.logger.warn("[%s] initializing survivor object without a Settlement..." % (self.User))


    def save(self, quiet=False):
        """ Saves a survivor's self.survivor to the mdb. Logs it. """
        mdb.survivors.save(self.survivor)
        if not quiet:
            self.logger.debug("[%s] saved changes to %s" % (self.User, self))


    def normalize(self):
        """ Run this when a Survivor object is initialized: it will enforce
        the data model and apply settlements defaults to the survivor. """

        # 2016-11 RANDOM_FIGHTING_ART bug
        if "RANDOM_FIGHTING_ART" in self.survivor["fighting_arts"]:
            self.survivor["fighting_arts"].remove("RANDOM_FIGHTING_ART")

        # see if we need to retire this guy, based on recent updates
        if int(self.survivor["hunt_xp"]) >= 16 and not "retired" in self.survivor.keys():
            self.retire()


        # if the survivor is legacy data model, he doesn't have a born_in_ly
        #   attrib, so we have to get him one:
        if not "born_in_ly" in self.survivor.keys():
            self.logger.warn("%s has no 'born_in_ly' value!" % self)
            if "father" not in self.survivor.keys() and "mother" not in self.survivor.keys():
                self.logger.warn("Defaulting birth year to 1 for %s" % self)
                self.survivor["born_in_ly"] = 1
            parent_birth_years = [self.Settlement.get_ly() - 1]
            for p in ["father","mother"]:
                if p in self.survivor.keys():
                    P = Survivor(survivor_id=self.survivor[p], session_object=self.Session)
                    if not "born_in_ly" in P.survivor.keys():
                        self.logger.warn("%s has no 'born_in_ly' value!" % P.get_name_and_id())
                    else:
                        self.logger.debug("%s %s was born in LY %s" % (p.capitalize(), P, P.survivor["born_in_ly"]))
                        parent_birth_years.append(P.survivor["born_in_ly"])
            self.logger.debug("Highest parent birth year is %s for %s: (%s parents)" % (max(parent_birth_years), self, (len(parent_birth_years) - 1)))
            self.survivor["born_in_ly"] = max(parent_birth_years) + 1
            self.logger.warn("Defaulting birth year to %s for %s" % (self.survivor["born_in_ly"], self))

        # if "father" or "mother" keys aren't Object ID's, we need to normalize them:
        for p in ["father","mother"]:
            if p in self.survivor.keys() and type(self.survivor[p]) == unicode:
                self.logger.warn("Normalizing unicode '%s' value to bson ObjectID for %s" % (p, self.get_name_and_id()))
                self.survivor[p] = ObjectId(self.survivor[p])

        # delete bogus attribs
        for a in ["view_game"]:
            if a in self.survivor.keys():
                del self.survivor[a]
                self.logger.debug("Automatically removed bogus key '%s' from %s." % (a, self.get_name_and_id()))

        self.save(quiet=True)



    def remove(self):
        """ Marks the survivor 'removed' with a datetime.now(). """

        self.logger.info("[%s] removing survivor %s" % (self.User, self))
        self.survivor["removed"] = datetime.now()
        self.save()

        self.Settlement.increment_population(-1)

        self.Settlement.log_event("%s has <b>permanently removed</b> %s from the settlement!" % (self.User.user["login"], self))
        self.logger.warn("[%s] marked %s as removed!" % (self.User, self))



    def get_name_and_id(self, include_id=True, include_sex=False):
        """ Laziness function to return a string of the Survivor's name, _id and
        sex values (i.e. so we can write DRYer log entries, etc.). """

        output = [self.survivor["name"]]
        if include_sex:
            output.append("[%s]" % self.survivor["sex"])
        if include_id:
            output.append("(%s)" % self.survivor["_id"])
        return " ".join(output)


    def is_founder(self):
        """ Returns True or False, erring on the side of False. We only want to
        return True when we're sure the survivor was a founder. """

        if not "born_in_ly" in self.survivor.keys():
            return False

        if "father" in self.survivor.keys() or "mother" in self.survivor.keys():
            return False

        if self.survivor["born_in_ly"] == 0:
            return True
        elif "founder" in self.survivor["epithets"]:
            return True
        else:
            return False


    def retire(self):
        """ Retires the survivor. Saves them afterwards, since this can be done
        pretty much anywhere.  This is the only way a survivor should ever be
        retired: if you're doing it somewhere else, fucking stop it."""

        self.survivor["retired"] = "checked"
        self.survivor["retired_in"] = self.Settlement.settlement["lantern_year"]
        self.logger.debug("[%s] just retired %s" % (self.User, self))
        self.Settlement.log_event("%s has retired." % self)
        mdb.survivors.save(self.survivor)


    def get_returning_survivor_status(self, return_type=None):
        """ Returns a bool of whether the survivor is currently a Returning
        Survivor. Use different return_type values for prettiness. """

        cur_ly = self.Settlement.get_ly()

        departing = False
        if cur_ly in self.get_returning_survivor_years():
            departing = True

        returning = False
        if cur_ly - 1 in self.get_returning_survivor_years():
            returning = True

        if return_type == "html_badge":
            if not returning and not departing:
                return ""

            if returning:
                r_tup = ("R%s" % (cur_ly-1), "returning_survivor_badge_color", "Returning survivor in LY %s" % (cur_ly - 1))
            if departing:
                r_tup = ("R%s" % (cur_ly), "departing_survivor_badge_color", "Returning survivor in LY %s" % cur_ly)

            letter, color, title = r_tup
            return html.survivor.returning_survivor_badge.safe_substitute(
                flag_letter = letter,
                color_class = color,
                div_title = title,
            )

        return returning


    def toggle(self, toggle_key, toggle_value, toggle_type="implicit"):
        """ Toggles an attribute on or off. The 'toggle_value' arg is either
        going to be a MiniFieldStorage list (from cgi.FieldStorage) or its going
        to be a single value, e.g. a string.

        If it's a list, assume we're toggling something on; if it's a single
        value, assume we're toggling it off.

        Review the hidden form inputs to see more about how this works.
        """

        # handle explicit toggles (i.e. input[type=submit] here)
        if "damage" in toggle_key.split("_"):
            toggle_type="explicit"


        if toggle_type == "explicit":
            if toggle_key not in self.survivor.keys():
                self.survivor[toggle_key] = "checked"
                self.logger.debug("%s toggled '%s' ON for survivor %s." % (self.User.user["login"], toggle_key, self.get_name_and_id()))
                if toggle_key == "retired":
                    self.retire()
                return True
            elif toggle_key in self.survivor.keys():
                del self.survivor[toggle_key]
                self.logger.debug("[%s] toggled '%s' OFF for survivor %s." % (self.User, toggle_key, self))
                return True

        mdb.survivors.save(self.survivor)



    def get_constellation(self, return_type=None):
        """ Returns the survivor's constellation. Non if they haven't got one.
        Use the 'html_badge' return type for asset links. """

        const = None
        if "constellation" in self.survivor.keys():
            const = self.survivor["constellation"]

        if return_type == "html_badge":
            if const:
                return html.survivor.survivor_constellation_badge.safe_substitute(value=const)
            else:
                return ""

        return const



    def remove_survivor_attribute(self, attrib):
        """ Tries to delete an attribute from a survivor's MDB document. Fails
        gracefully if it cannot. Includes special handling for certain
        attributes. """

        try:
            del self.survivor[attrib]
            self.logger.debug("[%s] removed '%s' key from %s" % (self.User, attrib, self))
        except:
            self.logger.error("[%s] attempted to remove '%s' key from %s, but that key does not exist!" % self.User, attrib, self)



    def get_returning_survivor_years(self):
        """ Returns a list of integers representing the lantern years during
        which a survivor is considered to be a Returning Survivor. """

        if not "returning_survivor" in self.survivor.keys():
            return []
        else:
            return self.survivor["returning_survivor"]



    def asset_link(self, view="survivor", button_class="survivor", link_text=False, include=["hunt_xp", "insanity", "sex", "dead", "retired", "returning"], disabled=False):
        """ Returns an asset link (i.e. html form with button) for the
        survivor. """

        if not link_text:
            link_text = '<b>%s</b>' % self.survivor["name"]
            if "sex" in include:
                link_text += " [%s]" % self.get_api_asset("effective_sex")

        if disabled:
            link_text += "<br />%s" % self.survivor["email"]

        if include != []:
            attribs = []


            if "dead" in include:
                if "dead" in self.survivor.keys():
                    button_class = "grey"
                    attribs.append("Dead")

            if "retired" in include:
                if "retired" in self.survivor.keys():
                    button_class = "warn"
                    attribs.append("Retired")

            if "settlement_name" in include:
                attribs.append(self.Settlement.settlement["name"])

            if "hunt_xp" in include:
                attribs.append("XP: %s" % self.survivor["hunt_xp"])

            if "insanity" in include:
                attribs.append("Insanity: %s" % self.survivor["Insanity"])

            if attribs != []:
                suffix = "<br /> "
                suffix += ", ".join(attribs)
                suffix += ""
                link_text += suffix

        if disabled:
            disabled = "disabled"
            button_class= "unclickable"

        output = html.dashboard.view_asset_button.safe_substitute(
            button_class = button_class,
            asset_type = view,
            asset_id = self.survivor["_id"],
            asset_name = link_text,
            disabled = disabled,
            desktop_text = "",
        )

        return output





    @ua_decorator
    def render_html_form(self):
        """ Render a Survivor Sheet for the survivor. MUST be wrapped in the
        ua_decorator func to work!
        """
        return html.survivor.form.safe_substitute(survivor_id = self.survivor["_id"])



#
#   SETTLEMENT CLASS
#

class Settlement:


    def __repr__(self):
        return self.get_name_and_id()


    def __init__(self, settlement_id=False, name=False, campaign=False, session_object=None):
        """ Initialize with a settlement from mdb. """
        self.logger = get_logger()

        # initialize session and user objects
        self.Session = session_object
        if self.Session is None or not self.Session:
            raise Exception("Settlements may not be initialized without a Session object!")
        try:
            self.User = self.Session.User
        except:
            self.logger.warn("Settlement %s initialized without a User object!" % settlement_id)

        # now set self.settlement
        self.set_settlement(ObjectId(settlement_id))

        # uncomment these to log which methods are initializing 
#        curframe = inspect.currentframe()
#        calframe = inspect.getouterframes(curframe, 2)
#        self.logger.warn("settlement initialized by %s" % calframe[1][3])



    #
    #   Settlement meta and manager-only methods below
    #

    def set_settlement(self, s_id, update_mins=False):
        """ Sets self.settlement. """

        self.settlement = mdb.settlements.find_one({"_id": s_id})

        if self.settlement is None:
            self.logger.error("[%s] failed to initialize settlement _id: %s" % (self.User, s_id))
            raise Exception("Could not initialize requested settlement %s!" % s_id)



    def update_mins(self):
        """ check 'population' and 'death_count' minimums and update the
        settlement's attribs if necessary.

        There's also some misc. house-keeping that happens here, e.g. changing
        sets to lists (since MDB doesn't support sets), etc.

        This one should be called FREQUENTLY, as it enforces the data model and
        sanitizes the settlement object's settlement dict.
        """

        # uncomment these to log which methods are calling update_mins()
#        curframe = inspect.currentframe()
#        calframe = inspect.getouterframes(curframe, 2)
#        self.logger.debug("update_mins() called by %s" % calframe[1][3])

        for min_key in ["population", "death_count", "survival_limit"]:
            min_val = self.get_min(min_key)
            orig_val = int(self.settlement[min_key])
            if orig_val < min_val:
                self.settlement[min_key] = min_val
                self.logger.debug("Automatically updated settlement %s (%s) %s from %s to %s" % (self.settlement["name"], self.settlement["_id"], min_key, orig_val, min_val))
                self.log_event("Automatically changed %s from %s to %s" % (min_key.replace("_"," "), orig_val, min_val))

            # just a little idiot- and user-proofing against negative values
            if self.settlement[min_key] < 0:
                self.settlement[min_key] = 0

        self.enforce_data_model()
        self.save(quiet=True)


    def enforce_data_model(self):
        """ NB: this method is a dead man walking as of the Anniversary Release:
        we're moving data model normalization to the API as of December 2016, so
        doing this kind of processing here is officially deprecated!

        mongo will FTFO if it sees a set(): uniquify our unique lists before
        saving them and exclude any non str/unicode objects that might have
        snuck in while iterating over the cgi.FieldStorage(). """

        # de-dupe keys in certain groups. Probably not necessary here anymore,
        # but let's hang onto this as long as we're still updating from HTML
        # forms (because they're messy)
        set_attribs = ["milestone_story_events", "innovations", "locations", "principles", "quarries"]
        for a in set_attribs:
            self.settlement[a] = list(set([i.strip() for i in self.settlement[a] if type(i) in (str, unicode)]))



    def save(self, quiet=False):
        """ Saves the settlement. Logs it. """
        mdb.settlements.save(self.settlement)
        if not quiet:
            self.logger.debug("[%s] saved changes to %s" % (self.User, self))


    #
    #   Settlement management and administration methods below
    #


    def remove(self):
        """ Marks the settlement and the survivors as "removed", which prevents
        them from showing up on the dashboard. """

        self.logger.warn("[%s] is removing settlement %s " % (self.User, self))
        for survivor in self.get_survivors():
            S = Survivor(survivor_id=survivor["_id"], session_object=self.Session)
            S.remove()
        self.settlement["removed"] = datetime.now()
        self.log_event("%s removed the settlement!" % (self.User.user["login"]))
        self.logger.warn("[%s] Finished marking %s as 'removed'." % (self.User, self))
        self.save()


    def log_event(self, msg, event_type=None):
        """ Logs a settlement event to mdb.settlement_events. """

        d = {
            "created_on": datetime.now(),
            "created_by": self.User.user["_id"],
            "settlement_id": self.settlement["_id"],
            "ly": self.settlement["lantern_year"],
            "event": msg,
            "event_type": event_type,
        }
        mdb.settlement_events.insert(d)
        self.logger.debug("Settlement event logged for %s" % self.get_name_and_id())




    #
    #   Settlement reference, retrieval and look-up methods below
    #


    def get_event(self, event_name=None):
        """ Searches through the settlement's API asset for an event matching
        'event_name'. Returns an empty dict if no event exists. """

        all_events = self.get_api_asset("game_assets","events")

        lookup_dict = {}
        for h in all_events.keys():
            lookup_dict[all_events[h]["name"]] = h

        if event_name not in lookup_dict.keys():
            self.logger.warn("[%s] event name '%s' not found in API event asset list!" % (self.User, event_name))
            return {}

        event_handle = lookup_dict[event_name]
        return all_events[event_handle]


    def get_story_event(self, event=None):
        """ Accepts certain 'event' values and spits out a string of HTML
        reflecting page numbers, etc.. """

        c_dict = self.get_campaign("dict")
        if "replaced_story_events" in c_dict.keys():
            if event in c_dict["replaced_story_events"]:
                event = c_dict["replaced_story_events"][event]

        if event == "Bold":
            v = 3
        elif event == "Insight":
            v = 3
        elif event == "Awake":
            v = 3
        else:
            return None

        p = self.get_event(event).get("page",None)

        if p == None:
            self.logger.warn("[%s] the 'page' attrib of event '%s' could not be retrieved!" % (self.User, event))

        output = html.survivor.stat_story_event_stub.safe_substitute(
            event=event,
            page=p,
            attrib_value=v,
        )

        return output


    def get_expansions(self, return_type=None):
        """ Returns expansions as a list. """

        if "expansions" in self.settlement.keys():
            expansions = list(set(self.settlement["expansions"]))
            self.settlement["expansions"] = expansions
        else:
            expansions = []

        if return_type == "dict":
            exp_dict = {}
            for exp_key in expansions:
                exp_dict[exp_key] = game_assets.expansions[exp_key]
            return exp_dict
        elif return_type == "comma-delimited":
            if expansions == []:
                return None
            else:
                return ", ".join(expansions)
        elif return_type == "list_of_names":
#            expansions_dict = self.get_api_asset("game_assets","expansions")
#            output_list = []
#            for e in expansions:
#                output_list.append(expansions_dict[e]["name"])
#            return output_list
            self.logger.error('Calling get_expansions(return_type="list_of_names") is deprecated!')
            return expansions

        return expansions


    def get_ly(self):
        """ Returns self.settlement["lantern_year"] as an int. """
        return int(self.settlement["lantern_year"])


    def increment_population(self, amount):
        """ Modifies settlement population. Saves the settlement to MDB. """
        current_pop = int(self.settlement["population"])
        new_pop = current_pop + amount
        self.log_event("Settlement population automatically adjusted by %s" % amount)
        self.settlement["population"] = current_pop
        mdb.settlements.save(self.settlement)
        self.logger.info("[%s] auto-incremented settlement %s population by %s" % (self.User, self, amount))


    def get_name_and_id(self):
        """ Laziness function for DRYer log construction. Called by self.__repr__() """
        return "'%s' (%s)" % (self.settlement["name"], self.settlement["_id"])


    def get_attribute(self, attrib=None):
        """ Returns the settlement attribute associated with 'attrib'. Using this
        is preferable to going straight to self.settlement[attrib] because we do
        business logic on these returns.

        Also, this will duck type settlement attributes to integers if it can,
        so using this method contributes to DRYness by removing the need for
        this type of thing:

            value = int(self.settlement["my thing I want"])

        Anyway, when in doubt, use this method.
        """

        if attrib in ["population","death_count","survival_limit"]:
            min_val = self.get_min(attrib)
            if int(self.settlement[attrib]) < min_val:
                return min_val  # this is an int because get_min always returns an int

        raw_value = self.settlement[attrib]

        try:
            return int(raw_value)
        except ValueError:
            return raw_value


    def get_survivors(self, return_type=False, user_id=None, exclude=[], exclude_dead=False):
        """ Returns the settlement's survivors. Leave 'return_type' unspecified
        if you want a mongo cursor object back. """

        query = {"removed": {"$exists": False}, "settlement": self.settlement["_id"], "_id": {"$nin": exclude}}

        if exclude_dead:
            query["dead"] = {"$exists": False}

        survivors = mdb.survivors.find(query).sort("name")

        if self.User is not None:
            user_login = self.User.user["login"]
        elif self.User is None and user_id is not None:
            self.User = User(user_id=user_id)
            user_login = self.User.user["login"]
        else:
            self.User = None
            user_login = None

        current_user_is_settlement_creator = False
        if self.User is not None and self.User.user["_id"] == self.settlement["created_by"]:
            current_user_is_settlement_creator = True
        elif self.User is not None and "admins" in self.settlement.keys() and self.User.user["login"] in self.settlement["admins"]:
            current_user_is_settlement_creator = True

        if return_type == "hunting_party":
            raise Exception("Using get_survivors() with the 'hunting_party' return type is not supported!")

        if return_type == "html_buttons":
            output = ""
            for survivor in survivors:
                S = Survivor(survivor_id=survivor["_id"])
                output += S.asset_link()
            return output

        if return_type == "sex_count":
            male = 0
            female = 0
            for s in survivors:
                if s["sex"] == "M":
                    male += 1
                elif s["sex"] == "F":
                    female += 1
            return "%sM/%sF" % (male,female)

        if return_type == "chronological_order":
            return mdb.survivors.find(query).sort("created_on")

        # finally, capture and scream bloody murder about deprecated return_types
        if return_type in ["angularjs", "JSON"]:
            raise Exception("Return type '%s' no longer supported by this method!" % return_type)

        return survivors


    def get_campaign(self, return_type=None):
        """ Returns the campaign of the settlement as a handle. Not to be
        confused with the User.get_campaigns() method, which returns campaigns a
        user is currently  associated with.

        For transitional/legacy purposes, this method can accept a few different
        'return_type' kwargs:

            - "dict"        returns the campaign definition dict
            - "name"        returns the campaign name (rather than handle)
            - "forbidden"   returns a list of 'forbidden' game assets

        NB: that the 'forbidden' return type includes innovations, locations,
        etc. and is not limited to one type of 'forbidden' game asset.

        """

        # legacy app data noramlization required because the dashboard breaks
        #   if it doesn't have this (and it doesn't do an API call)
        if self.settlement.get("campaign", None) is None:
            self.settlement["campaign"] = "People of the Lantern"
            self.logger.debug("[%s] defaulting 'campaign' attrib for %s" % (self.User, self))
            self.save()

        if return_type is not None:
            c_dict = self.get_api_asset("game_assets","campaign")

        if return_type == "dict":
            return c_dict
        elif return_type == "name":
            return c_dict["name"]
        elif return_type == "forbidden":
            forbidden = []
            f_dict = c_dict.get("forbidden",{})
            for k in f_dict.keys():
                forbidden.extend(f_dict[k])
            return list(set(forbidden))

        return self.settlement["campaign"]


    def get_min(self, value=None):
        """ Returns the settlement's minimum necessary values for the following:

            'population': the minimum number of survivors based on which have
                'dead' in their Survivor.survivor.keys().
            'deaths' or 'death_count': the minimum number of dead survivors.
            'survival_limit': the minimum survival limit, based on innovations.

        Returns an int. ALWAYS.
        """
        results = False
        settlement_id = ObjectId(self.settlement["_id"])

        if value == "population":
            results = mdb.survivors.find({"settlement": settlement_id, "dead": {"$exists": False}, "removed": {"$exists": False}}).count()
        elif value == "deaths" or value == "death_count":
            results = mdb.survivors.find({"settlement": settlement_id, "dead": {"$exists": True}}).count()
        elif value == "survival_limit":
            min_survival = 0

            if self.settlement["name"] != "":
                min_survival +=1

            innovations = copy(self.settlement["innovations"])
            innovations.extend(self.settlement["principles"])
            innovations = list(set(innovations))
            for innovation_key in innovations:
                if innovation_key in Innovations.get_keys() and "survival_limit" in Innovations.get_asset(innovation_key).keys():
                    min_survival += Innovations.get_asset(innovation_key)["survival_limit"]
            results = min_survival

        return int(results)


    def get_players(self, return_type=None, count_only=False):
        """ The Settlement's generic method for getting players. Comes back as a
        set of email addresses (i.e. user["login"] values). """

        creator = mdb.users.find_one({"_id": self.settlement["created_by"]})
        player_set = set([creator["login"]])
        survivors = mdb.survivors.find({"settlement": self.settlement["_id"]})
        for s in survivors:
            player_set.add(s["email"])

        if count_only:
            return len(player_set)

        return player_set


    def get_admins(self):
        """ Creates an admins list if one doesn't exist; adds the settlement
        creator to it if it's new; returns the list. """

        if not "admins" in self.settlement.keys():
            self.settlement["admins"] = []

        creator = mdb.users.find_one({"_id": self.settlement["created_by"]})
        if creator is not None and self.settlement["admins"] == []:
            self.settlement["admins"].append(creator["login"])

        return self.settlement["admins"]


    def toggle_admin_status(self, login):
        """ Adds or removes a login from self.settlement["admins"], depending
        on whether it's already there or not. """

        if login in self.settlement["admins"]:
            self.settlement["admins"].remove(login)
            msg = "removed %s from" % login
        else:
            self.settlement["admins"].append(login)
            msg = "added %s to" % login

        self.logger.debug("[%s] %s %s admins." % (self.User, msg, self))



    @ua_decorator
    def render_html_summary(self, user_id=False):
        """ Prints the campaign summary view HTML. Does template subs to
        initialize the AngularJS application. """

        return html.settlement.summary.safe_substitute()


    @ua_decorator
    def render_html_form(self):
        """ Render settlement.form from html.py. Do a few substitutions during
        the render (i.e. things that aren't yet managed by the angularjs app.

        Remember that this passes through @ua_decorator, so it gets some more
        substitutions done up there. """

        return html.settlement.form.safe_substitute( )



    def render_admin_panel_html(self):
        """ Renders a settlement as admin panel style HTML. This honestly
        probably belongs under a master render method for this class but...
        dang, you know? These render methods are monsters. I really gotta
        abstract further in one of these major refactor revisions..."""

        # write the top line
        output = "\n\n<b>%s</b> LY:%s (%s) - %s/%s<br/>\n" % (
            self.settlement["name"],
            self.settlement["lantern_year"],
            self.settlement["created_on"].strftime(ymd),
            self.settlement["population"],
            self.settlement["death_count"],
            )

        # write the removal info, if any exists
        removal_string = ""
        for removal_key in ["abandoned", "removed"]:
            if removal_key in self.settlement.keys():
                removal_string += '<font class="alert">%s</font> ' % removal_key.upper()
        if removal_string != "":
            removal_string = "&ensp; %s <br/>\n" % removal_string
        output += removal_string

        # now do the rest
        output += "&ensp;<i>%s</i><br/>\n" % self.get_campaign()
        output += "&ensp;Players: %s<br/>\n" % ", ".join(self.get_players())
        output += "&ensp;Expansions: %s\n" % ", ".join(self.get_expansions())

        return output


    def asset_link(self, context=None, update_mins=False):
        """ Returns an asset link (i.e. html form with button) for the
        settlement.

        Specify one of the following contexts, or leave the 'context' kwarg set
        to None if you want a generic link to the settlement back:

            'campaign_summary':         the "Edit Settlement" link that floats
                                        over the campaign summary view
            'asset_management':         the "Campaign Summary" link that floats
                                        over the create new asset forms,
                                        survior and settlement sheets, etc.
            'dashboard_campaign_list':  gradient_violet links with a summary of
                                        campaign facts.

        Anything else will get you the default, gradient_yellow link with the
        settlement flash and the name.
        """

#        if update_mins:
#            self.update_mins()  # update settlement mins before we create any text

        if context == "campaign_summary":
            button_class = "campaign_summary_gradient"
            link_text = html.dashboard.settlement_flash
            desktop_text = "Edit %s" % self.settlement["name"]
            asset_type = "settlement"
        elif context == "asset_management":
            button_class = "settlement_sheet_gradient"
            link_text = html.dashboard.campaign_flash
            desktop_text = "%s Campaign Summary" % self.settlement["name"]
            asset_type = "campaign"
        elif context == "dashboard_campaign_list":
            players = self.get_players()
            if len(players) > 1:
                players = "<br/>Players: %s" % (", ".join(players))
            else:
                players = ""
            return html.settlement.dashboard_campaign_asset.safe_substitute(
                asset_id=self.settlement["_id"],
                name=self.settlement["name"],
                campaign=game_assets.campaign_look_up[self.get_campaign()],
                ly=self.get_ly(),
                pop=self.settlement["population"],
                players_block=players,
            )
        else:
            button_class = "kd_dying_lantern dashboard_settlement_list_settlement_button"
            link_text = "<b class='dashboard_settlement_list_settlement_name'>%s</b>" % self.settlement["name"]
            link_text += "<br/><i>%s</i>" % game_assets.campaign_look_up[self.get_campaign()]

            if "abandoned" in self.settlement.keys():
                link_text += ' [ABANDONED]'

            link_text += "<br/>- Created: %s" % self.settlement["created_on"].strftime(ymd)
            link_text += "<br/>- %s expansions / %s player(s)" % (len(self.get_expansions()), self.get_players(count_only=True))
            link_text += "<br/>- LY: %s" % (self.get_ly())
            link_text += "<br/>- Population: %s" % (self.settlement["population"])
            link_text += "<br/>- Deaths: %s" % (self.settlement["death_count"])

            desktop_text = ""
            asset_type = "settlement"

        return html.dashboard.view_asset_button.safe_substitute(
            button_class = button_class,
            asset_type = asset_type,
            asset_id = self.settlement["_id"],
            asset_name = link_text,
            desktop_text = desktop_text,
        )






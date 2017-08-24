#!/usr/bin/python2.7

import os
import sys
os.chdir(os.path.dirname(sys.argv[0]))


# imports for root switch
import settings
from pwd import getpwuid, getpwnam


# general imports
from bson.son import SON
from bson import json_util
from bson.objectid import ObjectId
import collections
import daemon
from datetime import datetime, timedelta
import json
from lockfile.pidlockfile import PIDLockFile
from optparse import OptionParser
from retry import retry
import shutil
import subprocess
import stat
import time

# local imports
from assets import world as world_assets
from models import innovations as innovations_models
from models import monsters as monster_models
from models import expansions as expansions_models
from models import settlements as settlements_models
from models import survivors as survivors_models
from models import campaigns as campaigns_models
from models import epithets as epithets_models
import utils




#
# World object below
#

class World:

    def __init__(self, query_debug=False):
        """ Initializing a World object doesn't get you much beyond the ability
        to call the methods below. Typically you shouldn't initialize one of
        these unless you're trying to update warehoused data or maybe get info
        on a specific piece of warehosued data (which can more easily be gotten
        from the /world route JSON.)

        NB: if you're trying to fiddle/filter or otherwise futz with final
        output, check the self.list() method. """

        self.logger = utils.get_logger(settings.get("world","log_level"))
        self.query_debug = query_debug
        self.assets = world_assets.general

        # common list of banned names (across all collections)
        # maybe this should come from a config file?
        self.ineligible_names = [
            "-",                                # the 'blank' cause of death
            "test","Test","TEST",
            "unknown", "Unknown","UNKNOWN",
            "Anonymous","anonymous",
        ]


    def refresh_all_assets(self, force=False):
        """ Updates all assets. Set 'force' to True to ignore 'max_age' and
        'asset_max_age'. A wrapper for self.refresh_asset(). """

        self.logger.info("Refreshing stale warehouse assets...")

        self.total_refreshed_assets = 0
        for asset_key in self.assets.keys():
            self.refresh_asset(asset_key, force=force)
            self.total_refreshed_assets += 1

        self.logger.info("Refreshed %s/%s assets." % (self.total_refreshed_assets, len(self.assets.keys())))


    def refresh_asset(self, asset_key=None, force=False, dump=False):
        """ Updates a single asset. Checks the 'max_age' of the asset and falls
        back to settings.world.asset_max_age if it can't find one.

        Set 'force' to True if you want to force a refresh, regardless of the
        asset's age. """

        asset_dict = self.initialize_asset_dict(asset_key)

        # now determine whether we want to refresh it
        do_refresh = False
        current_age = None

        mdb_asset = utils.mdb.world.find_one({"handle": asset_key})
        if mdb_asset is None:
            self.logger.debug("Asset handle '%s' not found in mdb!" % asset_key)
            do_refresh = True
        else:
            current_age = datetime.now() - mdb_asset["created_on"]
        if current_age is None:
            do_refresh = True
        elif current_age.seconds > asset_dict["max_age"]:
            self.logger.debug("Asset '%s' has a current age of %s seconds (max age is %s seconds)." % (asset_key, current_age.seconds, asset_dict["max_age"]))
            do_refresh = True
        if force:
            do_refresh = True

        # now do the refresh, if necessary
        if do_refresh:
            self.logger.debug("Refreshing '%s' asset..." % asset_key)
            try:
                self.update_asset_dict(asset_dict)
                self.update_mdb(asset_dict)
                self.logger.debug("Updated '%s' asset in mdb." % asset_key)
            except Exception as e:
                self.logger.error("Exception caught while refreshing '%s' asset!" % asset_key)
                self.logger.exception(e)

        if dump:
            print(asset_dict)


    def initialize_asset_dict(self, asset_key):
        """ Turn an asset key (e.g. 'top_innovations', etc.) into a basic dict
        that is ready to be updated/processed. """

        # basic init
        if self.assets.get(asset_key, None) is None:
            msg = "Could not refresh '%s' asset: no such asset exists!" % asset_key
            self.logger.exception(msg)
            raise Exception(msg)

        asset_dict = self.assets[asset_key]
        asset_dict["handle"] = asset_key

        # default the asset's 'max_age' attribute if it hasn't got one
        if asset_dict.get("max_age", None) is None:
            asset_dict["max_age"] = settings.get("world", "asset_max_age") * 60

        return asset_dict



    def update_asset_dict(self, asset_dict):
        """ this is where the magic happens: a valid asset_dict goes in and a
        fully fleshed-out asset dictionary with current data comes out. """

        if asset_dict["handle"] not in dir(self):
            msg = "Could not refresh '%s' asset: no such world.World class method exists!" % asset_dict["handle"]
            self.logger.exception(msg)
            raise Exception(msg)

        try:
            exec "value = self.%s()" % asset_dict["handle"]
        except Exception as e:
            self.logger.error("Could not update asset dictionary for '%s' world asset!" % asset_dict["handle"])
            self.logger.exception(e)
            raise

        asset_dict.update({"created_on": datetime.now()})
        asset_dict.update({"value": value})

        # respect the asset dictionary's "limit" attrib, if extant
        if asset_dict.get("limit", None) is not None:
            asset_dict["value"] = asset_dict["value"][:asset_dict["limit"]]

        asset_dict["value_type"] = type(value).__name__

        return asset_dict


    def update_mdb(self, asset_dict):
        """ Creates a new document in mdb.world OR, if this handle already
        exists, updates an existing one. """

        existing_asset = utils.mdb.world.find_one({"handle": asset_dict["handle"]})
        if existing_asset is not None:
            asset_dict["_id"] = existing_asset["_id"]
        utils.mdb.world.save(asset_dict)
        utils.mdb.world.create_index("handle", unique=True)


    def remove(self, asset_id):
        """ Removes a single asset _id from mdb.world. """
        _id = ObjectId(asset_id)
        if utils.mdb.world.find_one({"_id": _id}) is not None:
            utils.mdb.world.remove(_id)
            self.logger.warn("Removed asset _id '%s'" % asset_id )
        else:
            self.logger.warn("Object _id '%s' was not found!" % asset_id)


    def list(self, output_type="JSON"):
        """ Dump world data in a few different formats."""

        # initialize our final dict
        d = utils.api_meta
        d["meta"]["object"]["panel_revision"] = settings.get("application","panel_revision")
        d["world"] = collections.OrderedDict()

        # get the raw world info (we'll sort it later)
        raw_world = {}
        for asset in utils.mdb.world.find():
            raw_world[asset["handle"]] = asset
            raw_world[asset["handle"]]["age_in_seconds"] = (datetime.now() - asset["created_on"]).seconds

        #
        # This is where we filter data key/value pairs from being returned
        #   by calls to the /world route
        #

        def recursive_key_del(chk_d, f_key):
            if f_key in chk_d.keys():
                del chk_d[f_key]

            for k in chk_d.keys():
                if type(chk_d[k]) == dict:
                    recursive_key_del(chk_d[k], f_key)

        for banned_key in ["max_age", "email","admins"]:
            recursive_key_del(raw_world, banned_key)


        # sort the world dict
        key_order = sorted(raw_world, key=lambda x: raw_world[x]["name"])
        for k in key_order:
            d["world"][k] = raw_world[k]

        # output options from here down:

        if output_type == "CLI":
            print("\n\tWarehouse data:\n")
            spacer = 25
            for k, v in d["world"].iteritems():
                utils.cli_dump(k, spacer, v)
                print("")
        elif output_type == "keys":
            return d["world"].keys()
        elif output_type == "keys_cli":
            output = ""
            for k in sorted(d["world"].keys()):
                output += "  %s\n" % k
            return output
        elif output_type == dict:
            return d
        elif output_type == "JSON":
            return json.dumps(d, default=json_util.default)


    def dump(self, asset_handle):
        """ Prints a single asset to STDOUT. CLI admin functionality. """

        asset = utils.mdb.world.find_one({"handle": asset_handle})
        print("\n\t%s\n" % asset_handle)
        spacer = 20
        for k, v in asset.iteritems():
            utils.cli_dump(k, spacer, v)
        print("\n")


    def do_query(self, asset_key):
        """ Executes a query and returns its results. Meant for CLI debugging
        and admin reference. """

        asset_dict = self.initialize_asset_dict(asset_key)
        self.logger.debug("'%s' asset dict initialized..." % asset_dict["handle"])
        return self.update_asset_dict(asset_dict)

    #
    # refresh method helpers and shortcuts
    #

    def pretty_survivor(self, survivor):
        """ Clean a survivor up and make it 'shippable' as part of the world
        JSON. This initializes the survivor and will normalize it. """

        # init
        S = survivors_models.Survivor(_id=survivor["_id"])
        survivor["epithets"] = S.get_epithets("pretty")

        # redact/remove
        survivor["attribute_detail"] = 'REDACTED'

        # add settlement info
        settlement = utils.mdb.settlements.find_one({"_id": survivor["settlement"]})
        survivor["settlement_name"] = settlement["name"]

        return survivor


    def get_eligible_documents(self, collection=None, required_attribs=None, limit=None, exclude_dead_survivors=True, include_settlement=False, sort_on=None):
        """ Returns a dict representing the baseline mdb query for a given
        collection.

        This should be used pretty much any time we need to go to the mdb for
        data. Writing direct queries is OK for one-offs, but this saves a lot of
        time and helps keep things DRY.
        """


        # base query dict; excludes ineligible names and docs w/o 'attrib'
        query = {"name": {"$nin": self.ineligible_names}}

        # add eligibility attrib if required
        if required_attribs is not None:
            if type(required_attribs) == list:
                for a in required_attribs:
                    query.update({a: {"$exists": True}})
            else:
                query.update({required_attribs: {"$exists": True}})

        # exclude dead survivors switch
        if collection == "survivors" and exclude_dead_survivors:
            query.update({
                "dead": {"$exists": False},
            })

        # customize based on collection name
        if collection == "settlements":
            query.update({
                "lantern_year": {"$gt": 0},
                "population": {"$gt": 1},
                "death_count": {"$gt": 0},
            })
        elif collection == "survivors":
            pass
#            query.update({ })
        elif collection == "users":
            query.update({
                "removed": {"$exists": False},
            })
        elif collection == "killboard":
            query.update({
                "settlement_name": {"$nin": self.ineligible_names},
            })
        else:
            self.logger.error("The collections '%s' is not within the scope of world.py")

        # get results
        sort_params = [("created_on",-1)]
        if sort_on is not None:
            sort_params = [(sort_on, -1)]
        results = utils.mdb[collection].find(query, sort=sort_params)

        # log an exception if results is None
        if results is None:
            self.logger.exception(utils.WorldQueryError(query=query))
            return None
        elif results.count() == 0:
            self.logger.exception(utils.WorldQueryError(query=query))
            return None

        # change results from a query object to a list
        results = [x for x in results]

        # hack around the dumbass implementation of .limit() in mongo
        if limit is not None:
            return results[limit - 1]
        else:
            return results


    def get_minmax(self, collection=None, attrib=None):
        """ Gets the highest/lowest value for 'attrib' across all eligible
        documents in 'collection'. Returns a tuple. """

        sample_set = self.get_eligible_documents(collection, attrib)

        if sample_set is None:
            return (None, None)

        data_points = []
        for sample in sample_set:
            data_points.append(int(sample[attrib]))
        return min(data_points), max(data_points)


    def get_average(self, collection=None, attrib=None, precision=2, return_type=float):
        """ Gets the average value for 'attrib' across all elgible documents in
        'collection' (as determined by the world.eligible_documents() method).

        Returns a float rounded to two decimal places by default. Use the
        'precision' kwarg to modify rounding precision and 'return_type' to
        coerce the return a str or int as desired. """

        sample_set = self.get_eligible_documents(collection, attrib)

        if sample_set is None:
            return None

        data_points = []
        for sample in sample_set:
            try:
                data_points.append(return_type(sample[attrib]))
            except: # in case we need to coerce a list to an int
                data_points.append(return_type(len(sample[attrib])))
        result = reduce(lambda x, y: x + y, data_points) / float(len(data_points))

        # coerce return based on 'return_type' kwarg
        if return_type == int:
            return result
        elif return_type == float:
            return round(result, precision)
        else:
            return None


    def get_list_average(self, data_points):
        """ Super generic function for turning a list of int or float data into
        a float average. """

        list_length = float(len(data_points))
        result = reduce(lambda x, y: x + y, data_points) / list_length
        return round(result,2)


    def get_top(self, collection=None, attrib=None, limit=5, asset_type=str):
        """ Assuming that 'collection' documents have a 'attrib' attribute, this
        will return the top five most popular names along with their counts. """

        query = {attrib: {"$nin": self.ineligible_names, "$exists": True}}

        if self.query_debug:
            self.logger.debug("MDB  name:   %s" % utils.mdb.name)
            self.logger.debug("MDB query:   %s" % query)

        if asset_type == str:
            results = utils.mdb[collection].group(
                [attrib], query, {"count": 0}, "function(o, p){p.count++}"
            )

            sorted_list = sorted(results, key=lambda k: k["count"], reverse=True)
            for i in sorted_list:
                i["value"] = i[attrib]
                i["count"] = int(i["count"])

        elif asset_type == list:
            sample_set = self.get_eligible_documents(collection, attrib)
            if sample_set is None:
                return None
            master_list = []
            for s in sample_set:
                master_list.extend(s[attrib])
            master_dict = {}
            for i in master_list:
                if i in master_dict.keys():
                    master_dict[i] += 1
                else:
                    master_dict[i] = 1
            return sorted(master_dict.items(), key=lambda x: x[1], reverse=True)

        else:
            raise Exception("%s is not a supported asset type for this query!" % asset_type)

        if self.query_debug:
            self.logger.debug("MDB results: %s" % sorted_list)

        return sorted_list[:limit]


    #
    # actual refresh methods from here down (nothing after)
    #

    # survivors
    def total_survivors(self):
        return utils.mdb.survivors.find().count()

    def live_survivors(self):
        return utils.mdb.survivors.find({"dead": {"$exists": False}}).count()

    def dead_survivors(self):
        return utils.mdb.survivors.find({"dead": {"$exists": True}}).count()

    # settlements
    def total_settlements(self):
        return utils.mdb.settlements.find().count()

    def active_settlements(self):
        return self.total_settlements() - self.abandoned_settlements()

    def removed_settlements(self):
        return utils.mdb.settlements.find({"removed": {"$exists": True}}).count()

    def abandoned_settlements(self):
        return utils.mdb.settlements.find({"abandoned": {"$exists": True}}).count()

    def abandoned_and_removed_settlements(self):
        return utils.mdb.settlements.find({"$or": [
            {"removed": {"$exists": True}},
            {"abandoned": {"$exists": True}},
        ]}).count()


    def total_users(self):
        return utils.mdb.users.find().count()

    def total_users_last_30(self):
        thirty_days_ago = datetime.now() - timedelta(days=30)
        return utils.mdb.users.find({"latest_activity": {"$gte": thirty_days_ago}}).count()

    def new_settlements_last_30(self):
        thirty_days_ago = datetime.now() - timedelta(days=30)
        return utils.mdb.settlements.find({"created_on": {"$gte": thirty_days_ago}}).count()

    def recent_sessions(self):
        recent_session_cutoff = datetime.now() - timedelta(hours=settings.get("application", "recent_user_horizon"))
        return utils.mdb.users.find({"latest_activity": {"$gte": recent_session_cutoff}}).count()

    # min/max queries
    def max_pop(self):
        return self.get_minmax("settlements","population")[1]

    def max_death_count(self):
        return self.get_minmax("settlements","death_count")[1]

    def max_survival_limit(self):
        return self.get_minmax("settlements","survival_limit")[1]

    # settlement averages
    def avg_ly(self):
        return self.get_average("settlements", "lantern_year")

    def avg_lost_settlements(self):
        return self.get_average("settlements", "lost_settlements")

    def avg_pop(self):
        return self.get_average("settlements", "population")

    def avg_death_count(self):
        return self.get_average("settlements", "death_count")

    def avg_survival_limit(self):
        return self.get_average("settlements", "survival_limit")

    def avg_milestones(self):
        return self.get_average("settlements", "milestone_story_events")

    def avg_storage(self):
        return self.get_average("settlements", "storage")

    def avg_defeated_monsters(self):
        return self.get_average("settlements", "defeated_monsters")

    def avg_expansions(self):
        return self.get_average("settlements", "expansions")

    def avg_innovations(self):
        return self.get_average("settlements", "innovations")

    def total_multiplayer_settlements(self):
        """ Iterates through all survivors, adding their settlement _id to a
        dict as its key; the value of that key is a list of
        survivor["created_by"] values. Any key whose list is longer than one
        is a multiplayer settlement. """

        all_settlements = {}
        all_survivors = utils.mdb.survivors.find()    # incldues removed/test/etc.
        for s in all_survivors:
            if s["settlement"] not in all_settlements.keys():
                all_settlements[s["settlement"]] = set([s["created_by"]])
            else:
                all_settlements[s["settlement"]].add(s["created_by"])

        multiplayer_count = 0
        for s in all_settlements.keys():
            if len(all_settlements[s]) > 1:
                multiplayer_count += 1

        return multiplayer_count

    # survivor averages
    def avg_disorders(self):
        return self.get_average("survivors", "disorders")

    def avg_abilities(self):
        return self.get_average("survivors", "abilities_and_impairments")

    def avg_hunt_xp(self):
        return self.get_average("survivors", "hunt_xp")

    def avg_insanity(self):
        return self.get_average("survivors", "Insanity")

    def avg_courage(self):
        return self.get_average("survivors", "Courage")

    def avg_understanding(self):
        return self.get_average("survivors", "Understanding")

    def avg_fighting_arts(self):
        return self.get_average("survivors", "fighting_arts")

    # user averages
    # these happen in stages in order to work around the stable version of mdb
    # (which doesn't support $lookup aggregations yet). 
    # Not super DRY, but it still beats using a relational DB.

    def avg_user_settlements(self):
        data_points = []
        for user in utils.mdb.users.find():
            data_points.append(utils.mdb.settlements.find({"created_by": user["_id"]}).count())
        return self.get_list_average(data_points)

    def avg_user_survivors(self):
        data_points = []
        for user in utils.mdb.users.find():
            data_points.append(utils.mdb.survivors.find({"created_by": user["_id"]}).count())
        return self.get_list_average(data_points)

    def avg_user_avatars(self):
        data_points = []
        for user in utils.mdb.users.find():
            data_points.append(utils.mdb.survivors.find({"created_by": user["_id"], "avatar": {"$exists": True}}).count())
        return self.get_list_average(data_points)

    # latest event queries
    def latest_kill(self):
        return self.get_eligible_documents(collection="killboard", required_attribs=["handle"], limit=1)

    def latest_survivor(self):
        s = self.get_eligible_documents(collection="survivors", limit=1, include_settlement=True)
        return self.pretty_survivor(s)

    def latest_fatality(self):
        s = self.get_eligible_documents(
            collection="survivors",
            required_attribs=["dead","cause_of_death"],
            limit=1,
            exclude_dead_survivors=False,
            include_settlement=True,
            sort_on="died_on",
        )
        return self.pretty_survivor(s)

    def latest_settlement(self):
        """ Get the latest settlement and punch it up with some additional info,
        since JSON consumers don't have MDB access and can't get it otherwise.
        """

#        s = self.get_eligible_documents(collection="settlements", limit=1)
        try:
            s = utils.mdb.settlements.find({"name": {"$nin": self.ineligible_names}}, sort=[("created_on",-1)])[0]
        except IndexError:
            self.logger.error("No settlements in mdb match the 'latest_settlement' criteria! Returning None...")
            return None

        S = settlements_models.Settlement(_id=s["_id"])

        s["campaign"] = S.get_campaign("name")
        s["expansions"] = S.get_expansions("pretty")
        s["player_count"] = S.get_players("count")

        for k in ['timeline',]:
            if k in s.keys():
                s[k] = "REDACTED"

        return s

    # compound returns below. Unlike the above functions, these return dict
    # and list type objects

    def killboard(self):
        known_types = utils.mdb.killboard.find().distinct("type")

        if known_types == []:
            self.logger.exception("No kills in mdb! Returning None for killboard...")
            return None

        killboard = {}
        for t in known_types:
            killboard[t] = {}
        monster_assets = monster_models.Assets()
        for m_handle in monster_assets.get_handles():
            m_asset = monster_assets.get_asset(m_handle)
            killboard[m_asset["type"]][m_handle] = {"name": m_asset["name"], "count": 0, "sort_order": m_asset["sort_order"]}
        results = utils.mdb.killboard.find({"handle": {"$exists": True}, "type": {"$exists": True}})
        for d in results:
            killboard[d["type"]][d["handle"]]["count"] += 1

        for type in killboard.keys():
            sort_order_dict = {}
            for m in killboard[type].keys():
                m_dict = killboard[type][m]
                m_dict.update({"handle": m})
                sort_order_dict[int(m_dict["sort_order"])] = m_dict

            killboard[type] = []
            previous = -1
            for k in sorted(sort_order_dict.keys()):
                m_dict = sort_order_dict[k]
                if m_dict["sort_order"] <= previous:
                    self.logger.error("Sorting error! %s sort order (%s) is not greater than previous (%s)!" % (m_dict["name"], m_dict["sort_order"], previous))
                killboard[type].append(m_dict)
                previous = m_dict["sort_order"]

        return killboard

    def top_survivor_names(self):
        return self.get_top("survivors","name")

    def top_settlement_names(self):
        return self.get_top("settlements","name")

    def top_causes_of_death(self):
        return self.get_top("survivors","cause_of_death",limit=10)

    def top_innovations(self):
        """ Does an innovations popularity contest, accounting for both names
        and handles (for legacy support). """

        I = innovations_models.Assets()
        I.filter("type", ["principle"])

        all_results = []
        for i_dict in I.get_dicts():
            aliases = [i_dict["name"], i_dict["handle"]]
            results = utils.mdb.settlements.find({"innovations": {"$in": aliases}})
            all_results.append({
                "name": i_dict["name"],
                "handle": i_dict["handle"],
                "count": results.count(),
            })

        return sorted(all_results, key=lambda x: x["count"], reverse=1)

    def principle_selection_rates(self):
        """ This is pretty much a direct port from V1. It's still a hot mess.
        This should probably get a refactor prior to launch. """

        I = innovations_models.Assets()
        mep_dict = I.get_mutually_exclusive_principles()

        popularity_contest = {}
        for principle in mep_dict.keys():
            tup = mep_dict[principle]

            all_options = []
            for l in tup:
                all_options.extend(l)

            sample_set = utils.mdb.settlements.find({"principles": {"$in": all_options} }).count()
            popularity_contest[principle] = {"sample_size": sample_set, "options": []}

            for option_list in tup:
                total = utils.mdb.settlements.find({"principles": {"$in": option_list}}).count()
                option_pretty_name = option_list[0]
                popularity_contest[principle]["options"].append(option_pretty_name)
                popularity_contest[principle][option_pretty_name] = {
                    "total": total,
                    "percentage": int(utils.get_percentage(total, sample_set)),
                }
        return popularity_contest

    def settlement_popularity_contest_expansions(self):
        """ Uses the assets in assets/expansions.py to return a popularity
        contest dict re: expansions stored on settlement objects. """

        popularity_contest = {}

        expansions_assets = expansions_models.Assets()
        for e in expansions_assets.get_handles():
            e_dict = expansions_assets.get_asset(e)
            e_name_count = utils.mdb.settlements.find({"expansions": {"$in": [e_dict["name"]]}}).count()
            e_handle_count = utils.mdb.settlements.find({"expansions": {"$in": [e]}}).count()
            popularity_contest[e_dict["name"]] = e_name_count
            popularity_contest[e_dict["name"]] += e_handle_count

        return popularity_contest

    def settlement_popularity_contest_campaigns(self):
        """ Uses the assets in assets/campaigns.py to return a popularity
        contest dict re: campaigns. """


        popularity_contest = {
            "People of the Lantern": utils.mdb.settlements.find({"campaign": {"$exists": False}}).count(),
        }

        campaigns = utils.mdb.settlements.find({"campaign": {"$exists": True}}).distinct("campaign")

        C = campaigns_models.Assets()

        for c in campaigns:
            total = utils.mdb.settlements.find({"campaign": c}).count()

            if C.get_asset_from_name(c) is None:
                c = C.get_asset(c)["name"]

            if c in popularity_contest.keys():
                popularity_contest[c] += total
            else:
                popularity_contest[c] = total

        return popularity_contest


    def current_hunt(self):
        """ Uses settlements with a 'current_quarry' attribute to determine who
        is currently hunting monsters.

        The mdb query is totally custom, so it's written out here, rather than
        stashed in a method of the World object, etc. """

        settlement = utils.mdb.settlements.find_one(
            {
                "removed": {"$exists": False},
                "abandoned": {"$exists": False},
                "name": {"$nin": self.ineligible_names},
                "current_quarry": {"$exists": True},
                "hunt_started": {"$gte": datetime.now() - timedelta(minutes=180)},
            }, sort=[("hunt_started", -1)],
        )

        if settlement is None:
            return None

        hunters = utils.mdb.survivors.find({
            "settlement": settlement["_id"],
            "in_hunting_party": {"$exists": True},
        }).sort("name")

        if hunters.count() == 0:
            return None

        return {"settlement": settlement, "survivors": [h for h in hunters]}


#
#   daemon code here
#

class WorldDaemon:
    """ The world daemon determines whether to update a given world asset (see
    assets/world.py) based on the default 'asset_max_age' in settings.cfg or
    based on the custom 'max_age' attribute of a given asset.

    Since the daemon does not always update all assets, it minimizes resource
    usage and can therefore be left running without whaling on CPU and/or
    physical memory.

    Finally, the world daemon DOES NOT actually refresh/update or otherwise
    gather any data or run any queries. Rather, it initializes a World object
    (see above) and then works with that object as necessary. """

    def __init__(self):

        self.logger = utils.get_logger(log_name="world_daemon", log_level=settings.get("world","log_level"))

        self.pid_dir = settings.get("application","pid_root_dir")
        self.pid_file_path = os.path.join(self.pid_dir, "world_daemon.pid")
        self.set_pid()



    def check_pid_dir(self):
        """ Checks to see if the pid directory exists and is writable. Creates a
        a new dir if it needs to do so. Also logs a WARN if the user requesting
        the check is not the owner of the pid dir. """

        if not os.path.isdir(self.pid_dir):
            self.logger.error("PID dir '%s' does not exist!" % self.pid_dir)
            try:
                shutil.os.mkdir(self.pid_dir)
                self.logger.critical("Created PID dir '%s'!" % self.pid_dir)
            except Exception as e:
                self.logger.error("Could not create PID dir '%s'!" % self.pid_dir)
                self.logger.exception(e)
                sys.exit(255)


        # warn if we're going to start off by trying to write a lock/pid file to
        # some other user's directory, b/c that would be bad
        pid_dir_owner = getpwuid(os.stat(self.pid_dir).st_uid).pw_name
        cur_user = os.getlogin()
        if pid_dir_owner != cur_user:
            self.logger.warn("PID dir owner is not the current user (%s)!" % cur_user)


    def set_pid(self):
        """ Updates 'self.pid' with the int in the daemon pid file. Returns None
        if there is no file or the file cannot be parsed. """
        self.pid = None

        if os.path.isfile(self.pid_file_path):
            try:
                self.pid = int(file(self.pid_file_path, "rb").read().strip())
            except Exception as e:
                self.logger.exception(e)

            try:
                os.kill(self.pid, 0)
            except OSError as e:
                self.logger.exception(e)
                self.logger.error("PID %s does not exist! Removing PID file..." % self.pid)
                shutil.os.remove(self.pid_file_path)
                self.pid = None


    def command(self, command=None):
        """ Executes a daemon command. Think of this as the router for incoming
        daemon commands/operations. Register all commands here. """

        if command == "start":
            self.start()
        elif command == "stop":
            self.stop()
        elif command == "restart":
            self.stop()
            time.sleep(3)
            self.start()
        elif command == "status":
            pass
        else:
            self.logger.error("Unknown daemon command ('%s')!" % command)

        # sleep a second and dump a status, regardless of command
        time.sleep(1)
        self.dump_status()



    @retry(
        tries=6,delay=2,jitter=1,
        logger=utils.get_logger(settings.get("world","log_level")),
    )
    def start(self):
        """ Starts the daemon. """

        self.set_pid()
        if self.pid is not None:
            try:
                os.kill(self.pid, 0)
                self.logger.warn("PID %s exists! Demon is already running! Exiting..." % self.pid)
                sys.exit(1)
            except OSError:
                self.logger.info("Starting World Daemon...")
        else:
            self.logger.info("Starting World Daemon...")

        # pre-flight sanity checks and initialization tasks
        self.check_pid_dir()

        context = daemon.DaemonContext(
            working_directory = (settings.get("api","cwd")),
            detach_process = True,
            umask=0o002, pidfile=PIDLockFile(self.pid_file_path),
            files_preserve = [self.logger.handlers[0].stream],
        )

        with context:
            while True:
                try:
                    self.run()
                except Exception as e:
                    self.logger.error("An exception occured during daemonization!")
                    self.logger.exception(e)
                    raise


    def run(self):
        """ A run involves checking all warehouse assets and, if they're older
        than their 'max_age' attrib (default to the world.asset_max_age value),
        it refreshes them.

        Once finished, it sleeps for world.refresh_interval, which is measured
        in minutes. """

        W = World()
        W.refresh_all_assets()
        self.logger.debug("World Daemon will sleep for %s minutes..." % settings.get("world","refresh_interval"))
        time.sleep(settings.get("world","refresh_interval") * 60)


    def stop(self):
        """ Stops the daemon. """

        self.set_pid()
        self.logger.warn("Preparing to kill PID %s..." % self.pid)
        if self.pid is not None:
            os.kill(self.pid, 15)
            time.sleep(2)
            try:
                os.kill(self.pid, 0)
            except:
                self.logger.warn("PID %s has been killed." % self.pid)
        else:
            self.logger.debug("Daemon is not running. Ignoring stop command...")


    def get_uptime(self, return_type=None):
        """ Uses the pid file to determine how long the daemon has been active.
        Returns None if the daemon isn't active. Otherwise, this returns a raw
        timedelta. """

        if os.path.isfile(self.pid_file_path):
            pid_file_age = time.time() - os.stat(self.pid_file_path)[stat.ST_MTIME]
            ut = timedelta(seconds=pid_file_age)
            uptime = "%sd %sh %sm" % (ut.days, ut.seconds//3600, (ut.seconds//60)%60)
        else:
            return None

        if return_type == "date":
            return datetime.fromtimestamp(os.stat(self.pid_file_path)[stat.ST_MTIME])

        return uptime


    def dump_status(self, output_type="CLI"):
        """ Prints daemon status to stdout. """

        active = False
        d = {"active": active}
        if self.pid is not None and os.path.isfile(self.pid_file_path):
            active = True

        if active:
            owner_uid = os.stat(self.pid_file_path).st_uid
            owner_name = getpwuid(owner_uid).pw_name

            try:
                utils.mdb.world.find()
            except Exception as e:
                self.logger.error("Daemon is active, but MDB cannot be reached!")
                self.logger.exception(e)
                raise

            d = {}
            d["active"] = active
            d["up_since"] = self.get_uptime("date")
            d["uptime_hms"] = self.get_uptime()
            d["owner_uid"] = owner_uid
            d["owner_name"] = owner_name
            d["pid"] = self.pid
            d["pid_file"] = self.pid_file_path
            d["assets"] = utils.mdb.world.find().count()

        if output_type == dict:
            return d
        elif output_type == "CLI":
            spacer = 15
            print("\n\tWorld Daemon stats:\n")
            for k, v in sorted(d.iteritems()):
                utils.cli_dump(k, spacer, v)
            print("\n")




if __name__ == "__main__":

    # never ever do anything in this file as root. 
    if os.getuid() == 0:
        sys.stderr.write("The API World Daemon may not be operated as root!\n")
        daemon_user = getpwnam(settings.get("world","daemon_user"))
        uid = daemon_user.pw_uid
        gid = daemon_user.pw_gid
        sys.stderr.write("Changing UID to %s\n" % (uid))
        try:
            os.setuid(uid)
        except Exception as e:
            sys.stderr.write("Could not set UID!")
            raise

    # optparse
    parser = OptionParser()
    parser.add_option("-l", dest="list", action="store_true", default=False, help="List warehoused asset handles")
    parser.add_option("-j", dest="list_JSON", action="store_true", default=False, help="Dump 'world' JSON")
    parser.add_option("-u", dest="update", default=False, help="Update one asset's warehouse value", metavar="top_principles")
    parser.add_option("-r", dest="refresh", action="store_true", default=False, help="Force a warehouse refresh")
    parser.add_option("-a", dest="asset", default=False, help="Retrieve an mdb world asset (print a summary)", metavar="latest_survivor")
    parser.add_option("-q", dest="query", default=False, help="Execute a query method (print results)", metavar="avg_pop")
    parser.add_option("-R", dest="remove_one", default=None, help="Remove an object _id from the warehouse", metavar="57f010ec4...")
    parser.add_option("-d", dest="daemon_cmd", help="Daemon controls: status|start|stop|restart", default=None, metavar="restart")
    (options, args) = parser.parse_args()

    # process specific/manual world operations first
    W = World()
    if options.remove_one is not None:
        W.remove(options.remove_one)
    if options.refresh:
        W.logger.debug("Beginning forced asset refresh...")
        W.refresh_all_assets(force=True)
    if options.asset:
        print(W.dump(options.asset))
    if options.update:
        W.refresh_asset(asset_key=options.update, force=True, dump=True)
    if options.query:
        W.query_debug=True
        W.logger.info("Manually executing query '%s' from CLI..." % (options.query))
        print(W.do_query(options.query))
        print("\n\tSee '%s' for complete query debug info!\n" % (W.logger.handlers[0].baseFilename))
    if options.list:
        print(W.list("keys_cli"))
    if options.list_JSON:
        print(W.list(dict)["world"])

    # now process daemon commands
    if options.daemon_cmd is not None:
        if options.daemon_cmd in ["status","start","stop","restart"]:
            D = WorldDaemon()
            D.command(options.daemon_cmd)
        else:
            print("\nInvalid daemon command. Use -h for help. Exiting...\n")
            sys.exit(255)


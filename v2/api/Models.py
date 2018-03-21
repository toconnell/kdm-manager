#!/usr/bin/python2.7

from bson.objectid import ObjectId
from collections import OrderedDict
from copy import copy, deepcopy
from datetime import datetime, timedelta
import json
from bson import json_util
import inspect
import operator
import os
import random
import socket
import unicodedata
from user_agents import parse as ua_parse

from flask import request, Response

import utils
import models
import settings

#
#   Base classes for game assets are here. Also, special exceptions for those
#       classes live here as well.
#

class AssetMigrationError(Exception):
    """ Handler for asset migration/conversion errors. """

    def __init__(self, message="An error occurred while migrating this asset!"):
        self.logger = utils.get_logger()
        self.logger.exception(message)
        Exception.__init__(self, message)

class AssetInitError(Exception):
    """ Handler for asset-based errors. """

    def __init__(self, message="An error occurred while initializing this asset!"):
        self.logger = utils.get_logger()
        self.logger.exception(message)
        Exception.__init__(self, message)

class AssetLoadError(Exception):
    """ Handler for asset-based errors. """

    def __init__(self, message="Asset could not be retrieved from mdb!"):
        self.logger = utils.get_logger()
        self.logger.exception(message)
        Exception.__init__(self, message)


class AssetCollection(object):
    """ The base class for game asset objects, i.e. working with the dict assets
    in the assets/ folder.

    Each model in the models/ folder should have a method that subclasses this
    base class.

    Most Asset() objects that use this as their base class will define their own
    self.assets dict, e.g. in their __init__() method. But is not mandatory:
    review the __init__ method of this class carefully before writing custom
    __init__ code in in an individual Asset() object module. """


    def __repr__(self):
        if not hasattr(self, 'type'):
            self.logger.warn("AssetCollection does not have a 'type' attribute!")
            return 'AssetCollection object (no type; %s assets)' % (len(self.assets))
        return "AssetCollection object '%s' (%s assets)" % (self.type, len(self.assets))


    def __init__(self):
        """ All Assets() models must base-class this guy to get access to the
        full range of AssetCollection methods, i.e. all of the common/ubiquitous
        ones.

        Base-classing also does a little user-friendliness/auto-magic when you
        invoke it:

            - you get self.logger for free.

            - if you set 'self.root_module' to be an actual module from the
            assets folder, that module will be scraped for dictionaries: those
            dictionaries will then be used as your self.assets dict, i.e. so
            that you DO NOT have to define your self.assets in your
            models.Assets() sub class.

            - if you have assets in your model.Assets.assets dict that DO NOT
            set their own type, you can set self.type on your model.Assets when
            you initialize it (but before you base-class this module) to force
            a default 'type' attribute on all of your self.assets dict items.

            - finally, all self.assets items get a 'handle' attribute that is
            the same as their actual dictionary key value. Individual assets
            SHOULD NEVER have a 'handle' attribute.

        """

        self.logger = utils.get_logger()


        if hasattr(self, "root_module"):
            self.type = os.path.splitext(self.root_module.__name__)[-1][1:]
            self.set_assets_from_root_module()

        # preserve 'raw' types as sub types
#        for a in self.assets.keys():
#            a_dict = self.assets[a]
#            if 'type' in a_dict.keys() and not 'sub_type' in a_dict.keys():
#                self.assets[a]['sub_type'] = self.assets[a]['type']

        # type override - be careful!
        if hasattr(self, "type_override"):
            self.type = self.type_override
            for a in self.assets.keys():
                self.assets[a]["type"] = self.type_override

        # set the default 'type_pretty' value 
        self.set_pretty_types()

        for a in self.assets.keys():
            self.assets[a]["handle"] = a


    #
    #   get / set / filter methods here
    #


    def set_assets_from_root_module(self):
        """ This is the vanilla AssetCollection initialization method. You feed
        it a 'module' value (which should be something from the assets/ folder)
        and it creates a self.assets dictionary by iterating through the module.

        If you need to do custom asset initialization, that is a fine and a good
        thing to do, but do it in the actual models/whatever.py file.

        Important! Adjusting the self.assets dict before calling this method
        will overwrite any adjustments because this method starts self.assets as
        a blank dict!
        """

        # the 'type' of all assets is the name of their root module. Full stop.
        # 'sub_type' is where we want to put any kind of 'type' info that we get
        # from the asset itself.

        all_assets = {}

        for module_dict, v in self.root_module.__dict__.iteritems():
            if isinstance(v, dict) and not module_dict.startswith('_'): # get all dicts in the module
                for dict_key in sorted(v.keys()):                               # get all keys in each dict

                    if 'sub_type' in v[dict_key].keys():
                        raise Exception("%s already has a sub type!!!!" % v[dict_key])

                    # do NOT modify the original/raw asset dictionary
                    a_dict = v[dict_key].copy()

                    # set sub_type from raw asset  'type', then set the base type
                    a_dict['sub_type'] = v[dict_key].get("type", module_dict)
                    a_dict["type"] = self.type

                    # add it back to self.assets
                    all_assets[dict_key] = a_dict

        self.assets = OrderedDict()
        for k in sorted(all_assets.keys()):
            self.assets[k] = all_assets[k]


    def set_pretty_types(self, capitalize=True):
        """ Iterates over self.assets; adds the "type_pretty" and 'sub_type_pretty'
        to all assets in the AssetCollection.assets dict """

        for h in self.assets.keys():
            a_dict = self.get_asset(handle=h)

            # flip a shit if we don't have a type
            if a_dict.get('type', None) is None:
                raise Exception("%s asset has no 'type' attribute! %s" % (self, a_dict))

            # set the pretty types here
            for type_attr in ['type', 'sub_type']:

                type_value = a_dict.get(type_attr, None)

                if type_value is None:
                    pretty_type = None
                else:
                    pretty_type = type_value.replace("_"," ")
                    if capitalize:
                        pretty_type = pretty_type.title()

                self.assets[h]["%s_pretty" % type_attr] = pretty_type


    #
    #   common get and lookup methods
    #

    def get_asset(self, handle=None, backoff_to_name=False, raise_exception_if_not_found=True):
        """ Return an asset dict based on a handle. Return None if the handle
        cannot be retrieved. """

        asset = copy(self.assets.get(handle, None))     # return a copy, so we don't modify the actual def

        # implement backoff logic
        if asset is None and backoff_to_name:
            asset = copy(self.get_asset_from_name(handle))

        # if the asset is still None, see if we want to raise an expception
        if asset is None and raise_exception_if_not_found:
            if not backoff_to_name:
                msg = "The handle '%s' is not in %s and could not be retrieved! " % (handle, self.get_handles())
                self.logger.error(msg)
            elif backoff_to_name:
                msg = "After backoff to name lookup, asset handle '%s' is not in %s and could not be retrieved." % (handle, self.get_names())
                self.logger.error(msg)
            raise utils.InvalidUsage(msg)

        # finally, return the asset (or the NoneType)
        return asset

    def get_assets_by_sub_type(self, sub_type=None):
        """ Returns a list of asset handles whose 'sub_type' attribute matches
        the 'sub_type' kwarg value."""

        handles = []
        for a_dict in self.get_dicts():
            sub = a_dict.get('sub_type', None)
            if sub == sub_type:
                handles.append(a_dict['handle'])
        return handles


    def get_assets_by_type(self, asset_type=None):
        """ Returns a list of asset handles whose 'type' attribute matches
        the 'asset_type' kwarg value."""

        handles = []
        for a_dict in self.get_dicts():
            a_type = a_dict.get('type', None)
            if a_type == asset_type:
                handles.append(a_dict['handle'])
        return handles


    def get_handles(self):
        """ Dumps all asset handles, i.e. the list of self.assets keys. """

        try:
            return sorted(self.assets, key=lambda x: self.assets[x]['name'])
        except:
            return sorted(self.assets.keys())


    def get_names(self):
        """ Dumps all asset 'name' attributes, i.e. a list of name values. """

        return sorted([self.assets[k]["name"] for k in self.get_handles()])

    def get_sorted_assets(self):
        """ Returns the asset collections 'assets' dict as an OrderedDict. """

        output = OrderedDict()
        for n in self.get_names():
            asset_dict = self.get_asset_from_name(n)
            output[asset_dict['handle']] = asset_dict
        return output

    def get_sub_types(self):
        """ Dumps a list of all asset 'sub_type' attributes. """

        subtypes = set()
        for a in self.get_handles():
            a_dict = self.get_asset(a)
            subtypes.add(a_dict.get('sub_type', None))
        return sorted(subtypes)

    def get_types(self):
        """ Dumps a list of all asset 'type' attributes. """

        subtypes = set()
        for a in self.get_handles():
            a_dict = self.get_asset(a)
            subtypes.add(a_dict.get('type', None))
        return subtypes

    def get_dicts(self):
        """ Dumps a list of dicts where each dict is an asset dict. """

        output = []
        for h in sorted(self.get_handles()):
            output.append(self.get_asset(h))
        return output



    def get_asset_from_name(self, name, case_sensitive=False, raise_exception_if_not_found=True):
        """ Tries to return an asset dict by looking up "name" attributes within
        the self.assets. dict. Returns None if it fails.

        By default, the mactching here is NOT case-sensitive: everything is
        forced to upper() to allow for more permissive matching/laziness. """

        if type(name) not in [str,unicode]:
            self.logger.error("get_asset_from_name() cannot proceed! '%s' is not a str or unicode object!" % name)
            if raise_exception_if_not_found:
                raise AssetInitError("The get_asset_from_name() method requires a str or unicode type name!")
            else:
                return None

        name = name.strip()

        # special backoff for this dumbass pseudo-expansion
        if name == 'White Box':
            name = 'White Box & Promo'

        if not case_sensitive:
            name = name.upper()

        name_lookup = {}
        for a in self.assets.keys():
            if "name" in self.assets[a]:
                if case_sensitive:
                    name_lookup[self.assets[a]["name"]] = a
                elif not case_sensitive:
                    asset_name_upper = self.assets[a]["name"].upper()
                    name_lookup[asset_name_upper] = a

        if name in name_lookup.keys():
            return self.get_asset(name_lookup[name])
        else:
            return None



    def filter(self, filter_attrib=None, filtered_attrib_values=[], reverse=False):
        """ Drops assets from the collection if their 'filter_attrib' value is
        in the 'attrib_values' list.

        Set 'reverse' kwarg to True to have the filter work in reverse, i.e. to
        drop all assets that DO NOT have 'filter_attrib' values in the
        'filtered_attrib_values' list.
        """

        if filter_attrib is None or filtered_attrib_values == []:
            self.logger.error("AssetCollection.filter() method does not accept None or empty list values!")
            return False

        for asset_key in self.assets.keys():
            if self.get_asset(asset_key).get(filter_attrib, None) is None:
                pass
            elif reverse:
                if self.get_asset(asset_key)[filter_attrib] not in filtered_attrib_values:
                    del self.assets[asset_key]
            else:
                if self.get_asset(asset_key)[filter_attrib] in filtered_attrib_values:
                    del self.assets[asset_key]



    #
    #   no set/get/filter methods below this point!
    #

    def request_response(self, a_name=None, a_handle=None):
        """ Processes a JSON request for a specific asset from the collection,
        initializes the asset (if it can) and then calls the asset's serialize()
        method to create an HTTP response. """

        # first, if the request is a GET, just dump everything and bail
        if request and request.method == "GET":
            return Response(response=json.dumps(self.assets, default=json_util.default), status=200, mimetype="application/json")

        # next, if the request has JSON, check for params
        if request and hasattr(request, 'json'):
            a_name = request.json.get("name", None)
            a_handle = request.json.get("handle", None)

        # if there are no lookups requested, dump everything and bail
        if a_name is None and a_handle is None:
            return Response(response=json.dumps(self.assets, default=json_util.default), status=200, mimetype="application/json")

        # finally, do lookups and create a response based on the outcome
        if a_handle is not None:
            A = self.get_asset(a_handle)
        elif a_name is not None:
            A = self.get_asset_from_name(a_name)

        if A is None:
            return utils.http_404

        return Response(response=json.dumps(A, default=json_util.default), status=200, mimetype="application/json")




class GameAsset(object):
    """ The base class for initializing individual game asset objects. All of
    the specific models in the models/ folder will sub-class this model for
    their generally available methods, etc.

    """

    def __init__(self, handle=None, name=None):

        # initialize basic vars
        self.logger = utils.get_logger()
        self.name = name
        self.handle = handle

    def __repr__(self):
        return "%s object '%s' (assets.%s['%s'])" % (self.type.title(), self.name, self.type, self.handle)


    def initialize(self):
        """ Call this method to initialize the object. """

        if self.handle is not None:
            self.initialize_from_handle()
        elif self.name is not None:
            self.initialize_from_name()
        elif self.handle is None and self.name is None:
            raise AssetInitError("Asset objects must be initialized with 'handle' or 'name' kwargs.")
        else:
            raise AssetInitError()


    def initialize_asset(self, asset_dict):
        """ Pass this a valid asset dictionary to set the object's attributes
        with a bunch of exec calls. """

        if type(asset_dict) != dict:
            raise AssetInitError("Asset objects may not be initialized with a '%s' type object!" % type(asset_dict))

        for k, v in asset_dict.iteritems():
            if type(v) == str:
                exec """self.%s = '%s' """ % (k,v.replace('"','\\"').replace("'","\\'"))
            elif type(v) == datetime:
                exec """self.%s = '%s' """ % (k,v.strftime(utils.ymd))
            else:
                exec "self.%s = %s" % (k,v)


    def initialize_from_handle(self):
        """ If we've got a not-None handle, we can initiailze the asset object
        by checking self.assets to see if our handle is a valid key.
        If we can't find a valid key, throw an exception. """

        # sanity warning
        if " " in self.handle:
            self.logger.warn("Asset handle '%s' contains whitespaces. Handles should use underscores." % self.handle)

        self.asset_dict = self.assets.get_asset(self.handle)
        self.initialize_asset(self.asset_dict)

        if self.name is None:
            raise AssetInitError("Asset handle '%s' could not be retrieved!" % self.handle)


    def initialize_from_name(self):
        """ If we've got a not-None name, we can initiailze the asset object
        by checking self.assets to see if we can find an asset whose "name"
        value matches our self.name. """


        # sanity warning
        if "_" in self.name:
            self.logger.warn("Asset name '%s' contains underscores. Names should use whitespaces." % self.name)

        lookup_dict = {}
        for asset_handle in self.assets.get_handles():
            asset_dict = self.assets.get_asset(asset_handle)
            lookup_dict[asset_dict["name"]] = asset_handle

        if self.name in lookup_dict.keys():
            self.handle = lookup_dict[self.name]
            self.initialize_from_handle()

        if self.handle is None:
            raise AssetInitError("Asset handle '%s' could not be retrieved!" % self.handle)


    def serialize(self, return_type=None):
        """ Allows the object to represent itself as JSON by transforming itself
        into a JSON-safe dict. """

        shadow_self = copy(self)

        for banned_attrib in ["logger", "assets"]:
            if hasattr(shadow_self, banned_attrib):
                delattr(shadow_self, banned_attrib)

        if return_type == dict:
            return shadow_self.__dict__

        return json.dumps(shadow_self.__dict__, default=json_util.default)


    #
    # look-up and manipulation methods below
    #

    def get(self, attrib):
        """ Wrapper method for trying to retrieve asset object attributes.
        Returns a None type value if the requested attrib doesn't exist. """

        try:
            return getattr(self, attrib)
        except:
            return None




class UserAsset(object):
    """ The base class for all user asset objects, such as survivors, sessions,
    settlements and users. All user asset controllers in the 'models' module
    use this as their base class. """


    def __repr__(self):
        """ Default __repr__ method for all user assets. Note that you should
        PROBABLY define a __repr__ for your individual assets, if for no other
        reason than to make the logs look cleaner. """

        try:
            exec 'repr_name = self.%s["name"]' % (self.collection[:-1])
        except:
            self.logger.warn("UserAsset object has no 'name' attribute!")
            repr_name = "UNKNOWN"
        return "%s object '%s' [%s]" % (self.collection, repr_name, self._id)


    def __init__(self, collection=None, _id=None, normalize_on_init=True, new_asset_attribs={}, Settlement=None):

        # initialize basic vars
        self.logger = utils.get_logger()
        self.normalize_on_init = normalize_on_init
        self.new_asset_attribs = new_asset_attribs

        if collection is not None:
            self.collection = collection
        elif hasattr(self,"collection"):
            pass
        else:
            err_msg = "User assets (settlements, users, etc.) may not be initialized without specifying a collection!"
            self.logger.error(err_msg)
            raise AssetInitError(err_msg)

        # use attribs to determine whether the object has been loaded
        self.loaded = False

        if _id is None:
            self.get_request_params()
            self.new()
            _id = self._id

        # if we're initializing with a settlement object already in memory, use it
        # if this object IS a Settlement, the load() call below will overwrite this
        self.Settlement = Settlement

        # now do load() stuff
        try:
            try:
                self._id = ObjectId(_id)
            except Exception as e:
                self.logger.error(e)
                raise utils.InvalidUsage("The asset OID '%s' does not appear to be a valid object ID! %s" % (_id,e), status_code=422)
            self.load()
            self.loaded = True
        except Exception as e:
            self.logger.error("Could not load _id '%s' from %s!" % (_id, self.collection))
            self.logger.exception(e)
            raise



    def save(self, verbose=True):
        """ Saves the user asset back to either the 'survivors' or 'settlements'
        collection in mdb, depending on self.collection. """

        if self.collection == "settlements":
            utils.mdb.settlements.save(self.settlement)
        elif self.collection == "survivors":
            utils.mdb.survivors.save(self.survivor)
        elif self.collection == "users":
            utils.mdb.users.save(self.user)
        else:
            raise AssetLoadError("Invalid MDB collection for this asset!")
        if verbose:
            self.logger.info("Saved %s to mdb.%s successfully!" % (self, self.collection))


    def load(self):
        """ Retrieves an mdb doc using self.collection and makes the document an
        attribute of the object. """

        mdb_doc = self.get_mdb_doc()

        if self.collection == "settlements":
            self.settlement = mdb_doc
            self._id = self.settlement["_id"]
            self.settlement_id = self._id
            self.get_campaign('initialize')     # sets an object
            self.get_survivors('initialize')    # sets a list of objects
            self.init_asset_collections()
        elif self.collection == "survivors":
            self.survivor = mdb_doc
            self._id = self.survivor["_id"]
            self.settlement_id = self.survivor["settlement"]
        elif self.collection == "users":
            self.user = mdb_doc
            self._id = self.user["_id"]
            self.login = self.user["login"]
        else:
            raise AssetLoadError("Invalid MDB collection for this asset!")



    def return_json(self):
        """ Calls the asset's serialize() method and creates a simple HTTP
        response. """
        return Response(response=self.serialize(), status=200, mimetype="application/json")


    #
    #   request helpers
    #

    def get_request_params(self, verbose=False):
        """ Checks the incoming request (from Flask) for JSON and tries to add
        it to self. """

        params = {}

        if verbose:
            self.logger.debug("%s request info: %s" % (request.method, request.url))
            self.logger.debug("%s request user: %s" % (request.method, request.User))

        if request.method == "GET" and verbose:
            self.logger.warn("%s:%s get_request_params() call is being ignored!" % (request.method, request.url))
            return False

#        self.logger.debug(request.get_json())

        if request.get_json() is not None:
            try:
                params = dict(request.get_json())
            except ValueError:
                self.logger.warn("%s request JSON could not be converted to dict!" % request.method)
                params = request.get_json()
        else:
            if verbose:
                self.logger.warn("%s request did not contain JSON data!" % request.method)
                self.logger.warn("Request URL: %s" % request.url)

        self.params = params



    def check_request_params(self, keys=[], verbose=True, raise_exception=True):
        """ Checks self.params for the presence of all keys specified in 'keys'
        list. Returns True if they're present and False if they're not.

        Set 'verbose' to True if you want to log validation failures as errors.
        """

        for k in keys:
            if k not in self.params.keys():
                if verbose:
                    self.logger.error("Request JSON is missing required parameter '%s'!" % k)
                if raise_exception:
                    curframe = inspect.currentframe()
                    calframe = inspect.getouterframes(curframe, 2)
                    caller_function = calframe[1][3]
                    msg = "Insufficient request parameters for this route! The %s() method requires values for the following keys: %s." % (caller_function, utils.list_to_pretty_string(keys))
                    self.logger.exception(msg)
                    self.logger.error("Bad request params were: %s" % self.params)
                    raise utils.InvalidUsage(msg, status_code=400)
                else:
                    return False

        return True



    #
    #   get/set methods for User Assets below here
    #


    def get_campaign(self, return_type=None):
        """ Returns the campaign handle of the settlement as a string, if
        nothing is specified for kwarg 'return_type'.

        Use 'name' to return the campaign's name (from its definition).

        'return_type' can also be dict. Specifying dict gets the
        raw campaign definition from assets/campaigns.py. """

        # first, get the handle; die if we can't
	if self.collection == "survivors":
            c_handle = self.Settlement.settlement["campaign"]
        elif self.collection == "settlements":
            # 2017-11-13 - bug fix - missing campaign attrib
            if not "campaign" in self.settlement.keys():
                self.settlement["campaign"] = 'people_of_the_lantern'
                self.logger.warn("%s is a legacy settlement! Adding missing 'campaign' attribute!" % self)
                self.save()
            c_handle = self.settlement["campaign"]
        else:
            msg = "Objects whose collection is '%s' may not call the get_campaign() method!" % (self.collection)
            raise AssetInitError(msg)

        # now try to get the dict
        C = models.campaigns.Assets()
        c_dict = C.get_asset(c_handle, backoff_to_name=True)

        # handle return_type requests
        if return_type == 'name':
            return c_dict["name"]
        elif return_type == dict:
            return c_dict
        elif return_type == 'initialize':
            self.campaign = models.campaigns.Campaign(c_dict['handle'])
            return True

        return c_handle


    def get_serialize_meta(self):
        """ Sets the 'meta' dictionary for the object when it is serialized. """

        output = deepcopy(utils.api_meta)

        if output['meta'].keys() != ['webapp','admins','api','object']:
            stack = inspect.stack()
            the_class = stack[1][0].f_locals["self"].__class__
            the_method = stack[1][0].f_code.co_name
            msg = "Models.UserAsset.get_serialize_meta() got modified 'meta' (%s) dict during call by %s.%s()!" % (output['meta'].keys(), the_class, the_method)
            self.logger.error(msg)

        try:
            output["meta"]["object"]["version"] = self.object_version
        except Exception as e:
            self.logger.error("Could not create 'meta' dictionary when serializing object!")
            self.logger.exception(e)
            self.logger.warn(output["meta"])
        return output


    def get_current_ly(self):
        """ Convenience/legibility function to help code readbility and reduce
        typos, etc. """

        if self.collection == "survivors":
            return int(self.Settlement.settlement["lantern_year"])
        return int(self.settlement["lantern_year"])


    def get_mdb_doc(self):
        """ Retrieves the asset's MDB document. Raises a special exception if it
        cannot for some reason. """

        mdb_doc = utils.mdb[self.collection].find_one({"_id": self._id})
        if mdb_doc is None:
            raise AssetLoadError("Asset _id '%s' could not be found in '%s'!" % (self._id, self.collection))
        return mdb_doc


    def list_assets(self, attrib=None, log_failures=True):
        """ Laziness method that returns a list of dictionaries where dictionary
        in the list is an asset in the object's list of those assets.

        Basically, if your object is a survivor, and you set 'attrib' to
        'abilities_and_impairments', you get back a list of dictionaries where
        dictionary is an A&I asset dictionary.

        Same goes for settlements: if you set 'attrib' to 'locations', you get
        a list where each item is a location asset dict.

        Important! This ignores unregistered/unknown/bogus items! Anything that
        cannot be looked up by its handle or name is ignored!
        """

        if attrib is None:
            msg = "The list_assets() method cannot process 'None' type values!"
            self.logger.error(msg)
            raise Exception(msg)

        output = []
        if attrib == "principles":
            A = models.innovations.Assets()
        else:
            exec "A = models.%s.Assets()" % attrib
        exec "asset_list = self.%s['%s']" % (self.collection[:-1], attrib)

        for a in asset_list:
            a_dict = A.get_asset(a, backoff_to_name=True, raise_exception_if_not_found=False)
            if a_dict is not None:
                output.append(a_dict)
            elif a_dict is None and log_failures:
                self.logger.error("%s Unknown '%s' asset '%s' cannot be listed!" % (self, attrib, a))
            else:
                pass # just ignore failures and silently fail

        return output




    #
    #   asset update methods below
    #
    @utils.log_event_exception_manager
    def log_event(self, msg=None, event_type=None, action=None, key=None, value=None, agent=None):
        """ This is the primary user-facing logging interface, so there' s a bit
        of a high bar for using it.

        The basic idea of creating a log entry is that we're doing a bit of the
        semantic logging (i.e. strongly typed) thing, so, depending on which
        kwargs you use when calling this method, your final outcome/message is
        going to vary somewhat.

        That said, none of the kwargs here are mandatory, because context.
        """

        # 
        #   baseline attributes
        #

        # for those who still raw-dog it; force to ASCII:
        if msg is not None:
            msg = msg.encode("ascii",'ignore')

        # 0.) method: determine caller method
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        method = calframe[2][3]

        # 1.) event: determine event type if it's None
        if event_type is None:
            event_type = method

        # 2.) action: figure out the action; set the special action vars
        if action is None:
            action = method.split("_")[0]
        action_word, action_preposition = utils.action_keyword(action)

        # 3.) key: default the key if we don't get one
        if key is None:
            key = " ".join(method.split("_")[1:])
        key = key.encode('ascii','ignore')

        # 4.) value; default the value if we don't get one
        if value is None:
            value = "UNKNOWN"
        value = value.encode('ascii','ignore')

        # set 'created_by'
        created_by = None
        created_by_email = None
        if request:
            if hasattr(request, 'User'):
                created_by = request.User.user['_id']
                created_by_email = request.User.user['login']
                if agent is None:
                    agent = "user"


        # set 'attribute_modified'

        attribute_modified = {
            'key': key,
            'value': value,
        }

        if attribute_modified['key'] is not None:
            attribute_modified['key_pretty'] = key.replace("_"," ").replace("and","&").title()
        if attribute_modified['value'] is not None:
            attribute_modified['value_pretty'] = str(value).replace("_"," ")

        d = {
            'version': 1.3,
            'agent': agent,
            "created_on": datetime.now(),
            'created_by': created_by,
            'created_by_email': created_by_email,
            "settlement_id": self.settlement_id,
            "ly": self.get_current_ly(),
            'event_type': event_type,
            'event': msg,
            'modified': {'attribute': attribute_modified},
        }

        # survivor, if it's a survivor
        if self.collection == 'survivors':
            d['survivor_id'] = self.survivor['_id']

        # target is the settlement, unless a survivor object calls this method
        action_target = "settlement"
        if 'survivor_id' in d.keys():
            d['modified']['asset'] = {
                'type': 'survivor',
                '_id': d['survivor_id'],
                'name': self.survivor['name'],
                'sex': self.get_sex(),
            }
            action_target = "survivor"
        else:
            d['modified']['asset'] = {"type": "settlement", "name": self.settlement['name'], '_id': self.settlement_id}

        # create the 'action'
        d['action'] = {'word': action_word, 'preposition': str(action_preposition)}
        if key is None and value is None:
            d['action']['repr'] = " ".join(['modified', action_target])
        elif key is not None and value is None:
            d['action']['repr'] = " ".join(['modified', action_target, key])
        elif key is None and value is None:
            d['action']['repr'] = " ".join(['modified', action_target])
        else:
            if action_target == "survivor" and action_preposition is None:
                d['action']['repr'] = action_word
            elif action_target == "survivor" and action_preposition is not None:
                d['action']['repr'] = " ".join([action_word, "'%s'" % value, action_preposition, str(key)])
            else:
                d['action']['repr'] = " ".join([action_word, "'%s'" % value, action_preposition, action_target, str(key)])

        # default a message, if incoming message is none
        if msg is None:
            if d['modified']['asset']['type'] == 'survivor':
                if d['agent'] == 'user' and action_preposition is None:
                    d['event'] = " ".join([
                        d['created_by_email'],
                        d['action']['word'],
                        "%s [%s]" % (self.survivor['name'], self.get_sex()),
                    ])
                elif d['agent'] == 'user' and action_preposition is not None:
                    d['event'] = " ".join([
                        d['created_by_email'],
                        d['action']['word'],
                        d['modified']['attribute']['value_pretty'],
                        d['action']['preposition'],
                        "%s [%s]" % (self.survivor['name'], self.get_sex()),
                        d['modified']['attribute']['key_pretty'],
                    ])
                else:
                    d['event'] = " ".join([
                        "%s [%s]" % (self.survivor['name'], self.get_sex()),
                        d['action']['word'],
                        d['modified']['attribute']['value_pretty'],
                        d['action']['preposition'],
                        d['modified']['attribute']['key_pretty'],
                    ])
            else:
                d['event'] = " ".join([d['created_by_email'], d['action']['repr'], ])

        # enforce terminal punctuation on the event "sentence"
        if d['event'][-1] not in ['.','!']:
            d['event'] += "."

        d['event'] = d['event'].decode('ascii','replace').encode('utf-8','replace')

        # finally, if we had a requester, now that we've settled on a message
        # text, update the requester's latest action with it
        if 'created_by' is not None:
            if request:
                ua_string = str(ua_parse(request.user_agent.string))
                request.User.set_latest_action(d['event'], ua_string)

        # finally, insert the event (i.e. save)
        utils.mdb.settlement_events.insert(d)
        self.logger.info("%s event: %s" % (self, d['event']))





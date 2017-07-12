#!/usr/bin/python2.7

from bson.objectid import ObjectId
from copy import copy
from datetime import datetime, timedelta
import json
from bson import json_util
import inspect

from flask import request, Response

import utils
import models

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


class AssetCollection():
    """ The base class for game asset objects, i.e. working with the dict assets
    in the assets/ folder.

    Each model in the models/ folder should have a method that subclasses this
    base class.

    Most Asset() objects that use this as their base class will define their own
    self.assets dict, e.g. in their __init__() method. But is not mandatory:
    review the __init__ method of this class carefully before writing custom
    __init__ code in in an individual Asset() object module. """


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
            self.set_assets_from_root_module()

        # type override
        if hasattr(self, "type"):
            for a in self.assets.keys():
                self.assets[a]["type"] = self.type

        # set the default 'type_pretty' value (no caps)
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

        self.assets = {}
        for k, v in self.root_module.__dict__.iteritems():
            if isinstance(v, dict) and not k.startswith('_'):
                for dict_key in v.keys():
                    if v[dict_key].get("type", None) is None:
                        v[dict_key]["type"] = k
                    self.assets.update(v)


    def set_pretty_types(self, capitalize=False):
        """ Iterates over self.assets; adds the "type_pretty" key to all assets. """
        for a in self.assets.keys():
            pretty_type = self.get_asset(a)["type"].replace("_"," ")
            if capitalize:
                pretty_type = pretty_type.capitalize()
            self.assets[a]["type_pretty"] = pretty_type


    #
    #   common get and lookup methods
    #


    def get_handles(self):
        """ Dumps all asset handles, i.e. the list of self.assets keys. """

        return sorted(self.assets.keys())


    def get_names(self):
        """ Dumps all asset 'name' attributes, i.e. a list of name values. """

        return sorted([self.assets[k]["name"] for k in self.get_handles()])

    def get_dicts(self):
        """ Dumps a list of dicts where each dict is an asset dict. """

        output = []
        for h in sorted(self.get_handles()):
            output.append(self.get_asset(h))
        return output


    def get_asset(self, handle, backoff_to_name=False):
        """ Return an asset dict based on a handle. Return None if the handle
        cannot be retrieved. """

        asset = copy(self.assets.get(handle, None))     # return a copy, so we don't modify the actual def

        if asset is None and backoff_to_name:
            return self.get_asset_from_name(handle)
        else:
            return asset


    def get_asset_from_name(self, name, case_sensitive=False):
        """ Tries to return an asset dict by looking up "name" attributes within
        the self.assets. dict. Returns None if it fails.

        By default, the mactching here is NOT case-sensitive: everything is
        forced to upper() to allow for more permissive matching/laziness. """

        if type(name) not in [str,unicode]:
            self.logger.error("get_asset_from_name() cannot proceed! '%s' is not a str or unicode object!" % name)
            raise AssetInitError("The get_asset_from_name() method requires a str or unicode type name!")

        name = name.strip()
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
            if reverse:
                if self.get_asset(asset_key)[filter_attrib] not in filtered_attrib_values:
                    del self.assets[asset_key]
            else:
                if self.get_asset(asset_key)[filter_attrib] in filtered_attrib_values:
                    del self.assets[asset_key]



    #
    #   no set/get/filter methods below this point!
    #

    def request_response(self, req):
        """ Processes a JSON request for a specific asset from the collection,
        initializes the asset (if it can) and then calls the asset's serialize()
        method to create an HTTP response. """

        a_name = req.get("name", None)
        a_handle = req.get("handle", None)

        try:
            if a_handle is not None:
                A = self.AssetClass(a_handle)
            elif a_name is not None:
                A = self.AssetClass(name=a_name)
            else:
                return utils.http_422
        except Exception as e:
            self.logger.exception(e)
            return utils.http_404

        return Response(response=A.serialize(), status=200, mimetype="application/json")




class GameAsset():
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
        return "%s object '%s' (assets.%ss['%s'])" % (self.type.title(), self.name, self.type, self.handle)


    def initialize(self):
        """ Call this method to initialize the object. """

        if self.handle is not None:
            self.initialize_from_handle()
        elif self.name is not None:
            self.initialize_from_name()
        elif handle is None and name is None:
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
                exec """self.%s = "%s" """ % (k,v)
            else:
                exec "self.%s = %s" % (k,v)


    def initialize_from_handle(self):
        """ If we've got a not-None handle, we can initiailze the asset object
        by checking self.assets to see if our handle is a valid key.
        If we can't find a valid key, throw an exception. """

        # sanity warning
        if " " in self.handle:
            self.logger.warn("Asset handle '%s' contains whitespaces. Handles should use underscores." % self.handle)

        asset_dict = self.assets.get_asset(self.handle)
        self.initialize_asset(asset_dict)

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


    def serialize(self):
        """ Allows the object to represent itself as JSON by transforming itself
        into a JSON-safe dict. """

        shadow_self = copy(self)

        for banned_attrib in ["logger", "assets"]:
            if hasattr(shadow_self, banned_attrib):
                delattr(shadow_self, banned_attrib)

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




class UserAsset():
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


    def __init__(self, collection=None, _id=None, normalize_on_init=True, new_asset_attribs={}):

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
            self.new()
            _id = self._id

        try:
            self._id = ObjectId(_id)
            self.load()
            self.loaded = True
        except Exception as e:
            self.logger.error("Could not load _id '%s' from %s!" % (_id, self.collection))
            self.logger.exception(e)
            raise


    def save(self):
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
        self.logger.info("Saved %s to mdb.%s successfully!" % (self, self.collection))


    def load(self):
        """ Retrieves an mdb doc using self.collection and makes the document an
        attribute of the object. """

        mdb_doc = self.get_mdb_doc()

        if self.collection == "settlements":
            self.settlement = mdb_doc
            self._id = self.settlement["_id"]
            self.settlement_id = self._id
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

    def get_asset(self, asset_class=None, asset_handle=None):
        """ Set 'asset_class' kwarg to the string of an asset collection and
        'asset_handle' to any handle within that asset collection and this
        func will return the value of 'asset_class' and an asset dict for the
        'asset_handle' value.

        This method will back off to the incoming request if 'asset_type' is
        None. """

        #
        #   initialize. Try to use kwargs, but back off to request params
        #   if incoming kwargs are None
        #

        if asset_class is None:
            self.check_request_params(["type", "handle"])
            asset_class = self.params["type"]
            asset_handle = self.params["handle"]
        elif asset_class is not None and asset_handle is None:
            self.check_request_params(["handle"])
            asset_handle = self.params["handle"]

        # try to get the asset; bomb out if we can't
        exec "A = models.%s.Assets()" % asset_class
        asset_dict = A.get_asset(asset_handle)
        if asset_dict is None:
            msg = "%s.Assets() class does not include handle '%s'!" % (asset_class, asset_handle)
            self.logger.exception(msg)
            raise utils.InvalidUsage(msg, status_code=400)

        return asset_class, asset_dict


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
                    msg = "Insufficient request params for %s() method!" % caller_function
                    self.logger.exception(msg)
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
            c_handle = self.settlement["campaign"]
        else:
            msg = "Objects whose collection is '%s' may not call the get_campaign() method!" % (self.collection)
            raise AssetInitError(msg)

        # now try to get the dict
        C = models.campaigns.Assets()

        if c_handle not in C.get_handles():
            err = "The handle '%s' does not reference any known campaign definition!" % c_handle
            raise AssetInitError(err)

        # handle return_type requests
        if return_type == 'name':
            return C.get_asset(c_handle)["name"]
        elif return_type == dict:
            return C.get_asset(c_handle)

        return c_handle


    def get_serialize_meta(self):
        """ Sets the 'meta' dictionary for the object when it is serialized. """

        output = copy(utils.api_meta)
        try:
            output["meta"]["object"]["version"] = self.object_version
        except Exception as e:
            self.logger.error("Could not create 'meta' dictionary when serializing object!")
            self.logger.exception(e)
            self.logger.warn(utils.api_meta)
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
            raise AssetLoadError()
        return mdb_doc


    def list_assets(self, attrib=None, log_failures=False):
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
            a_dict = A.get_asset(a, backoff_to_name=True)
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

    def log_event(self, msg, event_type=None):
        """ Logs a settlement event to mdb.settlement_events. """

        d = {
            "created_on": datetime.now(),
            "created_by": None,
            "settlement_id": self.settlement_id,
            "ly": self.get_current_ly(),
            "event": msg,
            "event_type": event_type,
        }
        utils.mdb.settlement_events.insert(d)
        self.logger.debug("%s event: %s" % (self, msg))





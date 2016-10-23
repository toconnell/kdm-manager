#!/usr/bin/python2.7

import utils

#
#   Base classes for game assets are here. Also, special exceptions for those
#       classes live here as well.
#


class AssetInitError(Exception):
    """ Handler for asset-based errors. """

    def __init__(self, message="An error occurred while initializing this asset!"):
        self.logger = utils.get_logger()
        self.logger.exception(message)
        Exception.__init__(self, message)


class AssetCollection():
    """ The base class for game asset objects, i.e. working with the dict assets
    in the assets/ folder.

    Each model in the models/ folder should have a method that subclasses this
    base class.

    All asset objects that use this as their base class MUST define their own
    self.assets dict (preferably in their __init__() method). """

    def __init__(self):
        """ Initialize with a blank self.assets dict. """
        self.assets = {}

    def get_handles(self):
        """ Dumps all asset handles, i.e. the list of self.assets keys. """
        return self.assets.keys()

    def get_asset(self, handle):
        """ Return an asset dict based on a handle. Return None if the handle
        cannot be retrieved. """
        try:
            return self.assets[handle]
        except:
            return None

    def get_asset_from_name(self, name, case_sensitive=False):
        """ Tries to return an asset dict by looking up "name" attributes within
        the self.assets. dict. Returns None if it fails.

        By default, the mactching here is NOT case-sensitive: everything is
        forced to upper() to allow for more permissive matching/laziness. """

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
            raise utils.AssetError("Asset handle '%s' could not be retrieved!" % self.handle)


    def initialize_from_name(self):
        """ If we've got a not-None name, we can initiailze the asset object
        by checking self.assets to see if we can find an asset whose "name"
        value matches our self.name. """

        # sanity warning
        if "_" in self.handle:
            self.logger.warn("Asset name '%s' contains underscores. Names should use whitespaces." % self.name)

        if self.handle is None:
            raise utils.AssetError("Asset handle '%s' could not be retrieved!" % self.handle)


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

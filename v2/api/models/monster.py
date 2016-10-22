#!/usr/bin/python2.7


import utils

from assets import monsters


class Monster:
    """ This is the base class for all monsters. We should NOT have to sub-class
    it with quarry/nemesis type child classes, but that design may change. """

    def __init__(self, handle=None, name=None):
        # initialize basic vars
        self.logger = utils.get_logger()
        self.name = name
        self.handle = handle

        # set assets
        self.set_assets()

        # now try to initialize an object based on kwargs and assets
        if handle is not None:
            self.initialize_from_handle()
        elif name is not None:
            self.initialize_from_name()
        elif handle is None and name is None:
            raise utils.AssetError("Either 'handle' or 'name' kwarg must be specified!")
        else:
            raise utils.AssetError()

        self.normalize()



    #
    # initialization methods including normalize
    #

    def set_assets(self):
        """ Initializes the class_asset values for the Monster object. These
        travel with every object to facilitate on-the-fly look-ups. """
        self.class_assets = {}
        self.class_assets.update(utils.AssetDict(monsters.quarries, {"type": "quarry"}))
        self.class_assets.update(utils.AssetDict(monsters.unique_quarries, {"type": "quarry", "unique": True}))
        self.class_assets.update(utils.AssetDict(monsters.nemeses, {"type": "nemesis"}))
        self.class_assets.update(utils.AssetDict(monsters.unique_nemeses, {"type": "nemesis", "unique": True}))


    def initialize_asset(self, d):
        """ Pass this a valid asset dictionary to set the object's attributes
        with a bunch of exec calls. """

        for k, v in d.iteritems():
            if type(v) == str:
                exec """self.%s = "%s" """ % (k,v)
            else:
                exec "self.%s = %s" % (k,v)


    def initialize_from_name(self):
        """ Try to initialize a monster object from a string. Lots of craziness
        here to protect the users from themselves. """

        # sanity warning
        if "_" in self.name:
            self.logger.warn("Asset name '%s' contains underscores. Names should use whitespace." % self.name)

        # first, check for an exact name match (long-shot)
        search_result = utils.search_dict(self.class_assets, self.name)
        if search_result is not None:
            self.initialize_asset(search_result)
            return True

        # next, split to a list and try to set asset and level
        name_list = self.name.split(" ")

        # accept any int in the string as the level
        for i in name_list:
            try:
                setattr(self, "level", int(i))
            except:
                pass

        # now iterate through the list and see if we can get a name from it
        for i in range(len((name_list))):
            parsed_name = " ".join(name_list[:i])
            search_result = utils.search_dict(self.class_assets, parsed_name)
            if search_result is not None:
                self.initialize_asset(search_result)
                if len(name_list) > i and name_list[i].upper() not in ["LEVEL","LVL","L"]:
                    setattr(self, "comment", (" ".join(name_list[i:])))
                return True

        # finally, create a list of misspellings and try to get an asset from that
        #   (this is expensive, so it's a last resort)
        m_dict = {}
        for asset_handle in self.class_assets.keys():
            asset_dict = self.class_assets[asset_handle]
            if "misspellings" in asset_dict.keys():
                for m in asset_dict["misspellings"]:
                    m_dict[m] = asset_handle


        for i in range(len((name_list))+1):
            parsed_name = " ".join(name_list[:i]).upper()
            if parsed_name in m_dict.keys():
                asset_key = m_dict[parsed_name]
                self.initialize_asset(self.class_assets[asset_key])
                if len(name_list) > i and name_list[i].upper() not in ["LEVEL","LVL","L"]:
                    setattr(self, "comment", (" ".join(name_list[i:])))
                return True


        # if we absolutely cannot guess wtf monster name this is, give up and
        #   throw a utils.Asseterror()
        if self.handle is None:
            raise utils.AssetError("Asset name '%s' could not be translated to an asset handle!" % self.name)


    def initialize_from_handle(self):
        """ If we've got a not-None handle, we can initiailze the Monster class
        by checking self.asset_dictionaries to see if our handle is a valid key.
        If we can't find a valid key, throw an exception. """

        # sanity warning
        if " " in self.handle:
            self.logger.warn("Asset handle '%s' contains whitespaces. Handles should use underscores." % self.handle)

        if self.handle in self.class_assets.keys():
            asset_dict = self.class_assets[self.handle]
            self.initialize_asset(asset_dict)

        if self.name is None:
            raise utils.AssetError("Asset handle '%s' could not be retrieved!" % self.handle)


    def normalize(self):
        """ Enforce our data model after initialization. """

        # unique monsters can't have levels, so strip them
        if hasattr(self, "__unique__"):
            try:
                del self.level
            except:
                pass


    #
    # look-up and manipulation methods below
    #
    def get(self, attrib):
        """ Wrapper method for trying to retrieve monster object attributes.
        Returns a None type value if the requested attrib doesn't exist. """

        try:
            return getattr(self, attrib)
        except:
            return None








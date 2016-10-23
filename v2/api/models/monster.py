#!/usr/bin/python2.7


from assets import monsters
import Models
import utils

class Assets(Models.AssetCollection):

    def __init__(self):
        self.assets = {}
        self.assets.update(utils.AssetDict(monsters.quarries, {"type": "quarry"}))
        self.assets.update(utils.AssetDict(monsters.unique_quarries, {"type": "quarry", "unique": True}))
        self.assets.update(utils.AssetDict(monsters.nemeses, {"type": "nemesis"}))
        self.assets.update(utils.AssetDict(monsters.unique_nemeses, {"type": "nemesis", "unique": True}))



class Monster(Models.GameAsset):
    """ This is the base class for all monsters. We should NOT have to sub-class
    it with quarry/nemesis type child classes, but that design may change. """

    def __init__(self, *args, **kwargs):
        Models.GameAsset.__init__(self,  *args, **kwargs)

        self.assets = Assets()
        self.initialize()
        self.normalize()


    #
    #   monster-specific initialization methods
    #

    def normalize(self):
        """ Enforce our data model after initialization. """

        # unique monsters can't have levels, so strip them
        if hasattr(self, "__unique__"):
            try:
                del self.level
            except:
                pass


    def initialize_from_name(self):
        """ Try to initialize a monster object from a string. Lots of craziness
        here to protect the users from themselves. """

        # sanity warning
        if "_" in self.name:
            self.logger.warn("Asset name '%s' contains underscores. Names should use whitespace." % self.name)

        # first, check for an exact name match (long-shot)
        asset_dict = self.assets.get_asset_from_name(self.name)
        if asset_dict is not None:
            self.initialize_asset(asset_dict)
            return True

        # next, split to a list and try to set asset and level
        name_list = self.name.split(" ")

        # accept any int in the string as the level
        for i in name_list:
            if i.isdigit():
                setattr(self, "level", int(i))

        # now iterate through the list and see if we can get a name from it
        for i in range(len((name_list))):
            parsed_name = " ".join(name_list[:i])
            asset_dict = self.assets.get_asset_from_name(parsed_name)
            if asset_dict is not None:
                self.initialize_asset(asset_dict)
                if len(name_list) > i and name_list[i].upper() not in ["LEVEL","LVL","L"]:
                    setattr(self, "comment", (" ".join(name_list[i:])))
                return True

        # finally, create a list of misspellings and try to get an asset from that
        #   (this is expensive, so it's a last resort)
        m_dict = {}
        for asset_handle in self.assets.get_handles():
            asset_dict = self.assets.get_asset(asset_handle)
            if "misspellings" in asset_dict.keys():
                for m in asset_dict["misspellings"]:
                    m_dict[m] = asset_handle

        for i in range(len((name_list))+1):
            parsed_name = " ".join(name_list[:i]).upper()
            if parsed_name in m_dict.keys():
                asset_handle = m_dict[parsed_name]
                self.initialize_asset(self.assets.get_asset(asset_handle))
                if len(name_list) > i and name_list[i].upper() not in ["LEVEL","LVL","L"]:
                    setattr(self, "comment", (" ".join(name_list[i:])))
                return True


        # if we absolutely cannot guess wtf monster name this is, give up and
        #   throw a utils.Asseterror()
        if self.handle is None:
            raise Models.AssetInitError("Asset name '%s' could not be translated to an asset handle!" % self.name)






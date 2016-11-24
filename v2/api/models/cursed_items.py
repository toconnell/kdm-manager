#!/usr/bin/python2.7


from assets import cursed_items
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self):

        self.assets = cursed_items.items
        for a in self.assets.keys():
            self.assets[a]["handle"] = a
            self.assets[a]["__type__"] = "cursed_item"


class CursedItem(Models.GameAsset):
    """ This is the base class for all cursed items."""

    def __init__(self, *args, **kwargs):
        Models.GameAsset.__init__(self,  *args, **kwargs)

        self.assets = Assets()
        self.initialize()

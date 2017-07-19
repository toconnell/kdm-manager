#!/usr/bin/python2.7


from datetime import datetime

from assets import expansions
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        """ Expansion assets are organized in assets/expansions.py according to
        release date, so when we initialize an asset dict from expansions.py, we
        manually add a "meta" style key to indicate their release date. """

        self.type = "expansion"
        self.assets = expansions.mar_2016_expansions
        for asset in self.assets:
            self.assets[asset]["released"] = datetime(2016,3,14)
        self.assets.update(expansions.promo_and_misc)
        Models.AssetCollection.__init__(self,  *args, **kwargs)


class Expansion(Models.GameAsset):
    """ This is the base class for all expansions. Private methods exist for
    enabling and disabling expansions (within a campaign/settlement). """

    def __init__(self, *args, **kwargs):
        Models.GameAsset.__init__(self,  *args, **kwargs)

        self.assets = Assets()
        self.initialize()

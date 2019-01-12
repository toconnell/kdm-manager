#!/usr/bin/python2.7


from datetime import datetime

from api.assets import expansions
from api import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        """ Expansion assets are organized in assets/expansions.py according to
        release date, so when we initialize an asset dict from expansions.py, we
        manually add a "meta" style key to indicate their release date. """

        self.root_module = expansions
        Models.AssetCollection.__init__(self,  *args, **kwargs)


class Expansion(Models.GameAsset):
    """ This is the base class for all expansions. Private methods exist for
    enabling and disabling expansions (within a campaign/settlement). """

    def __init__(self, *args, **kwargs):
        Models.GameAsset.__init__(self,  *args, **kwargs)

        self.assets = Assets()
        self.baseline()
        self.initialize()


    def baseline(self):
        """ Default some attributes for self. Everything here is subject
        to overwrite by the self.initialize() call. """

        self.survivor_special_attributes = []

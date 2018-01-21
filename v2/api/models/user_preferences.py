#!/usr/bin/python2.7

from assets import user_preferences
import Models
import utils
import settings

#
#   in which we treat ther user preferences like game assets
#

class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.root_module = user_preferences
        Models.AssetCollection.__init__(self,  *args, **kwargs)

        for p_key in self.assets.keys():
            default = settings.get('users', p_key)
            self.assets[p_key]['default'] = default


class Preference(Models.GameAsset):
    """ This is the base class for all expansions. Private methods exist for
        enabling and disabling expansions (within a campaign/settlement). """

    def __init__(self, *args, **kwargs):
        Models.GameAsset.__init__(self,  *args, **kwargs)
        self.assets = Assets()
        self.initialize()


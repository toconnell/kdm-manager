#!/usr/bin/python2.7


from assets import epithets
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.root_module = epithets
        Models.AssetCollection.__init__(self,  *args, **kwargs)

        # force all epithet assets to have 'max': 1, i.e. to prevent dupes
        for h in self.get_handles():
            self.assets[h]["max"] = 1

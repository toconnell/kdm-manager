#!/usr/bin/python2.7


from assets import epithets
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):

        self.assets = epithets.core
        self.assets.update(epithets.mar_2016_expansions)

        Models.AssetCollection.__init__(self,  *args, **kwargs)

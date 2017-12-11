#!/usr/bin/python2.7


from assets import cursed_items
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.root_module = cursed_items
        Models.AssetCollection.__init__(self,  *args, **kwargs)

#!/usr/bin/python2.7


from api import Models
from api.assets import cursed_items
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.root_module = cursed_items
        Models.AssetCollection.__init__(self,  *args, **kwargs)

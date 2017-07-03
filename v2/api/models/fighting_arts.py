#!/usr/bin/python2.7

from assets import fighting_arts
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.root_module = fighting_arts
        Models.AssetCollection.__init__(self,  *args, **kwargs)

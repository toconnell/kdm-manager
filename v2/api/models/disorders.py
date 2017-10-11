#!/usr/bin/python2.7

from assets import disorders
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.type = 'disorder'
        self.root_module = disorders
        Models.AssetCollection.__init__(self,  *args, **kwargs)

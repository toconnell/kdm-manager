#!/usr/bin/python2.7

from assets import abilities_and_impairments
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.root_module = abilities_and_impairments
        Models.AssetCollection.__init__(self,  *args, **kwargs)

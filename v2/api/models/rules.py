#!/usr/bin/python2.7

from assets import rules
import Models


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.root_module = rules
        Models.AssetCollection.__init__(self,  *args, **kwargs)


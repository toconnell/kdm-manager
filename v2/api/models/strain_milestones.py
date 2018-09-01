#!/usr/bin/python2.7

from assets import strain_milestones
import Models


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.root_module = strain_milestones
        Models.AssetCollection.__init__(self,  *args, **kwargs)


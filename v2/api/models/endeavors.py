#!/usr/bin/python2.7


from assets import endeavors
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.type = "endeavor"
        self.root_module = endeavors
        Models.AssetCollection.__init__(self,  *args, **kwargs)


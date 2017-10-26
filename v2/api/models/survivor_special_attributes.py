#!/usr/bin/python2.7


from assets import survivor_sheet_options
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.assets = survivor_sheet_options.survivor_special_attributes
        self.type = "special_attribute"
        Models.AssetCollection.__init__(self,  *args, **kwargs)

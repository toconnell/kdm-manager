#!/usr/bin/python2.7


from api.assets import survivor_sheet_options
from api import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.assets = survivor_sheet_options.survivor_special_attributes
        self.type_override = "special_attribute"
        Models.AssetCollection.__init__(self,  *args, **kwargs)

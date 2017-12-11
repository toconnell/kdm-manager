#!/usr/bin/python2.7


from assets import survivor_sheet_options
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.type_override = "weapon_proficiency"
        self.assets = survivor_sheet_options.weapon_proficiency
        Models.AssetCollection.__init__(self,  *args, **kwargs)

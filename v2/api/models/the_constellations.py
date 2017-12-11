#!/usr/bin/python2.7


from assets import survivor_sheet_options
import Models


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.assets = survivor_sheet_options.the_constellations
        self.type_override = "the_constellations"
        Models.AssetCollection.__init__(self,  *args, **kwargs)

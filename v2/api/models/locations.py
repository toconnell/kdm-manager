#!/usr/bin/python2.7


from assets import locations
import Models
import utils


logger = utils.get_logger()

class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):

        # this is pretty clunky. We should revise this before too long.

        self.assets = {}

        self.type="location"

        for l in locations.settlement.keys():
            l_dict = locations.settlement[l]
            l_dict["subtype"] = "settlement_location"
            self.assets[l] = l_dict

        for l in locations.resources.keys():
            l_dict = locations.resources[l]
            l_dict["subtype"] = "resource_location"
            self.assets[l] = l_dict

        for l in locations.gear.keys():
            l_dict = locations.gear[l]
            l_dict["subtype"] = "gear_location"
            self.assets[l] = l_dict


        Models.AssetCollection.__init__(self,  *args, **kwargs)

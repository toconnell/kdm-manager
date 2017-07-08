#!/usr/bin/python2.7

from assets import abilities_and_impairments
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.root_module = abilities_and_impairments
        Models.AssetCollection.__init__(self,  *args, **kwargs)

        self.set_pretty_types()
        self.set_default_max_numbers()


    def set_default_max_numbers(self):
        """ Called during initialization of the AssetCollection, this sets our
        default 'max' values on all A&I asset dictionaries. """

        for d in self.get_dicts():
            asset_max = d.get("max", None)
            asset_handle = d["handle"]
            if asset_max is None:
                self.assets[asset_handle]["max"] = 1
            elif asset_max is False:
                self.assets[asset_handle]["max"] = 666

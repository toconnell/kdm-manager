#!/usr/bin/python2.7


from assets import abilities_and_impairments
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.assets = abilities_and_impairments.weapon_specializations
        self.type = "weapon_specialization"
        Models.AssetCollection.__init__(self,  *args, **kwargs)

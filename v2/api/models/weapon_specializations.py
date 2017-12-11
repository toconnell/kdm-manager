#!/usr/bin/python2.7


from assets import abilities_and_impairments
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.type_override = "weapon_specialization"
        self.assets = abilities_and_impairments.weapon_specializations
        Models.AssetCollection.__init__(self,  *args, **kwargs)

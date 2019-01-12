#!/usr/bin/python2.7


from api.assets import abilities_and_impairments
from api import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.assets = abilities_and_impairments.weapon_mastery
        self.type_override = "weapon_mastery"
        Models.AssetCollection.__init__(self,  *args, **kwargs)

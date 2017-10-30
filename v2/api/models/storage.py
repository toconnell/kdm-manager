#!/usr/bin/python2.7

from assets import storage
from models import gear, resources
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.type="storage_location"
        self.root_module = storage
        Models.AssetCollection.__init__(self,  *args, **kwargs)


class Storage(Models.GameAsset):

    def __init__(self, *args, **kwargs):
        Models.GameAsset.__init__(self,  *args, **kwargs)
        self.assets = Assets()
        self.initialize()


    def get_collection(self):
        """ Creates a dictionary of the gear/resource assets that live in this
        location. """

        if self.sub_type == 'gear':
            A = gear.Assets()
        elif self.sub_type == 'resources':
            A = resources.Assets()
        return A.get_assets_by_sub_type(self.handle)




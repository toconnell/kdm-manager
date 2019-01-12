#!/usr/bin/python2.7

from api.assets import locations
from api import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.root_module = locations
        Models.AssetCollection.__init__(self,  *args, **kwargs)

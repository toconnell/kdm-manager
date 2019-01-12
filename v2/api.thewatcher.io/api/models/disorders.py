#!/usr/bin/python2.7

from api.assets import disorders
from api import Models
import utils

class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.root_module = disorders
        Models.AssetCollection.__init__(self,  *args, **kwargs)


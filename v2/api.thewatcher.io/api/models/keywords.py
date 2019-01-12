#!/usr/bin/python2.7

from api.assets import rules
from api import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.root_module = rules
        Models.AssetCollection.__init__(self,  *args, **kwargs)

        self.filter('sub_type','keyword',True)

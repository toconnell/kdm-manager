#!/usr/bin/python2.7

from api.assets import strain_milestones
from api import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.root_module = strain_milestones
        Models.AssetCollection.__init__(self,  *args, **kwargs)


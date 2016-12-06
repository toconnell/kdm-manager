#!/usr/bin/python2.7


from assets import survival_actions
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.assets = survival_actions.dictionary
        self.type = "survival_action"
        Models.AssetCollection.__init__(self,  *args, **kwargs)

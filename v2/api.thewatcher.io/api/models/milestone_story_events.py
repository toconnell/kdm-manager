#!/usr/bin/python2.7


from api.assets import campaigns
from api import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.type_override = "milestone_story_events"
        self.assets = campaigns._milestone_story_events
        Models.AssetCollection.__init__(self,  *args, **kwargs)

class Milestone(Models.GameAsset):

    def __init__(self, *args, **kwargs):
       Models.GameAsset.__init__(self,  *args, **kwargs)
       self.assets = Assets()
       self.initialize()

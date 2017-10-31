#!/usr/bin/python2.7


from assets import campaigns
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.assets = campaigns.milestone_story_events
        self.type = "milestone_story_events"
        Models.AssetCollection.__init__(self,  *args, **kwargs)

class Milestone(Models.GameAsset):

    def __init__(self, *args, **kwargs):
       Models.GameAsset.__init__(self,  *args, **kwargs)
       self.assets = Assets()
       self.initialize()

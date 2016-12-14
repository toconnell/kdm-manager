#!/usr/bin/python2.7


from assets import events
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.assets = events.story_events
        for a in self.assets.keys():
            self.assets[a]["type"] = "story_event"

        for a in events.settlement_events.keys():
            self.assets[a] = events.settlement_events[a]
            self.assets[a]["type"] = "settlement_event"


        # hunting events?

        Models.AssetCollection.__init__(self,  *args, **kwargs)


#!/usr/bin/python2.7



from assets import campaigns
import Models


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        """ Expansion assets are organized in assets/expansions.py according to
        release date, so when we initialize an asset dict from expansions.py, we
        manually add a "meta" style key to indicate their release date. """

        self.AssetClass = Campaign
        self.assets = campaigns.campaign_definitions
        self.type = "campaign_definition"

        Models.AssetCollection.__init__(self,  *args, **kwargs)


class Campaign(Models.GameAsset):
    """ This is the base class for all expansions. Private methods exist for
    enabling and disabling expansions (within a campaign/settlement). """

    def __init__(self, *args, **kwargs):
        Models.GameAsset.__init__(self,  *args, **kwargs)
        self.assets = Assets()
        self.initialize()

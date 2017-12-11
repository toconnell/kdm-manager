#!/usr/bin/python2.7



from assets import campaigns
import Models


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        """ Expansion assets are organized in assets/expansions.py according to
        release date, so when we initialize an asset dict from expansions.py, we
        manually add a "meta" style key to indicate their release date. """

        self.type_override = "campaign"
        self.root_module = campaigns
        Models.AssetCollection.__init__(self,  *args, **kwargs)


class Campaign(Models.GameAsset):
    """ This is the base class for all expansions. Private methods exist for
    enabling and disabling expansions (within a campaign/settlement). """

    def __init__(self, *args, **kwargs):

        Models.GameAsset.__init__(self,  *args, **kwargs)
        self.assets = Assets()
        self.baseline()
        self.initialize()


    def baseline(self):
        """ Campaign objects have a loose data model that we enforce by
        setting attributes manually.

        Theory being that we want to be able to only have to define SOME
        of these attributes in the actual assets/campaigns.py file and
        not have to write a bunch of exception-catching code in the
        methods/modules that work with these types of objects.

        All of the below is subject to overwrite by self.initialize().
        """

        self.default = False
        self.endeavors = []
        self.saviors = False
        self.survivor_special_attributes = []






#!/usr/bin/python2.7

from assets import gear
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.root_module = gear
        Models.AssetCollection.__init__(self,  *args, **kwargs)

        for a_dict in self.get_dicts():
            for list_attrib in ['keywords','rules']:
                if list_attrib not in a_dict.keys():
                    self.assets[a_dict['handle']][list_attrib] = []
            if 'desc' not in a_dict.keys():
                self.assets[a_dict['handle']]['desc'] = ""


class Gear(Models.GameAsset):

    def __repr__(self):
            return "%s object '%s' (assets.%s['%s'])" % (self.type.title(), self.name, self.type, self.handle)

    def __init__(self, *args, **kwargs):
        Models.GameAsset.__init__(self,  *args, **kwargs)
        self.assets = Assets()
        self.initialize()



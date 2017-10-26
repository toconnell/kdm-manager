#!/usr/bin/python2.7

from assets import resources
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.type = 'resources'
        self.root_module = resources
        Models.AssetCollection.__init__(self,  *args, **kwargs)

        for a_dict in self.get_dicts():
            for list_attrib in ['keywords','rules']:
                if list_attrib not in a_dict.keys():
                    self.assets[a_dict['handle']][list_attrib] = []
            if 'desc' not in a_dict.keys():
                self.assets[a_dict['handle']]['desc'] = ""

    def get_all_keywords(self):
        """ Returns a set of all keywords for all assets. """

        keywords = set()
        for a_dict in self.get_dicts():
            keywords = keywords.union(a_dict['keywords'])
        return sorted(keywords)


class Resource(Models.GameAsset):

    def __init__(self, *args, **kwargs):
        Models.GameAsset.__init__(self,  *args, **kwargs)
        self.assets = Assets()
        self.initialize()

        self.consumable_keywords = ['fish','consumable','flower']

    def is_consumable(self):
        """ Returns a Boolean representing whether the resource is consumable
        or not. """
        for k in self.keywords:
            if k in self.consumable_keywords:
                return True
        return False


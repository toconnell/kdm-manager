#!/usr/bin/python2.7

from assets import fighting_arts
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.root_module = fighting_arts
        Models.AssetCollection.__init__(self,  *args, **kwargs)

        for a in self.assets.keys():
            self.set_selector_text(a)

    def set_selector_text(self, asset_handle):
        """ A UI-friendliness method that creates a special text attribute
        called 'selector_text' that can be used in drop-downs, etc. """

        a_dict = self.get_asset(asset_handle)
        output = a_dict['name']

        parenthetical = []
        if a_dict['sub_type'] == 'secret_fighting_art':
            parenthetical.append('Secret')
        if a_dict.get('expansion', None) is not None:
            parenthetical.append(a_dict['expansion'].replace("_"," ").title())

        if parenthetical != []:
            output += " ("
            output += ", ".join(parenthetical)
            output += ")"

        self.assets[asset_handle]['selector_text'] = output

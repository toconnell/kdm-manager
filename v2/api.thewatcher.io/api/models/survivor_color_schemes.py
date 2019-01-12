#!/usr/bin/python2.7


from api.assets import survivor_sheet_options
from api import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.type_override = "color_schemes"
        self.assets = survivor_sheet_options.survivor_color_schemes
        Models.AssetCollection.__init__(self,  *args, **kwargs)
        self.post_process()

    def post_process(self):
        """ Creates the 'style_string' attribute based on the key/value pairs
        in the 'style' attrib. """

        for asset_dict in self.get_dicts():
            style_string = ""
            for k,v in asset_dict['style'].iteritems():
                style_string += '%s: %s;' % (k, v)
            self.assets[asset_dict['handle']]['style_string'] = style_string

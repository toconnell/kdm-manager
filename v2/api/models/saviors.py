#!/usr/bin/python2.7

from assets import saviors
import Models

class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.root_module = saviors
        Models.AssetCollection.__init__(self,  *args, **kwargs)


    def get_asset_by_color(self, color=None):
        """ This method will return an asset dictionary whose 'color' attrib
        matches the value of the 'color' kwarg.

        Important! You only want to call this method AFTER you filter the
        self.assets dict of the collection down to your campaign's version, like
        so:

            S = saviors.Assets()
            S.filter("version", ["1.3.1"], reverse=True)

        This pretty much guarantees that you'll only get a single result. If you
        would get multiple results, this method will bomb out and log an
        exception. """

        if color is None:
            msg = "get_asset_by_color() requires the 'color' kwarg!"
            self.logger.exception(msg)
            raise Exception(msg)

        output = None
        for d in self.get_dicts():
            if d["color"] == color and output is None:
                output = d
            elif d["color"] == color and output is not None:
                msg = "Multiple savior asset dicts have the color '%s'. Did you rememeber to filter?" % color
                self.logger.exception(msg)
                raise Exception(msg)

        if output is None:
            msg = "No asset dict found for color '%s'!" % color

        return output

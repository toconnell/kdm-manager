#!/usr/bin/python2.7


import random

from assets import names
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):

        # add settlement names
        self.assets = []
        for n in names.settlements:
            self.assets.append({"name": n, "type": "settlement"})

#        Models.AssetCollection.__init__(self,  *args, **kwargs)


    def get_random_settlement_name(self):
        """ Returns a random settlement name. What else would it do? """

        settlement_names = []
        for a in self.assets:
            if a["type"] == "settlement":
                settlement_names.append(a["name"])

        return random.choice(settlement_names)

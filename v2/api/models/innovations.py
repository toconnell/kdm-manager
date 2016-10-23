#!/usr/bin/python2.7


from assets import innovations
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self):

        self.assets = innovations.innovations
        for a in self.assets.keys():
            self.assets[a]["handle"] = a
            if "principle" in self.assets[a].keys():
                self.assets[a]["__type__"] = "principle"
            else:
                self.assets[a]["__type__"] = "innovation"


    def get_principles(self):
        """ Spits out the principles dict from assets/principles.py. """
        return innovations.principles

    def get_mutually_exclusive_principles(self):
        """ Returns a dictionary object listing game asset names for the
        mutually exclusive principle pairs. """

        output = {}
        principles = self.get_principles()
        for p in principles.keys():
            p_dict = principles[p]
            alternatives = set()
            for option in p_dict["option_handles"]:
                alternatives.add(self.get_asset(option)["name"])
            output[p_dict["name"]] = tuple(alternatives)
        return output



class Innovation(Models.GameAsset):
    """ This is the base class for all innovations."""

    def __init__(self, *args, **kwargs):
        Models.GameAsset.__init__(self,  *args, **kwargs)

        self.assets = Assets()
        self.initialize()

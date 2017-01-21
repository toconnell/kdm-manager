#!/usr/bin/python2.7


from assets import innovations
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self):

        self.assets = innovations.innovations
        for a in self.assets.keys():
            if "principle" in self.assets[a].keys():
                self.assets[a]["type"] = "principle"
            else:
                self.assets[a]["type"] = "innovation"


    def get_principles(self):
        """ Spits out the principles dict from assets/principles.py. """
        return innovations.principles

    def get_principle(self, p_handle):
        """ Returns a single principle asset dictionary. """
        return innovations.principles[p_handle]

    def get_principle_from_name(self, p_name):
        """ Use a name to get a principle asset. """

        lookup_dict = {}
        for p_key in innovations.principles.keys():
            p_dict = innovations.principles[p_key]
            lookup_dict[p_dict["name"]] = p_dict

        return lookup_dict[p_name]


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


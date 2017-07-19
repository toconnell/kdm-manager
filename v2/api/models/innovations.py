#!/usr/bin/python2.7


from assets import innovations, abilities_and_impairments
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.assets = innovations.innovations
        for a in self.assets.keys():
            if "principle" in self.assets[a].keys():
                self.assets[a]["type"] = "principle"
            else:
                self.assets[a]["type"] = "innovation"

        for m in abilities_and_impairments.weapon_mastery.keys():
            wm = abilities_and_impairments.weapon_mastery[m]
            wm["handle"] = m
            wm["type"] = "weapon_mastery"
            self.assets[m] = wm

        Models.AssetCollection.__init__(self,  *args, **kwargs)


    def get_principles(self):
        """ Spits out the principles dict from assets/principles.py. """
        return innovations.principles

    def get_principle(self, p_handle):
        """ Returns a single principle asset dictionary. """
        return innovations.principles[p_handle]


    def get_mutually_exclusive_principles(self):
        """ Returns a dictionary object listing game asset names for the
        mutually exclusive principle pairs. """

        output = {}
        principles = self.get_principles()
        for p in principles.keys():
            p_dict = principles[p]
            alternatives = []
            for option in p_dict["option_handles"]:
                alternatives_list = [self.get_asset(option)["name"], self.get_asset(option)["handle"]]
                alternatives.append(alternatives_list)
            output[p_dict["name"]] = tuple(alternatives)
        return output



class Innovation(Models.GameAsset):
    """ This is the base class for all innovations."""

    def __init__(self, *args, **kwargs):
        Models.GameAsset.__init__(self,  *args, **kwargs)

        self.assets = Assets()
        self.initialize()


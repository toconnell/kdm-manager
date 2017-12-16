#!/usr/bin/python2.7


from copy import copy

from assets import innovations, abilities_and_impairments, principles
import endeavors
import Models
import utils


class Assets(Models.AssetCollection):

    def __init__(self, *args, **kwargs):
        self.root_module = innovations
        Models.AssetCollection.__init__(self,  *args, **kwargs)

        # manual addition of weapon masteries
        for m in abilities_and_impairments.weapon_mastery.keys():
            wm = abilities_and_impairments.weapon_mastery[m]
            wm["handle"] = m
            wm["type"] = "weapon_mastery"
            self.assets[m] = wm


    #
    #   convenience/helper stuff for working with principles.py; this should
    #   probably ultimately be moved to a principles model
    #

    def get_principles(self):
        """ Spits out the principles dict from assets/principles.py. """
        return copy(principles.core)

    def get_principle(self, p_handle):
        """ Returns a single principle asset dictionary. """
        return copy(principles.core[p_handle])


    def get_mutually_exclusive_principles(self):
        """ Returns a dictionary object listing game asset names for the
        mutually exclusive principle pairs.

        Looks like this:

            {'New Life': (
                ['Protect the Young', 'protect_the_young'],
                ['Survival of the Fittest', 'survival_of_the_fittest']
            ),
            'Society': (
                ['Accept Darkness', 'accept_darkness'],
                ['Collective Toil', 'collective_toil']
            ),
            'Death': (
                ['Graves', 'graves'],
                ['Cannibalize', 'cannibalize'],
            ),
            'Conviction': (
                ['Romantic', 'romantic'],
                ['Barbaric', 'barbaric'],
            )}
        """

        output = {}
        principles = self.get_principles()
        for p in principles.keys():
            p_dict = principles[p]
            alternatives = []
            for option in p_dict["option_handles"]:
                alternatives_list = [self.get_asset(option)["name"], option]
                alternatives.append(alternatives_list)
            output[p_dict["name"]] = tuple(alternatives)

        return output



class Innovation(Models.GameAsset):
    """ This is the base class for all innovations."""

    def __init__(self, *args, **kwargs):
        Models.GameAsset.__init__(self,  *args, **kwargs)

        self.assets = Assets()
        self.initialize()



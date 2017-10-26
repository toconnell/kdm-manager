#!/usr/bin/python2.7

from copy import copy
import random

from assets import names
import Models
import utils


class Assets(Models.AssetCollection):
    """ This is our odd-ball AssetCollection.

    For starts, its the only AssetCollection that is initialized from lists,
    rather than dicts.

    The major weirdness is how we make list items into dictionaries, which
    involes an odd name-to-handle conversion method and some un-DRY iteration
    for creating dicts out of names.

    On account of that, it sets attribs for all of the assets in its 'assets'
    dict during initialization and, though it supports normal AssetCollection
    methods, it's not recommended to call most of them (given the general non-
    standardness of the 'assets' dict).
    """

    def __init__(self, *args, **kwargs):

        self.assets = {}

        # settlement
        for n in names.settlements:
            self.assets[self.name_to_handle("settlement", n)] = {"name": n, "type": "settlement"}

        # survivors
        for n in names.male:
            self.assets[self.name_to_handle("male", n)] = {"name": n, "type": "male"}
        for n in names.female:
            self.assets[self.name_to_handle("female", n)] = {"name": n, "type": "female"}
        for n in names.neuter:
            self.assets[self.name_to_handle("neuter", n)] = {"name": n, "type": "neuter"}

        Models.AssetCollection.__init__(self,  *args, **kwargs)


    def get_random_names(self, count=100):
        """ Returns 'count' random names for each sex. This is meant primarily
        as a front-end helper, so it returns a JSON-like dict. It also raises
        a big, wordy error if you ask it for too many names. """

        m = copy(names.male)
        f = copy(names.female)

        m.extend(copy(names.neuter))
        f.extend(copy(names.neuter))

        male = set()
        female = set()

        for l in m,f:
            if count > len(l):
                raise utils.InvalidUsage('Cannot return more than %s random names!' % len(l))

        for i in [(male, m), (female, f)]:
            l, s = (i)
            while len(l) < count:
                l.add(random.choice(s))

        return {'M': sorted(list(male)), 'F': sorted(list(female))}


    def name_to_handle(self, prefix, name):
        """ Flattens out 'name' and merges it with 'prefix' to make a sort of
        handle. """

        n = name.replace(" ","").lower()
        return "%s_%s" % (prefix, n)


    #
    #   private/unique get methods
    #

    def get_names_by_type(self, name_type=None):
        """ Returns a list of names whose 'type' attribute matches the value of
        'name_type'. """

        output = []
        for a in self.assets.keys():
            if self.assets[a]['type'] == name_type:
                output.append(self.assets[a]["name"])
        return output


    def get_random_settlement_name(self):
        """ Returns a random settlement name. What else would it do? """

        settlement_names = self.get_names_by_type('settlement')
        return random.choice(settlement_names)


    def get_random_survivor_name(self, sex="male", include_neuter=True):
        """ Returns a random survivor name. Use the 'include_neuter' bool to
        include/exclude neuter names. """

        if sex.lower() == 'm':
            sex = 'male'
        elif sex.lower() == 'f':
            sex = 'female'
        else:
            raise Exception("Unhandled sex!")

        survivor_names = self.get_names_by_type(sex)
        if include_neuter:
            survivor_names.extend(self.get_names_by_type('neuter'))
        return random.choice(survivor_names)


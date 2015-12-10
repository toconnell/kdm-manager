#!/usr/bin/env python

import game_assets
from utils import get_logger

class Model:
    """ This is the base class for all model classes. It provides the basic
    methods that all model objects (e.g. Innovations, Resources, etc.) have to
    support."""

    def __init__(self):
        self.logger = get_logger()

    def get_asset(self, game_asset_key):
        return self.game_assets[game_asset_key]

    def get_keys(self):
        return self.game_assets.keys()

    def render_as_html_dropdown(self, submit_on_change=True, exclude=[], disable=[]):
        """ Renders the model as an HTML dropdown and returns a string. Use the
        'submit_on_change' kwarg to control whether it submits on change.

        Use the 'exclude' kwarg to prevent certain keys from showing up in the
        resuting render.

        Use 'disabled' to provide a list of options that, if present, will be
        greyed out/disabled in the resulting pick-list.
        """

        self.pretty_name = self.name.replace("_", " ").title()

        options = self.get_keys()

        for excluded_key in exclude:
            if excluded_key in options:
                options.remove(excluded_key)

        if options == []:
            # stop here if we've got no options to return
            return "<!-- no available options for '%s' -->\n" % self.name
        else:
            options = sorted(options)

        if submit_on_change:
            submit_on_change = "this.form.submit()"

        output = '\n\t<select name="add_%s" onchange="%s">' % (self.name, submit_on_change)
        output += '\t<option selected disabled hidden value=''>Add %s</option>' % self.pretty_name
        for o in sorted(options):
            disabled = ""
            if o in disable:
                disabled = "disabled"
            output += '\t\t<option %s>%s</option>\n' % (disabled, o)
        output += '</select>\n'


        return output


#
#   Define and initialize all models below here ONLY!
#   All of these have to have a self.game_assets dictionary that includes all of
#       of the game assets associated with the model class.
#
#   self.name, by the bye, should be the singular appelation used in forms to
#       add/remove the game asset from one of our application assets, e.g. 
#       add_item/remove_item, add_disorder/remove_disorder, etc.
#

class abilitiesModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.game_assets = game_assets.abilities_and_impairments
        self.name = "ability"

    def get_maxed_out_abilities(self, survivor_abilities):
        """ Pass this a survivor["abilities_and_impairments"] list and it will
        return a list of ability/impairment keys for which the survivor is
        ineligible. """
        maxed_out = set()
        for ability_key in self.game_assets.keys():
            ability_dict = self.get_asset(ability_key)
            if "max" in ability_dict and ability_key in survivor_abilities:
                survivor_total = survivor_abilities.count(ability_key)
                if survivor_total == ability_dict["max"]:
                    maxed_out.add(ability_key)
        return sorted(list(maxed_out))

class disordersModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.game_assets = game_assets.disorders
        self.name = "disorder"

class epithetsModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.game_assets = game_assets.epithets
        self.name = "epithet"

class fightingArtsModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.game_assets = game_assets.fighting_arts
        self.name = "fighting_art"

class locationsModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.game_assets = game_assets.locations
        self.name = "location"

class itemsModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.game_assets = game_assets.items
        self.name = "item"

    def render_as_html_dropdown_with_divisions(self, recently_added=[]):

        locations = set()
        for item_key in self.get_keys():
            locations.add(self.get_asset(item_key)["location"])

        location_dict = {}
        for location in locations:
            location_dict[location] = set()

        for item_key in self.get_keys():
            item = self.get_asset(item_key)
            location_dict[item["location"]].add(item_key)

        locations = sorted(list(locations))
        output = '\n<select name="add_item" onchange="this.form.submit()">\n'
        output += '<option selected disabled hidden value=''>Add Item</option>\n'
        if recently_added != []:
            output += ' <option disabled> &ensp; &ensp; --- Recently Added ---  </option>\n'
            for item in recently_added:
                output += '  <option value="%s">%s</option>\n' % (item, item)
        for location_key in locations:
            output += ' <option disabled> &ensp; &ensp; --- %s ---  </option>\n' % location_key
            for item in sorted(location_dict[location_key]):
                output += '  <option value="%s">%s</option>\n' % (item, item)
        output += '</select>\n'

        return output

class innovationsModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.game_assets = game_assets.innovations
        self.name = "innovation"

    def get_always_available_innovations(self):
        always_available = set()
        for innovation in self.get_keys():
            if "always_available" in self.get_asset(innovation).keys():
                always_available.add(innovation)
        return always_available

class quarriesModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.game_assets = game_assets.quarries
        self.name = "quarry"

class resourcesModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.game_assets = game_assets.resources

class resourceDecksModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.game_assets = game_assets.resource_decks


# initialize all of our classes above when this module is imported
Abilities       = abilitiesModel()
Disorders       = disordersModel()
Epithets        = epithetsModel()
FightingArts    = fightingArtsModel()
Locations       = locationsModel()
Items           = itemsModel()
Innovations     = innovationsModel()
Quarries        = quarriesModel()
Resources       = resourcesModel()
ResourceDecks   = resourceDecksModel()





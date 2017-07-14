#!/usr/bin/env python

from copy import copy
import game_assets
from utils import get_logger
from string import capwords, Template
import json

def game_asset_to_json(asset_key, asset_model):
    d = {'name': asset_key}
    a_dict = asset_model.get_asset(asset_key)
    for k,v in a_dict.iteritems():
        d[k] = v
    return d


class Model:
    """ This is the base class for all model classes. It provides the basic
    methods that all model objects (e.g. Innovations, Resources, etc.) have to
    support."""

    def __init__(self):
        self.logger = get_logger()

    def load_settlement(self, settlement_object=None):
        """ NB: any object that subclsases this has to have its own, private
        initialize_API_assets() method, or else this will explode in your face.
        """

        self.Settlement = settlement_object
        if hasattr(self.Settlement, "api_asset"):
            self.initialize_API_assets()

    def get_asset(self, game_asset_key):
        return self.game_assets[game_asset_key]

    def get_keys(self, exclude_if_attrib_exists=None, Settlement=None):
        keys = []
        for asset_key in self.game_assets.keys():
            if not exclude_if_attrib_exists in self.game_assets[asset_key]:
                keys.append(asset_key)
        if Settlement is not None:
            for asset_key in keys:
                asset_dict = self.get_asset(asset_key)
                if "expansion" in asset_dict.keys() and asset_dict["expansion"] not in Settlement.get_expansions("list_of_names"):
                    keys.remove(asset_key)
        return keys

    def get_pretty_name(self):
        self.pretty_name = self.name.replace("_", " ").title()
        if self.name == "ability":
            self.pretty_name = "Ability or Impairment"
        return self.pretty_name


    def get_forbidden(self, settlement_object=None):
        """ Checks all assets for whether they are forbidden by settlement
        attributes, i.e. whether they're on a 'forbidden' list. """

        forbidden = set()
        for game_asset in self.get_keys():
            c_dict = settlement_object.get_campaign("dict")
            if game_asset in settlement_object.get_campaign("forbidden"):
                forbidden.add(game_asset)

        return forbidden


    def get_always_available(self, settlement_object=None):
        """ Checks all assets in the model against the settlement attributes and
        their own attributes to see if they're on an 'always_available' list
        or whether they have the 'always_available' attrib. Returns a list of
        ones that do. """

        campaign = settlement_object.get_campaign()
        expansions = settlement_object.get_expansions("list_of_names")

        always_available = set()
        for game_asset in self.get_keys():

            # first check the campaign
            c_dict = settlement_object.get_campaign("dict")
            if "always_available" in c_dict and game_asset in c_dict["always_available"]:
                always_available.add(game_asset)

            # then check the expansions
            for e in expansions:
                e_dict = game_assets.expansions[e]
                if "always_available" in e_dict.keys() and game_asset in e_dict["always_available"]:
                    always_available.add(game_asset)

            # finally, check the asset itself
            asset_dict = self.get_asset(game_asset)
            if "always_available" in asset_dict.keys():
                always_available.add(game_asset)

        # normatively speaking, forbidden trumps always_available (someone's got
        #   to have precedence, you know?)
        forbidden = settlement_object.get_campaign("forbidden")
        always_available = list(always_available)
        for game_asset in always_available:
            if game_asset in forbidden:
                always_available.remove(game_asset)
        always_available = set(always_available)

        return always_available


    def render_as_html_toggle_dropdown(self, selected=None, submit_on_change=True, expansions=[]):
        """ Creates a single dropdown for the model where 'None' is selected by
        by default, but the user can toggle to something else from the list of
        asset keys. """

        self.get_pretty_name()
        options = self.get_keys()

        for o in options:
            if "expansion" in self.get_asset(o) and self.get_asset(o)["expansion"] not in expansions:
                options.remove(o)


        soc = ""
        if submit_on_change:
            soc = "this.form.submit()"

        if selected is None:
            selected = "-"
        elif selected == "":
            selected = "-"

        output = '\n\t<select name="add_%s" onchange="%s" class="min_width">' % (self.name, soc)
        options.append("-")
        for o in sorted(options):
            s = ""
            if o == selected:
                s = "selected"
            output += '\t\t<option %s>%s</option>\n' % (s, o)
        output += '</select>\n'

        return output


    def render_as_html_dropdown(self, submit_on_change=True, exclude=[], disable=[], excluded_type=None, Settlement=None, survivor_id=None, select_type="string"):
        """ Renders the model as an HTML dropdown and returns a string. Use the
        'submit_on_change' kwarg to control whether it submits on change.

        Use the 'exclude' kwarg to prevent certain keys from showing up in the
        resuting render.

        Use the 'include' kwarg to force the option list to only show certain
        options in the render.

        Use 'disabled' to provide a list of options that, if present, will be
        greyed out/disabled in the resulting pick-list.

        The 'include_principles' kwarg is a hack that forces innovation lists to
        be returned without principle-type innovations.
        """

        self.get_pretty_name()
        options = self.get_keys()

        for excluded_key in exclude:
            if excluded_key in options:
                options.remove(excluded_key)

        # exclude if the asset wants to be excluded
        for self_ex_asset in self.get_keys():
            if "exclude_from_picker" in self.get_asset(self_ex_asset) and self_ex_asset in options:
                options.remove(self_ex_asset)

        # exclude by type
        if excluded_type is not None:
            excluded_assets = []
            for asset in self.get_keys():
                if "type" in self.get_asset(asset).keys() and self.get_asset(asset)["type"] == excluded_type:
                    excluded_assets.append(asset)
            for excluded_key in excluded_assets:
                options.remove(excluded_key)

        # exclude by expansion and campaign rules if we've got a Settlement obj
        excluded_assets = []
        if Settlement is not None:
            for asset in options:
                if "expansion" in self.get_asset(asset).keys() and self.get_asset(asset)["expansion"] not in Settlement.get_expansions("list_of_names"):
                    excluded_assets.append(asset)
                if asset in Settlement.get_campaign("forbidden"):
                    excluded_assets.append(asset)
        for excluded_key in excluded_assets:
            options.remove(excluded_key)

        if options == []:
            # stop here if we've got no options to return
            return "<!-- no available options for '%s' -->\n" % self.name
        else:
            options = sorted(options)


        if select_type=="angularjs":
            options_list = []
            for o in options:
                options_list.append(game_asset_to_json(o, self))

            html_stub = Template("""\n
            <select
                name = "add_$asset_name"
                ng-change="addItem('$survivor_id')"
                ng-options="option as option.name for option in $options_json"
                ng-model="addMe"
            >
            <option value="" disabled hidden selected ng-if="!selectedObject">Add $pretty_name</option>
            </select>
            \n""")

            output = html_stub.safe_substitute(
                pretty_name = self.pretty_name,
                asset_name = self.name,
                options_json=options_list,
                survivor_id=survivor_id,
            )
            output +="\n\n"
        else:
            if submit_on_change:
                submit_on_change = "this.form.submit(); showFullPageLoader();"

            output = """\n\t<select name="add_%s" onchange="%s" ng-model="addMe" ng-change="addItem('%s')">""" % (self.name, submit_on_change, survivor_id)
            output += '\t<option selected disabled hidden value=''>Add %s</option>' % self.pretty_name

            if self.name in ["disorder","fighting_art"]:
                output += '\t\t<option value="RANDOM_%s">* Random %s</option>' % (self.name.upper(), self.pretty_name)
                output += ' <option disabled> &ensp; &ensp; ---  </option>'

            for o in sorted(options):
                disabled = ""
                if o in disable:
                    disabled = "disabled"
                pretty_o = o
                if self.name == "ability":
                    option_classes = {}
                    a = Abilities.get_asset(o)
                    pretty_o = "%s (%s)" % (o, capwords(a["type"].replace("_"," ")))

                output += '\t\t<option value="%s" %s>%s</option>\n' % (o, disabled, pretty_o)
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


class disordersModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.game_assets = game_assets.disorders
        self.name = "disorder"

    def build_asset_deck(self, Settlement):
        expansions = Settlement.get_expansions("list_of_names")
        deck = []
        for disorder in game_assets.disorders.keys():
            d_dict = self.get_asset(disorder)
            if not "expansion" in d_dict.keys():
                deck.append(disorder)
            elif "expansion" in d_dict.keys():
                if d_dict["expansion"] in expansions:
                    deck.append(disorder)

        # remove forbidden assets
        forbidden = Settlement.get_campaign("forbidden")
        for d_key in deck:
            if d_key in forbidden:
                deck.remove(d_key)

        return sorted(deck)


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

    def build_survivor_deck(self, Survivor=None, Settlement=None):
        """ Builds a survivor's personal fighting arts deck. """

        fa_deck = self.get_keys(exclude_if_attrib_exists="secret")

		# remove survivor's current arts from the deck
        for fa in Survivor.survivor["fighting_arts"]:
            if fa in fa_deck:
                fa_deck.remove(fa)

		# remove non-enabled expansion content from the deck
        for fa in sorted(fa_deck):
            if "expansion" in self.get_asset(fa):
                if self.get_asset(fa)["expansion"] not in Settlement.get_expansions("list_of_names"):
                    fa_deck.remove(fa)

		# add always_available/remove forbidden items to the deck
        fa_deck.extend(self.get_always_available(Settlement))
        for forbidden_asset in self.get_forbidden(Settlement):
            fa_deck.remove(forbidden_asset)

        # uniquify and sort
        fa_deck = sorted(list(set(fa_deck)))

        # return
#        self.logger.debug("[%s] fighting arts deck: %s" % (Survivor, fa_deck))
        return fa_deck

class locationsModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.game_assets = game_assets.locations
        self.sort_alpha = True
        self.uniquify = True
        self.name = "location"

class itemsModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.game_assets = game_assets.items
        self.name = "item"

    def render_as_html_multiple_dropdowns(self, recently_added=[], expansions=[]):
        """ New storage UI. """

        output = ""

        def render_location(output, pretty_location_name=None, item_list=[]):
            """ Helper function for programmatically generating item drop-down
            lists. This should be refactored to be buttons one day. """

            output += '\n<select name="add_item" onchange="this.form.submit()">\n'
            output += ' <option disabled selected> %s </option>\n' % pretty_location_name
            for item in item_list:
                output += '  <option value="%s">%s</option>\n' % (item, item)
            output += '\n</select><br><hr class="invisible">'
            return output

        # start creating output
        if recently_added != []:
            output = render_location(output, pretty_location_name="Recently Added", item_list=recently_added)

        # get locations based on location attributes of items
        locations = set()
        for item_key in self.get_keys():
            item_asset = self.get_asset(item_key)
            if "expansion" in item_asset.keys() and item_asset["expansion"] not in expansions:
                pass
            else:
                locations.add(item_asset["location"])

        location_dict = {}
        for location in locations:
            location_dict[location] = set()

        for item_key in self.get_keys():
            item = self.get_asset(item_key)
            if "expansion" in item.keys() and item["expansion"] not in expansions:
                pass
            else:
                location_dict[item["location"]].add(item_key)

        # finally, use the location list to start creating html
        locations = sorted(list(locations))
        for location_key in locations:
            if location_key in Locations.get_keys():
                loc_asset = Locations.get_asset(location_key)
                if "expansion" in loc_asset and loc_asset["expansion"] not in expansions:
                    pass
                else:
                    output = render_location(output, pretty_location_name=location_key, item_list=sorted(location_dict[location_key]))
            else:
                output = render_location(output, pretty_location_name=location_key, item_list=sorted(location_dict[location_key]))

        return output



    def render_as_html_dropdown_with_divisions(self, recently_added=[]):
        """ Old storage UI. Deprecated. """

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
        self.sort_alpha = True
        self.uniquify = True
        self.name = "innovation"



class resourcesModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.game_assets = game_assets.resources

class resourcesModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.game_assets = game_assets.resources

class weaponProficienciesModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.game_assets = game_assets.weapon_proficiencies
        self.name = "weapon_proficiency_type"


class weaponMasteriesModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.game_assets = {}
        for weapon in game_assets.weapon_proficiencies:
            self.game_assets["Mastery - %s" % weapon] = {
                "type": "weapon proficiency",
                "all_survivors": "Specialization - %s" % weapon,
                "settlement_buff": "All survivors gain <i>Specialization - %s</i>." % weapon,
            }
        self.name = "weapon_mastery_type"




# initialize all of our classes above when this module is imported
Disorders       = disordersModel()
Epithets        = epithetsModel()
FightingArts    = fightingArtsModel()
Locations       = locationsModel()
Items           = itemsModel()
Innovations     = innovationsModel()
Resources       = resourcesModel()
WeaponMasteries = weaponMasteriesModel()
WeaponProficiencies = weaponProficienciesModel()

#
#   mutually exclusive principles
#

mutually_exclusive_principles = {
    "Death": ("Graves", "Cannibalize"),
    "New Life": ("Protect the Young", "Survival of the Fittest"),
    "Society": ("Collective Toil", "Accept Darkness"),
    "Conviction": ("Romantic", "Barbaric"),
    }



#
#   The User Preferences Model
#

preferences_dict = {
    "preserve_sessions": {
        "desc": "Preserve Sessions?",
        "affirmative": "Keep me logged in",
        "negative": "Remove sessions after 24 hours",
    },
    "random_names_for_unnamed_assets": {
        "desc": "Choose random names for Settlements/Survivors without names?",
        "affirmative": "Choose randomly",
        "negative": "Use 'Unknown' and 'Anonymous'",
    },
    "apply_new_survivor_buffs": {
        "type": "Automation",
        "desc": "Automatically apply settlement bonuses to new, newborn and current survivors where appropriate?",
        "affirmative": "Automatically apply",
        "negative": "Do not apply",
    },
    "apply_weapon_specialization": {
        "type": "Automation",
        "desc": "Automatically add weapon specializations if Innovations include the mastery?",
        "affirmative": "Add",
        "negative": "Do Not Add",
    },
    "show_endeavor_token_controls": {
        "type": "Campaign Summary",
        "desc": "Show Endeavor Token controls on Campaign Summary view?",
        "affirmative": "Show controls",
        "negative": "Hide controls",
    },
    "update_timeline": {
        "type": "Automation",
        "desc": "Automatically Update Timeline with Milestone Story Events?",
        "affirmative": "Update settlement timelines when milestone conditions are met",
        "negative": "Do not automatically update settlement timelines",
    },
    "show_epithet_controls": {
        "type": "Survivor Sheet",
        "desc": "Use survivor epithets?",
        "affirmative": "Show controls on Survivor Sheets",
        "negative": "Hide controls and survivor epithets on Survivor Sheets",
    },
    "show_remove_button": {
        "desc": "Show controls for removing Settlements and Survivors?",
        "affirmative": "Show controls on Settlement and Survivor Sheets",
        "negative": "Hide controls on Settlement and Survivor Sheets",
    },
    "confirm_on_remove_from_storage": {
        "type": "Settlement Sheet",
        "desc": "Confirm before removing items from Settlement Storage?",
        "affirmative": "Confirm with Pop-up",
        "negative": "Do not confirm",
    },
}

class userPreferences(Model):
    def __init__(self):
        Model.__init__(self)
        self.preferences_dict = preferences_dict
        self.game_assets = preferences_dict
    def get_keys(self):
        return self.preferences_dict.keys()
    def pref(self, user_object, pref_key):
        pref_dict = self.preferences_dict[pref_key]
        if user_object.get_preference(pref_key):
            pref_dict["affirmative_selected"] = "checked"
            pref_dict["negative_selected"] = ""
        else:
            pref_dict["affirmative_selected"] = ""
            pref_dict["negative_selected"] = "checked"
        return pref_dict
    def get_categories(self):
        """ Creates a list of available/extant headings for category. """
        categories = set(["General"])
        for k in self.get_keys():
            asset_dict = self.get_asset(k)
            if "type" in asset_dict.keys():
                categories.add(asset_dict["type"])
        return sorted(list(categories))
    def get_category_dict(self):
        """ Uses self.get_categories() to create a dict where each key is a
        category and the value is a list of preference keys. """
        d = {}
        categories = self.get_categories()
        for c in categories:
            d[c] = []
        for a in self.get_keys():
            asset_dict = self.get_asset(a)
            if "type" in asset_dict:
                d[asset_dict["type"]].append(a)
            else:
                d["General"].append(a)

        return d


Preferences = userPreferences()

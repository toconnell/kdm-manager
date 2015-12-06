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

    def render_as_html_dropdown(self, submit_on_change=True, exclude=[]):
        """ Renders the model as an HTML dropdown and returns a string. Use the
        'submit_on_change' kwarg to control whether it submits on change.

        Use the 'exclude' kwarg to prevent certain keys from showing up in the
        resuting render.
        """

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
        output += '\t<option selected disabled hidden value=''>Add %s</option>' % self.name.capitalize()
        for o in sorted(options):
            output += '\t\t<option>%s</option>\n' % o
        output += '</select>\n'


        return output


#
#   Define and initialize all models below here ONLY!
#   All of these have to have a self.game_assets dictionary that includes all of
#       of the game assets associated with the model class.
#

class abilitiesModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.game_assets = game_assets.abilities_and_impairments
        self.name = "ability"

class epithetsModel(Model):
    def __init__(self):
        Model.__init__(self)
        self.game_assets = game_assets.epithets
        self.name = "epithet"

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

    def render_as_html_dropdown_with_divisions(self):

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
Epithets        = epithetsModel()
Locations       = locationsModel()
Items           = itemsModel()
Innovations     = innovationsModel()
Quarries        = quarriesModel()
Resources       = resourcesModel()
ResourceDecks   = resourceDecksModel()



fighting_arts = {
    "Red Fist": {
        "secret": True,
        "desc": "At the start of each showdown, each survivor gains +1 strength token. Survivors may spend +1 strength tokens in place of survival.",
    },
    "King of a Thousand Battles": {
        "secret": True,
        "desc": "Gain +2 accuracy, +2 strength, +2 evasion. You may dodge any number of times in a rount. Only 1 survivor may have this Secret Fighting Art.",
    },
    "King's Step": {
        "secret": True,
        "desc": "Whenever you attack, you may discard any number of Battle Pressure hit locations drawn and draw an equal number of new hit locations. Whenever you attack, after drawing hit locations, but before rolling to wound, you may choose one hit location drawn and disacrd it to draw a new hit location. Traps will cancel these effects.",
    },
    "Legendary Lungs": {
        "secret": True,
        "desc": "Once per attack, for each successful hit, make an additional attack roll.",
    },
    "Zero Presence": {
        "secret": True,
        "desc": "Gain +1 strength when attacking a monster from its blind spot. Whenever you attack a monster, you are always considered to be in its blind spot.",
    },
    "Swordsman's Promise": {
        "secret": True,
        "desc": "At the start of each showdown, gain survival up to your settlement's survival limit if you have a sword in your gear grid.",
    },
    "Orator of Death": {
        "desc": "Once per showdown, you may spend Activation to have all non-deaf survivors gain +2 insanity. When you die, you encourage all survivors with your last words.",
    },
    "Leader": {
        "desc": "Whenever you encourage a survivor they gain +1 speed token until the end of the round.",
    },
    "Combo Master": {
        "desc": "On a perfect hit, make 1 additional attack roll.",
    },
    "Double Dash": {
        "desc": "During your act, once per round, you may spend Activation to gain Movement.",
    },
    "Timeless Eye": {
        "desc": "Your attack roll is a perfect hit on a result of a 9 or 10. You cannot use Timeless Eye if you have the blind severe head injury.",
    },
    "Mighty Strike": {
        "desc": "On a Perfect hit, gain +2 strength until the end of the attack.",
    },
    "Berserker": {
        "desc": "Once per showdown, you may spend Activation to suffer bash and the frenzy brain trauma.",
    },
    "Thrill Seeker": {
        "desc": "Whenever you gain survival during the showdown phase, gain 1 additional survival.",
    },
    "Tough": {
        "desc": "When rolling on a severe injury table, unless you roll a 1, add +1 to the result. (This does not include brain trauma. The result total cannot exceed 10.)",
    },
    "Rhythm Chaser": {
        "desc": "Gain +1 evasion token the first time you criticall wound during a showdown. Rhythm Chaser cannot be used if there are any shields or heavy gear in your grid.",
    },
    "Last Man Standing": {
        "desc": "While you are the only survivor on the showdown board, you may not gain bleeding tokens or be knocked down.",
    },
    "Crossarm Block": {
        "desc": "Whenever you are hit, after hit locations are rolled, you may change 1 result to the arms hit location.",
    },
    "Clutch Fighter": {
        "desc": "Whil you have 3 or more blood tokens, gain +1 strength and +1 accuracy.",
    },
    "Crazed": {
        "desc": "On a Perfect hit, gain +1 insanity.",
    },
    "Unconscious Fighter": {
        "desc": "It takes 7 bleeding tokens to kill you.",
    },
    "Ambidexterous": {
        "desc": "All melee weapons in your gear grid gain paired (add the speed of the second weapon when attacking with the first). Ambidexterous cannot be used if there are any shields, two-handed or heavy gear in your gear grid.",
    },
    "Strategist": {
        "desc": "During the showdown setup, after placing terrain, you may add a Giant Stone Face or a Toppled Pillar terrain card to the showdown board.",
    },
    "Monster Claw Style": {
        "desc": "Your Fist & Tooth attacks gain +1 accuracy, +1 strength and savage (after the first critical wound in an attack, savage weapons cause 1 additional wound. This rule does not trigger on Impervious hit locations).",
    },
    "Tumble": {
        "desc": "When something would collide with you, roll 1d10. On a result of 6+, you successfully tumble out of harm's way. Instead, please your survivor standing on the closest free space outside of the collision path.",
    },
    "Extra Sense": {
        "desc": "You may dodge 1 additional time per round.",
    },
}



disorders = {
    "Fear of the Dark": {
        "survivor_effect": "You retire.",
    },
    "Hoarder": {
        "survivor_effect": "Whenever you are a returning survivor, archive 1 resource gained from the last showdown and gain +1 courage.",
    },
    "Binge Eating Disorder": {
        "survivor_effect": "You cannot depart unless you have consumable gear in your gear grid. You must consume if a choice to consume arises.",
    },
    "Squeamish": {
        "survivor_effect": "You cannot depart with any stinky gear in your gear grid. If a status or effect would cause you to become stinky, lose all your survival.",
    },
    "Secretive": {
        "survivor_effect": "When you are a returning survivor, you quickly become preoccuiped with your own affairs. You must skip the next hunt to deal with them.",
        "skip_next_hunt": True,
    },
    "Seizures": {
        "survivor_effect": "During the showdown, whenever you suffer damage to your head location, you are knocked down.",
    },
    "Immortal": {
        "survivor_effect": "While you are insane, convert all damage dealt to your hit locations to brain damage. You are so busy reveling in your own glory that you cannot spend survival while insane.",
    },
    "Corprolalia": {
        "survivor_effect": "All your gear is noisy. You are always a threat unless you are knocked down, even if an effect says otherwise.",
    },
    "Prey": {
        "survivor_effect": "You may not spend survival unless you are insane.",
    },
    "Honorable": {
        "survivor_effect": "You cannot attack a monster from its blind spot or if it is knocked down.",
    },
    "Apathetic": {
        "survivor_effect": "You cannot use or gain survival. You cannot gain courage. Cure this disorder if you have 8+ understanding.",
    },
    "Weak Spot": {
        "survivor_effect": "When you gain this disorder, roll a random hit location and record it. You cannot depart unless you have armor at this hit location.",
    },
    "Hyperactive": {
        "survivor_effect": "During the showdown, you must move at least 1 space every round.",
    },
    "Aichmophobia": {
        "survivor_effect": "You cannot activate or depart with axes, swords, spears, daggers, scythes, or katars in your gear grid.",
    },
    "Hemophobia": {
        "survivor_effect": "During the showdown, whenever a survivor (including you) gains a bleeding token, you are knocked down.",
    },
    "Vestiphobia": {
        "survivor_effect": "You cannot wear armor at the body location. If you are wearing armor at the body location when you gain this disorder, archive it as you tear it off your person!",
    },
    "Traumatized": {
        "survivor_effect": "Whenever you end your act adjacent to a monster, you are knocked down.",
    },
    "Monster Panic": {
        "survivor_effect": "Whenever you suffer brain damage from an Intimidate action, suffer 1 additional brain damage.",
    },
    "Post-Traumatic Stress": {
        "survivor_effect": "Next settlement phase, you do not contribute or participate in any endeavors. Skip the next hunt to recover.",
        "skip_next_hunt": True,
    },
    "Rageholic": {
        "survivor_effect": "Whenever you suffer a severe injury, also suffer the frenzy brain trauma.",
    },
    "Indecision": {
        "survivor_effect": "If you are the event revealer of hunt events that call on you to make a roll, roll twice and use the lower result.",
    },
    "Anxiety": {
        "survivor_effect": "At the start of each showdown, gain the priority target token unless you have stinky gear in your gear grid.",
    },
    "Quixotic": {
        "survivor_effect": "If you are insane when you depart, gain +1 survival and +1 strength token.",
    },
}


#
#   Notes about render methods:
#       - they should never create a new form
#       - they should all work the same
#       - there should be a way to initialize a model class and render it as a
#           method of that class
#

def render_fighting_arts_dict(return_as=False, exclude=[]):
    """ Represents models.disorders. """

    fa_keys = sorted(fighting_arts.keys())

    for fa_key in exclude:
        fa_keys.remove(fa_key)

    if return_as == "html_select_add":
        html = '<select name="add_fighting_art" onchange="this.form.submit()">'
        html += '<option selected disabled hidden value="">Add Fighting Art</option>'
        for fa in fa_keys:
            html += '<option>%s</option>' % fa
        html += '</select>'
        return html

    return fa_keys

def render_epithet_DEPRECATED(return_as=False, exclude=[]):
    epithet_keys = sorted(epithets.keys())
    for epithet_key in exclude:
        try:
            epithet_keys.remove(epithet_key)
        except:
            pass
    if return_as == "html_select_add":
        html = '<select name="add_epithet" onchange="this.form.submit()">'
        html += '<option selected disabled hidden value="">Add Epithet</option>'
        for epithet in epithet_keys:
            html += '<option>%s</option>' % epithet
        html += '</select>'
        return html
    return epithet_keys

def render_disorder_dict(return_as=False, exclude=[]):
    """ Represents models.disorders. """

    disorder_keys = sorted(disorders.keys())

    for disorder_key in exclude:
        disorder_keys.remove(disorder_key)

    if return_as == "html_select_add":
        html = '<select name="add_disorder" onchange="this.form.submit()">'
        html += '<option selected disabled hidden value="">Add Disorder</option>'
        for disorder in disorder_keys:
            html += '<option>%s</option>' % disorder
        html += '</select>'
        return html

    return disorder_keys




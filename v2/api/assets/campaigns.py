#!/usr/bin/python2.7

#
#   Some comments on organization/architecture:
#   
#       - campaigns are really just a stack of assets, e.g. timeline, special
#       rules, always-available (or banned) innovations, milestones, principles,
#       etc.
#       - accordingly, we collect all campaign-related assets here, so any game
#       asset (formerly stored in the V1 game_assets.py file that is NOT stored
#       in its own, isolated assets file lives here.
#       - check the model methods when working with campaign assets, becase the
#       assets that load by default are fairly minimal and, if you need to work
#       with things like milestones and principles, you'll need to use special
#       methods to initialize those asset definitions, etc.
#       - similarly (but contrastively), initializing a campaign gets you a lot
#       of unusual, private methods for working with settlement and survivor
#       objects when those objectes are subject to a campaign.
#


# this is the generic, "People of the Lantern" timeline. individual campaign
#   dict items (defined in this module) may/may not supply their own timeline
default_timeline = [
    {"year": 0, "settlement_event": ["First Day"]},
    {"year": 1, "story_event": ["Returning Survivors"]},
    {"year": 2, "story_event": ["Endless Screams"]},
    {"year": 3, },
    {"year": 4, "nemesis_encounter": ["Nemesis Encounter: Butcher"]},
    {"year": 5, "story_event": ["Hands of Heat"]},
    {"year": 6, "story_event": ["Armored Strangers"]},
    {"year": 7, "story_event": ["Phoenix Feather"]},
    {"year": 8, },
    {"year": 9, "nemesis_encounter": ["Nemesis Encounter: King's Man"]},
    {"year": 10, },
    {"year": 11, "story_event": ["Regal Visit"]},
    {"year": 12, "story_event": ["Principle: Conviction"]},
    {"year": 13, }, {"year": 14, }, {"year": 15, },
    {"year": 16, "nemesis_encounter": ["Nemesis Encounter"]},
    {"year": 17, }, {"year": 18, },
    {"year": 19, "nemesis_encounter": ["Nemesis Encounter"]},
    {"year": 20, "story_event": ["Watched"], },
    {"year": 21, }, {"year": 22, },
    {"year": 23, "nemesis_encounter": ["Nemesis Encounter: Level 3"]},
    {"year": 24, }, {"year": 25, },
    {"year": 26, "nemesis_encounter": ["Nemesis Encounter: Watcher"]},
    {"year": 27, }, {"year": 28, }, {"year": 29, }, {"year": 30, }, {"year": 31, },
    {"year": 32, }, {"year": 33, }, {"year": 34, }, {"year": 35, }, {"year": 36, },
    {"year": 37, }, {"year": 38, }, {"year": 39, }, {"year": 40, },
]


# this is a collection of milestones that might or might not be used in a given
#   campaign. Campaign assets don't default for this stuff, so you've got to
#   reference all required milestones when defining the asset below
milestones = {
    "first_child": {
        "sort_order": 0,
        "story_event": "Principle: New Life",
    },
    "first_death": {
        "sort_order": 1,
        "story_event": "Principle: Death",
        "add_to_timeline": 'int(self.settlement["death_count"]) >= 1',
    },
    "pop_15": {
        "sort_order": 2,
        "story_event": "Principle: Society",
        "add_to_timeline": 'int(self.settlement["population"]) >= 15',
    },
    "innovations_5": {
        "sort_order": 3,
        "story_event": "Hooded Knight",
        "add_to_timeline": 'len(self.settlement["innovations"]) >= 5',
    },
    "innovations_8": {
        "sort_order": 2,
        "story_event": "Edged Tonometry",
        "add_to_timeline": 'len(self.settlement["innovations"]) >= 8',
    },
    "game_over": {
        "sort_order": 4,
        "story_event": "Game Over",
        "add_to_timeline": 'int(self.settlement["population"]) == 0 and int(self.settlement["lantern_year"]) >= 1',
    },
}



campaign_definitions = {
    "people_of_the_lantern": {
        "default": True,
        "name": "People of the Lantern",
        "always_available": ["Lantern Hoard", "Language"],
        "principles": ["new_life","death","society","conviction"],
        "nemesis_monsters": ["butcher","kings_man","the_hand"],
        "milestones": {
            "First child is born": milestones["first_child"],
            "First time death count is updated": milestones["first_death"],
            "Population reaches 15": milestones["pop_15"],
            "Settlement has 5 innovations": milestones["innovations_5"],
            "Population reaches 0": milestones["game_over"],
        "special_showdowns": ["watcher"],
        },
    },

    "people_of_the_skull": {
        "name": "People of the Skull",
        "always_available": ["Lantern Hoard", "Language"],
        "special_rules": [
            {"name": "People of the Skull",
             "desc": "Survivors can only place weapons and armor with the <b>bone</b> keyword in their gear grid. The people of the skull ignore the <b>Frail</b> rule.",
             "bg_color": "E3DAC9",
             "font_color": "333"},
            {"name": "People of the Skull",
             "desc": "When you name a survivor, if they have the word bone or skull in their name, in addition to +1 survival, players choose to gain +1 permanent accuracy, evasion, strength, luck or speed.",
             "bg_color": "E3DAC9",
             "font_color": "333"},
            {"name": "Black Skull",
             "desc": "If a weapon or armor is made with the Black Skull resource, a survivor may place it in their gear grid despite being iron.",
             "bg_color": "333",
             "font_color": "efefef"},
        ],
        "endeavors": {
            "Skull Ritual": {"cost": 1, "desc": "Costs one Skull resource. Nominate up to four survivors to consume the skull. They gain a permanent +1 to all their attributes."},
        },
        "principles": ["new_life","death","society","conviction"],
        "milestones": {
            "First child is born": milestones["first_child"],
            "First time death count is updated": milestones["first_death"],
            "Population reaches 15": milestones["pop_15"],
            "Settlement has 5 innovations": milestones["innovations_5"],
            "Population reaches 0": milestones["game_over"],
        },
    },

    "the_bloom_people": {
        "name": "The Bloom People",
        "always_available": ["Lantern Hoard", "Language"],
        "expansions": ["Flower Knight"],
        "storage": ["Sleeping Virus Flower"],
        "forbidden": ["Flower Addiction", "Flower Knight"],
        "milestones": {
            "First child is born": milestones["first_child"],
            "First time death count is updated": milestones["first_death"],
            "Population reaches 15": milestones["pop_15"],
            "Settlement has 5 innovations": milestones["innovations_5"],
            "Population reaches 0": milestones["game_over"],
        },
        "principles": ["new_life","death","society","conviction"],
        "endeavors": {
            "Forest Run": {"cost": 1, "desc": "You may exchange any number of monster resources for that number of random Flower resources."},
        },
        "settlement_buff": "All survivors are born with +1 permanent luck, +1 permanent green affinity and -2 permanent red affinities.",
        "newborn_survivor": {
            "affinities": {"red": -2, "green": 1,},
            "Luck": 1,
        },
    },

    "people_of_the_sun": {
        "name": "People of the Sun",
        "expansions": ["Sunstalker"],
        "forbidden": ["Leader", "Lantern Hoard"],
        "principles": ["potsun_new_life","death","society","conviction"],
        "milestones": {
            "First time death count is updated": milestones["first_death"],
            "Population reaches 15": milestones["pop_15"],
            "Settlement has 8 innovations": milestones["innovations_8"],
            "Population reaches 0": milestones["game_over"],
            "Not Victorious against Nemesis": {"sort_order": 4, "story_event": "Game Over"},
        },
        "timeline": [
            {"year": 0, "settlement_event": ["First Day"]},
            {"year": 1, "story_event": ["The Pool and the Sun"]},
            {"year": 2, "story_event": ["Endless Screams"]},
            {"year": 3, },
            {"year": 4, "story_event": ["Sun Dipping"]},
            {"year": 5, "story_event": ["The Great Sky Gift"]},
            {"year": 6, },
            {"year": 7, "story_event": ["Phoenix Feather"]},
            {"year": 8, }, {"year": 9, },
            {"year": 10, "story_event": ["Birth of Color"]},
            {"year": 11, "story_event": ["Principle: Conviction"]},
            {"year": 12, "story_event": ["Sun Dipping"]},
            {"year": 13, "story_event": ["The Great Sky Gift"]},
            {"year": 14, }, {"year": 15, }, {"year": 16, }, {"year": 17, }, {"year": 18, },
            {"year": 19, "story_event": ["Sun Dipping"]},
            {"year": 20, "story_event": ["Final Gift"]},
            {"year": 21, "nemesis_encounter": ["Nemesis Encounter: Kings Man Level 2"]},
            {"year": 22, "nemesis_encounter": ["Nemesis Encounter: Butcher Level 3"]},
            {"year": 23, "nemesis_encounter": ["Nemesis Encounter: Kings Man Level 3"]},
            {"year": 24, "nemesis_encounter": ["Nemesis Encounter: The Hand Level 3"]},
            {"year": 25, "story_event": ["The Great Devourer"]},
            {"year": 26, }, {"year": 27, }, {"year": 28, }, {"year": 29, }, {"year": 30, }, {"year": 31, },
            {"year": 32, }, {"year": 33, }, {"year": 34, }, {"year": 35, }, {"year": 36, },
            {"year": 37, }, {"year": 38, }, {"year": 39, }, {"year": 40, },
        ],
    },

    "people_of_the_stars": {
        "name": "People of the Stars",
        "expansions": ["Dragon King"],
        "always_available": ["Throne","Dragon Speech","Radiating Orb"],
        "forbidden": ["Lantern Hoard", "Language","Lantern Oven","Clan of Death","Family", "Dragon Armory"],
        "always_available_nemesis": "The Tyrant",
        "founder_epithet": "Foundling",
        "replaced_story_events": {
            "Bold": "Awake",
            "Insight": "Awake",
        },
        "new_survivor_additional_attribs": {
            "constellation": None,
            "constellation_traits": [],
        },
        "survivor_attribs": ["Scar","Noble surname","Reincarnated surname"],
        "special_rules": [
            {"name": "Removed Story Events", "desc": "If an event or card would cause you to add/trigger <b>Hands of Heat</b>, <b>Regal Visit</b>, <b>Armored Strangers</b>, <b>Watched</b>, or <b>Nemesis Encounter - Watcher</b>, do nothing instead.", "bg_color": "673AB7", "font_color": "FFF"},
        ],
        "principles": ["potsun_new_life","death","society","conviction"],
        "milestones": {
            "First child is born": milestones["first_child"],
            "First time death count is updated": milestones["first_death"],
            "Population reaches 15": milestones["pop_15"],
            "Population reaches 0": milestones["game_over"],
        },
        "nemesis_monsters": ["butcher","kings_man","the_hand"],
        "nemesis_encounters": [{"butcher":["Lvl 1"], "kings_man":["Lvl 1"], "the_hand":["Lvl 1"]}],
        "timeline": [
            {"year": 0, "settlement_event": ["First Day"]},
            {"year": 1, "story_event": ["The Foundlings"]},
            {"year": 2, "story_event": ["Endless Screams"]},
            {"year": 3, },
            {"year": 4, "nemesis_encounter": ["Nemesis Encounter - Dragon King Human Lvl 1"]},
            {"year": 5, "story_event": ["Midnight's Children"]},
            {"year": 6, },
            {"year": 7, "story_event": ["Phoenix Feather"]},
            {"year": 8, },
            {"year": 9, "nemesis_encounter": ["Nemesis Encounter - Dragon King Human Lvl 2"]},
            {"year": 10, "story_event": ["Unveil the Sky"]},
            {"year": 11, },
            {"year": 12, "story_event": ["Principle: Conviction"]},
            {"year": 13, "nemesis_encounter": ["Nemesis Encounter - Butcher Lvl 2"]},
            {"year": 14, }, {"year": 15, },
            {"year": 16, "nemesis_encounter": ["Nemesis Encounter - Lvl 2"]},
            {"year": 17, }, {"year": 18, },
            {"year": 19, "nemesis_encounter": ["Nemesis Encounter - Dragon King Human Lvl 3"]},
            {"year": 20, "story_event": ["The Dragon's Tomb"]},
            {"year": 21, }, {"year": 22, },
            {"year": 23, "nemesis_encounter": ["Nemesis Encounter - Lvl 3"]},
            {"year": 24, },
            {"year": 25, "nemesis_encounter": ["Nemesis Encounter - Death of the Dragon King"]},
            {"year": 26, }, {"year": 27, }, {"year": 28, }, {"year": 29, }, {"year": 30, }, {"year": 31, },
            {"year": 32, }, {"year": 33, }, {"year": 34, }, {"year": 35, }, {"year": 36, },
            {"year": 37, }, {"year": 38, }, {"year": 39, }, {"year": 40, },
        ],
    },
}


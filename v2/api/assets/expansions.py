#!/usr/bin/python2.7

from datetime import datetime

promo_and_misc = {
    "beta_challenge_scenarios": {
        "released": datetime(2016,2,1),
        "name": "Beta Challenge Scenarios",
        "ui": {"pretty_category": "Enhancement"},
        "flair": {
            "color": "FFF",
            "bgcolor": "4EC6F0",
        },
        "enforce_survival_limit": False,
        "subtitle": "Enables abilities & impairments, disorders, items etc. included in the Beta Challenge Scenarios.",
        "special_rules": [
            {
            "name": "Survival Limit Warning!",
            "bg_color": "F87217",
            "font_color": "FFF",
            "desc": "Survival Limit is not automatically enforced by the Manager when Beta Challenge Scenarios content is enabled.",
            },
        ],
    },
    "white_box": {
        "released": datetime(2016,8,16),
        "name": "White Box & Promo",
        "ui": {"pretty_category": "Enhancement"},
        "flair": {
            "color": "FFF",
            "bgcolor": "4EC6F0",
        },
        "subtitle": "Adds miscellaneous promotional content (items, Abilities & Impairments, etc.) to Settlement and Survivor Sheet drop-down lists. Content includes Gen Con, Black Friday and other promos.",
    },
    "percival": {
        "name": "Percival",
        "ui": {"pretty_category": "Enhancement"},
        "released": datetime(2016,8,16),
        'basic_hunt_event': ['dead_warrior'],
    },
}

mar_2016_expansions = {
    "gorm": {
        "name": "Gorm",
        "ui": {"pretty_category": "Quarry"},
        "flair": {
            "color": "EAE40A",
            "bgcolor": "958C83",
        },
        "quarries": ["gorm"],
        "always_available": {
            "location": ["Gormery", "Gormchymist"],
            "innovation": ["Nigredo"],
        },
        "timeline_add": [
            {"ly": 1, "handle": "gorm_approaching_storm"},
            {"ly": 2, 'handle': 'gorm_gorm_climate'},
        ],
    },
    "green_knight_armor": {
        "name": "Green Knight Armor",
        "ui": {"pretty_category": "Enhancement"},
        "subtitle": "Crafting GKA items requires DBK, Flower Knight, Lion Knight and Gorm expansions!",
        "always_available": {
            "location": ["Green Knight Armor"],
        },
        "flair": {
            "color": "EAE40A",
            "bgcolor": "958C83",
        },
    },
    "dung_beetle_knight": {
        "name": "Dung Beetle Knight",
        "ui": {"pretty_category": "Quarry"},
        "flair": {
            "color": "EAE40A",
            "bgcolor": "C3C8AB",
        },
        "quarries": ["dung_beetle_knight"],
        "always_available": {
            "location": ["Wet Resin Crafter"],
            "innocation": ["Subterranean Agriculture"],
        },
        "timeline_add": [
            {"ly": 8, "handle": "dbk_rumbling_in_the_dark"},
        ],
        "help": [
            {"type": "storage", "tip": "The <b>Regenerating Blade</b> is Rare Gear."},
            {"type": "storage", "tip": "<b>Calcified</b> gear is selectable from the <b>Black Harvest</b> section of the Settlement Storage controls."},
        ],
    },
    "spidicules": {
        "name": "Spidicules",
        "ui": {"pretty_category": "Quarry"},
        "flair": {
            "color": "333",
            "bgcolor": "C0B870",
        },
        "quarries": ["spidicules"],
        "always_available": {
            "location": ["Silk Mill"],
            "innovation": ["Legless Ball","Silk-Refining"],
        },
        "timeline_add": [
            {"ly": 2, "handle": "spid_young_rivals"},
        ],
        "timeline_rm": [
            {"ly": 2, "handle": "core_endless_screams"},
        ],
    },
    "slenderman": {
        "name": "Slenderman",
        "ui": {"pretty_category": "Nemesis"},
        "flair": {
            "color": "fff2b7",
            "bgcolor": "BEA9CB",
        },
        "nemesis_monsters": ["slenderman"],
        "rm_nemesis_monsters": ["kings_man"],
        "always_available": {
            "innovation": ["Dark Water Research"],
        },
        "timeline_add": [
            {"ly": 6, "handle": "slender_its_already_here"},
            {"ly": 9, "type": "nemesis_encounter", "name": "Nemesis Encounter"},
        ],
        "timeline_rm": [
            {"ly": 6, "handle": "core_armored_strangers"},
            {"ly": 9, "sub_type": "nemesis_encounter", "name": "Nemesis Encounter: King's Man Lvl 1"},
        ],
    },
    "lion_knight": {
        "name": "Lion Knight",
        "ui": {"pretty_category": "Nemesis"},
        "flair": {
            "color": "666",
            "bgcolor": "FCF78F",
        },
        "quarries": ["lion_knight"],
        "always_available": {
            "innovation": ["Stoic Statue"],
        },
        "special_showdowns": ["lion_knight"],
        "timeline_add": [
            {"ly":  6, "handle": "lk_uninvited_guest"},
            {"ly":  8, "handle": "lk_places_everyone"},
            {"ly":  8, "sub_type": "special_showdown", "name": "Special Showdown - Lion Knight Lvl 1"},
            {"ly": 12, "handle": "lk_places_everyone"},
            {"ly": 12, "sub_type": "special_showdown", "name": "Special Showdown - Lion Knight Lvl 2"},
            {"ly": 16, "handle": "lk_places_everyone"},
            {"ly": 16, "sub_type": "special_showdown", "name": "Special Showdown - Lion Knight Lvl 3"},
        ],
    },
    "lion_god": {
        "name": "Lion God",
        "ui": {"pretty_category": "Quarry"},
        "flair": {
            "color": "E8cE55",
            "bgcolor": "712C2B",
        },
        "quarries": ["lion_god"],
        "always_available": {
            "innovation": ["The Knowledge Worm"],
        },
        "timeline_add": [
            {"ly": 13, "handle": "lgod_silver_city"},
        ],
    },
    "sunstalker": {
        "name": "Sunstalker",
        "ui": {"pretty_category": "Quarry"},
        "flair": {
            "color": "000",
            "bgcolor": "ECD77E",
        },
        "quarries": ["sunstalker"],
        "always_available": {
            "location": ["Skyreef Sanctuary"],
            "innovation": ["Umbilical Bank"],
        },
        "timeline_add": [
            {"ly": 8, "handle": "ss_promise_under_the_sun"},
        ],
    },
    "dragon_king": {
        "name": "Dragon King",
        "ui": {"pretty_category": "Quarry"},
        "flair": {
            "color": "E8cE55",
            "bgcolor": "6260A9",
        },
        "quarries": ["dragon_king"],
        "always_available": {
            "location": ["Dragon Armory"],
        },
        "timeline_add": [
            {"ly": 8, "handle": "dk_glowing_crater"},
        ],
    },
    "manhunter": {
        "name": "Manhunter",
        "ui": {"pretty_category": "Nemesis"},
        "flair": {
            "color": "E8cE55",
            "bgcolor": "8D0000",
        },
        "nemesis_monsters": ["manhunter"],
        "special_showdowns": ["manhunter"],
        "always_available": {
            "innovation": ["War Room", "Settlement Watch", "Crimson Candy"],
        },
        "timeline_add": [
            {"ly": 5,  "handle": "mh_hanged_man"},
            {"ly": 5,  "sub_type": "special_showdown", "name": "Special Showdown - Manhunter"},
            {"ly": 10, "sub_type": "special_showdown", "name": "Special Showdown - Manhunter"},
            {"ly": 16, "sub_type": "special_showdown", "name": "Special Showdown - Manhunter"},
            {"ly": 22, "sub_type": "special_showdown", "name": "Special Showdown - Manhunter"},
        ],
    },
    "lonely_tree": {
        "name": "Lonely Tree",
        "ui": {"pretty_category": "Nemesis"},
        "nemesis_monsters": ["lonely_tree"],
        "special_showdowns": ["lonely_tree"],
        "flair": {
            "color": "EAE40A",
            "bgcolor": "958C83",
        },
    },
    "flower_knight": {
        "name": "Flower Knight",
        "ui": {"pretty_category": "Quarry"},
        "flair": {
            "color": "EAE40A",
            "bgcolor": "4E7D49",
        },
        "quarries": ["flower_knight"],
        "timeline_add": [
            {"ly": 5, "handle": "fk_crones_tale"}
        ],
    },
}

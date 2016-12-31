#!/usr/bin/python2.7

from datetime import datetime

promo_and_misc = {
    "beta_challenge_scenarios": {
        "released": datetime(2016,2,1),
        "name": "Beta Challenge Scenarios",
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
        "name": "White Box",
        "subtitle": "Enables promo and early-release items and abilities & impairments included in the so-called 'White Box' collection of survivor minis (released at Gen Con 2016).",
    },
}

mar_2016_expansions = {
    "gorm": {
        "name": "Gorm",
        "quarries": ["gorm"],
        "always_available": {
            "location": ["Gormery", "Gormchymist"],
            "innovation": ["Nigredo"],
        },
        "timeline_add": [
            {"ly": 1, "type": "story_event", "handle": "gorm_approaching_storm"},
            {"ly": 2, "type": "settlement_event", "name": "Gorm Climate"},
        ],
    },
    "dung_beetle_knight": {
        "name": "Dung Beetle Knight",
        "quarries": ["dung_beetle_knight"],
        "always_available": {
            "location": ["Wet Resin Crafter"],
            "innocation": ["Subterranean Agriculture"],
        },
        "timeline_add": [
            {"ly": 8, "type": "story_event", "handle": "dbk_rumbling_in_the_dark"},
        ],
    },
    "spidicules": {
        "name": "Spidicules",
        "quarries": ["spidicules"],
        "always_available": {
            "location": ["Silk Mill","Silk-Refining"],
            "innovation": ["Legless Ball"],
        },
        "timeline_add": [
            {"ly": 2, "type": "story_event", "handle": "spid_young_rivals"},
        ],
        "timeline_rm": [
            {"ly": 2, "type": "story_event", "name": "Endless Screams"},
        ],
    },
    "lion_knight": {
        "name": "Lion Knight",
        "quarries": ["lion_knight"],
        "always_available": {
            "innovation": ["Stoic Statue"],
        },
        "special_showdowns": ["lion_knight"],
        "timeline_add": [
            {"ly":  6, "type": "story_event", "handle": "lk_uninvited_guest"},
            {"ly":  8, "type": "story_event", "handle": "lk_places_everyone"},
            {"ly":  8, "type": "special_showdown", "name": "Special Showdown - Lion Knight Lvl 1"},
            {"ly": 12, "type": "story_event", "handle": "lk_places_everyone"},
            {"ly": 12, "type": "special_showdown", "name": "Special Showdown - Lion Knight Lvl 2"},
            {"ly": 16, "type": "story_event", "handle": "lk_places_everyone"},
            {"ly": 16, "type": "special_showdown", "name": "Special Showdown - Lion Knight Lvl 3"},
        ],
    },
    "lion_god": {
        "name": "Lion God",
        "quarries": ["lion_god"],
        "always_available": {
            "innovation": ["The Knowledge Worm"],
        },
        "timeline_add": [
            {"ly": 13, "type": "story_event", "handle": "lgod_silver_city"},
        ],
    },
    "sunstalker": {
        "name": "Sunstalker",
        "quarries": ["sunstalker"],
        "always_available": {
            "location": ["Skyreef Sanctuary"],
            "innovation": ["Umbilical Bank"],
        },
        "survivor_attribs": ["Purified","Sun Eater","Child of the Sun"],
        "timeline_add": [
            {"ly": 8, "type": "story_event", "handle": "ss_promise_under_the_sun", "excluded_campaign": "People of the Sun"},
        ],
    },
    "dragon_king": {
        "name": "Dragon King",
        "quarries": ["dragon_king"],
        "always_available": {
            "location": ["Dragon Armory"],
        },
        "timeline_add": [
            {"ly": 8, "type": "story_event", "handle": "dk_glowing_crater", "excluded_campaign": "People of the Stars"},
        ],
    },
    "manhunter": {
        "name": "Manhunter",
        "nemesis_monsters": ["manhunter"],
        "special_showdowns": ["manhunter"],
        "always_available": {
            "innovation": ["War Room", "Settlement Watch", "Crimson Candy"],
        },
        "timeline_add": [
            {"ly": 5, "type": "story_event", "handle": "mh_hanged_man"},
            {"ly":  5, "type": "special_showdown", "name": "Special Showdown - Manhunter"},
            {"ly": 10, "type": "special_showdown", "name": "Special Showdown - Manhunter"},
            {"ly": 16, "type": "special_showdown", "name": "Special Showdown - Manhunter"},
            {"ly": 22, "type": "special_showdown", "name": "Special Showdown - Manhunter"},
        ],
    },
    "lonely_tree": {
        "name": "Lonely Tree",
#        "nemesis_monsters": ["lonely_tree"],
        "special_showdowns": ["lonely_tree"],
    },
    "flower_knight": {
        "name": "Flower Knight",
        "quarries": ["flower_knight"],
        "timeline_add": [
            {"ly": 5, "type": "story_event", "handle": "fk_crones_tale", "excluded_campaign": "The Bloom People"}
        ],
    },
}

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
        "always_available": ["Gormery", "Gormchymist", "Nigredo"],
        "timeline_add": [
            {"ly": 1, "type": "story_event", "handle": "gorm_approaching_storm"},
            {"ly": 2, "type": "settlement_event", "name": "Gorm Climate"},
        ],
    },
    "dung_beetle_knight": {
        "name": "Dung Beetle Knight",
        "always_available": ["Wet Resin Crafter","Subterranean Agriculture"],
        "timeline_add": [
            {"ly": 8, "type": "story_event", "handle": "dbk_rumbling_in_the_dark"},
        ],
    },
    "spidicules": {
        "name": "Spidicules",
        "always_available": ["Legless Ball","Silk Mill","Silk-Refining"],
        "timeline_add": [
            {"ly": 2, "type": "story_event", "handle": "spid_young_rivals"},
        ],
        "timeline_rm": [
            {"ly": 2, "type": "story_event", "name": "Endless Screams"},
        ],
    },
    "lion_knight": {
        "name": "Lion Knight",
        "always_available": ["Stoic Statue"],
        "special_rules": [
            {
            "name": "Special Showdowns - Update",
            "bg_color": "FFD740",
            "font_color": "000",
            "desc": "Special Showdowns interrupt the Settlement Phase. After they conclude, the Settlement Phase continues where it left off, regardless of victory of defeat. Heal all light and heavy injuries from the remaining survivors and remove all tokens. Do not repeat any steps of the settlement phase.",
            },
        ],
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
        "always_available": ["The Knowledge Worm"],
        "timeline_add": [
            {"ly": 13, "type": "story_event", "handle": "lgod_silver_city"},
        ],
    },
    "sunstalker": {
        "name": "Sunstalker",
        "always_available": ["The Sun", "Sun Language", "Umbilical Bank"],
        "survivor_attribs": ["Purified","Sun Eater","Child of the Sun"],
        "timeline_add": [
            {"ly": 8, "type": "story_event", "handle": "ss_promise_under_the_sun", "excluded_campaign": "People of the Sun"},
        ],
    },
    "dragon_king": {
        "name": "Dragon King",
        "always_available": ["Dragon Armory"],
        "timeline_add": [
            {"ly": 8, "type": "story_event", "handle": "dk_glowing_crater", "excluded_campaign": "People of the Stars"},
        ],
    },
    "manhunter": {
        "name": "Manhunter",
        "always_available": ["War Room", "Settlement Watch", "Crimson Candy"],
#        "always_available_nemesis": True,
        "special_rules": [
            {
            "name": "Special Showdowns - Update",
            "bg_color": "B71C1C",
            "font_color": "fff",
            "desc": "Special Showdowns interrupt the Settlement Phase. After they conclude, the Settlement Phase continues where it left off, regardless of victory of defeat. Heal all light and heavy injuries from the remaining survivors and remove all tokens. Do not repeat any steps of the settlement phase.",
            },
        ],
        "special_showdowns": ["manhunter"],
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
        "special_showdowns": ["lonely_tree"],
#        "always_available_nemesis": True,
    },
    "flower_knight": {
        "name": "Flower Knight",
        "timeline_add": [
            {"ly": 5, "type": "story_event", "handle": "fk_crones_tale", "excluded_campaign": "The Bloom People"}
        ],
    },
}

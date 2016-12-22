#!/usr/bin/python2.7


quarries = {
    "white_lion": {
        "name": "White Lion",
        "sort_order": 0,
    },
    "gorm": {
        "name": "Gorm",
        "expansion": "gorm",
        "sort_order": 1,
    },
    "screaming_antelope": {
        "name": "Screaming Antelope",
        "sort_order": 2,
        "misspellings": ["XCREAMING ANTALOPE","SCREAMING ANTALOPE"],
    },
    "spidicules": {
        "name": "Spidicules",
        "expansion": "spidicules",
        "sort_order": 3,
    },
    "flower_knight": {
        "name": "Flower Knight",
        "expansion": "flower_knight",
        "sort_order": 4,
    },
    "phoenix": {
        "name": "Phoenix",
        "sort_order": 5,
        "misspellings": ["PHONIEX"],
    },
    "sunstalker": {
        "name": "Sunstalker",
        "expansion": "sunstalker",
        "sort_order": 6,
    },
    "dragon_king": {
        "name": "Dragon King",
        "expansion": "dragon_king",
        "sort_order": 7,
    },
    "dung_beetle_knight": {
        "name": "Dung Beetle Knight",
        "expansion": "dung_beetle_knight",
        "sort_order": 8,
    },
    "lion_god": {
        "name": "Lion God",
        "expansion": "lion_god",
        "sort_order": 9
    },
}

unique_quarries = {
    "beast_of_sorrow": {
        "name": "Beast of Sorrow",
        "sort_order": 20,
    },
    "great_golden_cat": {
        "name": "Great Golden Cat",
        "sort_order": 21,
    },
    "mad_steed": {
        "name": "Mad Steed",
        "sort_order": 22,
    },
    "golden_eyed_king": {
        "name": "Golden Eyed King",
        "sort_order": 23,
    },
    "old_master": {
        "name": "Old Master",
        "expansion": "dung_beetle_knight",
        "sort_order": 30,
    },
}

nemeses = {
    "lonely_tree": {
        "name": "Lonely Tree",
        "sort_order": 100,
        "selectable": False,
    },
    "butcher": {
        "name": "Butcher",
        "sort_order": 101,
        "misspellings": ["THE BUTCHER", "BUTCHEE"],
    },
    "the_tyrant": {
        "name": "The Tyrant",
        "sort_order": 102,
        "selectable": False,
        "misspellings": ["DRAGON KING HUMAN","TYRANT"],
    },
    "manhunter": {
        "name": "Manhunter",
        "sort_order": 103,
        "selectable": False,
        "levels": 4,
        "misspellings": ["THE MANHUNTER", "MAN HUNTER"],
    },
    "kings_man": {
        "name": "King's Man",
        "sort_order": 104,
        "misspellings": ["KINGSMAN", "KINGMAN", "THE KING'S MAN", "THE KINGSMAN"],
    },
    "lion_knight": {
        "name": "Lion Knight",
        "selectable": False,
        "expansion": "lion_knight",
        "sort_order": 105,
        "misspellings": ["LIONKNIGHT", "THE LION KNIGHT", "THE LIONKNIGHT"],
    },
    "the_hand": {
        "name": "The Hand",
        "sort_order": 105,
        "misspellings": ["HAND"],
    },
}

unique_nemeses = {
    "ancient_sunstalker": {
        "name": "Ancient Sunstalker",
        "expansion": "sunstalker",
        "sort_order": 200,
        "final_boss": True,
    },
    "watcher": {
        "name": "Watcher",
        "sort_order": 201,
        "misspellings": ["THE WATCHER"],
        "final_boss": True,
    },
}


#
#   helpers and shorthands below
#

base_game_quarries = [
    "white_lion",
    "screaming_antelope",
    "phoenix",
    "beast_of_sorrow",
    "great_golden_cat",
    "mad_steed",
    "golden_eyed_king",
]

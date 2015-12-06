#!/usr/bin/env python

#
#   Only game_asset dictionaries belong in this file. Do not add any methods or
#       other helpers here. Those all belong in models.py
#


epithets = {
    "Monster Teeth": {},
    "Metal Jaw": {},
    "Haunted": {},
    "Skull Eater": {},
    "Rival": {},
    "Warborn": {},
    "Shape Shifter": {},
    "The Wanderer": {},
    "One-eyed": {},
    "Berserker": {},
    "The Wolf": {},
    "Brawler": {},
    "Thunderer": {},
    "Swift-footed": {},
    "Iron-hearted": {},
    "Man-slaying": {},
    "Fast Runner": {},
    "The Insane": {},
    "The Mad": {},
    "Huntress": {},
    "Hunter": {},
    "The Destroyer": {},
    "Patriarch": {},
    "Matriarch": {},
    "Dimmed by the Lantern": {},
    "Masticated": {},
    "Death Taster": {},
    "Pure Warrior": {},
    "Cursed": {},
    "Twilight Knight": {},
    "Swamp Explorer": {},
    "Lantern Experimenter": {},
    "Speaker of the First Words": {},
    "Voice of Reason": {},
    "Bone Witch": {},
    "Murdered": {},
    "Murderer": {},
    "Lucernae": {},
    "Caratosis": {},
    "Dormenatus": {},
}



locations = {
    "Lantern Hoard": {
        "consequences": ["Bone Smith", "Skinnery", "Organ Grinder"],
    },
    "Bone Smith": {
        "color": "777744",
        "consequences": ["Weapon Crafter"],
    },
    "Skinnery": {
        "color": "777744",
        "consequences": ["Leather Worker"],
    },
    "Organ Grinder": {
        "color": "777744",
        "consequences": ["Stone Circle"],
    },
    "Rare Gear": {
        "is_resource": True,
        "color": "FFD700",
    },
    "Blacksmith": {},
    "Stone Circle": {
        "color": "999"
    },
    "Leather Worker": {},
    "Weapon Crafter": {},
    "Barber Surgeon": {},
    "Plumery": {},
    "Mask Maker": {},
    "Exhausted Lantern Hoard": {},
    "Catarium": {
        "color": "eee",
    },
    "Unique Items": {
        "is_resource": True,
        "color": "7E6FF3",
    },
    "White Lion Resources": {
        "is_resource": True,
        "color": "FFCC66",
    },
    "Screaming Antelope Resources": {
        "is_resource": True,
        "color": "FFCC66",
    },
    "Phoenix Resources": {
        "is_resource": True,
        "color": "FFCC66",
    },
    "Basic Resources": {
        "is_resource": True,
        "color": "51C327",
    },
    "Strange Resources": {
        "is_resource": True,
        "color": "CCFFCC",
    },
    "Starting Gear": {
        "is_resource": True,
        "color": "CCC",
    },
}


items = {
    "Portcullis Key": {
        "type": "Resource",
        "location": "Unique Items",
    },
    "Love Juice": {
        "type": "Resource",
        "location": "Basic Resources",
    },
    "Skull": {
        "type": "Resource",
        "location": "Basic Resources",
    },
    "???": {
        "type": "Resource",
        "location": "Basic Resources",
    },
    "Monster Bone": {
        "type": "Resource",
        "location": "Basic Resources",
    },
    "Monster Organ": {
        "type": "Resource",
        "location": "Basic Resources",
    },
    "Monster Hide": {
        "type": "Resource",
        "location": "Basic Resources",
    },
    "Broken Lantern": {
        "type": "Resource",
        "location": "Basic Resources",
    },
    "Iron": {
        "type": "Resource",
        "location": "Strange Resources",
    },
    "Leather": {
        "type": "Resource",
        "location": "Strange Resources",
    },
    "Elder Cat Teeth": {
        "type": "Resource",
        "location": "Strange Resources",
    },
    "Phoenix Crest": {
        "type": "Resource",
        "location": "Strange Resources",
    },
    "Second Heart": {
        "type": "Resource",
        "location": "Strange Resources",
    },
    "Perfect Crucible": {
        "type": "Resource",
        "location": "Strange Resources",
    },
    "Legendary Horns": {
        "type": "Resource",
        "location": "Strange Resources",
    },
    "Fresh Acanthus": {
        "type": "Resource",
        "location": "Strange Resources",
    },
    "White Fur": {
        "location": "White Lion Resources",
    },
    "Lion Claw": {
        "location": "White Lion Resources",
    },
    "Eye of Cat": {
        "location": "White Lion Resources",
    },
    "Great Cat Bones": {
        "location": "White Lion Resources",
    },
    "Shimmering Mane": {
        "location": "White Lion Resources",
    },
    "Lion Tail": {
        "location": "White Lion Resources",
    },
    "Curious Hand": {
        "location": "White Lion Resources",
    },
    "Golden Whiskers": {
        "location": "White Lion Resources",
    },
    "Sinew": {
        "location": "White Lion Resources",
    },
    "Lion Testes": {
        "location": "White Lion Resources",
    },
    "Pelt": {
        "location": "Screaming Antelope Resources",
    },
    "Shank Bone": {
        "location": "Screaming Antelope Resources",
    },
    "Large Flat Tooth": {
        "location": "Screaming Antelope Resources",
    },
    "Beast Steak": {
        "location": "Screaming Antelope Resources",
    },
    "Muscly Gums": {
        "location": "Screaming Antelope Resources",
    },
    "Spiral Horn": {
        "location": "Screaming Antelope Resources",
    },
    "Bladder": {
        "location": "Screaming Antelope Resources",
    },
    "Screaming Brain": {
        "location": "Screaming Antelope Resources",
    },
    "Tall Feathers": {
        "location": "Phoenix Resources",
    },
    "Phoenix Eye": {
        "location": "Phoenix Resources",
    },
    "Phoenix Whisker": {
        "location": "Phoenix Resources",
    },
    "Pustules": {
        "location": "Phoenix Resources",
    },
    "Small Feathers": {
        "location": "Phoenix Resources",
    },
    "Muculent Droppings": {
        "location": "Phoenix Resources",
    },
    "Wishbone": {
        "location": "Phoenix Resources",
    },
    "Shimmering Halo": {
        "location": "Phoenix Resources",
    },
    "Bird Beak": {
        "location": "Phoenix Resources",
    },
    "Black Skull": {
        "location": "Phoenix Resources",
    },
    "Small Hand Parasites": {
        "location": "Phoenix Resources",
    },
    "Phoenix Finger": {
        "location": "Phoenix Resources",
    },
    "Hollow Wing Bones": {
        "location": "Phoenix Resources",
    },
    "Rainbow Droppings": {
        "location": "Phoenix Resources",
    },
    "Claw Head Arrow": {
        "attack": (1,6,6),
        "location": "Catarium",
    },
    "Cat Eye Circlet": {
        "location": "Catarium",
    },
    "Lion Skin Cloak": {
        "location": "Catarium",
    },
    "Whisker Harp": {
        "location": "Catarium",
    },
    "White Lion Boots": {
        "location": "Catarium",
    },
    "White Lion Gauntlet": {
        "location": "Catarium",
    },
    "King Spear": {
        "location": "Catarium",
    },
    "White Lion Helm": {
        "location": "Catarium",
    },
    "White Lion Skirt": {
        "location": "Catarium",
    },
    "Lion Beast Katar": {
        "location": "Catarium",
    },
    "Cat Fang Knife": {
        "location": "Catarium",
    },
    "Frenzy Drink": {
        "location": "Catarium",
    },
    "Lion Headdress": {
        "location": "Catarium",
    },
    "Cat Gut Bow": {
        "location": "Catarium",
    },
    "White Lion Coat": {
        "location": "Catarium",
    },
   "Founding Stone": {
        "location": "Starting Gear",
    },
    "Cloth": {
        "location": "Starting Gear",
    },
    "Rawhide Headband": {
        "location": "Skinnery",
    },
    "Rawhide Boots": {
        "location": "Skinnery",
    },
    "Rawhide Gloves": {
        "location": "Skinnery",
    },
    "Bandages": {
        "location": "Skinnery",
    },
    "Rawhide Pants": {
        "location": "Skinnery",
    },
    "Rawhide Vest": {
        "location": "Skinnery",
    },
    "Rawhide Whip": {
        "location": "Skinnery",
    },
    "Rawhide Drum": {
        "location": "Skinnery",
    },
    "Bone Axe": {
        "location": "Bone Smith",
    },
    "Bone Blade": {
        "location": "Bone Smith",
    },
    "Bone Darts": {
        "location": "Bone Smith",
    },
    "Skull Helm": {
        "location": "Bone Smith",
    },
    "Bone Dagger": {
        "location": "Bone Smith",
    },
    "Bone Pickaxe": {
        "location": "Bone Smith",
    },
    "Bone Sickle": {
        "location": "Bone Smith",
    },
    "Lucky Charm": {
        "location": "Organ Grinder",
    },
    "Fecal Salve": {
        "location": "Organ Grinder",
    },
    "Monster Grease": {
        "location": "Organ Grinder",
    },
    "Monster Tooth Necklace": {
        "location": "Organ Grinder",
    },
    "Dried Acanthus": {
        "location": "Organ Grinder",
    },
    "Regal Gauntlet": {
        "location": "Rare Gear",
    },
    "Regal Plackart": {
        "location": "Rare Gear",
    },
    "Regal Greaves": {
        "location": "Rare Gear",
    },
    "Regal Helm": {
        "location": "Rare Gear",
    },
    "Regal Faulds": {
        "location": "Rare Gear",
    },
    "Forsaker Mask": {
        "location": "Rare Gear",
    },
    "Adventure Sword": {
        "location": "Rare Gear",
    },
    "Steel Shield": {
        "location": "Rare Gear",
    },
    "Steel Sword": {
        "location": "Rare Gear",
    },
    "Twilight Sword": {
        "location": "Rare Gear",
    },
    "Butcher Cleaver": {
        "location": "Rare Gear",
    },
    "Lantern Halberd": {
        "location": "Rare Gear",
    },
    "Muramasa": {
        "location": "Rare Gear",
    },
    "Thunder Maul": {
        "location": "Rare Gear",
    },
    "Screaming Bracers": {
        "location": "Stone Circle",
    },
    "Screaming Horns": {
        "location": "Stone Circle",
    },
    "Screaming Leg Warmers": {
        "location": "Stone Circle",
    },
    "Screaming Skirt": {
        "location": "Stone Circle",
    },
    "Screaming Coat": {
        "location": "Stone Circle",
    },
    "Beast Knuckle": {
        "location": "Stone Circle",
    },
    "Lance of Longinus": {
        "location": "Stone Circle",
    },
    "Boss Mehndi": {
        "location": "Stone Circle",
    },
    "Green Charm": {
        "location": "Stone Circle",
    },
    "Red Charm": {
        "location": "Stone Circle",
    },
    "Blue Charm": {
        "location": "Stone Circle",
    },
    "Blood Paint": {
        "location": "Stone Circle",
    },
    "Bone Earrings": {
        "location": "Stone Circle",
    },
}


innovations = {
    "Graves": {
        "type": "death principle",
        "consequences": [],
        "settlement_buff": "All new survivors gain +1 understanding. When a survivor dies during the hunt or showdown phase, gain +2 Endeavors. When a survivor dies during the settlement phase, gain +1 Endeavor.",
        "survivor_buff": "All new survivors gain +1 understanding.",
    },
    "Cannibalize": {
        "type": "death principle",
        "consequences": [],
        "survival_limit": 1,
        "settlement_buff": "Whenever a survivor dies, draw one basic resource and add it to the settlement storage.",
    },
    "Barbaric": {
        "type": "conviction principle",
        "consequences": [],
        "survival_limit": 1,
        "survivor_buff": "All current and newborn survivors gain +1 peromanent strength.",
    },
    "Romantic": {
        "type": "conviction principle",
        "consequences": [],
        "survival_limit": 1,
        "settlement_buff": "You may innovate one additional time during the settlement phase. In addition, all current and newborn survivors gain +1 understanding.",
        "survivor_buff": "All current and newborn survivors gain +1 understanding.",
    },
    "Collective Toil": {
        "type": "society principle",
        "consequences": [],
        "settlement_buff": "At the start of the settlement phase, gain +1 Endeavor for every 10 population.",
    },
    "Accept Darkness": {
        "type": "society principle",
        "consequences": [],
        "survivor_buff": "Add +2 to all Brain Trauma Rolls.",
    },
    "Protect the Young": {
        "type": "new life principle",
        "consequences": [],
        "survivor_buff": "When rolling on the Intimacy story event, roll twice and pick one result.",
    },
    "Survival of the Fittest": {
        "type": "new life principle",
        "consequences": [],
        "survival_limit": 1,
        "settlement_buff": "When rolling on the Intimacy story event, roll twice and pick the lowest result. All newborn survivors gain +1 strength.",
        "survivor_buff": "All newborn survivors gain +1 strength.",
    },
    "Clan of Death": {
        "type": "home",
        "consequences": [],
        "survivor_buff": "All newborn survivors gain +1 accuracy, +1 strength and +1 evasion.",
    },
    "Sacrifice": {
        "type": "faith",
        "consequences": [],
    },
    "Scarification": {
        "type": "faith",
        "consequences": [],
    },
    "Records": {
        "type": "education",
        "consequences": [],
    },
    "Shrine": {
        "type": "faith",
        "consequences": ["Sacrifice"],
    },
    "Scrap Smelting": {
        "type": "science",
        "consequences": [],
    },
    "Cooking": {
        "type": "science",
        "consequences": [],
        "survival_limit": 1,
    },
    "Paint": {
        "type": "art",
        "consequences": ["Pictograph", "Sculpture", "Face Painting"],
        "survival_action": "Dash",
    },
    "Drums": {
        "type": "music",
        "consequences": ["Song of the Brave", "Forbidden Dance"],
    },
    "Inner Lantern": {
        "type": "faith",
        "consequences": ["Shrine", "Scarification"],
        "survival_action": "Surge",
    },
    "Symposium": {
        "type": "education",
        "consequences": ["Nightmare Training", "Storytelling", ],
        "survival_limit": 1,
        "departure_buff": "Departing survivors gain +1 survival.",
        "settlement_buff": "When a survivor innovates, draw an additional 2 Innovation Cards to choose from.",
    },
    "Hovel": {
        "type": "home",
        "consequences": ["Partnership", "Family", "Bed"],
        "departure_buff": "Departing survivors gain +1 survival.",
        "survival_limit": 1,
    },
    "Storytelling": {
        "type": "education",
        "consequences": ["Records"],
        "survival_limit": 1,
    },
    "Nightmare Training": {
        "type": "education",
        "consequences": [],
    },
    "Language": {
        "type": "starting",
        "consequences": ["Ammonia", "Hovel", "Inner Lantern", "Drums", "Paint", "Symposium"],
        "survival_limit": 1,
        "survival_action": "Encourage",
    },
    "Ammonia": {
        "type": "science",
        "consequences": ["Bloodletting", "Lantern Oven"],
        "departure_buff": "Departing survivors gain +1 survival.",
    },
    "Lantern Oven": {
        "type": "science",
        "consequences": ["Cooking", "Scrap Smelting"],
        "departure_buff": "Departing Survivors gain +1 survival.",
    },
    "Memento Mori": {
        "consequences": [],
        "type": "art",
    },
    "Face Painting": {
        "type": "art",
        "consequences": [],
    },
    "Sculpture": {
        "type": "art",
        "consequences": ["Pottery"],
        "survival_limit": 1,
        "departure_buff": "Departing survivors gain +2 survival when they depart for a Nemesis Encounter.",
    },
    "Pictograph": {
        "type": "art",
        "consequences": ["Memento Mori", ],
        "survivor_buff": "Anytime during the hunt or showdown phase, a survivor may Run Away (story event).",
    },
    "Pottery": {
        "type": "art",
        "consequences": [],
        "survival_limit": 1,
        "settlement_buff": "If the settlement loses all its resources, you may select up to two resources and keep them.",
    },
    "Heart Flute": {
        "type": "music",
        "consequences": [],
    },
    "Saga": {
        "type": "music",
        "consequences": [],
        "survivor_buff": "All newborn survivors gain +2 hunt experience and +2 survival from knowing the epic.",
    },
    "Forbidden Dance": {
        "type": "music",
        "consequences": [],
    },
    "Bed": {
        "type": "home",
        "consequences": [],
        "survival_limit": 1,
    },
    "Family": {
        "type": "home",
        "consequences": ["Clan of Death", ],
        "departure_buff": "Departing survivors gain +1 survival.",
        "settlement_buff": "Survivors nominated for intimacy may give themselves a surname if they do not have one. A newbord survivor inherits the surname of one parent, their weapon type and half (rounded down) of their weapon proficiency levels.",
    },
    "Song of the Brave": {
        "type": "music",
        "consequences": ["Saga",],
        "survivor_buff": "All non-deaf survivors add +1 to their roll results on the Overwhelming Darkness story event.",
    },
    "Partnership": {
        "type": "home",
        "consequences": [],
    },
    "Bloodletting": {
        "type": "science",
        "consequences": [],
    },
    "Final Fighting Art": {
        "type": "education",
        "consequences": [],
        "survival_limit": 1,
    },
    "Ultimate Weapon": {
        "type": "science",
        "consequences": [],
        "survival_limit": 1,
    },
    "Guidepost": {
        "type": "other",
        "consequences": [],
        "departure_buff": "Departing survivors gain +1 survival.",
    },
}



quarries = {
    "White Lion": {    },
    "Screaming Antelope": {    },
    "Phoenix": {    },
}


resource_decks = {
    "White Lion": [ "White Fur", "White Fur", "White Fur", "White Fur", "Lion Claw", "Lion Claw", "Lion Claw", "Eye of Cat", "Great Cat Bones", "Great Cat Bones", "Great Cat Bones", "Great Cat Bones", "Shimmering Mane", "Lion Tail", "Curious Hand", "Golden Whiskers", "Sinew", "Sinew", "Lion Testes" ],
    "Screaming Antelope": ["Pelt", "Pelt", "Pelt", "Pelt", "Shank Bone", "Shank Bone", "Shank Bone", "Shank Bone", "Large Flat Tooth", "Large Flat Tooth", "Beast Steak", "Beast Steak", "Muscly Gums", "Spiral Horn", "Bladder", "Screaming Brain"],
    "Phoenix": ["Tall Feathers", "Tall Feathers", "Tall Feathers", "Phoenix Eye", "Phoenix Whisker", "Pustules", "Pustules", "Small Feathers", "Small Feathers", "Small Feathers", "Muculent Droppings", "Muculent Droppings", "Muculent Droppings", "Wishbone", "Shimmering Halo", "Bird Beak", "Black Skull", "Small Hand Parasites", "Phoenix Finger", "Phoenix Finger", "Hollow Wing Bones", "Hollow Wing Bones", "Hollow Wing Bones", "Rainbow Droppings"],
    "Basic Resources": ["???", "???", "Skull", "Broken Lantern", "Broken Lantern", "Monster Bone", "Monster Bone", "Monster Bone", "Monster Bone", "Love Juice", "Love Juice", "Monster Organ", "Monster Organ", "Monster Organ", "Monster Hide", "Monster Hide", "Monster Hide", "Monster Hide", "Monster Hide", "Monster Hide", "Monster Hide"]
}



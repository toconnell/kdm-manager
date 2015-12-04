#!/usr/bin/env python

from utils import get_logger

resource_decks = {
    "White Lion": [ "White Fur", "White Fur", "White Fur", "White Fur", "Lion Claw", "Lion Claw", "Lion Claw", "Eye of Cat", "Great Cat Bones", "Great Cat Bones", "Great Cat Bones", "Great Cat Bones", "Shimmering Mane", "Lion Tail", "Curious Hand", "Golden Whiskers", "Sinew", "Sinew", "Lion Testes" ],
    "Screaming Antelope": ["Pelt", "Pelt", "Pelt", "Pelt", "Shank Bone", "Shank Bone", "Shank Bone", "Shank Bone", "Large Flat Tooth", "Large Flat Tooth", "Beast Steak", "Beast Steak", "Muscly Gums", "Spiral Horn", "Bladder", "Screaming Brain"],
    "Phoenix": ["Tall Feathers", "Tall Feathers", "Tall Feathers", "Phoenix Eye", "Phoenix Whisker", "Pustules", "Pustules", "Small Feathers", "Small Feathers", "Small Feathers", "Muculent Droppings", "Muculent Droppings", "Muculent Droppings", "Wishbone", "Shimmering Halo", "Bird Beak", "Black Skull", "Small Hand Parasites", "Phoenix Finger", "Phoenix Finger", "Hollow Wing Bones", "Hollow Wing Bones", "Hollow Wing Bones", "Rainbow Droppings"],
    "Basic Resources": ["???", "???", "Skull", "Broken Lantern", "Broken Lantern", "Monster Bone", "Monster Bone", "Monster Bone", "Monster Bone", "Love Juice", "Love Juice", "Monster Organ", "Monster Organ", "Monster Organ", "Monster Hide", "Monster Hide", "Monster Hide", "Monster Hide", "Monster Hide", "Monster Hide", "Monster Hide"]
}


quarries = {
    "White Lion": {    },
    "Screaming Antelope": {    },
    "Phoenix": {    },
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


locations = {
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
    "Bone Smith": {
        "color": "777744",
    },
    "Rare Gear": {
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
    "Lantern Hoard": {},
    "Skinnery": {
        "color": "777744",
    },
    "Organ Grinder": {
        "color": "777744",
    },
}

items = {
    "Love Juice": {
        "location": "Basic Resources",
    },
    "Skull": {
        "location": "Basic Resources",
    },
    "???": {
        "location": "Basic Resources",
    },
    "Monster Bone": {
        "location": "Basic Resources",
    },
    "Monster Organ": {
        "location": "Basic Resources",
    },
    "Monster Hide": {
        "location": "Basic Resources",
    },
    "Broken Lantern": {
        "location": "Basic Resources",
    },
    "Iron": {
        "location": "Strange Resources",
    },
    "Leather": {
        "location": "Strange Resources",
    },
    "Elder Cat Teeth": {
        "location": "Strange Resources",
    },
    "Phoenix Crest": {
        "location": "Strange Resources",
    },
    "Second Heart": {
        "location": "Strange Resources",
    },
    "Perfect Crucible": {
        "location": "Strange Resources",
    },
    "Legendary Horns": {
        "location": "Strange Resources",
    },
    "Fresh Acanthus": {
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
        "desc": "When something would collide with you, roll 1d10. On a result of 6+, you successfully tumble out of harm's way. Instead, please your survivor standingo n the closest free space outside of the collision path.",
    },
    "Extra Sense": {
        "desc": "You may dodge 1 additional time per round.",
    },
}

epithets = {
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

abilities_and_impairments = {
    "Intracranial hemmorhage": {
        "type": "impairment",
        "desc": "You can no longer use or gain any survival. This injury is permanent and can be recorded once.",
        "max": 1,
    },
    "Deaf": {
        "type": "impairment",
        "desc": "Suffer -1 permanent evasion. This injury is permanent and can be recorded once.",
        "max": 1,
    },
    "Shattered Jaw": {
        "type": "impairment",
        "desc": "You can no longer consume or be affected by events requiring you to consume. You can no longer incourage. This injury is permanent and can be recorded once.",
        "max": 1,
    },
    "Dismembered Arm": {
        "type": "impairment",
        "desc": "You can no longer activate two-handed weapons. This injury is permanent, and can be recorded twice. A survivor with two dismembered arm severe injuries cannot activate any weapons.",
        "max": 2,
    },
    "Ruptured Muscle": {
        "type": "impairment",
        "desc": "You can no longer activate fighting arts. This injury is permanent and can be recorded once.",
        "max": 1,
    },
    "Blind": {
        "type": "impairment",
        "desc": "TK",
    },
    "Warped Pelvis": {
        "type": "impairment",
        "desc": "Suffer -1 permanent luck. This injury is permanent and can be recorded multiple times.",
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
        "survivor_effect": "You cannot wear armor at the body location. If you are wearing armor at the body locationw hen you gain this disorder, archive it as you tear it off your person!",
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

def render_epithet_dict(return_as=False, exclude=[]):
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

def render_item_dict(return_as=False):
    """ Represents the models.items dictionary in a number of different ways.
    Leave 'return_as' unspecified to get a dictionary where the locations are
    the keys. """

    logger = get_logger()

    locations = set()
    for item_key in items.keys():
        locations.add(items[item_key]["location"])

    location_dict = {}
    for location in locations:
        location_dict[location] = set()

    for item_key in items.keys():
        item = items[item_key]
        location_dict[item["location"]].add(item_key)

    if return_as == "html_select_box":
        locations = sorted(list(locations))
        html = '<select name="add_item" onchange="this.form.submit()">\n'
        html += '<option selected disabled hidden value=''>Add Item</option>\n'
        for location_key in locations:
            html += ' <option disabled> &ensp; &ensp; --- %s ---  </option>\n' % location_key
            for item in sorted(location_dict[location_key]):
                html += '  <option value="%s">%s</option>\n' % (item, item)
        html += '</select>\n'
        return html


    return location_dict




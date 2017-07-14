#
#   these are the 'macro' options used when creating new settlements. See the
#   new_settlement_special() method of the settlements.Settlement model/class
#

specials = {
    "create_first_story_survivors": {
        "name": "First Story",
        "title": 'Four "First Story" Survivors',
        "desc": 'Two male and two female survivors will be randomly generated and automatically added to the <i>Departing Survivors</i> group. Starting gear will be added to Settlement Storage.',
        "current_quarry": "White Lion (First Story)",
        "random_survivors": [
            {"sex": "M", "Waist": 1, "in_hunting_party": "checked"},
            {"sex": "M", "Waist": 1, "in_hunting_party": "checked"},
            {"sex": "F", "Waist": 1, "in_hunting_party": "checked"},
            {"sex": "F", "Waist": 1, "in_hunting_party": "checked"},
        ],
        "storage": [
            {"name": "Founding Stone", "quantity": 4},
            {"name": "Cloth", "quantity": 4},
        ],
        "timeline_events": [
            {"ly": 0, "type": "showdown_event", "name": "White Lion (First Story)"},
        ],
    },

    "create_seven_swordsmen": {
        "name": "Seven Swordsmen",
        "title": "Seven Swordsmen",
        "desc": 'Seven survivors with the "Ageless" ability and Sword mastery will be randomly generated.',
        "random_survivors": [
            {"sex": "R", 'abilities_and_impairments': ['ageless','mastery_sword']},
            {"sex": "R", 'abilities_and_impairments': ['ageless','mastery_sword']},
            {"sex": "R", 'abilities_and_impairments': ['ageless','mastery_sword']},
            {"sex": "R", 'abilities_and_impairments': ['ageless','mastery_sword']},
            {"sex": "R", 'abilities_and_impairments': ['ageless','mastery_sword']},
            {"sex": "R", 'abilities_and_impairments': ['ageless','mastery_sword']},
            {"sex": "R", 'abilities_and_impairments': ['ageless','mastery_sword']},
        ],
    },

}



#
#   the survivors in the BCS PDF
#

beta_challenge_scenarios = {
    "adam": {
        "name": "Adam",
        "attribs": {
            "name": "Adam",
            "sex": "M",
            "survival": 4,
            "Insanity": 4,
            "Courage": 6,
            "Understanding": 3,
            "Weapon Proficiency": 3,
            "Strength": 1,
            "weapon_proficiency_type": "Sword",
            "fighting_arts": ["Timeless Eye"],
            "abilities_and_impairments": ["partner", "sword_specialization"],
        },
#        "storage": [
#            "Leather Mask",
#            "Leather Cuirass",
#            "Leather Bracers",
#            "Leather Skirt",
#            "Leather Boots",
#            "Scrap Sword",
#        ],
    },
    "anna": {
        "name": "Anna",
        "attribs": {
            "name": "Anna",
            "sex": "F",
            "survival": 4,
            "Insanity": 4,
            "Courage": 3,
            "Understanding": 6,
            "Weapon Proficiency": 3,
            "Evasion": 1,
            "weapon_proficiency_type": "Spear",
            "fighting_arts": ["Leader"],
            "abilities_and_impairments": ["partner", "spear_specialization"],
        },
#        "storage": [
#            "Leather Mask",
#            "Leather Cuirass",
#            "Leather Bracers",
#            "Leather Skirt",
#            "Leather Boots",
#            "King Spear",
#        ],
    },
    "paul_the_survivor": {
        "name": "Paul the Survivor",
        "attribs": {
            "name": "Paul",
            "sex": "M",
            "survival": 5,
            "Insanity": 9,
            "Courage": 3,
            "Understanding": 3,
            "fighting_arts": ["Thrill Seeker","Clutch Fighter","Extra Sense"],
            "disorders": ["Rageholic","Sworn Enemy"],
        },
        "storage": [
#            "Rawhide Pants",
#            "Rawhide Gloves",
#            "Rawhide Vest",
#            "Rawhide Boots",
#            "Bone Dagger",
#            "Scrap Sword",
#            "Piranha Helm",
#            "Petal Lantern",
        ],
    },
    "candy_and_cola":{
        "name": "Candy & Cola",
        "attribs": {"name": "Candy & Cola", "Movement": 6, "disorders": ["Hyperactive"], "sex": "F"},
    },
    "kara_black": {
        "name": "Kara Black",
        "attribs": {"name": "Kara Black", "survival": 3, "Strength": 1, "fighting_arts": ["Leader","Tough"], "sex": "F"},
#        "storage": ["Founding Stone", "Cloth", "Giant Stone Face"],
    },
    "messenger_of_the_first_story": {
        "name": "Messenger of the First Story",
        "attribs": {
            "name": "Messenger of the First Story",
            "sex": "F",
            "survival": 6,
            "Insanity": 6,
            "Courage": 6,
            "Strength": 1,
            "Evasion": 1,
            "Speed": 1,
            "fighting_arts": ["Last Man Standing"],
        },
#        "storage": [
#            "Screaming Horns",
#            "Screaming Coat",
#            "Screaming Skirt",
#            "Screaming Bracers",
#            "Screaming Leg Warmers",
#            "Monster Grease",
#            "Cat Eye Circlet",
#            "Dried Acanthus",
#            "Arm of the First Tree",
#        ],
    },
    "messenger_of_courage":{
        "name": "Messenger of Courage",
        "attribs": {
            "name": "Messenger of Courage",
            "sex": "F",
            "survival": 6,
            "Insanity": 9,
            "Courage":  9,
            "Understanding": 5,
            "Strength": 1,
            "Evasion": 2,
            "Speed": 2,
            "hunt_xp": 2,
            "Weapon Proficiency": 5,
            "weapon_proficiency_type": "Twilight Sword",
            "fighting_arts": ["Last Man Standing"],
            "cursed_items": ["twilight_sword"],
            "abilities_and_impairments": ["twilight_sword_specialization"],
            "epithets": ["twilight_sword"],
        },
#        "storage": [
#            "Scout's Tunic",
#            "Fairy Bottle",
#            "Leather Skirt",
#            "Leather Boots",
#            "Leather Bracers",
#            "Feather Mantle",
#            "Twilight Sword"
#        ],
    },
    "messenger_of_humanity":{
        "name":  "Messenger of Humanity",
        "attribs": {
            "name":  "Messenger of Humanity",
            "sex": "M",
            "survival": 10,
            "abilities_and_impairments": ["bitter_frenzy", "solid", "grand_weapon_specialization"],
            "fighting_arts": ["Berserker", "Crossarm Block", "Unconscious Fighter"],
            "disorders": ["Rageholic"],
        },
#        "storage": [
#            "Lantern Helm",
#            "Lantern Cuirass",
#            "Lantern Greaves",
#            "Lantern Mail",
#            "Lantern Gauntlets",
#            "Beacon Shield",
#            "Dragon Slayer"
#            "Stone Arm"
#        ],
    },
    "snow_the_savior":{
        "name": "Snow the Savior",
        "attribs": {
            "name": "Snow",
            "sex": "F",
            "survival": 6,
            "Insanity": 8,
            "Courage": 5,
            "Understanding": 5,
            "fighting_arts": ["Unconscious Fighter"],
            "abilities_and_impairments": ["red_glow", "blue_glow", "green_glow"]
        },
    },

}

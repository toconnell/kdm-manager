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
            "survival": 4,
            "Insanity": 4,
            "Courage": 6,
            "Understanding": 3,
            "Weapon Proficiency": 3,
            "Strength": 1,
            "weapon_proficiency_type": "Sword",
            "fighting_arts": ["Timeless Eye"],
            "abilities_and_impairments": ["Partner", "Specialization - Sword"],
            "ability_customizations": {"Partner": "Partner: Anna"},
        },
    },
    "anna": {
        "name": "Anna",
        "attribs": {
            "sex": "F",
            "survival": 4,
            "Insanity": 4,
            "Courage": 3,
            "Understanding": 6,
            "Weapon Proficiency": 3,
            "Evasion": 1,
            "weapon_proficiency_type": "Spear",
            "fighting_arts": ["Leader"],
            "abilities_and_impairments": ["Partner", "Specialization - Spear"],
            "ability_customizations": {"Partner": "Partner: Adam"},
        },
    },
    "paul_the_survivor": {
        "name": "Paul the Survivor",
        "attribs": {
            "name": "Paul",
            "survival": 5,
            "Insanity": 9,
            "Courage": 3,
            "Understanding": 3,
            "fighting_arts": ["Thrill Seeker","Clutch Fighter","Extra Sense"],
            "disorders": ["Rageholic","Sworn Enemy"],
            "abilities_and_impairments": ["Sworn Enemy"],
            "ability_customizations": {"Sworn Enemy": "Halberdless Man"},
        },
    },
    "candy_and_cola":{
        "name": "Candy & Cola",
        "attribs": {"Movement": 6, "disorders": ["Hyperactive"], "sex": "F"},
    },
    "kara_black": {
        "name": "Kara Black",
        "attribs": {"survival": 3, "Strength": 1, "fighting_arts": ["Leader","Tough"], "sex": "F"},
    },
    "messenger_of_the_first_story": {
        "name": "Messenger of the First Story",
        "attribs": {"sex": "F", "survival": 6, "Insanity": 6, "Courage": 6, "Strength": 1, "Evasion": 1, "Speed": 1,"fighting_arts": ["Last Man Standing"], },
    },
    "messenger_of_courage":{
        "name": "Messenger of Courage",
        "attribs": {"sex": "F", "survival": 6, "Insanity": 9, "Courage":  9, "Understanding": 5, "Strength": 1, "Evasion": 2, "Speed": 2, "hunt_xp": 2, "Weapon Proficiency": 5, "weapon_proficiency_type": "Twilight Sword", "fighting_arts": ["Last Man Standing"], "abilities_and_impairments": ["Specialization - Twilight Sword"]},
    },
    "messenger_of_courage":{
        "name":  "Messenger of Humanity",
        "attribs": {"survival": 10, "abilities_and_impairments": ["Bitter Frenzy", "Solid", "Specialization - Grand Weapon"], "fighting_arts": ["Berserker", "Crossarm Block", "Unconscious Fighter"], "disorders": ["Rageholic"]},
    },
    "snow_the_savior":{
        "name": "Snow the Savior",
        "attribs": {"name": "Snow", "sex": "F", "survival": 6, "Insanity": 8, "Courage": 5, "Understanding": 5, "fighting_arts": ["Unconscious Fighter"], "abilities_and_impairments": ["Red Glow", "Blue Glow", "Green Glow"]},
    },

}

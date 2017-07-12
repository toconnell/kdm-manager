#!/usr/bin/python


innovations = {
    #
    #   Innovations including a survival action unlock
    #

    # core
    "inner_lantern": {
        "name": "Inner Lantern",
        "type": "faith",
        "consequences": ["shrine", "scarification"],
        "survival_action": "surge",
    },
    "paint": {
        "name": "Paint",
        "type": "art",
        "consequences": ["pictograph","sculpture","face_painting"],
        "survival_action": "dash",
    },
    "language": {
        "name": "Language",
        "type": "starting innovation",
        "consequences": ["hovel","inner_lantern","drums","paint","symposium","ammonia"],
        "survival_limit": 1,
        "survival_action": "encourage",
    },

    # expansions
    "dragon_speech": {
        "name": "Dragon Speech",
        "type": "starting innovation",
        "expansion": "dragon_king",
        "survival_limit": 1,
        "survival_action": "encourage",
        "consequences": ["hovel", "inner_lantern","drums","paint","symposium","ammonia"],
    },
    "sun_language": {
        "name": "Sun Language",
        "expansion": "sunstalker",
        "type": "starting innovation",
        "survival_limit": 1,
        "survival_action": "embolden",
        "consequences": ["ammonia","drums","hovel","paint","symposium","hands_of_the_sun"],
    },
    "hands_of_the_sun": {
        "name": "Hands of the Sun",
        "expansion": "sunstalker",
        "type": "faith",
        "survival_action": "overcharge",
        "consequences": ["aquarobics", "sauna_shrine"],
    },


    #
    #   core game innovations start here
    #

    # core - art
    "sculpture": {
        "name": "Sculpture",
        "type": "art",
        "consequences": ["pottery"],
        "survival_limit": 1,
        "departure_buff": "Departing survivors gain +2 survival when they depart for a Nemesis Encounter.",
    },
    "pottery": {
        "name": "Pottery",
        "type": "art",
        "survival_limit": 1,
        "settlement_buff": "If the settlement loses all its resources, you may select up to two resources and keep them.",
        "endeavors": [
            {
                "name": "Build",
                "cost": 1,
                "desc": "Barber Surgeon (3 x organ, 1 x scrap)",
                "remove_after": "barber_surgeon"
            },
        ],
    },
    "face_painting": {
        "name": "Face Painting",
        "type": "art",
        "endeavors": [
            {"name": "Battle Paint", "cost": 1, "type": "art"},
            {"name": "Founder's Eye", "cost": 1, "type": "art"},
        ],
    },
    "pictograph": {
        "name": "Pictograph",
        "type": "art",
        "consequences": ["memento_mori"],
        "survivor_buff": 'At the start of a standing survivor\'s act, they may trigger the <font class=kdm_font>g</font> <b>Run Away</b> story event. Limit, once per act.',
    },
    "memento_mori": {
        "name": "Momento Mori",
        "type": "art",
        "endeavors": [
            {"name": "Momento Mori", "cost": 1, "type": "art"},
        ],
    },

    # core - home
    "hovel": {
        "name": "Hovel",
        "type": "home",
        "consequences": ["partnership","family","bed","shadow_dancing","bloodline","settlement_watch"],
        "departure_buff": "Departing survivors gain +1 survival.",
        "survival_limit": 1,
    },
    "partnership": {
        "name": "Partnership",
        "type": "home",
        "endeavors": [
            {"name": "Partner", "cost": 2, "type": "home"},
        ],
    },
    "bed": {
        "name": "Bed",
        "type": "home",
        "survival_limit": 1,
        "endeavors": [
            {"name": "Rest", "cost": 1, "type": "home"},
        ],
    },
    "family": {
        "name": "Family",
        "type": "home",
        "consequences": ["clan_of_death"],
        "departure_buff": "Departing survivors gain +1 survival.",
        "settlement_buff": "Survivors nominated for intimacy may give themselves a surname if they do not have one. A newborn survivor inherits the surname of one parent, their weapon type and half (rounded down) of their weapon proficiency levels.",
    },
    "clan_of_death": {
        "name": "Clan of Death",
        "type": "home",
        "survivor_buff": "All newborn survivors gain <b>+1 Accuracy</b>, <b>+1 Strength</b> and <b>+1 Evasion</b>.",
        "newborn_survivor": {"Strength": 1, "Accuracy": 1, "Evasion": 1},
    },

    # core - faith
    "shrine": {
        "name": "Shrine",
        "type": "faith",
        "consequences": ["sacrifice"],
        "endeavors": [
            {"name": "Armor Ritual", "cost": 1, "type": "faith"},
        ],
    },
    "scarification": {
        "name": "Scarification",
        "type": "faith",
        "endeavors": [
            {"name": "Initiation", "cost": 1, "type": "faith"},
        ],
    },
    "sacrifice": {
        "name": "Sacrifice",
        "type": "faith",
        "endeavors": [
            {"name": "Death Ritual", "type": "faith", "cost": 1,},
        ],
    },

    # core - education
    "symposium": {
        "name": "Symposium",
        "type": "education",
        "consequences": ["nightmare_training", "storytelling"],
        "survival_limit": 1,
        "settlement_buff": "When a survivor innovates, draw an additional 2 Innovation Cards to choose from.",
    },
    "nightmare_training": {
        "name": "Nightmare Training",
        "type": "education",
        "consequences": ["round_stone_training"],
        "endeavors": [
            {"name": "Train", "cost": 1, "type": "education"},
        ],
    },
    "storytelling": {
        "name": "Storytelling",
        "type": "education",
        "consequences": ["records","war_room"],
        "survival_limit": 1,
        "endeavors": [
            {"name": "Tale as Old as Time", "cost": 2, "type": "education"},
        ],
    },
    "records": {
        "name": "Records",
        "type": "education",
        "endeavors": [
            {"name": "Knowledge", "cost": 2, "type": "education"},
        ],
    },
    "final_fighting_art": {
        "name": "Final Fighting Art",
        "type": "education",
        "survival_limit": 1,
    },

    # core - science
    "ammonia": {
        "name": "Ammonia",
        "type": "science",
        "consequences": ["bloodletting","lantern_oven"],
        "departure_buff": "Departing survivors gain +1 survival.",
    },
    "bloodletting": {
        "name": "Bloodletting",
        "type": "science",
        "endeavors": [
            {"name": "Breathing a Vein", "cost": 1, "type": "science"},
        ],
    },
    "lantern_oven": {
        "name": "Lantern Oven",
        "type": "science",
        "consequences": ["cooking", "scrap_smelting"],
        "departure_buff": "Departing Survivors gain +1 survival.",
    },
    "scrap_smelting": {
        "name": "Scrap Smelting",
        "type": "science",
        "special_innovate": {"locations": ["weapon_crafter"]},
        "endeavors": [
            {"name": "Purification", "cost": 1, "type": "science"},
            {
                "name": "Build",
                "cost": 1,
                "desc": "Blacksmith (6 x bone, 3 x scrap)",
                "remove_after": "blacksmith"
            },
        ],
    },
    "cooking": {
        "name": "Cooking",
        "type": "science",
        "survival_limit": 1,
        "endeavors": [
            {"name": "Culinary Inspiration", "cost": 1, "type": "science"},
        ],
    },
    "ultimate_weapon": {
        "name": "Ultimate Weapon",
        "type": "science",
        "survival_limit": 1,
    },


    # core - muzak
    "drums": {
        "name": "Drums",
        "type": "music",
        "consequences": ["song_of_the_brave", "forbidden_dance"],
        "endeavors": [
            {"name": "Bone Beats", "cost": 1, "type": "music"},
        ],
    },
    "forbidden_dance": {
        "name": "Forbidden Dance",
        "type": "music",
        "consequences": ["petal_spiral", "choreia"],
        "endeavors": [
            {"name": "Fever Dance", "cost": 1, "type": "music"},
        ],
    },
    "song_of_the_brave": {
        "name": "Song of the Brave",
        "type": "music",
        "consequences": ["saga"],
        "survivor_buff": "All non-deaf survivors add +1 to their roll results on the Overwhelming Darkness story event.",
    },
    "saga": {
        "name": "Saga",
        "type": "music",
        "survivor_buff": "All newborn survivors gain +2 hunt experience and +2 survival from knowing the epic.",
        "newborn_survivor": {"hunt_xp": 2, "survival": 2},
    },
    "heart_flute": {
        "name": "Heart Flute",
        "type": "music",
        "endeavors": [
            {"name": "Devil's Melody", "cost": 1, "type": "music"},
        ],
    },

    # core - other
    "guidepost": {
        "name": "Guidepost",
        "type": "other",
        "departure_buff": "Departing survivors gain +1 survival.",
    },


    #
    #   expansion innovations below!
    #

    # Gorm
    "nigredo": {
        "name": "Nigredo",
        "expansion": "gorm",
        "type": "science",
        "survival_limit": 1,
        "consequences": ["albedo"],
        "endeavors": [
            {"name": "Nigredo", "cost": 1, "type": "science"},
        ],
    },
    "albedo": {
        "name": "Albedo",
        "expansion": "gorm",
        "type": "science",
        "consequences": ["citrinitas"],
        "endeavors": [
            {"name": "Albedo", "cost": 2, "type": "science"},
        ],
    },
    "citrinitas": {
        "name": "Citrinitas",
        "expansion": "gorm",
        "type": "science",
        "survival_limit": 1,
        "consequences": ["rubedo"],
        "endeavors": [
            {"name": "Citrinitas", "cost": 3, "type": "science"},
        ],
    },
    "rubedo": {
        "name": "Rubedo",
        "expansion": "gorm",
        "type": "science",
        "endeavors": [
            {"name": "Rubedo", "cost": 4, "type": "science"},
        ],
    },

    # Lion God
    "the_knowledge_worm": {
        "name": "The Knowledge Worm",
        "type": "other",
        "expansion": "lion_god",
        "settlement_buff": 'At the start of each settlement phase, add 1 scrap to settlement storage.<br/><b>Departing Survivors</b> gain +3 survival and +3 insanity. If any of those survivors have 10+ insanity, <font class="kdm_font">g</font> <b>A Gracious Host</b>.',
    },

    # Sunstalker - NB: sun_language and hands_of_the_sun handles are below!
    "aquarobics": {
        "name": "Aquarobics",
        "expansion": "sunstalker",
        "type": "faith",
        "survival_limit": 1,
        "endeavors": [
            {"name": "Underwater Train", "cost": 1, "type": "faith"},
        ],
    },

    "sauna_shrine": {
        "name": "Sauna Shrine",
        "expansion": "sunstalker",
        "type": "faith",
        "endeavors": [
            {"name": "Tribute", "cost": 1, "type": "faith"},
        ],
        "departure_buff": "When survivors <b>depart</b> for a Nemesis Encounter or Special Showdown, they gain +10 survival.",
    },

    "umbilical_bank": {
        "name": "Umbilical Bank",
        "expansion": "sunstalker",
        "consequences": ["pottery"],
        "type": "science",
        "settlement_buff": "When a survivor is born, you may add 1 <b>Life String</b> strange resource to storage.",
        "endeavors": [
            {
                "name": '<font class="kdm_font">g</font> Umbilical Symbiosis',
                "cost": 1,
                "type": "science"
            },
            {
                "name": "Special Innovate",
                "cost": 1,
                "desc": "Pottery (3 x organ)",
                "remove_after": "pottery"
            },
        ],
    },

    "filleting_table": {
        "name": "Filleting Table",
        "expansion": "sunstalker",
        "type": "science",
        "settlement_buff": "Once per settlement phase, if the <b>returning survivors</b> are victorious, gain 1 random basic resource.",
        "endeavors": [
            {"name": "Advanced Cutting", "cost": 1, "type": "science"},
        ],
    },

    "shadow_dancing": {
        "name": "Shadow Dancing",
        "expansion": "sunstalker",
        "type": "home",
        "endeavors": [
            {"name": "Final Dance", "cost": 1, "type": "home"},
        ],
    },

    # DBK
    "subterranean_agriculture": {
        "name": "Subterranean Agriculture",
        "expansion": "dung_beetle_knight",
        "type": "science",
        "endeavors": [
            {
                "cost": 1,
                "desc": "Wet Resin Crafter (2 x organ, 2 x bone)",
                "remove_after": "wet_resin_crafter"
            },
            {
                "name": "Underground Sow",
                "type": "science",
                "desc": 'If <b>Black Harvest</b> is not on the timeline, <font class="kdm_font">g</font> <b>Underground Sow</b>.',
                "cost": 1
            },
            {
                "name": "Underground Fertilize",
                "type": "science",
                "desc": 'If <b>Black Harvest</b> is on the timeline, you may spend 1 Preserved Caustic Dung to increase its rank by 1 to a maximum rank of 3. Limit, once per settlement phase.',
                "cost": 1,
            },
        ],
    },
    "round_stone_training": {
        "name": "Round Stone Training",
        "expansion": "dung_beetle_knight",
        "type": "education",
        "endeavors": [
            {"name": "Train", "cost": 1, "type": "education"},
        ],
    },

    # Flower Knight
    "petal_spiral": {
        "name": "Petal Spiral",
        "type": "music",
        "expansion": "flower_knight",
        "endeavors": [
            {"name": "Trace Petals", "cost": 1, "type": "music"},
        ],
    },

    # Lion Knight
    "stoic_statue": {
        "name": "Stoic Statue",
        "consequences": ["black_mask", "white_mask"],
        "expansion": "lion_knight",
        "type": "other",
        "endeavors": [
            {"name": "Worship the monster", "cost": 1, "type": "other"},
        ],
    },
    "black_mask": {
        "name": "Black Mask",
        "consequences": ["white_mask"],
        "expansion": "lion_knight",
        "type": "other",
        "endeavors": [
            {"name": "Visit the retinue", "cost": 1, "type": "other"},
            {"name": "Face the monster", "cost": 2, "type": "other"},
        ],
    },
    "white_mask": {
        "name": "White Mask",
        "consequences": ["black_mask"],
        "expansion": "lion_knight",
        "type": "other",
        "endeavors": [
            {"name": "Visit the retinue", "cost": 1, "type": "other"},
            {"name": "Leave the monster an offering", "cost": 1, "type": "other"},
        ],
    },


    # Manhunter
    "settlement_watch": {
        "name": "Settlement Watch",
        "type": "home",
        "expansion": "manhunter",
        "survivor_buff": "<b>Departing Survivors</b> gain +2 survival when they depart for a Nemesis Encounter or a Special Showdown.",
        "endeavors": [
            {"name": "New Recruits", "cost": 1, "type": "home"},
        ],
        "available_if": [
            ("Manhunter Lvl 1","defeated_monsters"),
            ("Manhunter Lvl 2","defeated_monsters"),
        ],
    },
    "war_room": {
        "name": "War Room",
        "type": "education",
        "expansion": "manhunter",
        "survival_limit": 1,
        "endeavors": [
            {
                "name": "Hunt Plan",
                "type": "education",
                "desc": 'The hunt team makes a plan. The group may reroll 1 <b>Hunt Event Table</b> result (d100) this lantern year. They must reroll before performing the event.',
                "cost": 1
            },
        ],
    },
    "crimson_candy": {
        "name": "Crimson Candy",
        "type": "science",
        "expansion": "manhunter",
        "survivor_buff": "At the start of the showdown, each survivor gains &#9733; survival.",
        "endeavors": [
            {"name": "Crimson Cannibalism", "cost": 1, "type": "science"},
        ],
    },


    # Spidicules
    "choreia": {
        "name": "Choreia",
        "type": "music",
        "expansion": "spidicules",
        "endeavors": [
            {
                "name": "Spider Dance",
                "cost": 1,
                "type": "music",
                "desc": "Nominate a male and a female survivor and roll 1d10."
            },
        ],
    },

    "silk_refining": {
        "name": "Silk-Refining",
        "expansion": "spidicules",
        "type": "other",
        "survival_limit": 1,
        "endeavors": [
            {
                "type": "other",
                "desc": '<font class="kdm_font">g</font> <b>Silk Surgery</b>.',
                "cost": 1,
            },
            {
                "type": "other",
                "desc": 'Convert 1 silk resource into 1 hide basic resource.',
                "cost": 1,
            },
            {
                "type": "other",
                "desc": 'Spend 2 silk, 1 bone, and 1 organ to build the <b>Silk Mill</b> settlement location.',
                "cost": 1,
                "remove_after": "silk_mill",
            },
        ],
    },

    "legless_ball": {
        "name": "Legless Ball",
        "expansion": "spidicules",
        "type": "other",
        "survivor_buff": '<b>Departing survivors</b> gain +2 insanity.',
        "subhead": 'Spend only 1 <font class="kdm_font">d</font> here per settlement phase.',
        "endeavors": [
            {
                "type": "other",
                "cost": 1,
                "desc": 'Add 1 <b>Web Silk</b> strange resource to settlement storage.',
            },
            {
                "type": "other",
                "cost": 1,
                "desc": 'A survivor with 10+ insanity may put the Spidicules out of its misery. Gain the <b>Grinning Visage</b> rare gear and lose this innovation. (Archive this card.)',
            },
        ],
    },


    # Slenderman
    "dark_water_research": {
        "name": "Dark Water Research",
        "type": "science",
        "expansion": "slenderman",
        "levels": 3,
        "endeavors": [
            {"cost": 2, "name": '<font class="kdm_font">g</font> Light-Forging'},
            {
                "cost": 1,
                "desc": 'Spend 2x resources and 2x Dark Water to increase the level of <b>Dark Water Research</b> by 1, to a maximum of 3. (Update your settlement record sheet.)',
            },
        ],
    },

    # Dragon King
    "arena": {
        "name": "Arena",
        "type": "education",
        "expansion": "dragon_king",
        "endeavors": [
            {"name": "Spar", "cost": 1, "type": "education"},
        ],
    },

    "empire": {
        "name": "Empire",
        "type": "home",
        "expansion": "dragon_king",
        "survivor_buff": 'Newborn survivors are born with +1 permanent strength and the <font class="maroon_text">Pristine</font> ability.',
        "newborn_survivor": {
            "Strength": 1,
            "abilities_and_impairments": ["Pristine"],
        },
    },

    "bloodline": {
        "name": "Bloodline",
        "type": "home",
        "expansion": "dragon_king",
        "consequences": ["empire"],
        "survivor_buff": """Newborn survivors inherit the following from their parents:<ul><li>The <font class="maroon_text">Oracle's Eye</font>, <font class="maroon_text">Iridescent Hide</font>, or <font class="maroon_text">Pristine</font> ability (choose 1)</li><li>1 <b>Surname</b></li><li>Half of one parent's weapon proficiency levels (rounded up)</li></ul>""",
    },

    "radiating_orb": {
        "name": "Radiating Orb",
        "type": "science",
        "expansion": "dragon_king",
        "settlement_buff": "<b>Departing Survivors</b> and newborn survivors gain +1 survival.<br/><b>Departing survivors</b> with a constellation gain +1 survival.",
        "consequences": ["cooking","scrap_smelting"],
        "newborn_survivor": {"survival": 1},
    },




    #
    #    principles - keep this at the end of the dict
    #

    "graves" : {
        "name": "Graves",
        "principle": "death",
        "settlement_buff": 'All new survivors gain +1 understanding.<br/>When a survivor dies during the hunt or showdown phase, gain +2 <font class="kdm_font">d</font>.<br/>When a survivor dies during the settlement phase, gain +1 <font class="kdm_font">d</font>.',
        "survivor_buff": "All new survivors gain +1 understanding.",
        "new_survivor": {"Understanding": 1},
    },
    "cannibalize": {
        "name": "Cannibalize",
        "principle": "death",
        "survival_limit": 1,
        "settlement_buff": "Whenever a survivor dies, draw one basic resource and add it to the settlement storage.",
    },
    "protect_the_young": {
        "name": "Protect the Young",
        "principle": "new_life",
        "settlement_buff": "When rolling on the Intimacy story event, roll twice and pick one result.",
    },
    "survival_of_the_fittest": {
        "name": "Survival of the Fittest",
        "principle": "new_life",
        "survival_limit": 1,
        "settlement_buff": "When rolling on the Intimacy story event, roll twice and pick the lowest result. All current and newborn survivors gain +1 strength and evasion.<br/>Once per lifetime, a survivor may reroll a single roll result. They must keep this new result.",
        "survivor_buff": "All current and newborn survivors gain +1 strength and evasion.",
        "current_survivor": {"Strength": 1, "Evasion": 1},
        "newborn_survivor": {"Strength": 1, "Evasion": 1},
    },
    "collective_toil": {
        "name": "Collective Toil",
        "principle": "society",
        "settlement_buff": "At the start of the settlement phase, gain +1 Endeavor for every 10 population.",
    },
    "accept_darkness": {
        "name": "Accept Darkness",
        "principle": "society",
        "survivor_buff": "Add +2 to all Brain Trauma Rolls.",
    },
    "romantic": {
        "name": "Romantic",
        "principle": "conviction",
        "survival_limit": 1,
        "settlement_buff": "You may innovate one additional time during the settlement phase. In addition, all current and newborn survivors gain +1 understanding.",
        "survivor_buff": "All current and newborn survivors gain +1 understanding.",
        "living_survivor": {"Understanding": 1},
        "newborn_survivor": {"Understanding": 1},
    },
    "barbaric": {
        "name": "Barbaric",
        "principle": "conviction",
        "survival_limit": 1,
        "survivor_buff": "All current and newborn survivors gain +1 permanent Strength.",
        "living_survivor": {"Strength": 1},
        "newborn_survivor": {"Strength": 1},
    },
}


principles = {
    "new_life": {
        "name": "New Life",
        "handle": "new_life",
        "sort_order": 0,
        "milestone": "First child is born",
        "show_controls": ['"First child is born" in self.settlement["milestone_story_events"]'],
        "option_handles": ["protect_the_young", "survival_of_the_fittest"],
    },
    "potsun_new_life": {
        "name": "New Life",
        "handle": "potsun_new_life",
        "sort_order": 0,
        "show_controls": ["True"],
        "option_handles": ["survival_of_the_fittest"],
    },
    "death": {
        "name": "Death",
        "handle": "death",
        "sort_order": 1,
        "milestone": "First time death count is updated",
        "show_controls": ['int(self.settlement["death_count"]) >= 1'],
        "option_handles": ["graves", "cannibalize"],
    },
    "society": {
        "name": "Society",
        "handle": "society",
        "sort_order": 2,
        "milestone": "Population reaches 15",
        "options": ["Collective Toil","Accept Darkness"],
        "show_controls": ['int(self.settlement["population"]) >= 15'],
        "option_handles": ["accept_darkness", "collective_toil"],
    },
    "conviction": {
        "name": "Conviction",
        "handle": "conviction",
        "sort_order": 3,
        "options": ["Barbaric","Romantic"],
        "show_controls": ['int(self.settlement["lantern_year"]) >= 12'],
        "option_handles": ["romantic", "barbaric"],
    },
}

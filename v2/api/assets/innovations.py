#!/usr/bin/python


innovation = {
    #
    #   Innovations including a survival action unlock
    #

    # core
    "inner_lantern": {
        "name": "Inner Lantern",
        "innovation_type": "faith",
        "consequences": ["shrine", "scarification"],
        "survival_action": "surge",
    },
    "paint": {
        "name": "Paint",
        "innovation_type": "art",
        "consequences": ["pictograph","sculpture","face_painting"],
        "survival_action": "dash",
    },
    "language": {
        "name": "Language",
        "innovation_type": "starting innovation",
        "consequences": ["hovel","inner_lantern","drums","paint","symposium","ammonia"],
        "survival_limit": 1,
        "survival_action": "encourage",
    },



    #
    #   core game innovations start here
    #

    # core - art
    "sculpture": {
        "name": "Sculpture",
        "innovation_type": "art",
        "consequences": ["pottery"],
#        "survival_limit": 1,
#        "departure_buff": "Departing survivors gain +2 survival when they depart for a Nemesis Encounter.",
        "departing_survival_bonus": {"nemesis": 2,},
        "endeavors": ['sculpture_0', 'sculpture_1'],
    },
    "pottery": {
        "name": "Pottery",
        "innovation_type": "art",
        "survival_limit": 1,
#        "settlement_buff": "If the settlement loses all its resources, you may select up to two resources and keep them.",
        "endeavors": ['pottery_fermentation', 'pottery_ret'],
    },
    "face_painting": {
        "name": "Face Painting",
        "innovation_type": "art",
        "endeavors": ['face_painting_battle_paint', 'face_painting_founders_eye'],
    },
    "pictograph": {
        "name": "Pictograph",
        "innovation_type": "art",
        "consequences": ["memento_mori"],
#        "survivor_buff": 'At the start of a standing survivor\'s act, they may trigger the <font class=kdm_font>g</font> <b>Run Away</b> story event. Limit, once per act.',
        "survivor_buff": "At the start of a standing survivor's act, they may decide to skip their act and <font class=kdm_font>g</font> <b>Run Away</b>.<br/>After a hunt is resolved, a survivor may decide it's time to go home and <font class=kdm_font>g</font> <b>Run Away</b>.",
    },
    "memento_mori": {
        "name": "Momento Mori",
        "innovation_type": "art",
        "endeavors": ['momento_mori_default'],
    },

    # core - home
    "hovel": {
        "name": "Hovel",
        "innovation_type": "home",
        "consequences": ["partnership","family","bed","shadow_dancing","bloodline","settlement_watch"],
        "departure_buff": "Departing survivors gain +1 survival.",
        "departing_survival_bonus": {"general": 1},
        "survival_limit": 1,
        'desc': 'The settlement accepts this nightmarish landscape as their home.<br/><b>Departing survivors</b> gain +1 survival.',
    },
    "partnership": {
        "name": "Partnership",
        "innovation_type": "home",
        "endeavors": ['partnership_default'],
    },
    "bed": {
        "name": "Bed",
        "innovation_type": "home",
        "survival_limit": 1,
        "endeavors": ['bed_rest'],
    },
    "family": {
        "name": "Family",
        "desc": '<b>Departing survivors</b> gain +1 survival.<br/>Survivors nominated for <b>Intimacy</b> may give themselves a surname if they do not have one.<br/>A newborn survivor inherits the surname of one parent, their weapon type and half (rounded down) of their weapon proficiency levels.',
        "departing_survival_bonus": {
            "general": 1,
        },
        "innovation_type": "home",
        "consequences": ["clan_of_death"],
        "departure_buff": "Departing survivors gain +1 survival.",
        "settlement_buff": "Survivors nominated for intimacy may give themselves a surname if they do not have one. A newborn survivor inherits the surname of one parent, their weapon type and half (rounded down) of their weapon proficiency levels.",
        "primary_donor_parent": {
            "attributes": ['weapon_proficiency_type'],
            "specials": ["surname","one_half_weapon_proficiency"],
        },
    },
    "clan_of_death": {
        "name": "Clan of Death",
        "innovation_type": "home",
        "survivor_buff": "All newborn survivors gain <b>+1 Accuracy</b>, <b>+1 Strength</b> and <b>+1 Evasion</b>.",
        "newborn_survivor": {"Strength": 1, "Accuracy": 1, "Evasion": 1},
    },

    # core - faith
    "shrine": {
        "name": "Shrine",
        "innovation_type": "faith",
        "consequences": ["sacrifice"],
        "endeavors": ['shrine_armor_ritual'],
    },
    "scarification": {
        "name": "Scarification",
        "innovation_type": "faith",
        "endeavors": ['scarification_initiation'],
    },
    "sacrifice": {
        "name": "Sacrifice",
        "innovation_type": "faith",
        "endeavors": ['sacrifice_death_ritual'],
    },
    "destiny": {
        "name": "Destiny",
        "innovation_type": "faith",
#        "desc": "The settlement's future is unavoidable. All survivors gain the <b>endure</b> survival action.",
        "survival_action": "endure",
        'survival_limit': 1,
        "available_if": [
            ("Watcher","defeated_monsters"),
        ],
},

    # core - education
    "symposium": {
        "name": "Symposium",
        "innovation_type": "education",
        "consequences": ["nightmare_training", "storytelling"],
        "survival_limit": 1,
        "settlement_buff": "When a survivor innovates, draw an additional 2 Innovation Cards to choose from.",
    },
    "nightmare_training": {
        "name": "Nightmare Training",
        "innovation_type": "education",
        "consequences": ["round_stone_training"],
        "endeavors": ['nightmare_training_train'],
    },
    "storytelling": {
        "name": "Storytelling",
        "innovation_type": "education",
        "consequences": ["records","war_room"],
        "survival_limit": 1,
        "endeavors": ['storytelling_story_time'],
    },
    "records": {
        "name": "Records",
        "innovation_type": "education",
        "endeavors": ['records_0_scholar_of_death', 'records_1_monster_volume'],
    },
    "final_fighting_art": {
        "name": "Final Fighting Art",
        "innovation_type": "education",
        "survival_limit": 1,
    },

    # core - science
    "ammonia": {
        "name": "Ammonia",
        "innovation_type": "science",
        'desc': 'A pungent, bilious substance ideal for crafting leather and treating wounds.<br/><b>Departing survivors</b> gain +1 survival.',
        "departing_survival_bonus": {"general": 1,},
        "consequences": ["bloodletting","lantern_oven"],
        "departure_buff": "Departing survivors gain +1 survival.",
    },
    "bloodletting": {
        "name": "Bloodletting",
        "innovation_type": "science",
        "endeavors": ['bloodletting_breathing_a_vein'],
    },
    "lantern_oven": {
        "name": "Lantern Oven",
        "innovation_type": "science",
        'desc': 'By agitating lanterns, a source of <b>Heat</b> becomes available to the settlement.<br/><b>Departing survivors</b> gain +1 survival.',
        "departing_survival_bonus": {"general": 1,},
        "consequences": ["cooking", "scrap_smelting"],
        "departure_buff": "Departing Survivors gain +1 survival.",
    },
    "scrap_smelting": {
        "name": "Scrap Smelting",
        "innovation_type": "science",
        "special_innovate": {"locations": ["weapon_crafter"]},
        "endeavors": ['scrap_smelting_purification', 'scrap_smelting_build_blacksmith'],
    },
    "cooking": {
        "name": "Cooking",
        "innovation_type": "science",
        "survival_limit": 1,
        "settlement_buff": '+1 <font class="kdm_font">d</font> (At the start of the Settlement Phase, gain +1 endeavor.)',
        "endeavors": ['cooking_default', 'cooking_stone_nose_gruel'],
    },
    "ultimate_weapon": {
        "name": "Ultimate Weapon",
        "innovation_type": "science",
        "survival_limit": 1,
    },


    # core - muzak
    "drums": {
        "name": "Drums",
        "innovation_type": "music",
        "consequences": ["song_of_the_brave", "forbidden_dance"],
        "endeavors": ['drums_bone_beats'],
    },
    "forbidden_dance": {
        "name": "Forbidden Dance",
        "innovation_type": "music",
        "consequences": ["petal_spiral", "choreia","heart_flute"],
        "survivor_buff": "When a survivor uses the <b>Synchronized Strike</b> secret fighting art, reroll missed attack rolls once.",
        "endeavors": ['forbidden_dance_default'],
    },
    "song_of_the_brave": {
        "name": "Song of the Brave",
        "innovation_type": "music",
        "consequences": ["saga"],
#        "survivor_buff": "All non-deaf survivors add +1 to their roll results on the Overwhelming Darkness story event.",
        "survivor_buff": "The survivors life their voices into the darkness. On <b>arrival</b>, each non-deaf survivor may remove 1 negative attribute token.<br/>During the <b>Overwhelming Darkness</b> story event, each non-deaf survivor may select the Path fo the Brave.",
    },
    "saga": {
        "name": "Saga",
        "innovation_type": "music",
#        "survivor_buff": "All newborn survivors gain +2 hunt experience and +2 survival from knowing the epic.",
        'settlement_buff': "A telling of the settlement's survival set to a soft rhythmic beating of drums.<br/>All newborn survivors gain: +2 Courage, +2 Understanding, +2 Hunt XP.",
#        "newborn_survivor": {"hunt_xp": 2, "survival": 2},
        "newborn_survivor": {"hunt_xp": 2, "Courage": 2, "Understanding": 2},
    },
    "heart_flute": {
        "name": "Heart Flute",
        "innovation_type": "music",
        'survivor_buff': 'When a survivor uses the <b>Synchronized Strike</b> fighting art, their <font class="kdm_pink_font">attack assist</font> may spend 1 survival to change any monster <font class="kdm_font">e</font> to a <font class="kdm_font">e</font> <b>FAILURE</b> before any wound attempts are made. Limit, once per attack.',
        "endeavors": ['heart_flute_devils_melody']
    },

    # core - other
    "guidepost": {
        "name": "Guidepost",
        "innovation_type": "other",
        "departing_survival_bonus": {"general": 1,},
        "departure_buff": "Departing survivors gain +1 survival.",
        'endeavors': ['guidepost_default'],
        'desc': 'The soft glow of its light fills the survivors with a sense of security. <b>Departing survivors</b> gain +1 survival.<br/><font class="kdm_font_10">d</font>: The survivor attempts to pull the weapon free from the ground. Roll 1d10 and add their strength. If the result is 12+, gain the <b>Lantern Halberd</b> rare gear and lose this innovation (Archive this card).',
    },


    #
    #    principles - keep this at the end of the dict
    #

    "graves" : {
        "name": "Graves",
        'type': 'principle',
        "principle": "death",
        "settlement_buff": 'All new survivors gain +1 understanding.<br/>When a survivor dies during the hunt or showdown phase, gain +2 <font class="kdm_font">d</font>.<br/>When a survivor dies during the settlement phase, gain +1 <font class="kdm_font">d</font>.',
        "survivor_buff": "All new survivors gain +1 understanding.",
        "new_survivor": {"Understanding": 1},
    },
    "cannibalize": {
        "name": "Cannibalize",
        'type': 'principle',
        "principle": "death",
        "survival_limit": 1,
#        "settlement_buff": "Whenever a survivor dies, draw one basic resource and add it to the settlement storage.",
        "settlement_buff": "Whenever a survivor dies, draw 1 basic resource and add it to the settlement storage. Do not gain a resource if a survivor is lost, ceases to exist, or is exiled.",
    },
    "protect_the_young": {
        "name": "Protect the Young",
        'type': 'principle',
        "principle": "new_life",
        "settlement_buff": "When rolling on the Intimacy story event, roll twice and pick one result.",
    },
    "survival_of_the_fittest": {
        "name": "Survival of the Fittest",
        'type': 'principle',
        "principle": "new_life",
        "survival_limit": 1,
        "settlement_buff": "When rolling on the Intimacy story event, roll twice and pick the lowest result. All current and newborn survivors gain +1 strength and evasion.<br/>Once per lifetime, a survivor may reroll a single roll result. They must keep this new result.",
#        "survivor_buff": "All current and newborn survivors gain +1 strength and evasion.",
        "current_survivor": {"Strength": 1, "Evasion": 1},
        "newborn_survivor": {"Strength": 1, "Evasion": 1},
    },
    "collective_toil": {
        "name": "Collective Toil",
        'type': 'principle',
        "principle": "society",
        "settlement_buff": "At the start of the settlement phase, gain +1 Endeavor for every 10 population.",
    },
    "accept_darkness": {
        "name": "Accept Darkness",
        'type': 'principle',
        "principle": "society",
        "survivor_buff": "Add +2 to all Brain Trauma Rolls.",
    },
    "romantic": {
        "name": "Romantic",
        'type': 'principle',
        "principle": "conviction",
        "survival_limit": 1,
#        "settlement_buff": "You may innovate one additional time during the settlement phase. In addition, all current and newborn survivors gain +1 understanding.",
#        "survivor_buff": "All current and newborn survivors gain +1 understanding.",
#        "current_survivor": {"Understanding": 1},
#        "newborn_survivor": {"Understanding": 1},
        "survivor_buff": "When you gain a random fighting art, draw 3 fighting art cards and select 1 to keep.",
    },
    "barbaric": {
        "name": "Barbaric",
        'type': 'principle',
        "principle": "conviction",
        "survival_limit": 1,
        "survivor_buff": "All current and newborn survivors gain +1 permanent Strength.",
        "current_survivor": {"Strength": 1},
        "newborn_survivor": {"Strength": 1},
    },
}

expansion = {
    "dragon_speech": {
        "name": "Dragon Speech",
        "innovation_type": "starting innovation",
        "expansion": "dragon_king",
        "survival_limit": 1,
        "survival_action": "encourage",
        "consequences": ["hovel", "inner_lantern","drums","paint","symposium","ammonia"],
    },
    "sun_language": {
        "name": "Sun Language",
        "expansion": "sunstalker",
        "innovation_type": "starting innovation",
        "survival_limit": 1,
        "survival_action": "embolden",
        "consequences": ["ammonia","drums","hovel","paint","symposium","hands_of_the_sun"],
    },
    "hands_of_the_sun": {
        "name": "Hands of the Sun",
        "expansion": "sunstalker",
        "innovation_type": "faith",
        "survival_action": "overcharge",
        "consequences": ["aquarobics", "sauna_shrine"],
    },
    # Gorm
    "nigredo": {
        "name": "Nigredo",
        "expansion": "gorm",
        "innovation_type": "science",
        "survival_limit": 1,
        "consequences": ["albedo"],
        "endeavors": ['gorm_nigredo'],
    },
    "albedo": {
        "name": "Albedo",
        "expansion": "gorm",
        "innovation_type": "science",
        "consequences": ["citrinitas"],
        "endeavors": ['gorm_albedo'],
    },
    "citrinitas": {
        "name": "Citrinitas",
        "expansion": "gorm",
        "innovation_type": "science",
        "survival_limit": 1,
        "consequences": ["rubedo"],
        "endeavors": ['gorm_citrinitas'],
    },
    "rubedo": {
        "name": "Rubedo",
        "expansion": "gorm",
        "innovation_type": "science",
        "endeavors": ['gorm_rubedo'],
    },

    # Lion God
    "the_knowledge_worm": {
        "name": "The Knowledge Worm",
        "innovation_type": "other",
        "expansion": "lion_god",
        "settlement_buff": 'At the start of each settlement phase, add 1 scrap to settlement storage.<br/><b>Departing Survivors</b> gain +3 survival and +3 insanity. If any of those survivors have 10+ insanity, <font class="kdm_font">g</font> <b>A Gracious Host</b>.',
        "desc": 'At the start of each settlement phase, add 1 scrap to settlement storage.<br/><b>Departing Survivors</b> gain +3 survival and +3 insanity. If any of those survivors have 10+ insanity, <font class="kdm_font">g</font> <b>A Gracious Host</b>.',
        'departing_survival_bonus': {'general': 3},
    },

    # Sunstalker - NB: sun_language and hands_of_the_sun handles are below!
    "aquarobics": {
        "name": "Aquarobics",
        "expansion": "sunstalker",
        "innovation_type": "faith",
        "survival_limit": 1,
        "endeavors": ['aquarobics_underwater_train'],
    },

    "sauna_shrine": {
        "name": "Sauna Shrine",
        "expansion": "sunstalker",
        "innovation_type": "faith",
        "endeavors": ['sauna_shrine_tribute'],
        "departure_buff": "When survivors <b>depart</b> for a Nemesis Encounter or Special Showdown, they gain +10 survival.",
        "desc": "When survivors <b>depart</b> for a Nemesis Encounter or Special Showdown, they gain +10 survival.",
        'departing_survival_bonus': {'nemesis': 10, 'special': 10,}
    },

    "umbilical_bank": {
        "name": "Umbilical Bank",
        "expansion": "sunstalker",
        "consequences": ["pottery"],
        "innovation_type": "science",
        "settlement_buff": "When a survivor is born, you may add 1 <b>Life String</b> strange resource to storage.",
        "endeavors": ['umbilical_bank_umbilical_symbiosis','umbilical_bank_special_innovate_pottery'],
    },

    "filleting_table": {
        "name": "Filleting Table",
        "expansion": "sunstalker",
        "innovation_type": "science",
        "settlement_buff": "Once per settlement phase, if the <b>returning survivors</b> are victorious, gain 1 random basic resource.",
        "endeavors": ['filleting_table_advanced_cutting'],
    },

    "shadow_dancing": {
        "name": "Shadow Dancing",
        "expansion": "sunstalker",
        "innovation_type": "home",
        "endeavors": ['shadow_dancing_final_dance'],
    },

    # DBK
    "subterranean_agriculture": {
        "name": "Subterranean Agriculture",
        "expansion": "dung_beetle_knight",
        "innovation_type": "science",
        "endeavors": [
            'subterranean_agriculture_0',
            'subterranean_agriculture_1',
            'subterranean_agriculture_2_build_wet_resin_crafter',
        ],
    },
    "round_stone_training": {
        "name": "Round Stone Training",
        "expansion": "dung_beetle_knight",
        "innovation_type": "education",
        "endeavors": ['round_stone_training_train'],
    },

    # Flower Knight
    "petal_spiral": {
        "name": "Petal Spiral",
        "innovation_type": "music",
        "expansion": "flower_knight",
        "endeavors": ['petal_spiral_trace_petals'],
    },

    # Lion Knight
    "stoic_statue": {
        "name": "Stoic Statue",
        "consequences": ["black_mask", "white_mask"],
        "expansion": "lion_knight",
        "innovation_type": "other",
        "endeavors": ['stoic_statue_worship_the_monster'],
    },
    "black_mask": {
        "name": "Black Mask",
        "consequences": ["white_mask"],
        "expansion": "lion_knight",
        "innovation_type": "other",
        "endeavors": ['lion_knight_black_mask_face_the_monster','lion_knight_0_visit_the_retinue'],
    },
    "white_mask": {
        "name": "White Mask",
        "consequences": ["black_mask"],
        "expansion": "lion_knight",
        "innovation_type": "other",
        "endeavors": ['lion_knight_0_visit_the_retinue','lion_knight_white_mask_leave_the_monster'],
    },


    # Manhunter
    "settlement_watch": {
        "name": "Settlement Watch",
        "innovation_type": "home",
        "expansion": "manhunter",
        "survivor_buff": "<b>Departing Survivors</b> gain +2 survival when they depart for a Nemesis Encounter or a Special Showdown.",
        "endeavors": ['settlement_watch_new_recruits'],
        "available_if": [
            ("Manhunter Lvl 1","defeated_monsters"),
            ("Manhunter Lvl 2","defeated_monsters"),
        ],
        "desc": "<b>Departing Survivors</b> gain +2 survival when they depart for a Nemesis Encounter or a Special Showdown.",
        'departing_survival_bonus': {'nemesis': 2, 'special': 2},
    },
    "war_room": {
        "name": "War Room",
        "innovation_type": "education",
        "expansion": "manhunter",
        "survival_limit": 1,
        'settlement_buff': "Quarries cannot move off of the hunt board. If the survivors would move backwards on the hunt board, roll 1d10. On a 4+ they don't.",
        "endeavors": ['war_room_default'],
    },
    "crimson_candy": {
        "name": "Crimson Candy",
        "innovation_type": "science",
        "expansion": "manhunter",
        "survivor_buff": "At the start of the showdown, each survivor gains &#9733; survival.",
        "endeavors": ['crimson_candy_crimson_cannibalism'],
    },


    # Spidicules
    "choreia": {
        "name": "Choreia",
        "innovation_type": "music",
        "expansion": "spidicules",
        "endeavors": ['choreia_spider_dance'],
    },

    "silk_refining": {
        "name": "Silk-Refining",
        "expansion": "spidicules",
        "innovation_type": "other",
        "survival_limit": 1,
        "endeavors": ['silk_refining_0','silk_refining_1','silk_refining_2'],
    },

    "legless_ball": {
        "name": "Legless Ball",
        "expansion": "spidicules",
        "innovation_type": "other",
        "survivor_buff": '<b>Departing survivors</b> gain +2 insanity.',
        "subhead": 'Spend only 1 <font class="kdm_font">d</font> here per settlement phase.',
        "endeavors": ['legless_ball_0','legless_ball_1'],
    },


    # Slenderman
    "dark_water_research": {
        "name": "Dark Water Research",
        "innovation_type": "science",
        "expansion": "slenderman",
        "levels": 3,
        "endeavors": ['dark_water_research_0', 'dark_water_research_1'],
    },

    # Dragon King
    "arena": {
        "name": "Arena",
        "innovation_type": "education",
        "expansion": "dragon_king",
        "endeavors": ['arena_spar'],
    },

    "empire": {
        "name": "Empire",
        "innovation_type": "home",
        "expansion": "dragon_king",
        "survivor_buff": 'Newborn survivors are born with +1 permanent strength and the <font class="maroon_text">Pristine</font> ability.',
        "newborn_survivor": {
            "Strength": 1,
            "abilities_and_impairments": ["Pristine"],
        },
    },

    "bloodline": {
        "name": "Bloodline",
        "innovation_type": "home",
        "expansion": "dragon_king",
        "consequences": ["empire"],
        "survivor_buff": """Newborn survivors inherit the following from their parents:<ul><li>The <font class="maroon_text">Oracle's Eye</font>, <font class="maroon_text">Iridescent Hide</font>, or <font class="maroon_text">Pristine</font> ability (choose 1)</li><li>1 <b>Surname</b></li><li>Half of one parent's weapon proficiency levels (rounded up)</li></ul>""",
    },

    "radiating_orb": {
        "name": "Radiating Orb",
        "innovation_type": "science",
        "expansion": "dragon_king",
        "settlement_buff": "<b>Departing Survivors</b> and newborn survivors gain +1 survival.<br/><b>Departing survivors</b> with a constellation gain +1 survival.",
        "consequences": ["cooking","scrap_smelting"],
        "newborn_survivor": {"survival": 1},
        "desc": "<b>Departing Survivors</b> and newborn survivors gain +1 survival.<br/><b>Departing survivors</b> with a constellation gain +1 survival.",
        'departing_survival_bonus': {'all': 1,},
    },
}


ui_prompts = {
    'retired': {'name': 'Retired', 'desc': 'Retired survivors cannot depart, but still contribute to the total population of the settlement, and may participate in settlement events and endeavors.'},
    'max_courage': {'name': 'Max Courage', 'desc': 'The maximum value a survivor may have for this attribute is nine.'},
    'max_understanding': {'name': 'Max Understanding', 'desc': 'The maximum value a survivor may have for this attribute is nine.'},
    'max_weapon_proficiency': {'name': 'Max Weapon Proficiency', 'desc': 'The maximum value a survivor may have for this attribute is nine.'},
}

settlement_event = {

    "core_acid_storm": {
        "name": "Acid Storm",
        'endeavors': ['acid_storm_exercise','acid_storm_distillation'],
    },
    "core_clinging_mist": {"name": "Clinging Mist"},
    "core_cracks_in_the_ground": {
        "name": "Cracks in the Ground",
        'endeavors': ['vapor_visions','vapor_scar'],
    },
    "core_dark_dentist": {"name": "Dark Dentist"},
    "core_dark_trader": {"name": "Dark Trader"},
    "core_elder_council": {"name": "Elder Council"},
    "core_glossolalia": {
        "name": "Glossolalia",
        'endeavors': ['automatic_writing', 'deep_listen'],
    },
    "core_haunted": {"name": "Haunted"},
    "core_heat_wave": {
        "name": "Heat Wave",
        'endeavors': ['find_fluid','breathe_fumes'],
    },
    "core_lights_in_the_sky": {
        "name": "Lights in the Sky",
        'endeavors': [
            'lights_in_the_sky_01',
            'lights_in_the_sky_02',
            'lights_in_the_sky_03',
        ],
    },
    "core_first_day": {"name": "First Day"},
    "core_hunt_reenactment": {"name": "Hunt Reenactment"},
    "core_murder": {"name": "Murder"},
    "core_nickname": {"name": "Nickname", 'endeavors': ['rename'],},
    "core_open_maw": {"name": "Open Maw", 'endeavors': ['brave_the_maw'],},
    "core_plague": {"name": "Plague", 'endeavors': ['treatment'], },
    "core_rivalry": {"name": "Rivalry", 'endeavors': ['duel'],},
    "core_skull_eater": {"name": "Skull Eater"},
    "core_stranger_in_the_dark": {"name": "Stranger in the Dark"},
    "core_triathalon_of_death": {"name": "Triathalon of Death"},
    "core_weird_dream": {"name": "Weird Dream"},

    # gorm
    "gorm_gorm_climate": {"name": "Gorm Climate", "expansion": "gorm"},

    # promo/white box
    "promo_strange_spot": {"name": "A Strange Spot", "expansion": "white_box"},
    "promo_story_in_the_snow": {"name": "Story in the Snow", "expansion": "white_box"},

    # spidicules
    "spid_season_of_the_spiderling": {"name": "Season of the Spiderling", "expansion": "spidicules"},
    "spid_silk_storm": {
        "name": "Silk Storm", "expansion": "spidicules",
        'endeavors': ['talk_to_legless_ball', 'silk_diet'],
    },

    # slenderman
    "slender_phantom": {"name": "Phantom", "expansion": "slenderman"},
    "slender_slender_blight": {"name": "Slender Blight", "expansion": "slenderman"},

}

story_event = {

    "core_age": {"name": "Age", "page":107,},
    "core_armored_strangers": {"name": "Armored Strangers", "page": 109, },
    "core_birth_of_a_savior": {"name": "Birth of a Savior", "page":111,},
    "core_bold": {"name": "Bold", "page": 113, },
    "core_bone_witch": {"name": "Bone Witch", "page": 115, },
    "core_cooking": {"name": "Cooking", "page": 117, },
    "core_crush_and_devour": {"name": "Crush and Devour", "page": 119, },
    "core_endless_screams": {"name": "Endless Screams", "page": 121, },
    "core_game_over": {"name": "Game Over", "page": 123, },
    "core_hands_of_heat": {"name": "Hands of Heat", "page": 125},
    "core_herb_gathering": {"name": "Herb Gathering", "page": 127},
    "core_hooded_knight": {"name": "Hooded Knight", "page": 129, },
    "core_insight": {"name": "Insight", "page": 131, },
    "core_intimacy": {"name": "Intimacy", "page": 133, },
    "core_kings_curse": {"name": "King's Curse", "page": 135, },
    "core_kings_step": {"name": "King's Step", "page": 137, },
    "core_lantern_research": {'name': 'Lantern Research', 'page': 139},
    "core_legendary_lungs": {"name": "Legendary Lungs", "page": 141, },
    "core_legendary_monsters": {"name": "Legendary Monsters", "page": 143, },
    "core_mineral_gathering": {"name": "Mineral Gathering", "page": 145, },
    "core_overwhelming_darkness": {"name": "Overwhelming Darkness", "page": 147, },
    'core_oxidation': {'name': 'Oxidation', 'page': 149},
    "core_phoenix_feather": {"name": "Phoenix Feather", "page": 151, },
    "core_conviction": {"name": "Principle: Conviction", "page": 153, },
    "core_death": {"name": "Principle: Death", "page": 155, },
    "core_new_life": {"name": "Principle: New Life", "page": 157, },
    "core_society": {"name": "Principle: Society", "page": 159, },
    "core_regal_visit": {"name": "Regal Visit", "page": 161, },
    "core_returning_survivors": {"name": "Returning Survivors", "page": 163, },
    "core_run_away": {"name": "Run Away", "page": 165, },
    "core_see_the_truth": {"name": "See the Truth", "page": 167, },
    "core_white_secret": {"name": "White Secret", "page": 181, },
    "core_white_speaker": {"name": "White Speaker", "page": 183, },
    "core_zero_presence": {"name": "Zero Presence", "page": 185, },
    "core_watched": {"name": "Watched", "page": 187, },
    "core_blackout": {"name": "Blackout", "page": 191, },

    # sunstalker 
    "ss_pool_and_sun": {"name": "The Pool and the Sun", "page": 15, "expansion": "sunstalker"},
    "ss_sun_dipping": {"name": "Sun Dipping", "page": 19, "expansion": "sunstalker"},
    "ss_great_sky_gift": {"name": "The Great Sky Gift", "page": 21, "expansion": "sunstalker"},
    "ss_promise_under_the_sun": {"name": "Promise Under the sun", "page": 4, "expansion": "sunstalker"},
    "ss_birth_of_color": {"name": "Birth of Color", "page": 23, "expansion": "sunstalker"},
    "ss_final_gift": {"name": "Final Gift", "page": 25, "expansion": "sunstalker"},
    "ss_great_devourer": {"name": "The Great Devourer", "page": 33, "expansion": "sunstalker"},
    "ss_edged_tonometry": {"name": "Edged Tonometry", "page": 29, "expansion": "sunstalker"},

    # Lonely Tree
    "lt_lonley_lady": {"name": "The Lonely Lady", "page": 2, "expansion": "lonely_tree"},

    # Flower Knight
    "fk_crones_tale": {"name": "A Crone's Tale", "page": 4, "expansion": "flower_knight"},
    "fk_forest_wants_what_it_wants": {"name": "The Forest Wants What It Wants", "page": 12, "expansion": "flower_knight"},
    "fk_breakthrough": {"name": "Breakthrough", "page": 14, "expansion": "flower_knight"},
    "fk_sense_memory": {"name": "Sense Memory", "page": 16, "expansion": "flower_knight"},
    "fk_warm_virus": {"name": "A Warm Virus", "page": 18, "expansion": "flower_knight"},
    "fk_necrotoxic_mistletoe": {"name": "Necrotoxic Mistletoe", "page": 20, "expansion": "flower_knight"},

    # Lion Knight
    "lk_uninvited_guest": {"name": "An Uninvited Guest", "page": 5, "expansion": "lion_knight"},
    "lk_places_everyone": {"name": "Places, Everyone!", "page": 7, "expansion": "lion_knight"},
    "lk_intermission": {"name": "Intermission", "page": 10, "expansion": "lion_knight"},
    "lk_strange_caravan": {"name": "Strange Caravan", "page": 13, "expansion": "lion_knight"},
    "lk_finale": {"name": "Finale", "page": 14, "expansion": "lion_knight"},

    # DBK
    "dbk_rumbling_in_the_dark": {"name": "Rumbling in the Dark", "page": 4, "expansion": "dung_beetle_knight"},
    "dbk_spelunking_of_death": {"name": "Spelunking of Death", "page": 13, "expansion": "dung_beetle_knight"},
    "dbk_underground_sow": {"name": "Underground Sow", "page": 15, "expansion": "dung_beetle_knight"},
    "dbk_black_harvest": {"name": "Black Harvest", "page": 17, "expansion": "dung_beetle_knight"},
    "dbk_secret_meeting": {"name": "Secret Meeting", "page": 19, "expansion": "dung_beetle_knight"},

    # Lion God
    "lgod_silver_city": {"name": "The Silver City", "page": 2, "expansion": "lion_god"},
    "lgod_necropolis": {"name": "Necropolis", "page": 10, "expansion": "lion_god"},
    "lgod_knowledge_worm": {"name": "The Knowledge Worm", "page": 12, "expansion": "lion_god"},
    "lgod_gracious_host": {"name": "A Gracious Host", "page": 15, "expansion": "lion_god"},
    "lgod_death_reading": {"name": "Death Reading", "page": 16, "expansion": "lion_god"},

    # Gorm
    "gorm_approaching_storm": {"name": "The Approaching Storm", "page": 3, "expansion": "gorm"},
    "gorm_fetid_grotto": {"name": "Fetid Grotto", "page": 5, "expansion": "gorm"},
    "gorm_final_march": {"name": "Final March", "page": 7, "expansion": "gorm"},
    "gorm_melting_horror": {"name": "Melting Horror", "page": 11, "expansion": "gorm"},

    # Dragon King
    "dk_glowing_crater": {"name": "Glowing Crater", "page": 4, "expansion": "dragon_king"},
    "dk_meltdown": {"name": "Meltdown", "page": 8, "expansion": "dragon_king"},
    "dk_foundlings": {"name": "Foundlings", "page": 10, "expansion": "dragon_king"},
    "dk_intimacy": {"name": "Intimacy", "page": 12, "expansion": "dragon_king"},
    "dk_midnights_children": {"name": "Midnight's Children", "page": 14, "expansion": "dragon_king"},
    "dk_awake": {"name": "Awake", "page": 16, "expansion": "dragon_king"},
    "dk_unveil_the_sky": {"name": "Unveil the Sky", "page": 18, "expansion": "dragon_king"},
    "dk_faces_in_the_sky": {"name": "Faces in the Sky", "page": 20, "expansion": "dragon_king"},
    "dk_tomb": {"name": "The Tomb", "page": 22, "expansion": "dragon_king"},
    "dk_death_of_the_dragon_king": {"name": "Death of the Dragon King", "page": 27, "expansion": "dragon_king"},

    # Manhunter
    "mh_hanged_man": {"name": "The Hanged Man", "page": 3, "expansion": "manhunter"},
    "mh_lottery": {"name": "Lottery", "page": 11, "expansion": "manhunter"},
    "mh_death_pit": {"name": "Death Pit", "page": 13, "expansion": "manhunter"},
    "mh_sonorous_rest": {"name": "Sonorous Rest", "page": 15, "expansion": "manhunter"},
    "mh_bleeding_heart": {"name": "Bleeding Heart", "page": 17, "expansion": "manhunter"},
    "mh_tools_of_War": {"name": "Tools of War", "page": 19, "expansion": "manhunter"},

    # Spidicules
    "spid_young_rivals": {"name": "Young Rivals", "page": 4, "expansion": "spidicules"},
    "spid_forest_wants_what_it_wants": {"name": "The Forest Wants What it Wants", "page": 11, "expansion": "spidicules"},
    "spid_spidisisyphus": {"name": "Spidisisyphus", "page": 13, "expansion": "spidicules"},
    "spid_puppets_embalming": {"name": "Puppet's Embalming", "page": 15, "expansion": "spidicules"},
    "spid_silk_surgery": {"name": "Silk Surgery", "page": 17, "expansion": "spidicules"},
    "spid_taken": {"name": "Taken", "page": 19, "expansion": "spidicules"},

    # Slenderman
    "slender_its_already_here": {"name": "It's Already Here", "page": 2, "expansion": "slenderman",},
    "slender_dark_place": {"name": "Dark Place", "page": 11, "expansion": "slenderman",},
    "slender_light_forging": {"name": "Light-Forging", "page": 13, "expansion": "slenderman",},
    "slender_forgotten_fear": {"name": "Forgotten Fear", "page": 15, "expansion": "slenderman",},
}

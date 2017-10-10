#
#   There are three types of locations in Kingdom Death: Monster.
#
#   The first type of location is settlement locations. These are added to the
#   settlement locations and function like a normal settlement game asset. The
#   'Lantern Hoard' is one of these, as is the Dragon King's 'Throne'.
#
#   The second type of location is a gear location. These are 'pseudo' locations
#   that do not get added to options (decks) or to the Settlement Sheet, but
#   certain types of gear comes from them. Examples include "Rare Gear" and
#   items created in the "Sense Memory" story event.
#
#   The third type of location is resources. Resource type gear comes from these
#   bogus 'locations'. The 'Strange Resources' and 'Vermin' type of items belong
#   to these locations.
#
#



resources = {
    "basic_resources": {
        "name": "Basic Resources",
        "color": "B1FB17",
    },
    "vermin_resources": {
        "name": "Vermin",
        "color": "99CC66",
    },
    "strange_resources": {
        "name": "Strange Resources",
        "color": "9DC209",
    },
    "white_lion_resources": {
        "name": "White Lion Resources",
        "color": "DCD900",
    },
    "screaming_antelope_resources": {
        "name": "Screaming Antelope Resources",
        "color": "DCD900",
    },
    "phoenix_resources": {
        "name": "Phoenix Resources",
        "color": "DCD900",
    },
    "spidicules_resources": {
        "name": "Spidicules Resources",
        "expansion": "spidicules",
        "color": "DCD900",
    },
    "gorm_resources":{
        "name": "Gorm Resources",
        "expansion": "gorm",
        "color": "DCD900",
    },
    "flower_knight_resources":{
        "name": "Flower Knight Resources",
        "expansion": "flower_knight",
        "color": "DCD900",
    },
    "dbk_resources": {
        "name": "Dung Beetle Knight Resources",
        "expansion": "dung_beetle_knight",
        "color": "DCD900",
    },
    "dragon_king_resources":{
        "name": "Dragon King Resources",
        "expansion": "dragon_king",
        "color": "DCD900",
    },
}


gear = {
    "starting_gear": {
        "name": "Starting Gear",
        "color": "CCC",
    },
    "light_forging_gear": {
        "name": "Light-Forging",
        "expansion": "slenderman",
        "color": "570A75",
        "font-color": "fff",
    },
    "green_knight_armor_gear": {
        "name": "Green Knight Armor",
        "expansion": "green_knight_armor",
        "color": "42AB59",
        "font_color": "fff",
    },
    "manhunter_gear": {
        "name": "Manhunter Gear",
        "expansion": "manhunter",
        "color": "000",
        "font_color": "F50057",
    },
    "sense_memory_gear": {
        "name": "Sense Memory",
        "expansion": "flower_knight",
        "color": "145314",
        "font_color": "FFF",
    },
    "rare_gear": {
        "name": "Rare Gear",
        "color": "9DC209",
    },
    "promo": {
        "name": "Promo",
        "expansion": "white_box",
        "color": "3BB9FF",
    },
    "gear_recipe": {
        "name": "Gear Recipe",
        "color": "333",
        "font_color": "FFF",
    },
    "ivory_carver": {
        "name": "Ivory Carver",
        "color": "FFFFF0",
    },
    "other": {
        "name": "other",
        "font_color": "FFF",
        "color": "FF00FF",
    },
    "black_harvest": {
        "name": "Black Harvest",
        "expansion": "dung_beetle_knight",
        "color": "333",
        "font_color": "FFF",
    },

}

location = {

    #
    #   Core locations! Keep these on top
    #

    "lantern_hoard": {
        "name": "Lantern Hoard",
        "consequences": [
            "Bone Smith",
            "Skinnery",
            "Organ Grinder",
            "Catarium",
            "Plumery",
            "Exhausted Lantern Hoard",
            "Mask Maker"
        ],
        "endeavors": {
            "Innovate": {
                "cost": 1,
                "desc": "Once per settlement phase, you may spend the listed resources (1 Endeavor, 1 Bone, 1 Organ, 1 Hide) to draw 2 innovation cards. Keep 1 and return the other to the deck."
            },
            "Shared Experience": {
                "cost": 1,
                "requires": ["Symposium"],
                "desc": "Nominate a survivor that has 2 or more Hunt XP than yourself. They describe illuminating details of their desired death. If you are not deaf, gain +1 Hunt XP from their story.  If the nominated survivor has abroken jaw, instead gain +1 insanity.",
            },
            "Build": {"cost":1, "desc": "Bone Smith", "remove_after": "Bone Smith"},
            " Build": {"cost":1, "desc": "Skinnery", "remove_after": "Skinnery"},
            "  Build": {"cost":1, "desc": "Organ Grinder", "remove_after": "Organ Grinder"},
        },
    },
    "exhausted_lantern_hoard": {
        "name": "Exhausted Lantern Hoard",
        "color": "ddd",
    },

    "bone_smith": {
        "name": "Bone Smith",
        "color": "e3dac9",
        "consequences": ["Weapon Crafter"],
        "endeavors": {
            "Build": {"cost": 1, "desc": "Weapon Crafter (3 x bone, 1 x hide)", "remove_after": "Weapon Crafter"},
        },
    },
    "weapon_crafter": {
        "name": "Weapon Crafter",
        "color": "E1D4C0",
        "endeavors": {
            "Scrap Scavenge": {"cost": 1, },
            "Special Innovate": {
                "cost": 1,
                "desc": "Scrap Smelting (2 x scrap, 5 x bone, 5 x organ)",
                "remove_after": "Scrap Smelting"
            },
        },
    },

    "skinnery": {
        "name": "Skinnery",
        "color": "FFCBA4",
        "consequences": ["Leather Worker"],
        "endeavors": {
            "Build": {
                "cost": 1,
                "desc": "Leather Worker (3 x hide, 1 x organ)",
                "remove_after": "Leather Worker"
            },
        },
    },
    "leather_worker": {
        "name": "Leather Worker",
        "color": "7F462C",
        "font_color": "FFF",
        "endeavors": {
            "Leather-Making": {
                "cost": 1,
                "desc": "Spend any number of hide to add an equal number of leather strange resources to the settlement storage.",
                "requires": ["Ammonia"],
                },
        },
    },

    "organ_grinder": {
        "name": "Organ Grinder",
        "color": "B58AA5",
        "consequences": ["Stone Circle"],
        "endeavors": {
            "Augury": {"cost": 1},
            "Build": {
                "cost": 1,
                "desc": "Stone Circle (3 x organ, 1 x hide)",
                "remove_after": "Stone Circle"
            },
        },
    },

    "stone_circle": {
        "name": "Stone Circle",
        "color": "835C3B",
        "font_color": "FFF",
        "endeavors": {
            "Harvest Ritual": {
                "cost": 1,
                "desc": "Spend any number of monster resources to draw an equal number of basic resources."
            },
        },
    },

    "plumery": {
        "name": "Plumery",
        "color": "FF5EAA",
    },
    "catarium": {
        "name": "Catarium",
        "color": "BA8B02",
    },

    "blacksmith": {
        "name": "Blacksmith",
        "requires": ("innovations", "Scrap Smelting"),
        "color": "625D5D",
        "font_color": "FFF",
    },
    "barber_surgeon": {
        "name": "Barber Surgeon",
        "requires": ("innovations", "Pottery"),
        "color": "E55451",
        "font_color": "FFF",
    },
    "mask_maker": {
        "name": "Mask Maker",
        "color": "FFD700",
        "endeavors": {
            "White Lion Mask": {"cost": 1, "desc": "You may hunt the Great Golden Cat."},
            "Antelope Mask": {"cost": 1, "desc": "You may hunt the Mad Steed."},
            "Phoenix Mask": {"cost": 1, "desc": "You may hunt the Golden Eyed King."},
        },
    },



    # DBK

    "wet_resin_crafter": {
        "name": "Wet Resin Crafter",
        "expansion": "dung_beetle_knight",
        "color": "C9CE62",
    },


    #
    #   Gorm locations!
    #

    "gormchymist": {
        "name": "Gormchymist",
        "expansion": "gorm",
        "color": "8C001A",
        "font_color": "FFF",
        "endeavors": {
            "Special Innovate": {
                "cost": 1,
                "desc": "Gain the next Gormchymy innovation (1 x strange resource, 1 x gorm brain)"
            },
        },
    },
    "gormery": {
        "name": "Gormery",
        "expansion": "gorm",
        "color": "600313",
        "font_color": "FFF",
    },


    #
    #   Sunstalker Locations
    #

    "the_sun": {
        "name": "The Sun",
        "expansion": "sunstalker",
        "consequences": [
            "bone_smith",
            "skinnery",
            "organ_grinder",
            "catarium",
            "plumery",
            "mask_maker",
            "sacred_pool"
        ],
        "endeavors": {
            "Innovate": {
                "cost": 1,
                "desc": "Once per settlement phase, you may spend the listed resources (1 Bone, 1 Organ, 1 Hide) to draw 2 innovation cards. Keep 1 and return the other to the deck."
            },
            "Build": {"cost":1, "desc": "Bone Smith", "remove_after": "Bone Smith"},
            " Build": {"cost":1, "desc": "Skinnery", "remove_after": "Skinnery"},     # hacks!
            "  Build": {"cost":1, "desc": "Organ Grinder", "remove_after": "Organ Grinder"},
        },
        "special_rules": [
            {
                "name": "Extreme Heat",
                "desc": "Survivors cannot wear heavy gear.",
                "bg_color": "DD3300",
                "font_color": "FFF",
            },
            {
                "name": "Supernova",
                "desc": 'If you suffer defeat against a nemesis monster, the sun cleanses the settlement, instantly killing everyone. <font class="kdm_font">g</font> <b>Game Over</b>',
                "bg_color": "990000",
                "font_color": "FFF",
            },
        ],
    },

    "sacred_pool": {
        "name": "Sacred Pool",
        "expansion": "sunstalker",
        "levels": 3,
        "color": "eee541",
        "endeavors": {
            "Sacred Water": {
                "cost": 1,
                "desc": 'Once per settlement phase, the settlement drinks the oil that builds up on the surface of the pool. <font class="kdm_font">g</font> <b>Intimacy</b>.'
            },
            "Purification Ceremony": {
                "cost": 2,
                "desc": "You may endeavor here once per lifetime. Your body is infused with sacred water and <b>Purified</b> (record this). You cannot <b>depart</b> this year. Gain the <b>Protective</b> disorder and roll 1d10. On 8+, gain +1 permanent attribute of your choice. Otherwise, gain +1 permanent strength or accuracy."
            },
            "Sun Sealing": {
                "requires": ["sauna_shrine"],
                "cost": 1,
                "desc": "You sit for a year, in the boiling darkness of the Shrine. Gain the <b>Hellfire</b> secret fighting art. You cannot <b>depart</b> this year."
            },
        },
    },

    "skyreef_sanctuary": {
        "name": "Skyreef Sanctuary",
        "expansion": "sunstalker",
        "color": "FFF541",
    },



    #
    #   Dragon King locations!
    #

    "dragon_armory": {
        "name": "Dragon Armory",
        "expansion": "dragon_king",
        "color": "6A1B9A",
        "font_color": "FFF",
    },
    "throne": {
        "name": "Throne",
        "expansion": "dragon_king",
        "consequences": ["Bone Smith", "Skinnery", "Organ Grinder", "Catarium", "Plumery", "Mask Maker"],
        "endeavors": {
            "Innovate": {"cost": 1, "desc": "Once per settlement phase, you may spend the listed resources (1 Endeavor, 1 Bone, 1 Organ, 1 Hide) to draw 2 innovation cards. Keep 1 and return the other to the deck."},
            "Fear and Trembling": {"cost": 1, "desc": 'Once per settlement phase, a survivor may spend <font class="kdm_font">d</font> to approach the throne and roll 1d10.'},
            "Build": {"cost":1, "desc": "Bone Smith", "remove_after": "Bone Smith"},
            " Build": {"cost":1, "desc": "Skinnery", "remove_after": "Skinnery"},
            "  Build": {"cost":1, "desc": "Organ Grinder", "remove_after": "Organ Grinder"},
        },
    },


    # Spidicules

    "silk_mill": {
        "name": "Silk Mill",
        "expansion": "spidicules",
        "color": "C0CA33",
        "font_color": "000",
    },

}

#!/usr/bin/env python


locations = {
    "Light-Forging": {
        "color": "570A75",
        "font_color": "fff",
    },
    "Green Knight Armor": {
        "color": "42AB59",
        "font_color": "fff",
    },
    "Silk Mill":{
        "color": "C0CA33",
        "font_color": "000",
    },
    "Manhunter Gear":{
        "color": "000",
        "font_color": "F50057",
    },
    "Dragon Armory":{
        "color": "6A1B9A",
        "font_color": "FFF",
    },
    "Sense Memory": {
        "color": "145314",
        "font_color": "FFF",
    },
    "Rare Gear": {
        "color": "9DC209",
    },
    "Promo": {
        "color": "3BB9FF",
    },
    "Gear Recipe": {
        "color": "333",
        "font_color": "FFF",
    },
    "Ivory Carver": {
        "color": "FFFFF0",
    },
    "Unique Items": {
        "font_color": "FFF",
        "color": "FF00FF",
    },
    "Throne": {
        "consequences": ["Bone Smith", "Skinnery", "Organ Grinder", "Catarium", "Plumery", "Mask Maker"],
        "endeavors": {
            "Innovate": {"cost": 1, "desc": "Once per settlement phase, you may spend the listed resources (1 Endeavor, 1 Bone, 1 Organ, 1 Hide) to draw 2 innovation cards. Keep 1 and return the other to the deck."},
            "Fear and Trembling": {"cost": 1, "desc": 'Once per settlement phase, a survivor may spend <font class="kdm_font">d</font> to approach the throne and roll 1d10.'},
            "Build": {"cost":1, "desc": "Bone Smith", "remove_after": "Bone Smith"},
            " Build": {"cost":1, "desc": "Skinnery", "remove_after": "Skinnery"},
            "  Build": {"cost":1, "desc": "Organ Grinder", "remove_after": "Organ Grinder"},
        },
    },
    "Lantern Hoard": {
        "consequences": ["Bone Smith", "Skinnery", "Organ Grinder", "Catarium", "Plumery", "Exhausted Lantern Hoard", "Mask Maker"],
        "endeavors": {
            "Innovate": {"cost": 1, "desc": "Once per settlement phase, you may spend the listed resources (1 Endeavor, 1 Bone, 1 Organ, 1 Hide) to draw 2 innovation cards. Keep 1 and return the other to the deck."},
            "Shared Experience": {
                "cost": 1,
                "requires": ["Symposium"],
                "desc": "Nominate a survivor that has 2 or more Hunt XP than yourself. They describe illuminating details of their desired death. If you are not deaf, gain +1 Hunt XP from their story.  If the nominated survivor has a broken jaw, instead gain +1 insanity.",
            },
            "Build": {"cost":1, "desc": "Bone Smith", "remove_after": "Bone Smith"},
            " Build": {"cost":1, "desc": "Skinnery", "remove_after": "Skinnery"},     # hacks!
            "  Build": {"cost":1, "desc": "Organ Grinder", "remove_after": "Organ Grinder"},    # craaaazzzzzyyy hacks!
        },
    },
    "Bone Smith": {
        "color": "e3dac9",
        "consequences": ["Weapon Crafter"],
        "endeavors": {
            "Build": {"cost": 1, "desc": "Weapon Crafter (3 x bone, 1 x hide)", "remove_after": "Weapon Crafter"},
        },
    },
    "Skinnery": {
        "color": "FFCBA4",
        "consequences": ["Leather Worker"],
        "endeavors": {
            "Build": {"cost": 1, "desc": "Leather Worker (3 x hide, 1 x organ)", "remove_after": "Leather Worker"},
        },
    },
    "Organ Grinder": {
        "color": "B58AA5",
        "consequences": ["Stone Circle"],
        "endeavors": {
            "Augury": {"cost": 1},
            "Build": {"cost": 1, "desc": "Stone Circle (3 x organ, 1 x hide)", "remove_after": "Stone Circle"},
        },
    },
    "Blacksmith": {
        "requires": ("innovations", "Scrap Smelting"),
        "color": "625D5D",
        "font_color": "FFF",
    },
    "Stone Circle": {
        "color": "835C3B",
        "font_color": "FFF",
        "endeavors": {
            "Harvest Ritual": {"cost": 1, "desc": "Spend any number of monster resources to draw an equal number of basic resources."},
        },
    },
    "Leather Worker": {
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
    "Weapon Crafter": {
        "color": "E1D4C0",
        "endeavors": {
            "Scrap Scavenge": {"cost": 1, },
            "Special Innovate": {"cost": 1, "desc": "Scrap Smelting (2 x scrap, 5 x bone, 5 x organ)", "remove_after": "Scrap Smelting"},
        },
    },
    "Barber Surgeon": {
        "requires": ("innovations", "Pottery"),
        "color": "E55451",
        "font_color": "FFF",
    },
    "Plumery": {
        "color": "FF5EAA",
        "consequences": [],
    },
    "Mask Maker": {
        "color": "FFD700",
        "endeavors": {
            "White Lion Mask": {"cost": 1, "desc": "You may hunt the Great Golden Cat."},
            "Antelope Mask": {"cost": 1, "desc": "You may hunt the Mad Steed."},
            "Phoenix Mask": {"cost": 1, "desc": "You may hunt the Golden Eyed King."},
        },
    },
    "Exhausted Lantern Hoard": {
        "color": "ddd",
        "consequences": [],
    },
    "Catarium": {
        "color": "BA8B02",
        "consequences": [],
    },
    "Gormchymist": {
        "color": "8C001A",
        "font_color": "FFF",
        "consequences": [],
        "expansion": "Gorm",
        "endeavors": {
            "Special Innovate": {"cost": 1, "desc": "Gain the next Gormchymy innovation (1 x strange resource, 1 x gorm brain)"},
        },
    },
    "Gormery": {
        "color": "600313",
        "font_color": "FFF",
        "consequences": [],
        "expansion": "Gorm",
    },
    "Black Harvest": {
        "color": "333",
        "font_color": "FFF",
        "expansion": "Dung Beetle Knight",
    },
    "Wet Resin Crafter": {
        "expansion": "Dung Beetle Knight",
        "color": "C9CE62",
    },
    "The Sun": {
        "expansion": "Sunstalker",
        "consequences": [
            "Bone Smith",
            "Skinnery",
            "Organ Grinder",
            "Catarium",
            "Plumery",
            "Mask Maker",
            "Sacred Pool"
        ],
        "endeavors": {
            "Innovate": {"cost": 1, "desc": "Once per settlement phase, you may spend the listed resources (1 Bone, 1 Organ, 1 Hide) to draw 2 innovation cards. Keep 1 and return the other to the deck."},
            "Build": {"cost":1, "desc": "Bone Smith", "remove_after": "Bone Smith"},
            " Build": {"cost":1, "desc": "Skinnery", "remove_after": "Skinnery"},     # hacks!
            "  Build": {"cost":1, "desc": "Organ Grinder", "remove_after": "Organ Grinder"},    # craaaazzzzzyyy hacks!
        },
        "special_rules": [
            {"name": "Extreme Heat", "desc": "Survivors cannot wear heavy gear.", "bg_color": "DD3300", "font_color": "FFF"},
            {"name": "Supernova", "desc": 'If you suffer defeat against a nemesis monster, the sun cleanses the settlement, instantly killing everyone. <font class="kdm_font">g</font> <b>Game Over</b>', "bg_color": "990000", "font_color": "FFF"},
        ],
    },
    "Sacred Pool": {
        "expansion": "Sunstalker",
        "levels": 3,
        "endeavors": {
            "Sacred Water": {"cost": 1, "desc": 'Once per settlement phase, the settlement drinks the oil that builds up on the surface of the pool. <font class="kdm_font">g</font> <b>Intimacy</b>.'},
            "Purification Ceremony": {"cost": 2, "desc": "You may endeavor here once per lifetime. Your body is infused with sacred water and <b>Purified</b> (record this). You cannot <b>depart</b> this year. Gain the <b>Protective</b> disorder and roll 1d10. On 8+, gain +1 permanent attribute of your choice. Otherwise, gain +1 permanent strength or accuracy."},
            "Sun Sealing": {"requires": ["Sauna Shrine"], "cost": 1, "desc": "You sit for a year, in the boiling darkness of the Shrine. Gain the <b>Hellfire</b> secret fighting art. You cannot <b>depart</b> this year."},
        },
        "color": "eee541",
    },
    "Skyreef Sanctuary": {
        "expansion": "Sunstalker",
        "color": "FFF541",
        "consequences": [],
    },
}


# boy, this is a really good example of why you don't try to make dictionary
# keys out of your raw asset values. Fuck you, Poots: next time I'm using bson
# object keys or some shit
item_normalization_exceptions = {
    ("Belt Of Gender Swap", "Belt of Gender Swap"),
    ("Quiver And Sunstring", "Quiver and Sunstring"),
    ("Sun Lure And Hook", "Sun Lure and Hook"),
	("Arm Of The First Tree", "Arm of the First Tree"),
    ("Dbk Errant Badge", "DBK Errant Badge"),
    ("Finger Of God", "Finger of God"),
    ("Eye Of Cat", "Eye of Cat"),
}



items = {
    "Gloom Hammer": {
        "expansion": "Slenderman",
        "location": "Light-Forging",
    },
    "Gloom Katana": {
        "expansion": "Slenderman",
        "location": "Light-Forging",
    },
    "Gloom Sheath": {
        "expansion": "Slenderman",
        "location": "Light-Forging",
    },
    "Gloom Bracelets": {
        "expansion": "Slenderman",
        "location": "Light-Forging",
    },
    "Gloom-Coated Arrow": {
        "expansion": "Slenderman",
        "location": "Light-Forging",
    },
    "Gloom Mehndi": {
        "expansion": "Slenderman",
        "location": "Light-Forging",
    },
    "Dark Water Vial": {
        "expansion": "Slenderman",
        "location": "Light-Forging",
    },
    "Raptor-Worm Collar": {
        "expansion": "Slenderman",
        "location": "Light-Forging",
    },
    "Gloom Cream": {
        "expansion": "Slenderman",
        "location": "Light-Forging",
    },
    "Slender Ovule": {
        "expansion": "Slenderman",
        "location": "Light-Forging",
    },
    "Crystal Sword Mold": {
        "expansion": "Slenderman",
        "location": "Strange Resources",
    },
    "Dark Water": {
        "expansion": "Slenderman",
        "location": "Strange Resources",
    },
    "Green Boots" : {
        "expansion": "Green Knight Armor",
        "location": "Green Knight Armor",
    },
    "Green Plate" : {
        "expansion": "Green Knight Armor",
        "location": "Green Knight Armor",
    },
    "Green Gloves" : {
        "expansion": "Green Knight Armor",
        "location": "Green Knight Armor",
    },
    "Green Helm" : {
        "expansion": "Green Knight Armor",
        "location": "Green Knight Armor",
    },
    "Green Faulds" : {
        "expansion": "Green Knight Armor",
        "location": "Green Knight Armor",
    },
    "Fetorsaurus" : {
        "expansion": "Green Knight Armor",
        "location": "Green Knight Armor",
    },
    "Griswaldo" : {
        "expansion": "Green Knight Armor",
        "location": "Green Knight Armor",
    },
    "Venom Sac": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["organ",],
    },
    "Arachnid Heart": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["organ",],
    },
    "Serrated Fangs": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["bone",],
        "endeavors": {
            "Razor Push-ups": {"cost": 1, "type": "education",},
        },
    },
    "Eyeballs": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["organ",],
    },
    "Unlaid Eggs": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["organ",],
    },
    "Large Appendage": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["bone",],
    },
    "Exoskeleton": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["hide",],
    },
    "Chitin": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["hide",],
    },
    "Small Appendages": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["hide",],
    },
    "Stomach": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["organ",],
    },
    "Spinnerets": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["organ","scrap"],
    },
    "Thick Web Silk": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["hide"],
    },
    "Silken Nervous System": {
        "expansion": "Spidicules",
        "location": "Strange Resources",
        "resource_family": ["organ"],
    },
    "Web Silk": {
        "expansion": "Spidicules",
        "location": "Strange Resources",
    },
    "Silk Armor Set": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Throwing Knife": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Hooded Scrap Katar": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Silk Wraps": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Silk Whip": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Silk Turban": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Silk Sash": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Silk robes": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Silk Boots": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Silk Bomb": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Silk Body Suit": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Green Ring": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Red Ring": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Blue Ring": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Amber Poleaxe": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Amber Edge": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Grinning Visage": {
        "expansion": "Spidicules",
        "location": "Rare Gear",
        "desc": 'When you wound with this shield, you may spend 1 survival to add <font class="inline_shield">1</font> to all hit locations.<br/>Limit, once per attack.',
        "type": ["weapon","melee","shield"],
    },
    "The Weaver": {
        "expansion": "Spidicules",
        "location": "Rare Gear",
        "desc": 'When you wound a monster, add <font class="inline_shield">1</font> to a random hit location.',
        "type": ["weapon","melee","sword","amber"],
    },
    "Detective Cap": {
        "expansion": "white_box",
        "location": "Promo",
    },
    "Twilight Revolver": {
        "expansion": "white_box",
        "location": "Promo",
    },
    "Xmaxe": {
        "expansion": "white_box",
        "location": "Promo",
    },
    "Black Friday Lantern": {
        "expansion": "White Box",
        "location": "Promo",
        "desc": "On <b>Arrival</b> (at the start of the showdown), you may archive this and Ambush the monster. Limit, once per campaign.",
        "attributes": {"Evasion": 1},
        "type": ["item","lantern","other"],
    },
    "Jack O' Lantern": {
        "expansion": "White Box",
        "location": "Gear Recipe",
    },
    "Nightmare Breast Pump": {
        "expansion": "White Box",
        "location": "Promo",
    },
    "Dragon Vestments": {
        "expansion": "Dragon King",
        "location": "Rare Gear",
    },
    "Celestial Spear": {
        "expansion": "Dragon King",
        "location": "Rare Gear",
    },
    "Hazmat Shield": {
        "expansion": "Dragon King",
        "location": "Rare Gear",
    },
    "Husk of Destiny": {
        "expansion": "Dragon King",
        "location": "Rare Gear",
    },
    "Red Power Core": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Blue Power Core": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Nuclear Knife": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Nuclear Scythe": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Blast Shield": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Shielded Quiver": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Dragon Bite Bolt": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Dragon Belt": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Dragon Chakram": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Regal Edge": {
        "expansion": "Dragon King",
        "location": "Rare Gear",
    },
    "Dragon Boots": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Dragonskull Helm": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Talon Knife": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Dragon Gloves": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Dragon Mantle": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Dragon Armor Set": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Blast Sword": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Horn Fragment": {
        "expansion": "Dragon King",
        "location": "Dragon King Resources",
        "resource_family": ["bone"],
    },
    "King's Claws": {
        "expansion": "Dragon King",
        "location": "Dragon King Resources",
        "resource_family": ["bone"],
    },
    "Husk": {
        "expansion": "Dragon King",
        "location": "Dragon King Resources",
        "resource_family": ["hide"],
    },
    "Veined Wing": {
        "expansion": "Dragon King",
        "location": "Dragon King Resources",
        "resource_family": ["hide"],
    },
    "Dragon Iron": {
        "expansion": "Dragon King",
        "location": "Dragon King Resources",
        "resource_family": ["scrap"],
    },
    "King's Tongue": {
        "expansion": "Dragon King",
        "location": "Dragon King Resources",
        "resource_family": ["hide"],
    },
    "Hardened Ribs": {
        "expansion": "Dragon King",
        "location": "Dragon King Resources",
        "resource_family": ["bone"],
    },
    "Cabled Vein": {
        "expansion": "Dragon King",
        "location": "Dragon King Resources",
        "resource_family": ["organ"],
    },
    "Radioactive Dung": {
        "expansion": "Dragon King",
        "location": "Dragon King Resources",
        "resource_family": ["organ","scrap"],
    },
    "Lantern Bloom": {
        "expansion": "Flower Knight",
        "location": "Flower Knight Resources",
        "resource_family": ["hide",],
    },
    "Sighing Bloom": {
        "expansion": "Flower Knight",
        "location": "Flower Knight Resources",
        "resource_family": ["organ",],
    },
    "Osseous Bloom": {
        "expansion": "Flower Knight",
        "location": "Flower Knight Resources",
        "resource_family": ["bone",],
    },
    "Lantern Bud": {
        "expansion": "Flower Knight",
        "location": "Flower Knight Resources",
        "resource_family": ["scrap",],
    },
    "Warbling Bloom": {
        "expansion": "Flower Knight",
        "location": "Flower Knight Resources",
        "resource_family": ["hide",],
    },
    "Vespertine Foil": {
        "expansion": "Flower Knight",
        "location": "Sense Memory",
    },
    "Vespertine Bow": {
        "expansion": "Flower Knight",
        "location": "Sense Memory",
    },
    "Vespertine Cello": {
        "expansion": "Flower Knight",
        "location": "Sense Memory",
    },
    "Satchel": {
        "expansion": "Flower Knight",
        "location": "Sense Memory",
    },
    "Vespertine Arrow": {
        "expansion": "Flower Knight",
        "location": "Sense Memory",
    },
    "Flower Knight Badge": {
        "expansion": "Flower Knight",
        "location": "Sense Memory",
    },
    "Flower Knight Helm": {
        "expansion": "Flower Knight",
        "location": "Rare Gear",
    },
    "Replica Flower Sword": {
        "expansion": "Flower Knight",
        "location": "Rare Gear",
    },
    "Sleeping Virus Flower": {
        "expansion": "Flower Knight",
        "location": "Rare Gear",
    },
    "Cycloid Scale Hood": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Cycloid Scale Sleeves": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Cycloid Scale Jacket": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Cycloid Scale Skirt": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Cycloid Scale Shoes": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Cycloid Scale Armor": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Sunspot Dart": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Sunshark Bow": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Sunshark Arrows": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Denticle Axe": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Skleaver": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Ink Sword": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Sunspot Lantern": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Quiver and Sunstring": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Shadow Saliva Shawl": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Sun Lure and Hook": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Sky Harpoon": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Ink Blood Bow": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Sun Vestments": {
        "expansion": "Sunstalker",
        "location": "Sacred Pool",
    },
    "Sunring Bow": {
        "expansion": "Sunstalker",
        "location": "Sacred Pool",
    },
    "Apostle Crown": {
        "expansion": "Sunstalker",
        "location": "Sacred Pool",
    },
    "Prism Mace": {
        "expansion": "Sunstalker",
        "location": "Sacred Pool",
    },
    "God's String": {
        "expansion": "Sunstalker",
        "location": "Rare Gear",
    },
    "Eye Patch": {
        "expansion": "Sunstalker",
        "location": "Rare Gear",
    },
    "Huge Sunteeth": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["bone"],
    },
    "Small Sunteeth": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["bone"],
    },
    "Shadow Tentacles": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["organ","hide"],
    },
    "Shark Tongue": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["organ"],
    },
    "Cycloid Scales": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["hide"],
    },
    "Inner Shadow Skin": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["hide"],
    },
    "Prismatic Gills": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["organ"],
    },
    "Sunshark Fin": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["bone","hide"],
    },
    "Sunshark Bone": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["bone"],
    },
    "Stink Lung": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["organ"],
    },
    "Brain Root": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["organ"],
    },
    "Fertility Tentacle": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["organ"],
    },
    "Shadow Ink Gland": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["organ"],
    },
    "Sunshark Blubber": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["organ"],
    },
    "Black Lens": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["organ"],
    },
    "Riot Mace": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Rib Blade": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Regeneration Suit": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Pulse Lantern": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Knuckle Shield": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Greater Gaxe": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Gorn": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Gaxe": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Black Sword": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Gorment Mask": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Gorment Suit": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Gorment Sleeves": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Gorment Boots": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Armor Spikes": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Acid Tooth Dagger": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Gorment Armor Set": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Healing Potion": {
        "location": "Gormchymist",
    },
    "Wisdom Potion": {
        "location": "Gormchymist",
    },
    "Steadfast Potion": {
        "location": "Gormchymist",
    },
    "Power Potion": {
        "location": "Gormchymist",
    },
    "Life Elixir": {
        "location": "Gormchymist",
    },
    "First Aid Kit" : {
        "location": "Barber Surgeon",
    },
    "Brain Mint" : {
        "location": "Barber Surgeon",
    },
    "Elder Earrings" : {
        "location": "Barber Surgeon",
    },
    "Musk Bomb" : {
        "location": "Barber Surgeon",
    },
    "Scavenger Kit" : {
        "location": "Barber Surgeon",
    },
    "Bug Trap" : {
        "location": "Barber Surgeon",
    },
    "Speed Powder" : {
        "location": "Barber Surgeon",
    },
    "Almanac" : {
        "location": "Barber Surgeon",
    },
    "God Mask" : {
        "location": "Mask Maker",
    },
    "Phoenix Mask" : {
        "location": "Mask Maker",
    },
    "Man Mask" : {
        "location": "Mask Maker",
    },
    "White Lion Mask" : {
        "location": "Mask Maker",
    },
    "Antelope Mask" : {
        "location": "Mask Maker",
    },
    "Death Mask" : {
        "location": "Mask Maker",
    },
    "Phoenix Armor Set": {
        "location": "Plumery",
    },
    "Arc Bow": {
        "location": "Plumery",
    },
    "Hollowpoint Arrow": {
        "location": "Plumery",
    },
    "Hollow Sword": {
        "location": "Plumery",
    },
    "Feather Shield": {
        "location": "Plumery",
    },
    "Phoenix Faulds": {
        "location": "Plumery",
    },
    "Sonic Tomahawk": {
        "location": "Plumery",
    },
    "Crest Crown": {
        "location": "Plumery",
    },
    "Phoenix Helm": {
        "location": "Plumery",
    },
    "Phoenix Greaves": {
        "location": "Plumery",
    },
    "Hours Ring": {
        "location": "Plumery",
    },
    "Bird Bread": {
        "location": "Plumery",
    },
    "Phoenix Plackart": {
        "location": "Plumery",
    },
    "Bloom Sphere": {
        "location": "Plumery",
    },
    "Phoenix Gauntlet": {
        "location": "Plumery",
    },
    "Feather Mantle": {
        "location": "Plumery",
    },
    "Scrap Shield" : {
        "location": "Blacksmith",
    },
    "Dragon Slayer" : {
        "location": "Blacksmith",
    },
    "Lantern Armor Set": {
        "location": "Blacksmith",
    },
    "Lantern Cuirass" : {
        "location": "Blacksmith",
    },
    "Lantern Gauntlets" : {
        "location": "Blacksmith",
    },
    "Perfect Slayer" : {
        "location": "Blacksmith",
    },
    "Lantern Greaves" : {
        "location": "Blacksmith",
    },
    "Lantern Helm" : {
        "location": "Blacksmith",
    },
    "Beacon Shield" : {
        "location": "Blacksmith",
    },
    "Lantern Mail" : {
        "location": "Blacksmith",
    },
    "Ring Whip" : {
        "location": "Blacksmith",
    },
    "Lantern Sword" : {
        "location": "Blacksmith",
    },
    "Lantern Glaive" : {
        "location": "Blacksmith",
    },
    "Lantern Dagger" : {
        "location": "Blacksmith",
    },
    "Leather Armor Set": {
        "location": "Leather Worker",
    },
    "Leather Bracers": {
        "location": "Leather Worker",
    },
    "Leather Cuirass": {
        "location": "Leather Worker",
    },
    "Leather Mask": {
        "location": "Leather Worker",
    },
    "Leather Skirt": {
        "location": "Leather Worker",
    },
    "Hunter Whip": {
        "location": "Leather Worker",
    },
    "Round Leather Shield": {
        "location": "Leather Worker",
    },
    "Leather Boots": {
        "location": "Leather Worker",
    },
    "Portcullis Key": {
        "location": "Unique Items",
    },
    "Love Juice": {
        "location": "Basic Resources",
        "resource_family": ["organ"],
        "consumable": True,
    },
    "Skull": {
        "location": "Basic Resources",
        "resource_family": ["bone"],
    },
    "???": {
        "location": "Basic Resources",
        "resource_family": ["organ","hide","bone"],
        "consumable": True,
    },
    "Monster Bone": {
        "location": "Basic Resources",
        "resource_family": ["bone"],
    },
    "Monster Organ": {
        "location": "Basic Resources",
        "resource_family": ["organ"],
        "consumable": True,
    },
    "Monster Hide": {
        "location": "Basic Resources",
        "resource_family": ["hide"],
    },
    "Scrap": {
        "location": "Basic Resources",
        "resource_family": ["scrap"],
    },
    "Broken Lantern": {
        "location": "Basic Resources",
        "resource_family": ["scrap"],
    },
    "Iron": {
        "location": "Strange Resources",
        "resource_family": ["scrap"],
    },
    "Leather": {
        "location": "Strange Resources",
        "resource_family": ["hide"],
    },
    "Elder Cat Teeth": {
        "location": "Strange Resources",
        "resource_family": ["bone"],
    },
    "Phoenix Crest": {
        "location": "Strange Resources",
        "resource_family": ["organ"],
    },
    "Second Heart": {
        "location": "Strange Resources",
        "resource_family": ["organ","bone"],
    },
    "Perfect Crucible": {
        "location": "Strange Resources",
    },
    "Legendary Horns": {
        "location": "Strange Resources",
        "resource_family": ["bone","scrap"],
    },
    "Gormite": {
        "location": "Strange Resources",
        "resource_family": ["scrap"],
        "expansion": "Gorm",
    },
    "Pure Bulb": {
        "location": "Strange Resources",
        "resource_family": ["organ"],
        "expansion": "Gorm",
    },
    "Stomach Lining": {
        "location": "Strange Resources",
        "resource_family": ["organ"],
        "expansion": "Gorm",
    },
    "Active Thyroid": {
        "location": "Strange Resources",
        "resource_family": ["organ"],
        "expansion": "Gorm",
    },
    "Fresh Acanthus": {
        "location": "Strange Resources",
    },
    "White Fur": {
        "location": "White Lion Resources",
        "resource_family": ["hide"],
    },
    "Lion Claw": {
        "location": "White Lion Resources",
        "resource_family": ["bone"],
    },
    "Eye of Cat": {
        "location": "White Lion Resources",
        "resource_family": ["organ"],
        "consumable": True,
    },
    "Great Cat Bones": {
        "location": "White Lion Resources",
        "resource_family": ["bone"],
    },
    "Shimmering Mane": {
        "location": "White Lion Resources",
        "resource_family": ["hide"],
    },
    "Lion Tail": {
        "location": "White Lion Resources",
        "resource_family": ["hide"],
    },
    "Curious Hand": {
        "location": "White Lion Resources",
        "resource_family": ["hide"],
    },
    "Golden Whiskers": {
        "location": "White Lion Resources",
        "resource_family": ["organ"],
    },
    "Sinew": {
        "location": "White Lion Resources",
        "resource_family": ["organ"],
    },
    "Lion Testes": {
        "location": "White Lion Resources",
        "resource_family": ["organ"],
    },
    "Pelt": {
        "location": "Screaming Antelope Resources",
        "resource_family": ["hide"],
    },
    "Shank Bone": {
        "location": "Screaming Antelope Resources",
        "resource_family": ["bone"],
    },
    "Large Flat Tooth": {
        "location": "Screaming Antelope Resources",
        "resource_family": ["bone"],
    },
    "Beast Steak": {
        "location": "Screaming Antelope Resources",
        "resource_family": ["organ"],
        "consumable": True,
    },
    "Muscly Gums": {
        "location": "Screaming Antelope Resources",
        "resource_family": ["organ"],
        "consumable": True,
    },
    "Spiral Horn": {
        "location": "Screaming Antelope Resources",
        "resource_family": ["bone"],
    },
    "Bladder": {
        "location": "Screaming Antelope Resources",
        "resource_family": ["organ"],
        "consumable": True,
    },
    "Screaming Brain": {
        "location": "Screaming Antelope Resources",
        "resource_family": ["organ"],
        "consumable": True,
    },
    "Tail Feathers": {
        "location": "Phoenix Resources",
        "resource_family": ["hide"],
    },
    "Phoenix Eye": {
        "location": "Phoenix Resources",
        "resource_family": ["organ", "scrap"],
    },
    "Phoenix Whisker": {
        "location": "Phoenix Resources",
        "resource_family": ["hide"],
    },
    "Pustules": {
        "location": "Phoenix Resources",
        "resource_family": ["organ"],
        "consumable": True,
    },
    "Small Feathers": {
        "location": "Phoenix Resources",
        "resource_family": ["hide"],
    },
    "Muculent Droppings": {
        "location": "Phoenix Resources",
        "resource_family": ["organ"],
    },
    "Wishbone": {
        "location": "Phoenix Resources",
        "resource_family": ["bone"],
    },
    "Shimmering Halo": {
        "location": "Phoenix Resources",
        "resource_family": ["organ"],
    },
    "Bird Beak": {
        "location": "Phoenix Resources",
        "resource_family": ["bone"],
    },
    "Black Skull": {
        "location": "Phoenix Resources",
        "resource_family": ["scrap","bone"],
    },
    "Small Hand Parasites": {
        "location": "Phoenix Resources",
        "resource_family": ["organ"],
    },
    "Phoenix Finger": {
        "location": "Phoenix Resources",
        "resource_family": ["bone"],
    },
    "Hollow Wing Bones": {
        "location": "Phoenix Resources",
        "resource_family": ["bone"],
    },
    "Rainbow Droppings": {
        "location": "Phoenix Resources",
        "resource_family": ["organ"],
        "consumable": True,
    },
    "White Lion Armor Set": {
        "location": "Catarium",
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
    "White Lion Gauntlets": {
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
        "type": "gear",
        "location": "Starting Gear",
    },
    "Cloth": {
        "type": "gear",
        "location": "Starting Gear",
    },
    "Rawhide Armor Set": {
        "location": "Skinnery",
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
    "Screaming Armor Set": {
        "location": "Stone Circle",
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
    "Lance Of Longinus": {
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
    "Zanbato": {
        "location": "Weapon Crafter",
    },
    "Counterweighted Axe": {
        "location": "Weapon Crafter",
    },
    "Scrap Sword": {
        "location": "Weapon Crafter",
    },
    "Scrap Dagger": {
        "location": "Weapon Crafter",
    },
    "Skullcap Hammer": {
        "location": "Weapon Crafter",
    },
    "Whistling Mace": {
        "location": "Weapon Crafter",
    },
    "Finger of God": {
        "location": "Weapon Crafter",
    },
    "Rainbow Katana": {
        "location": "Weapon Crafter",
    },
    "Blood Sheath": {
        "location": "Weapon Crafter",
    },
    "Nightmare Tick" : {
        "location": "Vermin",
    },
    "Lonely Ant" : {
        "location": "Vermin",
    },
    "Crab Spider" : {
        "location": "Vermin",
    },
    "Hissing Cockroach" : {
        "location": "Vermin",
    },
    "Sword Beetle" : {
        "location": "Vermin",
    },
    "Cyclops Fly" : {
        "location": "Vermin",
    },
    "Fairy Bottle": {
        "attribs": ["item","fragile","other"],
        "location": "Rare Gear",
		"expansion": "Beta Challenge Scenarios",
    },
    "Scout's Tunic": {
        "attribs": ["armor","set","leather"],
        "location": "Rare Gear",
		"expansion": "Beta Challenge Scenarios",
    },
    "Aya's Sword": {
        "attribs": ["weapon","melee","sword"],
        "location": "Rare Gear",
		"expansion": "Beta Challenge Scenarios",
    },
    "Aya's Spear": {
        "attribs": ["weapon","melee","spear"],
        "location": "Rare Gear",
		"expansion": "Beta Challenge Scenarios",
    },
    "Arm of the First Tree": {
        "attribs": ["weapon","melee","club"],
        "location": "Rare Gear",
		"expansion": "Beta Challenge Scenarios",
    },
    "Stone Arm": {
        "attribs": ["item","stone","heavy"],
        "location": "Rare Gear",
		"expansion": "Beta Challenge Scenarios",
    },
    "Giant Stone Face": {
        "attribs": ["weapon","melee","grand","heavy","two-handed","stone"],
        "location": "Rare Gear",
		"expansion": "Beta Challenge Scenarios",
    },
    "Petal Lantern": {
        "attribs": ["item","lantern","other"],
        "location": "Rare Gear",
		"expansion": "Beta Challenge Scenarios",
    },
    "Piranha Helm": {
        "attribs": ["armor","set","rawhide"],
        "location": "Rare Gear",
		"expansion": "Beta Challenge Scenarios",
    },
    "Cola Bottle Lantern": {
        "attribs": ["item","fragile","other"],
        "location": "Rare Gear",
		"expansion": "Beta Challenge Scenarios",
    },
    "Mammoth Hand": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["bone","hide","organ"],
    },
    "Jiggling Lard": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["hide","organ"],
    },
    "Stout Kidney": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["organ"],
        "consumable": True,
    },
    "Stout Heart": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["organ"],
    },
    "Stout Hide": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["hide"],
    },
    "Stout Vertebrae": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["bone"],
    },
    "Handed Skull": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["bone"],
    },
    "Dense Bone": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["bone"],
    },
    "Milky Eye": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["organ"],
    },
    "Gorm Brain": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["organ"],
    },
    "Acid Gland": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["organ"],
    },
    "Meaty Rib": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["bone","organ"],
    },
    "Preserved Caustic Dung": {
        "expansion": "Dung Beetle Knight",
        "location": "Strange Resources",
        "resource_family": ["organ"],
    },
    "Scell": {
        "expansion": "Dung Beetle Knight",
        "location": "Strange Resources",
        "resource_family": ["organ"],
    },
    "Beetle Horn": {
        "expansion": "Dung Beetle Knight",
        "location": "Dung Beetle Knight Resources",
        "resource_family": ["bone"],
    },
    "Century Fingernails": {
        "expansion": "Dung Beetle Knight",
        "location": "Dung Beetle Knight Resources",
        "resource_family": ["bone"],
    },
    "Century Shell": {
        "expansion": "Dung Beetle Knight",
        "location": "Dung Beetle Knight Resources",
        "resource_family": ["hide","scrap"],
    },
    "Compound Eye": {
        "expansion": "Dung Beetle Knight",
        "location": "Dung Beetle Knight Resources",
        "resource_family": ["organ"],
    },
    "Elytra": {
        "expansion": "Dung Beetle Knight",
        "location": "Dung Beetle Knight Resources",
        "resource_family": ["bone","hide","organ"],
    },
    "Scarab Shell": {
        "expansion": "Dung Beetle Knight",
        "location": "Dung Beetle Knight Resources",
        "resource_family": ["hide"],
    },
    "Scarab Wing": {
        "expansion": "Dung Beetle Knight",
        "location": "Dung Beetle Knight Resources",
        "resource_family": ["organ"],
    },
    "Underplate Fungus": {
        "expansion": "Dung Beetle Knight",
        "location": "Dung Beetle Knight Resources",
        "resource_family": ["hide"],
    },
    "Rolling Armor Set": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "DBK Errant Badge": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "Rainbow Wing Belt": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "Rubber Bone Harness": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "Scarab Circlet": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "Seasoned Monster Meat": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "The Beetle Bomb": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "Seasoned Monster Meat": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "Century Greaves": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "Century Shoulder Pads": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "Digging Claw": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "Calcified Zanbato": {
        "expansion": "Dung Beetle Knight",
        "location": "Black Harvest",
    },
    "Calcified Digging Claw": {
        "expansion": "Dung Beetle Knight",
        "location": "Black Harvest",
    },
    "Calcified Shoulder Pads": {
        "expansion": "Dung Beetle Knight",
        "location": "Black Harvest",
    },
    "Calcified Greaves": {
        "expansion": "Dung Beetle Knight",
        "location": "Black Harvest",
    },
    "Hidden Crimson Jewel": {
        "expansion": "Dung Beetle Knight",
        "location": "Rare Gear",
    },
    "Trash Crown": {
        "expansion": "Dung Beetle Knight",
        "location": "Rare Gear",
    },
    "Regenerating Blade": {
        "expansion": "Dung Beetle Knight",
        "location": "Rare Gear",
    },
    "Calcified Juggernaut Blade": {
        "expansion": "Dung Beetle Knight",
        "location": "Rare Gear",
    },
    "Hideous Disguise": {
        "expansion": "Lion Knight",
        "location": "Rare Gear",
    },
    "Lion Knight Badge": {
        "expansion": "Lion Knight",
        "location": "Rare Gear",
    },
    "Lion Knight's Left Claw": {
        "expansion": "Lion Knight",
        "location": "Rare Gear",
    },
    "Lion Knight's Right claw": {
        "expansion": "Lion Knight",
        "location": "Rare Gear",
    },
	"Ancient Lion Claws": {
		"expansion": "Lion God",
		"location": "Rare Gear",
	},
	"Golden Plate": {
		"expansion": "Lion God",
		"location": "Rare Gear",
	},
	"Lion God Statue": {
		"expansion": "Lion God",
		"location": "Rare Gear",
	},
	"Bone Witch Mehndi": {
		"expansion": "Lion God",
		"location": "Rare Gear",
	},
	"Butcher's Blood": {
		"expansion": "Lion God",
		"location": "Rare Gear",
	},
	"Glyph of Solitude": {
		"expansion": "Lion God",
		"location": "Rare Gear",
	},
	"Lantern Mehndi": {
		"expansion": "Lion God",
		"location": "Rare Gear",
	},
	"Death Mehndi": {
		"expansion": "Lion God",
		"location": "Rare Gear",
	},
	"Necromancer's Eye": {
		"expansion": "Lion God",
		"location": "Rare Gear",
	},
    "Canopic Jar": {
        "expansion": "Lion God",
        "location": "Strange Resources",
        "resource_family": ["organ","scrap"],
    },
    "Old Blue Box": {
        "expansion": "Lion God",
        "location": "Strange Resources",
        "resource_family": ["scrap"],
    },
    "Sarcophagus": {
        "expansion": "Lion God",
        "location": "Strange Resources",
        "resource_family": ["scrap"],
    },
    "Silver urn": {
        "expansion": "Lion God",
        "location": "Strange Resources",
        "resource_family": ["bone","scrap"],
    },
    "Triptych": {
        "expansion": "Lion God",
        "location": "Strange Resources",
        "resource_family": ["hide","scrap"],
    },
    "Jowls": {
        "expansion": "Sunstalker",
        "location": "Strange Resources",
        "resource_family": ["scrap"],
    },
    "Hagfish": {
        "expansion": "Sunstalker",
        "location": "Strange Resources",
        "resource_family": ["bone","hide"],
    },
    "Bugfish": {
        "expansion": "Sunstalker",
        "location": "Strange Resources",
        "resource_family": ["organ"],
    },
    "Salt": {
        "expansion": "Sunstalker",
        "location": "Strange Resources",
    },
    "Sun Stones": {
        "expansion": "Sunstalker",
        "location": "Strange Resources",
        "resource_family": ["bone"],
    },
    "1,000 Year Sunspot": {
        "expansion": "Sunstalker",
        "location": "Strange Resources",
        "resource_family": ["bone","organ"],
    },
    "3,000 Year Sunspot": {
        "expansion": "Sunstalker",
        "location": "Strange Resources",
        "resource_family": ["bone","organ","scrap"],
    },
    "Lonely Fruit": {
        "expansion": "Lonely Tree",
        "location": "Strange Resources",
    },
    "Drifting Dream Fruit": {
        "expansion": "Lonely Tree",
        "location": "Strange Resources",
    },
    "Jagged Marrow Fruit": {
        "expansion": "Lonely Tree",
        "location": "Strange Resources",
        "resource_family": ["bone","scrap"],
    },
    "Blistering Plasma Fruit": {
        "expansion": "Lonely Tree",
        "location": "Strange Resources",
        "resource_family": ["organ"],
    },
    "Blue Lantern": {
        "expansion": "White Box",
        "location": "Rare Gear",
    },
    "Dormant Twilight Cloak": {
        "expansion": "White Box",
        "location": "Rare Gear",
    },
    "Sword of Silence": {
        "expansion": "White Box",
        "location": "Rare Gear",
    },
    "Belt of Gender Swap": {
        "expansion": "White Box",
        "location": "Promo",
    },
    "Blood Plasma Gun": {
        "expansion": "White Box",
        "location": "Promo",
    },
    "Blood Plasma Katana": {
        "expansion": "White Box",
        "location": "Promo",
    },
    "Twilight Thong": {
        "expansion": "White Box",
        "location": "Promo",
    },
    "Bloodskin": {
        "expansion": "White Box",
        "location": "Rare Gear",
    },
    "Speaker Cult Knife": {
        "expansion": "White Box",
        "location": "Rare Gear",
    },
    "Vibrant Lantern": {
        "expansion": "White Box",
        "location": "Promo",
    },
    "Dying Lantern": {
        "expansion": "White Box",
        "location": "Promo",
    },
    "Prismatic Lantern": {
        "expansion": "White Box",
        "location": "Promo",
    },
    "Cloth Leggings": {
        "expansion": "White Box",
        "location": "Gear Recipe",
    },
    "Hard Breastplate": {
        "expansion": "White Box",
        "location": "Gear Recipe",
    },
    "Vagabond Armor Set": {
        "expansion": "White Box",
        "location": "Gear Recipe",
    },
    "Tabard": {
        "expansion": "White Box",
        "location": "Gear Recipe",
    },
    "White Dragon Gauntlets": {
        "expansion": "White Box",
        "location": "Ivory Carver",
    },
    "Radiant Heart": {
        "expansion": "Dragon King",
        "location": "Strange Resources",
        "resource_family": ["organ"],
    },
    "Pituitary Gland": {
        "expansion": "Dragon King",
        "location": "Strange Resources",
        "resource_family": ["organ"],
    },
    "Shining Liver": {
        "expansion": "Dragon King",
        "location": "Strange Resources",
        "resource_family": ["organ"],
    },
    "Red Vial": {
        "expansion": "Manhunter",
        "location": "Strange Resources",
    },
    "Crimson Vial": {
        "expansion": "Manhunter",
        "location": "Strange Resources",
        "resource_family": ["scrap"],
    },
    "Hunter's Heart": {
        "expansion": "Manhunter",
        "location": "Manhunter Gear",
    },
    "Tool Belt": {
        "expansion": "Manhunter",
        "location": "Manhunter Gear",
    },
    "Manhunter's Hat": {
        "expansion": "Manhunter",
        "location": "Manhunter Gear",
    },
    "Deathpact": {
        "expansion": "Manhunter",
        "location": "Manhunter Gear",
    },
    "Reverberating Lantern": {
        "expansion": "Manhunter",
        "location": "Manhunter Gear",
    },

}



#
#   Innovations
#

innovations = {
    "Choreia": {
        "type": "music",
        "expansion": "Spidicules",
        "endeavors": {
            "Spider Dance": {"cost": 1, "type": "music", "desc": "Nominate a male and a female survivor and roll 1d10."},
        },
    },
    "Silk-Refining": {
        "expansion": "Spidicules",
        "type": "other",
        "survival_limit": 1,
        "endeavors": {
            "end_0": {
                "hide_name": True,
                "type": "other",
                "desc": '<font class="kdm_font">g</font> <b>Silk Surgery</b>.',
                "cost": 1,
            },
           "end_1": {
                "hide_name": True,
                "type": "other",
                "desc": 'Convert 1 silk resource into 1 hide basic resource.',
                "cost": 1,
            },
           "end_2": {
                "hide_name": True,
                "type": "other",
                "desc": 'Spend 2 silk, 1 bone, and 1 organ to build the <b>Silk Mill</b> settlement location.',
                "remove_after": "Silk Mill",
                "cost": 1,
            },
        },
    },
    "Legless Ball": {
        "expansion": "Spidicules",
        "type": "other",
        "survivor_buff": '<b>Departing survivors</b> gain +2 insanity.',
        "subhead": 'Spend only 1 <font class="kdm_font">d</font> here per settlement phase.',
        "endeavors": {
            "end_0": {
                "hide_name": True,
                "type": "other",
                "desc": 'Add 1 <b>Web Silk</b> strange resource to settlement storage.',
                "cost": 1,
            },
           "end_1": {
                "hide_name": True,
                "type": "other",
                "desc": 'A survivor with 10+ insanity may put the Spidicules out of its misery. Gain the <b>Grinning Visage</b> rare gear and lose this innovation. (Archive this card.)',
                "cost": 1,
            },
        },
    },

    "Settlement Watch": {
        "type": "home",
        "expansion": "Manhunter",
        "survivor_buff": "<b>Departing Survivors</b> gain +2 survival when they depart for a Nemesis Encounter or a Special Showdown.",
        "endeavors": {
            "New Recruits": {"cost": 1, "type": "home",},
        },
    },
    "War Room": {
        "type": "education",
        "expansion": "Manhunter",
        "survival_limit": 1,
        "endeavors": {
            "Hunt Plan": {
                "hide_name": True,
                "type": "education",
                "desc": 'The hunt team makes a plan. The group may reroll 1 <b>Hunt Event Table</b> result (d100) this lantern year. They must reroll before performing the event.',
                "cost": 1
            },
        },
    },
    "Crimson Candy": {
        "type": "science",
        "expansion": "Manhunter",
        "survivor_buff": "At the start of the showdown, each survivor gains &#9733; survival.",
        "endeavors": {
            "Crimson Cannibalism": {"cost": 1, "type": "science"},
        },
    },

    "Dragon Speech": {
        "type": "starting innovation",
        "expansion": "Dragon King",
        "survival_limit": 1,
        "survival_action": "Encourage",
        "consequences": ["Hovel", "Inner Lantern", "Drums", "Paint", "Symposium", "Ammonia"],
    },
    "Arena": {
        "type": "education",
        "expansion": "Dragon King",
        "endeavors": {
            "Spar": {"cost": 1, "type": "education"},
        },
    },
    "Empire": {
        "type": "home",
        "expansion": "Dragon King",
        "survivor_buff": 'Newborn survivors are born with +1 permanent strength and the <font class="maroon_text">Pristine</font> ability.',
        "newborn_survivor": {"Strength": 1, "abilities_and_impairments": "Pristine"},
    },
    "Bloodline": {
        "type": "home",
        "expansion": "Dragon King",
        "consequences": ["Empire",],
        "survivor_buff": """Newborn survivors inherit the following from their parents:<ul><li>The <font class="maroon_text">Oracle's Eye</font>, <font class="maroon_text">Iridescent Hide</font>, or <font class="maroon_text">Pristine</font> ability (choose 1)</li><li>1 <b>Surname</b></li><li>Half of one parent's weapon proficiency levels (rounded up)</li></ul>""",
    },
    "Radiating Orb": {
        "type": "science",
        "expansion": "Dragon King",
        "settlement_buff": "<b>Departing Survivors</b> and newborn survivors gain +1 survival.<br/><b>Departing survivors</b> with a constellation gain +1 survival.",
        "consequences": ["Cooking", "Scrap Smelting"],
        "newborn_survivor": {"survival": 1},
    },

    "Petal Spiral": {
        "type": "music",
        "expansion": "Flower Knight",
        "endeavors": {
            "Trace Petals": {"cost": 1, "type": "music"},
        },
    },

    "Dark Water Research": {
        "type": "science",
        "expansion": "Slenderman",
        "endeavors": {
            '<font class="kdm_font">g</font> Light-Forging': {"cost": 2, "type": "science"},
            "end_0": {
                "hide_name": True,
                "type": "science",
                "desc": 'Spend 2x resources and 2x Dark Water to increase the level of <b>Dark Water Research</b> by 1, to a maximum of 3. (Update your settlement record sheet.)',
                "cost": 1,
            },
        },
        "levels": 3,
    },
    "Sun Language": {
        "expansion": "Sunstalker",
        "type": "starting innovation",
        "survival_limit": 1,
        "survival_action": "Embolden",
        "consequences": ["Ammonia", "Drums", "Hovel", "Paint", "Symposium", "Hands of the Sun"],
    },
    "Hands of the Sun" : {
        "expansion": "Sunstalker",
        "type": "faith",
        "survival_action": "Overcharge",
        "consequences": ["Aquarobics", "Sauna Shrine"],
    },
    "Aquarobics" : {
        "expansion": "Sunstalker",
        "type": "faith",
        "survival_limit": 1,
        "endeavors": {
            "Underwater Train": {"cost": 1, "type": "faith"},
        },
    },
    "Sauna Shrine" : {
        "expansion": "Sunstalker",
        "type": "faith",
        "endeavors": {
            "Tribute": {"cost": 1, "type": "faith"},
        },
        "departure_buff": "When survivors <b>depart</b> for a Nemesis Encounter or Special Showdown, they gain +10 survival.",
    },
    "Umbilical Bank" : {
        "expansion": "Sunstalker",
        "consequences": ["Pottery"],
        "type": "science",
        "settlement_buff": "When a survivor is born, you may add 1 <b>Life String</b> strange resource to storage.",
        "endeavors": {
            '<font class="kdm_font">g</font> Umbilical Symbiosis': {"cost": 1, "type": "science"},
            "Special Innovate": {"cost": 1, "desc": "Pottery (3 x organ)", "remove_after": "Pottery"},
        },
    },
    "Filleting Table" : {
        "expansion": "Sunstalker",
        "type": "science",
        "settlement_buff": "Once per settlement phase, if the <b>returning survivors</b> are victorious, gain 1 random basic resource.",
        "endeavors": {
            "Advanced Cutting": {"cost": 1, "type": "science"},
        },
    },
    "Shadow Dancing" : {
        "expansion": "Sunstalker",
        "type": "home",
        "endeavors": {
            "Final Dance": {"cost": 1, "type": "home"},
        },
    },

	"The Knowledge Worm" :{
		"type": "other",
		"expansion": "Lion God",
		"settlement_buff": 'At the start of each settlement phase, add 1 scrap to settlement storage.<br/><b>Departing Survivors</b> gain +3 survival and +3 insanity. If any of those survivors have 10+ insanity, <font class="kdm_font">g</font> <b>A Gracious Host</b>.',
	},

    "Stoic Statue" : {
        "consequences": ["Black Mask", "White Mask"],
        "expansion": "Lion Knight",
        "type": "other",
        "endeavors": {
            "Worship the monster": {"cost": 1, "type": "other"}
        },
    },
    "Black Mask" : {
        "consequences": ["White Mask"],
        "expansion": "Lion Knight",
        "type": "other",
        "endeavors": {
            "Visit the retinue": {"cost": 1, "type": "other"},
            "Face the monster": {"cost": 2, "type": "other"},
        },
    },
    "White Mask" : {
        "consequences": ["Black Mask"],
        "expansion": "Lion Knight",
        "type": "other",
        "endeavors": {
            "Visit the retinue": {"cost": 1, "type": "other"},
            "Leave the monster an offering": {"cost": 1, "type": "other"},
        },
    },

    "Subterranean Agriculture": {
        "expansion": "Dung Beetle Knight",
        "type": "science",
        "endeavors": {
            "Build": {"cost": 1, "desc": "Wet Resin Crafter (2 x organ, 2 x bone)", "remove_after": "Wet Resin Crafter"},
            "Underground Sow": {
                "hide_name": True,
                "type": "science",
                "desc": 'If <b>Black Harvest</b> is not on the timeline, <font class="kdm_font">g</font> <b>Underground Sow</b>.',
                "cost": 1
            },
           "Underground Fertilize": {
                "hide_name": True,
                "type": "science",
                "desc": 'If <b>Black Harvest</b> is on the timeline, you may spend 1 Preserved Caustic Dung to increase its rank by 1 to a maximum rank of 3. Limit, once per settlement phase.',
                "cost": 1,
            },
        },
    },
    "Round Stone Training": {
        "expansion": "Dung Beetle Knight",
        "type": "education",
        "endeavors": {
            "Train": {"cost": 1, "type": "education"},
        },
    },

    "Nigredo": {
        "expansion": "Gorm",
        "type": "science",
        "survival_limit": 1,
        "consequences": ["Albedo"],
        "endeavors": {
            "Nigredo": {"cost": 1, "type": "science"},
        },
    },
    "Albedo": {
        "expansion": "Gorm",
        "type": "science",
        "consequences": ["Citrinitas"],
        "endeavors": {
            "Albedo": {"cost": 2, "type": "science"},
        },
    },
    "Citrinitas": {
        "expansion": "Gorm",
        "type": "science",
        "survival_limit": 1,
        "consequences": ["Rubedo"],
        "endeavors": {
            "Citrinitas": {"cost": 3, "type": "science"},
        },
    },
    "Rubedo": {
        "expansion": "Gorm",
        "type": "science",
        "endeavors": {
            "Rubedo": {"cost": 4, "type": "science"},
        },
    },

    "Graves": {
        "type": "principle",
        "milestone": "First time death count is updated",
        "settlement_buff": 'All new survivors gain +1 understanding.<br/>When a survivor dies during the hunt or showdown phase, gain +2 <font class="kdm_font">d</font>.<br/>When a survivor dies during the settlement phase, gain +1 <font class="kdm_font">d</font>.',
        "survivor_buff": "All new survivors gain +1 understanding.",
        "new_survivor": {"Understanding": 1},
    },
    "Cannibalize": {
        "type": "principle",
        "milestone": "First time death count is updated",
        "survival_limit": 1,
        "settlement_buff": "Whenever a survivor dies, draw one basic resource and add it to the settlement storage.",
    },
    "Barbaric": {
        "type": "principle",
        "survival_limit": 1,
        "survivor_buff": "All current and newborn survivors gain +1 permanent Strength.",
        "current_survivor": {"Strength": 1},
        "newborn_survivor": {"Strength": 1},
    },
    "Romantic": {
        "type": "principle",
        "survival_limit": 1,
        "settlement_buff": "You may innovate one additional time during the settlement phase. In addition, all current and newborn survivors gain +1 understanding.",
        "survivor_buff": "All current and newborn survivors gain +1 understanding.",
        "current_survivor": {"Understanding": 1},
        "newborn_survivor": {"Understanding": 1},
    },
    "Collective Toil": {
        "type": "principle",
        "milestone": "Population reaches 15",
        "settlement_buff": "At the start of the settlement phase, gain +1 Endeavor for every 10 population.",
    },
    "Accept Darkness": {
        "type": "principle",
        "milestone": "Population reaches 15",
        "survivor_buff": "Add +2 to all Brain Trauma Rolls.",
    },
    "Protect the Young": {
        "type": "principle",
        "milestone": "First child is born",
        "settlement_buff": "When rolling on the Intimacy story event, roll twice and pick one result.",
    },
    "Survival of the Fittest": {
        "type": "principle",
        "milestone": "First child is born",
        "survival_limit": 1,
        "settlement_buff": "When rolling on the Intimacy story event, roll twice and pick the lowest result. All current and newborn survivors gain +1 strength and evasion.<br/>Once per lifetime, a survivor may reroll a single roll result. They must keep this new result.",
        "survivor_buff": "All current and newborn survivors gain +1 strength and evasion.",
        "current_survivor": {"Strength": 1, "Evasion": 1},
        "newborn_survivor": {"Strength": 1, "Evasion": 1},
    },

    "Clan of Death": {
        "type": "home",
        "survivor_buff": "All newborn survivors gain <b>+1 Accuracy</b>, <b>+1 Strength</b> and <b>+1 Evasion</b>.",
        "newborn_survivor": {"Strength": 1, "Accuracy": 1, "Evasion": 1},
    },
    "Sacrifice": {
        "type": "faith",
        "endeavors": {
            "Death Ritual": {"type": "faith", "cost": 1,},
        },
    },
    "Scarification": {
        "type": "faith",
        "endeavors": {
            "Initiation": {"cost": 1, "type": "faith"},
        },
    },
    "Records": {
        "type": "education",
        "endeavors": {
            "Knowledge": {"cost": 2, "type": "education"},
        },
    },
    "Shrine": {
        "type": "faith",
        "consequences": ["Sacrifice"],
        "endeavors": {
            "Armor Ritual": {"cost": 1, "type": "faith"},
        },
    },
    "Scrap Smelting": {
        "type": "science",
        "special_innovate": ("locations","Weapon Crafter"),
        "endeavors": {
            "Purification": {"cost": 1, "type": "science"},
            "Build": {"cost": 1, "desc": "Blacksmith (6 x bone, 3 x scrap)", "remove_after": "Blacksmith"},
        },
    },
    "Cooking": {
        "type": "science",
        "survival_limit": 1,
        "endeavors": {
            "Culinary Inspiration": {"cost": 1, "type": "science"},
        },
    },
    "Drums": {
        "type": "music",
        "consequences": ["Song of the Brave", "Forbidden Dance"],
        "endeavors": {
            "Bone Beats": {"cost": 1, "type": "music"},
        },
    },
    "Inner Lantern": {
        "type": "faith",
        "consequences": ["Shrine", "Scarification"],
        "survival_action": "Surge",
    },
    "Symposium": {
        "type": "education",
        "consequences": ["Nightmare Training", "Storytelling",],
        "survival_limit": 1,
        "settlement_buff": "When a survivor innovates, draw an additional 2 Innovation Cards to choose from.",
    },
    "Hovel": {
        "type": "home",
        "consequences": ["Partnership", "Family", "Bed", "Shadow Dancing","Bloodline","Settlement Watch"],
        "departure_buff": "Departing survivors gain +1 survival.",
        "survival_limit": 1,
    },
    "Storytelling": {
        "type": "education",
        "consequences": ["Records","War Room"],
        "survival_limit": 1,
        "endeavors": {
            "Tale as Old as Time": {"cost": 2, "type": "education"},
        },
    },
    "Nightmare Training": {
        "type": "education",
        "consequences": ["Round Stone Training"],
        "endeavors": {
            "Train": {"cost": 1, "type": "education"},
        },
    },
    "Momento Mori": {
        "type": "art",
        "endeavors": {
            "Momento Mori": {"cost": 1, "type": "art"},
        },
    },
    "Face Painting": {
        "type": "art",
        "endeavors": {
            "Battle Paint": {"cost": 1, "type": "art"},
            "Founder's Eye": {"cost": 1, "type": "art"},
        },
    },
    "Pottery": {
        "type": "art",
        "survival_limit": 1,
        "settlement_buff": "If the settlement loses all its resources, you may select up to two resources and keep them.",
        "endeavors": {
            "Build": {"cost": 1, "desc": "Barber Surgeon (3 x organ, 1 x scrap)", "remove_after": "Barber Surgeon"},
        },
    },
    "Sculpture": {
        "type": "art",
        "consequences": ["Pottery"],
        "survival_limit": 1,
        "departure_buff": "Departing survivors gain +2 survival when they depart for a Nemesis Encounter.",
    },
    "Paint": {
        "type": "art",
        "consequences": ["Pictograph", "Sculpture", "Face Painting"],
        "survival_action": "Dash",
    },
    "Pictograph": {
        "type": "art",
        "consequences": ["Momento Mori"],
#        "survivor_buff": 'Anytime during the hunt or showdown phase, a survivor may <font class="kdm_font">g</font> <b>Run Away</b>.',
        "survivor_buff": 'At the start of a standing survivor\'s act, they may trigger the <font class="kdm_font">g</font> <b>Run Away</b> story event. Limit, once per act.',
    },
    "Heart Flute": {
        "type": "music",
        "endeavors": {
            "Devil's Melody": {"cost": 1, "type": "music"},
        },
    },
    "Forbidden Dance": {
        "type": "music",
        "consequences": ["Petal Spiral", "Choreia"],
        "endeavors": {
            "Fever Dance": {"cost": 1, "type": "music"},
        },
    },
    "Bed": {
        "type": "home",
        "survival_limit": 1,
        "endeavors": {
            "Rest": {"cost": 1, "type": "home"},
        },
    },
    "Bloodletting": {
        "type": "science",
        "endeavors": {
            "Breathing a Vein": {"cost": 1, "type": "science"},
        },
    },
    "Saga": {
        "type": "music",
        "survivor_buff": "All newborn survivors gain +2 hunt experience and +2 survival from knowing the epic.",
        "newborn_survivor": {"hunt_xp": 2, "survival": 2},
    },
    "Family": {
        "type": "home",
        "consequences": ["Clan of Death"],
        "departure_buff": "Departing survivors gain +1 survival.",
        "settlement_buff": "Survivors nominated for intimacy may give themselves a surname if they do not have one. A newborn survivor inherits the surname of one parent, their weapon type and half (rounded down) of their weapon proficiency levels.",
    },
    "Song of the Brave": {
        "type": "music",
        "consequences": ["Saga",],
        "survivor_buff": "All non-deaf survivors add +1 to their roll results on the Overwhelming Darkness story event.",
    },
    "Language": {
        "type": "starting innovation",
        "consequences": ["Hovel", "Inner Lantern", "Drums", "Paint", "Symposium", "Ammonia"],
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
        "always_available": True,
    },
    "Final Fighting Art": {
        "type": "education",
        "survival_limit": 1,
        "always_available": True,
    },
    "Ultimate Weapon": {
        "type": "science",
        "survival_limit": 1,
        "always_available": True,
    },
    "Guidepost": {
        "type": "other",
        "departure_buff": "Departing survivors gain +1 survival.",
        "always_available": True,
    },
    "Partnership": {
        "always_available": True,
        "type": "home",
        "endeavors": {
            "Partner": {"cost": 2, "type": "home"},
        },
    },
}



#
#   Settlement Sheet assets
#

resources = {
    "White Lion Resources": {
        "color": "DCD900",
    },
    "Screaming Antelope Resources": {
        "color": "DCD900",
    },
    "Phoenix Resources": {
        "color": "DCD900",
    },
    "Spidicules Resources": {
        "color": "DCD900",
    },
    "Flower Knight Resources": {
        "expansion": "Flower Knight",
        "color": "DCD900",
    },
    "Gorm Resources": {
        "expansion": "Gorm",
        "color": "DCD900",
    },
    "Sunstalker Resources": {
        "expansion": "Sunstalker",
        "color": "DCD900",
    },
    "Dung Beetle Knight Resources": {
        "expansion": "Dung Beetle Knight",
        "color": "DCD900",
    },
    "Dragon King Resources": {
        "expansion": "Dragon King",
        "color": "DCD900",
    },
    "Basic Resources": {
        "color": "B1FB17",
    },
    "Vermin": {
        "color": "99CC66",
    },
    "Strange Resources": {
        "color": "9DC209",
    },
    "Starting Gear": {
        "color": "CCC",
    },
}




#
#   Survivor Sheet assets
#

survivor_attributes = ["Movement", "Accuracy", "Strength", "Evasion", "Luck", "Speed"]


#
#   Expansion assets and definitions
#

expansions = {
    "Beta Challenge Scenarios": {
        "subtitle": "Enables abilities & impairments, disorders, items etc. included in the Beta Challenge Scenarios.",
        "enforce_survival_limit": False,
        "special_rules": [
        {"name": "Survival Limit Warning!", "desc": "Survival Limit is not automatically enforced by the Manager when Beta Challenge Scenarios content is enabled.", "bg_color": "F87217", "font_color": "FFF"},
        ],
    },
    "Green Knight Armor": {
        "always_available": ["Green Knight Armor"],
    },
    "Slenderman": {
        "always_available": ["Dark Water Research"],
    },
    "Dragon King": {
        "always_available": ["Dragon Armory"],
        "timeline_add": [
            {"ly": 8, "type": "story_event", "name": "Glowing Crater", "excluded_campaign": "People of the Stars"},
        ],
    },
    "Gorm": {
        "always_available": ["Gormery", "Gormchymist", "Nigredo"],
        "timeline_add": [
            {"ly": 1, "type": "story_event", "name": "The Approaching Storm"},
            {"ly": 2, "type": "settlement_event", "name": "Gorm Climate"},
        ],
    },
    "Manhunter": {
        "always_available": ["War Room", "Settlement Watch", "Crimson Candy"],
        "always_available_nemesis": "Manhunter",
        "timeline_add": [
            {"ly": 5, "type": "story_event", "name": "The Hanged Man"},
            {"ly": 10, "type": "special_showdown", "name": "Special Showdown - Manhunter"},
            {"ly": 16, "type": "special_showdown", "name": "Special Showdown - Manhunter"},
            {"ly": 22, "type": "special_showdown", "name": "Special Showdown - Manhunter"},
        ],
    },
    "Spidicules": {
        "always_available": ["Legless Ball","Silk Mill","Silk-Refining"],
        "timeline_add": [
            {"ly": 2, "type": "story_event", "name": "Young Rivals"},
        ],
        "timeline_rm": [
            {"ly": 2, "type": "story_event", "name": "Endless Screams"},
        ],
    },
    "Dung Beetle Knight": {
        "always_available": ["Wet Resin Crafter","Subterranean Agriculture"],
        "timeline_add": [
            {"ly": 8, "type": "story_event", "name": "Rumbling in the Dark"},
        ],
    },
    "Lion Knight": {
        "always_available": ["Stoic Statue"],
        "timeline_add": [
            {"ly": 6, "type": "story_event", "name": "An Uninvited Guest"},
            {"ly": 8, "type": "story_event", "name": "Places, Everyone!"},
            {"ly": 12, "type": "story_event", "name": "Places, Everyone!"},
            {"ly": 16, "type": "story_event", "name": "Places, Everyone!"},
        ],
    },
    "Lion God": {
        "always_available": ["The Knowledge Worm"],
        "timeline_add": [
            {"ly": 13, "type": "story_event", "name": "The Silver City"},
        ],
    },
    "Sunstalker": {
        "always_available": ["The Sun", "Sun Language", "Umbilical Bank","Skyreef Sanctuary"],
        "timeline_add": [
            {"ly": 8, "type": "story_event", "name": "Promise Under the Sun", "excluded_campaign": "People of the Sun"},
        ],
    },
    "Lonely Tree": {
        "always_available_nemesis": "Lonely Tree",
    },
    "White Box": {
        "subtitle": "Enables promo and early-release items and abilities & impairments included in the so-called 'White Box' collection of survivor minis (released at Gen Con 2016).",
    },
    "Flower Knight": {
        "timeline_add": [{"ly": 5, "type": "story_event", "name": "A Crone's Tale", "excluded_campaign": "The Bloom People"}],
    },
}


# this is a collection of milestones that might or might not be used in a given
#   campaign. Campaign assets don't default for this stuff, so you've got to
#   reference all required milestones when defining the asset below
milestones = {
    "first_child": {
        "sort_order": 0,
        "story_event": "Principle: New Life",
    },
    "first_death": {
        "sort_order": 1,
        "story_event": "Principle: Death",
        "add_to_timeline": 'int(self.settlement["death_count"]) >= 1',
    },
    "pop_15": {
        "sort_order": 2,
        "story_event": "Principle: Society",
        "add_to_timeline": 'int(self.settlement["population"]) >= 15',
    },
    "innovations_5": {
        "sort_order": 3,
        "story_event": "Hooded Knight",
        "add_to_timeline": 'len(self.settlement["innovations"]) >= 5',
    },
    "innovations_8": {
        "sort_order": 4,
        "story_event": "Edged Tonometry",
        "add_to_timeline": 'len(self.settlement["innovations"]) >= 8',
    },
    "game_over": {
        "sort_order": 10,
        "story_event": "Game Over",
        "add_to_timeline": 'int(self.settlement["death_count"]) >= 1 and int(self.settlement["population"]) == 0 and int(self.settlement["lantern_year"]) >= 1',
    },
}

# create generic principle definitions here, just like milestones above
principles = {
    "new_life": {
        "sort_order": 0,
        "milestone": "First child is born",
        "show_controls": ['"First child is born" in self.settlement["milestone_story_events"]'], 
        "options": ["Protect the Young","Survival of the Fittest"],
    },
    "death": {
        "sort_order": 1,
        "milestone": "First time death count is updated",
        "show_controls": ['int(self.settlement["death_count"]) >= 1'],
        "options": ["Cannibalize","Graves"]
    },
    "society": {
        "sort_order": 2,
        "milestone": "Population reaches 15",
        "options": ["Collective Toil","Accept Darkness"],
        "show_controls": ['int(self.settlement["population"]) >= 15'],
    },
    "conviction": {
        "sort_order": 3,
        "options": ["Barbaric","Romantic"],
        "show_controls": ['int(self.settlement["lantern_year"]) >= 12'],
    },
}


# temporary/transitional lookup table for campaign names
campaign_look_up = {
    "people_of_the_sun": "People of the Sun",
    "people_of_the_lantern": "People of the Lantern",
    "people_of_the_skull": "People of the Skull",
    "people_of_the_stars": "People of the Stars",
    "the_bloom_people": "The Bloom People",
    "the_green_knight": "The Green Knight",
    "People of the Sun": "People of the Sun",
    "People of the Lantern": "People of the Lantern",
    "People of the Skull": "People of the Skull",
    "People of the Stars": "People of the Stars",
    "The Bloom People": "The Bloom People",
    "The Green Knight": "The Green Knight",
}



core = {
    'accessory': {
        'name': 'Accessory',
        'type': 'keyword',
        'desc': """A gear special rule. Accessory gear may be worn in addition to armor on a hit location. Each accessory specifies the hit location it covers.""",
    },
    'ammo_bow': {
        'name': 'Ammo - Bow',
        'type': 'special_rule',
        'desc': """A gear special rule. You must have a bow in your gear grid to activate this card. Ammo has the range of a bow in your gear grid.""",
    },
    'ammuntion': {
        'name': 'Ammunition',
        'type': 'keyword',
        'desc': """A gear keyword. This gear is ammunition for another weapon gear.""",
    },
    'archive': {
        'name': 'Archive',
        'type': 'keyword',
        'desc': """Remove this card from play and return it to the game box. Unless it is recorded into settlement storage or the survivor's record sheet, any archived card is permanently lost.""",
    },
    'arrow': {
        'name': 'Arrow',
        'type': 'keyword',
        'desc': """A gear keyword. This gear card is an arrow.""",
    },
    'balm': {
        'name': 'Balm',
        'type': 'keyword',
        'desc': """A gear keyword. Balm items work by rubbing them on a survivor's skin.""",
    },
    'block': {
        'name': 'Block X',
        'type': 'special_rule',
        'desc': """A gear special rule. Spend activation to ignore X hits the next time you are attacked. Lasts until your next act. A survivor may not use block more than once per attack.""",
    },
    'bone': {
        'name': 'Bone',
        'type': 'keyword',
        'desc': """A gear keyword. Bone is one of the primary materials used to craft this gear.""",
    },
    'consume': {
        'name': 'Consume',
        'type': 'special_rule',
        'desc': """A special rule. This consumable gear or resources may be ingested by survivors for a listed result. Some are archived after use.""",
        'related': ['consumable','archive'],
    },
    'consumable': {
        'name': 'Consumable',
        'type': 'keyword',
        'desc': """A keyword. This may be consumed by survivors.""",
        'related': ['consume'],
    },
    'cumbersome': {
        'name': 'Cumbersome',
        'type': 'special_rule',
        'desc': """A gear special rule. Survivors must spend both movement and activation to activate Cumbersome gear. Ignore this if the weapon is activated indirectly (Pounce. Charge, etc).""",
    },
    'cursed': {
        'name': 'Cursed',
        'type': 'special_rule',
        'desc': """A gear special rule. This gear cannot be removed from the gear grid for any reason. If the survivor dies, archive this gear.""",
        'related': ['archive'],
    },
    'deadly': {
        'name': 'Deadly',
        'type': 'special_rule',
        'desc': """A gear special rule. Gain +l luck while attacking with this weapon. This increases the odds of inflicting critical wounds.""",
    },
    'deflect': {
        'name': 'Deflect X',
        'type': 'special_rule',
        'desc': """A gear special rule, when you Deflect X, gain (or lose) deflect tokens until you have X of them. When you are hit, if you have any deflect tokens, you ignore that hit and lose a deflect token. When you Deflect X, you lose the benefits of Block.""",
    },
    'devastating': {
        'name': 'Devastating X',
        'type': 'special_rule',
        'desc': """A gear special rule. When a devastating weapon wounds a monster, it will inflict X additional wounds.""",
    },
    'early_iron': {
        'name': 'Early Iron',
        'type': 'special_rule',
        'desc': """A gear special rule. When any of your attack roll results are a l, cancel your attack.""",
    },
    'feather': {
        'name': 'Feather',
        'type': 'keyword',
        'desc': """A gear keyword. This gear is substantively crafted of feathers.""",
    },
    'finesse': {
        'name': 'Finesse',
        'type': 'keyword',
        'desc': """A gear keyword. This gear requires finesse to use. This keyword does not interact with the core game in any way and is one of those annoying keywords for expansions.""",
    },
    'flammable': {
        'name': 'Flammable',
        'type': 'keyword',
        'desc': """A gear keyword. Fire can destroy this gear.""",
    },
    'fragile': {
        'name': 'Fragile',
        'type': 'keyword',
        'desc': """A gear keyword. This gear is easily broken.""",
    },
    'frail': {
        'name': 'Frail',
        'type': 'special_rule',
        'desc': """A gear special rule. Frail weapons are destroyed if a survivor attempts to wound a Super-dense location with them. Archive the weapon at the end of the attack.""",
        'related': ['archive'],
    },
    'fur': {
        'name': 'Fur',
        'type': 'keyword',
        'desc': """ A gear keyword. This gear is substantively crafted of thick fur.""",
    },
    'heavy': {
        'name': 'Heavy',
        'type': 'keyword',
        'desc': """A gear keyword. This gear has substantial weight.""",
    },
    'herb': {
        'name': 'Hide',
        'type': 'keyword',
        'desc': """A gear keyword. An item primarily made of herbs.""",
    },
    'instrument': {
        'name': 'Instrument',
        'type': 'keyword',
        'desc': """A gear keyword. This gear can be used to play music.""",
    },
    'irreplaceable': {
        'name': 'Irreplaceable',
        'type': 'special_rule',
        'desc': """A gear special rule. If a survivor dies, archive all irreplaceable gear in their gear grids.""",
        'related': ['archive'],
    },
    'jewelry': {
        'name': 'Jewelry',
        'type': 'keyword',
        'desc': """A gear keyword. Decorative and functional!""",
    },
    'lantern': {
        'name': 'Lantern',
        'type': 'keyword',
        'desc': """A gear keyword. A lantern illuminates the darkness.""",
    },
    'leather': {
        'name': 'Leather',
        'type': 'keyword',
        'desc': """A gear keyword. Cured hides are a crucial component of this gear.""",
    },
    'melee': {
        'name': 'Melee',
        'type': 'keyword',
        'desc': """ A weapon gear keyword. To attack with a melee weapon, survivors must be in a space adjacent to the monster. Melee weapons with Reach can attack from further away.""",
    },
    'metal': {
        'name': 'Metal',
        'type': 'keyword',
        'desc': """A gear keyword. This gear is substantively crafted of metal.""",
    },
    'noisy': {
        'name': 'Noisy',
        'type': 'keyword',
        'desc': """A gear keyword. This gear Is hard to keep quiet.""",
    },
    'obstacle': {
        'name': 'Obstacle',
        'type': 'keyword',
        'desc': """A terrain rule. This terrain blocks survivor and monster field of view. Interrupting ranged weapon attacks and monster targeting. To check if field of view is blocked, draw an imaginary line from the center of the miniature's base to the center of the intended target's base. If the line comes in contact with a space occupied by an obstacle, the field of view is blocked and the target is not In field of view.""",
    },
    'other': {
        'name': 'Other',
        'type': 'keyword',
        'desc': """A gear keyword. The effects of this gear are otherworldly.""",
    },
    'outfit': {
        'name': 'Outfit',
        'type': 'special_rule',
        'desc': """This completes an armor set if you're wearing the rest of the set and it shares a material keyword with the missing armor gear. For example, if you're wearing an Oxidized Lantern Helm and Phoenix Armor on every other hit location, you would gain the Phoenix Armor Set bonus because the Phoenix Helm also has the metal keyword.""",
    },
    'paired': {
        'name': 'Paired',
        'type': 'special_rule',
        'desc': """A gear special rule. Paired weapons are two Identical weapons that can be used as one. Add the speed of the second weapon when attacking with the first. These weapons must have the same name, and both must be In your gear grid.""",
    },
    'pickaxe': {
        'name': 'Pickaxe',
        'type': 'keyword',
        'desc': """A gear keyword, in certain situations, this can be used to mine minerals.""",
    },
    'range': {
        'name': 'Range',
        'type': 'special_rule',
        'desc': """A gear special rule. Survivors this many or fewer spaces away from a monster may attack with this weapon. Ranged weapons cannot be used If field of view to the monster is blocked (by terrain with the Obstacle rule).""",
        'related': ['range','obstacle'],
    },
    'ranged': {
        'name': 'Ranged',
        'type': 'keyword',
        'desc': """A gear keyword. A ranged weapon, like a bow or dart, allows survivors to attack from a distance.""",
        'related': ['range'],
    },
    'rawhide': {
        'name': 'Rawhide',
        'type': 'keyword',
        'desc': """A gear keyword. This gear is crafted of uncured hides.""",
    },
    'reach': {
        'name': 'Reach',
        'type': 'special_rule',
        'desc': """A gear special rule. Reach weapons are long enough to attack monsters when the survivor Is not adjacent. Reach specifies the maximum number of spaces away that a survivor can attack with this weapon."""
    },
    'savage': {
        'name': 'Savage',
        'type': 'special_rule',
        'desc': """A gear special rule. After the first critical wound in an attack, savage weapons cause 1 additional wound. This rule does not trigger on Impervious hit locations.""",
    },
    'selfish': {
        'name': 'Selfish',
        'type': 'special_rule',
        'desc': """A gear special rule. A gear with this rule may not be in a same gear grid with any gear with the "other" keyword.""",
    },
    'sentient': {
        'name': 'Sentient',
        'type': 'special_rule',
        'desc': """A gear special rule. A survivor must be insane to activate this gear.""",
    },
    'set': {
        'name': 'Set',
        'type': 'keyword',
        'desc': """A gear keyword listed on some armor cards. This means this armor is part of an armor set.""",
    },
    'sharp': {
        'name': 'Sharp',
        'type': 'special_rule',
        'desc': """A gear special rule. Add 1dlO strength to each wound attempt using this gear. This d1O is not a wound roll, and cannot cause critical wounds.""",
    },
    'sickle': {
        'name': 'Sickle',
        'type': 'keyword',
        'desc': """A gear keyword. In certain situations, this can be used to harvest herbs.""",
    },
    'slow': {
        'name': 'Slow',
        'type': 'special_rule',
        'desc': """A gear special rule. Slow weapons always have an attack speed of 1. Do not add speed modifiers.""",
    },
    'soluble': {
        'name': 'Soluble',
        'type': 'keyword',
        'desc': """A gear keyword. Able to be dissolved in liquid.""",
    },
    'stinky': {
        'name': 'Stinky',
        'type': 'keyword',
        'desc': """A gear keyword. This item has a strong odor.""",
    },
    'tool': {
        'name': 'Tool',
        'type': 'keyword',
        'desc': """A gear keyword. Some tools trigger story events or grant bonuses.""",
    },
    'two_handed': {
        'name': 'Two-handed',
        'type': 'keyword',
        'desc': """A gear keyword. This weapon requires two hands to use. Some gear and rules do not work with two-handed weapons.""",
    },
    'unique': {
        'name': 'Unique',
        'type': 'special_rule',
        'desc': """A gear special rule. A settlement may only have one copy of this gear card at a time.""",
    },
    'unwieldy': {
        'name': 'Unwieldy',
        'type': 'special_rule',
        'desc': """A gear special rule. If any attack dice roll results are 1, the weapon causes 1 random damage to the survivor for each 1 roiled. Continue the attack as normal.""",
    },
    'vital': {
        'name': 'Vital',
        'type': 'special_rule',
        'desc': """A gear special rule. If the settlement has any gear with this rule, the survivors cannot depart without this gear. If the survivor holding Vital gear perishes before the showdown, another survivor must pick up the Vital gear (discarding gear to make room in their grid if needed).""",
    },
}

expansion = {

    # promo / whitebox
    'female_only': {
        'expansion': 'white_box',
        'name': 'Female Only',
        'desc': None,
    },

    # sunstalker
    'prismatic': {
        'expansion': 'sunstalker',
        'type': 'special_rule',
        'name': 'Prismatic',
        'desc': 'Your complete affinities and incomplete affinity halves count as all colors.',
    },
    'shadow_walk': {
        'expansion': 'sunstalker',
        'type': 'special_rule',
        'name': 'Shadow Walk',
        'desc': None,
    },
}

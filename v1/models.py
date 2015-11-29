#!/usr/bin/env python

from utils import get_logger

quarries = {
    "White Lion": {},
    "Screaming Antelope": {},
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
        "note": "When rolling on the Intimacy story event, roll twice and pick one result.",
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
    "Blacksmith": {},
    "Stone Circle": {},
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
}


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




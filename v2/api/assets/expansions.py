#!/usr/bin/python2.7

gorm = {
    "name": "Gorm",
    "always_available": ["Gormery", "Gormchymist", "Nigredo"],
    "timeline_add": [
        {"ly": 1, "type": "story_event", "name": "The Approaching Storm"},
        {"ly": 2, "type": "settlement_event", "name": "Gorm Climate"},
    ],
}

flower_knight = {
    "name": "Flower Knight",
    "timeline_add": [
        {"ly": 5, "type": "story_event", "name": "A Crone's Tale", "excluded_campaign": "The Bloom People"}
    ],
}

dung_beetle_knight = {
    "name": "Dung Beetle Knight",
    "always_available": ["Wet Resin Crafter","Subterranean Agriculture"],
    "timeline_add": [
        {"ly": 8, "type": "story_event", "name": "Rumbling in the Dark"},
    ],
}

sunstalker = {
    "name": "Sunstalker",
    "always_available": ["The Sun", "Sun Language", "Umbilical Bank"],
    "survivor_attribs": ["Purified","Sun Eater","Child of the Sun"],
    "timeline_add": [
        {"ly": 8, "type": "story_event", "name": "Promise Under the Sun", "excluded_campaign": "People of the Sun"},
    ],
}

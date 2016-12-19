#!/usr/bin/python


innovations = {

    #
    #   Innovations including a survival action unlock
    #

    "dragon_speech": {
        "name": "Dragon Speech",
        "type": "starting innovation",
        "expansion": "Dragon King",
        "survival_limit": 1,
        "survival_action": "Encourage",
        "consequences": ["Hovel", "Inner Lantern", "Drums", "Paint", "Symposium", "Ammonia"],
    },
    "sun_language": {
        "name": "Sun Language",
        "expansion": "Sunstalker",
        "type": "starting innovation",
        "survival_limit": 1,
        "survival_action": "Embolden",
        "consequences": ["Ammonia", "Drums", "Hovel", "Paint", "Symposium", "Hands of the Sun"],
    },
    "hands_of_the_sun": {
        "name": "Hands of the Sun",
        "expansion": "Sunstalker",
        "type": "faith",
        "survival_action": "Overcharge",
        "consequences": ["Aquarobics", "Sauna Shrine"],
    },
    "inner_lantern": {
        "name": "Inner Lantern",
        "type": "faith",
        "consequences": ["Shrine", "Scarification"],
        "survival_action": "Surge",
    },
    "paint": {
        "name": "Paint",
        "type": "art",
        "consequences": ["Pictograph", "Sculpture", "Face Painting"],
        "survival_action": "Dash",
    },
    "language": {
        "name": "Language",
        "type": "starting innovation",
        "consequences": ["Hovel", "Inner Lantern", "Drums", "Paint", "Symposium", "Ammonia"],
        "survival_limit": 1,
        "survival_action": "Encourage",
    },

    #
    #    principles
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
        "sort_order": 0,
        "milestone": "First child is born",
        "show_controls": ['"First child is born" in self.settlement["milestone_story_events"]'],
        "option_handles": ["protect_the_young", "survival_of_the_fittest"],
    },
    "potsun_new_life": {
        "name": "New Life",
        "sort_order": 0,
        "show_controls": ["True"],
        "option_handles": ["survival_of_the_fittest"],
    },
    "death": {
        "name": "Death",
        "sort_order": 1,
        "milestone": "First time death count is updated",
        "show_controls": ['int(self.settlement["death_count"]) >= 1'],
        "option_handles": ["graves", "cannibalize"],
    },
    "society": {
        "name": "Society",
        "sort_order": 2,
        "milestone": "Population reaches 15",
        "options": ["Collective Toil","Accept Darkness"],
        "show_controls": ['int(self.settlement["population"]) >= 15'],
        "option_handles": ["accept_darkness", "collective_toil"],
    },
    "conviction": {
        "name": "Conviction",
        "sort_order": 3,
        "options": ["Barbaric","Romantic"],
        "show_controls": ['int(self.settlement["lantern_year"]) >= 12'],
        "option_handles": ["romantic", "barbaric"],
    },
}

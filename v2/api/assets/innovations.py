#!/usr/bin/python


innovations = {
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
        "settlement_buff": "When rolling on the Intimacy story event, roll twice and pick the lowest result. All newborn survivors gain +1 Strength.",
        "survivor_buff": "All newborn survivors gain +1 Strength.",
        "newborn_survivor": {"Strength": 1},
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
    "death": {
        "name": "Death",
        "option_handles": ["graves", "cannibalize"],
    },
    "new_life": {
        "name": "New Life",
        "option_handles": ["protect_the_young", "survival_of_the_fittest"],
    },
    "society": {
        "name": "Society",
        "option_handles": ["accept_darkness", "collective_toil"],
    },
    "conviction": {
        "name": "Conviction",
        "option_handles": ["romantic", "barbaric"],
    },
}

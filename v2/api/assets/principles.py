#!/usr/bin/python

core = {
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

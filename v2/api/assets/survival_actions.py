#!/usr/bin/python

survival_action = {

    #   define all survival actions here, regardless of campaign or
    #   expansion. Remember: survival actions are defined by the campaign,
    #   but whether they're avalable is determined by settlement innovations
    #   as well as survivor impairments, so there is no need to define expansion
    #   or other SA attributes here.

    "dodge": {
        "name": "Dodge",
        "available": True,
        "sort_order": 0,
        "title_tip": "Available by default.",
    },
    "encourage": {
        "name": "Encourage",
        "sort_order": 1,
    },
    "dash": {
        "name": "Dash",
        "sort_order": 3,
    },
    "surge":{
        "name": "Surge",
        "sort_order": 4,
    },
    "overcharge": {
        "name": "Overcharge",
        "sort_order": 5,
    },
    "embolden": {
        "name": "Embolden",
        "sort_order": 2,
    },
}

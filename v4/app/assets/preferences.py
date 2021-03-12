DEFAULTS = {
    'default': True,
    'subscriber_level': 0,
    'type': 'general',
}

OPTIONS = {
    "beta": {
        "desc": "Enable Beta (&beta;) features of the Manager?",
        "affirmative": "Enable",
        "negative": "Disable",
        "subscriber_level": 2,
        'default': False,
    },

    # new assets
    "random_names_for_unnamed_assets": {
        "type": "general",
        "desc": (
            "Let the Manager choose random names for Settlements/Survivors "
            "without names?"
        ),
        "affirmative": "Choose randomly",
        "negative": "Use 'Unknown' and 'Anonymous'",
    },

    # new survivors
    "apply_new_survivor_buffs": {
        "type": "new_survivor_creation",
        "desc": (
            "Automatically apply settlement bonuses to new, newborn and "
            "current survivors where appropriate?"
        ),
        "affirmative": "Automatically apply",
        "negative": "Do not apply",
    },
    "apply_weapon_specialization": {
        "type": "new_survivor_creation",
        "desc": (
            "Automatically add weapon specialization ability to living "
            "survivors if settlement Innovations list includes that weapon "
            "mastery?"
        ),
        "affirmative": "Add",
        "negative": "Do Not Add",
    },

    # interface - campaign summary
    "show_endeavor_token_controls": {
        "type": "campaign_summary",
        "desc": "Show Endeavor Token controls on Campaign Summary view?",
        "affirmative": "Show controls",
        "negative": "Hide controls",
    },

    # interface - survivor sheet
    "show_epithet_controls": {
        "type": "survivor_sheet",
        "desc": "Use survivor epithets (tags)?",
        "affirmative": "Show controls on Survivor Sheets",
        "negative": "Hide controls and tags on Survivor Sheets",
    },

    # interface
    "show_remove_button": {
        "type": "ui",
        "desc": "Show controls for removing Settlements and Survivors?",
        "affirmative": "Show the Delete button",
        "negative": "Hide the Delete button",
        'default': False,
    },
    "show_ui_tips": {
        "type": "ui",
        "desc": "Display in-line help and user interface tips?",
        "affirmative": "Show UI tips",
        "negative": "Hide UI tips",
        "subscriber_level": 2,
    },
    "show_dashboard_alerts": {
        "type": "ui",
        "desc": "Display webapp alerts on the Dashboard?",
        "affirmative": "Show alerts",
        "negative": "Hide alerts",
        "subscriber_level": 2,
    },
}

TYPES = {
    'general': {
        'name': 'General Preferences',
        'sort': 0,
    },
    'ui': {
        'name': 'Interface',
        'sort': 1,
    },
    'campaign_summary': {
        'name': 'Campaign Summary',
        'sort': 2,
    },
    'survivor_sheet': {
        'name': 'Survivor Sheet',
        'sort': 3,
    },
    'new_survivor_creation': {
        'name': 'New Survivor Creation',
        'sort': 4,
    },
}

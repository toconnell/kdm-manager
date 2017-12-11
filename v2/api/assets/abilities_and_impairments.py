#!/usr/bin/python


ability = {
    'ageless': {
        'desc': 'You may hunt if you are retired. When you gain Hunt XP, you may decide not to gain it.',
        'name': 'Ageless',
        'type': 'ability'
    },
    'analyze': {
        'desc': "At the start of the Survivors' turn, if you are adjacent to the monster, reveal the top AI card, then place back on top of the deck.",
        'name': 'Analyze',
        'type': 'ability',
        'base_attribute': 'Understanding',
    },
    'bitter_frenzy': {
#        'desc': 'You may spend survival and use fighting arts, weapon specialization, and weapon mastery while Frenzied.',
        'desc': 'Each showdown, the first time you suffer the frenzy brain trauma, gain d10 survival. You may spend survival while <b>Frenzied</b>.',
        'name': 'Bitter Frenzy',
        'type': 'ability'
    },
    'blue_life_exchange': {
        'desc': 'In the <b>Aftermath</b>, gain 3 additional Hunt XP. You may not place <b>other</b> gear in your grid. Gain +1 permanent luck with each <b>Age</b> milestone. When you retire, you cease to exist.',
        'selectable': False,
        'name': 'Blue Life Exchange',
        'related': ['dream_of_the_lantern', 'lucernae'],
        'type': 'ability'
    },
    'bone_witch_scarred_eyes':{
        'Accuracy': -4,
        'Strength': 4,
        'desc': 'Suffer -4 permanent Accuracy and gain +4 permanent strength.',
        'name': 'Bone Witch - Scarred Eyes',
        'type': 'impairment'
    },
    'bone_witch_wounds': {
        'Accuracy': -1,
        'Strength': -1,
        'desc': 'Suffer -1 permanent strength, -1 permanent accuracy and skip the next hunt.',
        'name': 'Bone Witch - Wounds',
        'skip_next_hunt': True,
        'type': 'impairment'
    },
    'burnt_nerves': {
        'name': 'Burnt Nerves',
        'desc': 'You are immune to <b>Bash</b>.',
    },
    'cancerous_illness': {
        'desc': 'You cannot gain survival.',
        'name': 'Cancerous Illness',
        'type': 'impairment',
        'cannot_gain_survival': True,
    },
    'caratosis': {
#        'desc': 'For each <font class="affinity_red"> &nbsp; red &nbsp;</font> affinity you have, 1 of your attack rolls hits automatically each attack.',
        'desc': 'Before making an attack roll, you may declare "Caratosis X" in a loud, booming voice. If you do, that attack gains X automatic hits. X cannot be more than your total red affinities. When the attack ends, gain +X hunt Xp.<br/>When you trigger Age 2, gain the <b>Beast of Caratosis</b> secret fighting art.',
        'selectable': False,
        'name': 'Caratosis',
        'epithet': 'caratosis',
        'related': ['dream_of_the_beast', 'life_exchange'],
        'type': 'ability'
    },
    'crystal_skin': {
#        'desc': 'You cannot place armor in your gear grid. When you <b>depart</b>, gain <font class="inline_shield">2</font> to all hit locations. Suffer -1 to the result of all severe injury rolls.',
        'desc': 'You ignore <b>cursed</b> and cannot wear armor. When you <b>depart</b>, gain <font class="inline_shield">3</font> to all hit locations. Suffer -2 to the result of all severe injury rolls. When you participate in <b>Intimacy</b>, newborns gain <b>Crystal Skin</b> in addition to any other roll results.',
        'name': 'Crystal Skin',
        'type': 'ability',
        'inheritable': True,
        'max': 1,
    },
    'dormenatus': {
#        'desc': 'When you <b>depart</b>, gain +1 to every hit location for each <font class="affinity_green"> &nbsp; green &nbsp;</font> affinity you have.',
        'desc': """When you suffer damage, you may declare 'Dormenatus X' in a loud, booming voice. If you do, gain <font class="inline_shield">x</font> to each hit location. X cannot be more than your total green affinities. After the damage is resolved, gain +X hunt XP.<br/>When you trigger Age 2, gain the <b>Grace of Dormenatus</b> secret fighting art.""",
        'selectable': False,
        'name': 'Dormenatus',
        'epithet': 'dormenatus',
        'related': ['dream_of_the_crown', 'life_exchange'],
        'type': 'ability'
    },
    'dream_of_the_beast': {
        'Strength': 1,
        'affinities': {'red': 1},
        'desc': '1 permanent red affinity.',
        'epithet': 'red_savior',
        'selectable': False,
        'name': 'Dream of the Beast',
        'related': ['caratosis', 'life_exchange'],
        'type': 'ability'
    },
    'dream_of_the_crown': {
        'Evasion': 1,
        'affinities': {'green': 1},
        'desc': '1 permanent green affinity.',
        'epithet': 'green_savior',
        'selectable': False,
        'name': 'Dream of the Crown',
        'related': ['dormenatus', 'life_exchange'],
        'type': 'ability'
    },
    'dream_of_the_lantern': {
        'Luck': 1,
        'affinities': {'blue': 1},
        'desc': '1 permanent blue affinity.',
        'epithet': 'blue_savior',
        'selectable': False,
        'name': 'Dream of the Lantern',
        'related': ['lucernae', 'life_exchange'],
        'type': 'ability'
    },
    'endless_babble': {
        'desc': 'When you <b>depart</b>, <b>departing survivors</b> gain +1 insanity. You may not encourage.',
        'name': 'Endless Babble',
        'survival_actions': {
            'disable': ['encourage'],
        },
        'type': 'impairment'
    },
    'explore': {
        'desc': 'When you roll on an investigate table, add +2 to your roll result.',
        'name': 'Explore',
        'type': 'ability',
        'base_attribute': 'Understanding',
    },
    'fated_battle': {
        'desc': 'At the start of a showdown with the picked monster, gain +1 speed token.',
        'name': 'Fated Battle',
        'type': 'ability'
    },
    'green_life_exchange': {
        'desc': 'In the <b>Aftermath</b>, gain 3 additional Hunt XP. You may not place <b>other</b> gear in your grid. Gain +1 permanent evasion with each <b>Age</b> milestone. When you retire, you cease to exist.',
         'selectable': False,
         'name': 'Green Life Exchange',
         'related': ['dream_of_the_crown', 'dormenatus'],
         'type': 'ability'
    },
    "homing_instinct": {
        "name": "Homing Instinct",
        "type": "ability",
        "desc": "Add +5 to your rolls on the Run Away story event."
    },
    "iron_will": {
        "name": "Iron Will",
        "desc": "You cannot be knocked down. Reduce all knockback you suffer to <b>knockback 1</b>.",
        "type": "ability",
    },
    "kings_curse": {
        'desc': 'At the Aftermath, <font class="kdm_font">g</font> <b>King\'s Curse</b>.',
        'epithet': "kings_curse",
        'name': "King's Curse",
        'type': 'curse'
    },
    'legendcaller': {
        'desc': 'Once a lifetime, on a hunt board space after <b>Overwhelming Darkness</b>, in place of rolling a random hunt event, use "53" as your result.',
        'epithet': 'legendcaller',
        'name': 'Legendcaller',
        'type': 'ability'
    },
    'leprosy': {
#        'desc': 'Reduce all damage suffered by 1 to a minimum of 1. When rolling on the severe injury table, -2 to any result.',
        'desc': 'Reduce all damage suffered by 1 to a minimum of 1. Suffer -2 to severe injury rolls.',
        'epithet': 'leper',
        'name': 'Leprosy',
        'type': 'impairment'
    },
    'leyline_walker': {
        'desc': 'While there is no armor or accessory gear in your grid, gain +3 evasion.',
        'epithet': 'leyline_walker',
        'name': 'Leyline Walker',
        'type': 'ability'
    },
    'lovelorn_rock': {
        'desc': 'Forever in love, the straggler loses one gear slot permanently to the rock. This survivor must always leave one gear space empty to hold their rock. The rock can be lost like normal gear.',
        'name': 'Lovelorn Rock',
        'type': 'impairment',
        'epithet': 'lithophile',
    },
    'lucernae': {
#        'desc': 'For every <font class="affinity_blue"> &nbsp; blue &nbsp;</font> affinity you have, your ranged weapons gain this amount of <b>range</b> and your melee weapons gain this amount of <b>reach</b>.',
        'desc': """Before making a wound attempt, you may declare "Lucernae X" in a loud, booming voice. If you do, that wound attempt gains X luck. X cannot be more than your total blue affinities. When the attack ends, you gain +X hunt XP.<br/> When you trigger Age 2, gain the <b>Lucernae's Lantern</b> secret Fighting Art.""",
        'selectable': False,
        'name': 'Lucernae',
        'epithet': 'lucernae',
        'related': ['dream_of_the_lantern', 'life_exchange'],
        'type': 'ability'
    },
    'mad_oracle': {
        'desc': 'Once per showdown, as a monster draws an AI, name a card out loud. If the AI card drawn is the card you named, gain +1 evasion token.',
        'name': 'Mad Oracle',
        'type': 'ability',
    },
    'marrow_hunger': {
        'desc': 'When the Murder or Skull Eater settlement events are drawn, this survivor is nominated.',
        'epithet': 'skull_eater',
        'name': 'Marrow Hunger',
        'type': 'impairment'
    },
    'matchmaker': {
        'desc': 'When you are a returning survivor, once per year you may spend 1 Endeavor to trigger Intimacy (story event).',
        'name': 'Matchmaker',
        'type': 'ability',
        'endeavors': ['matchmaker_trigger_intimacy'],
        'base_attribute': 'Courage',
    },
    'metal_maw': {
        'desc': 'Your Fist & Tooth gains <b>Sharp</b>. (Add 1d10 strength to each wound attempt using this gear. This d10 is not a wound roll, and cannot cause critical wounds.)',
        'name': 'Metal Maw',
        'type': 'ability'
    },
    'partner': {
#        'desc': 'When you both <b>depart</b>, gain +2 survival. While adjacent to your partner, gain +1 strength. Partners may only nominate each other for <b><font class="kdm_font">g</font> Intimacy</b>. When a partner dies, the remaining partner gains a random disorder and loses this ability.',
        'desc': 'When you both <b>Arrive</b>, gain survival up to the survival limit. Partners may only nominate each other for <b><font class="kdm_font">g</font> Intimacy</b>. When a partner dies, the remaining partner gains a random disorder and loses this ability.',
        'name': 'Partner',
        'type': 'ability'
    },
    'peerless': {
        'desc': 'When you gain insanity, you may gain an equal amount of survival.',
        'name': 'Peerless',
        'type': 'ability'
    },
    'possessed': {
        'Accuracy': 1,
        'Strength': 2,
        'cannot_use_fighting_arts': True,
        'desc': 'Cannot use weapon specialization, weapon mastery, or fighting arts.',
        'name': 'Possessed',
        'type': 'ability',
    },
    'prepared': {
        'desc': 'When rolling to determine a straggler, add your hunt experience to your roll result.',
        'name': 'Prepared',
        'type': 'ability',
        'base_attribute': 'Courage',
    },
    'life_exchange': {
        'desc': 'In the <b>Aftermath</b>, gain 1 additional Hunt XP. You may not wear <b>other</b> gear. If you trigger the White Secret story event, you cease to exist. When you retire, you cease to exist.',
        'name': 'Life Exchange',
    },
    'red_life_exchange': {
        'desc': 'In the <b>Aftermath</b>, gain 3 additional Hunt XP. You may not place <b>other</b> gear in your grid. Gain +1 permanent strength with each <b>Age</b> milestone. When you retire, you cease to exist.',
        'selectable': False,
        'name': 'Red Life Exchange',
        'related': ['caratosis', 'dream_of_the_beast'],
        'type': 'ability'
    },
    'sour_death': {
#        'desc': 'When you are knocked down, you may encourage yourself. If you do, gain +1 strength token.',
        'desc': "When you are knocked down, you may encourage yourself (even if you're deaf). If you do, gain +1 strength token.",
        'name': 'Sour Death',
        'type': 'ability'
    },
    'stalwart': {
        'desc': 'Ignore being knocked down by brain trauma and intimidation actions.',
        'name': 'Stalwart',
        'type': 'ability',
        'base_attribute': 'Courage',
    },
    'story_of_the_forsaker': {
        'desc': 'You cannot be knocked down during a showdown with a nemesis monster.',
        'name': 'Story of the Forsaker',
        'type': 'ability'
    },
    'story_of_the_goblin': {
        'desc': 'Once per showdown you may...roll 1d10. On a 3+, gain the priority target token and the monster gains +1 damage token.',
        'name': 'Story of the Goblin',
        'type': 'ability'
    },
    'story_of_the_young_hero': {
        'desc': 'At the start of your act, you may...[g]ain 2 bleeding tokens and +1 survival.',
        'name': 'Story of the Young Hero',
        'type': 'ability'
    },
    'sweet_battle': {
#        'desc': 'You may surge without spending survival. If you do, the Activation must be used to activate a weapon.',
        'desc': 'Once per round, you may <b>surge</b> without spending survival. If you do, the Activation must be used to activate the weapon.',
        'name': 'Sweet Battle',
        'type': 'ability',
        'survival_actions': {
            'enable': ['surge'],
        },
    },
    'thundercaller': {
        'desc': 'Once a lifetime, on a hunt board space after <b>Overwhelming Darkness</b>, in place of rolling a random hunt event, use "100" as your result.',
        'epithet': 'thundercaller',
        'name': 'Thundercaller',
        'type': 'ability'
    },
    'tinker': {
        'desc': 'When you are a returning survivor, gain +1 Endeavor to use this settlement phase.',
        'name': 'Tinker',
        'type': 'ability',
        'base_attribute': 'Understanding',
    },
    'twilight_sword': {
        'desc': 'You may select <b>Twilight Sword</b> as a weapon proficiency type. This weapon may not be removed from your gear grid for any reason. When you die, archive your <b>Twilight Sword</b> card.',
        'epithet': 'twilight_sword',
        'name': 'Twilight Sword',
        'type': 'curse'
    },
}

severe_injury = {
    'bleeding_kidneys': {
        'desc': 'Gain 2 bleeding tokens.',
        'name': 'Bleeding kidneys',
        'max': False,
        "bleeding_tokens": 2,
    },
    'blind': {
        'Accuracy': -1,
        'desc': 'Lose an eye. Suffer -1 permanent Accuracy. This injury is permanent and can be recorded twice. A survivor with two <b>blind</b> severe injuries suffers -4 permanent accuracy and retires at the end of the next showdown or settlement phase, having lost all sight. Gain 1 bleeding token.',
        'epithet': 'the_blind',
        'max': 2,
        'name': 'Blind',
        "bleeding_tokens": 1,
    },
    'broken_arm': {
        'Accuracy': -1,
        'Strength': -1,
        'desc': 'An ear-shattering crunch. Suffer -1 permanent Accuracy and -1 permanent Strength. This injury is permanent and can be recorded twice. Gain 1 bleeding token.',
        'max': 2,
        'name': 'Broken arm',
        "bleeding_tokens": 1,
    },
    'broken_hip': {
        'Movement': -1,
        'desc': 'Your hip is dislocated. You can no longer <b>dodge</b>. Suffer -1 permanent movement. This injury is permanent and can be recorded once. Gain 1 bleeding token.',
        'name': 'Broken hip',
        'survival_actions': {
            'disable': ['dodge'],
        },
        "bleeding_tokens": 1,
    },
    'broken_leg': {
        'Movement': -1,
        'desc': 'An ear-shattering crunch! Adjacent survivors suffer 1 brain damage. Suffer -1 permanent movement. This injury is permanent, and can be recorded twice. Gain 1 bleeding token.',
        'max': 2,
        'name': 'Broken leg',
        "bleeding_tokens": 1,
    },
    'broken_rib': {
        'Speed': -1,
        'desc': 'It even hurts to breathe. Suffer -1 permanent speed. This injury is permanent, and can be recorded multiple times. Gain 1 bleeding token.',
        'name': 'Broken rib',
        "max": False,
        "bleeding_tokens": 1,
    },
    'bruised_tailbone': {
        'desc': 'The base of your spine is in agony. You cannot <b>dash</b> until showdown ends. You are knocked down. Gain 1 bleeding token.',
        'name': 'Bruised tailbone',
        "max": False,
        "bleeding_tokens": 1,
    },
    'collapsed_lung': {
        'desc': "You can't catch a breath. Gain -1 movement token. Gain 1 bleeding token.",
        'name': 'Collapsed Lung',
        "max": False,
        "attribute_detail": {"Movement": {"tokens": -1}},
        "bleeding_tokens": 1,
    },
    'concussion': {
        'desc': 'Your brain is scrambled like an egg. Gain a random disorder. Gain 1 bleeding token.',
        'name': 'Concussion',
        "max": False,
        "bleeding_tokens": 1,
    },
    'contracture': {
        'Accuracy': -1,
        'desc': 'The arm will never be the same. Suffer -1 permanent Accuracy. This injury is permanent and can be recorded multiple times. Gain 1 bleeding token.',
        'name': 'Contracture',
        "max": False,
        "bleeding_tokens": 1,
    },
    'deaf': {
        'Evasion': -1,
        'desc': 'Suffer -1 permanent Evasion. This injury is permanent and can be recorded once.',
        'name': 'Deaf',
    },
    'destroyed_back': {
        'Movement': -2,
        'desc': 'A sharp cracking noise. Suffer -2 permanent movement. You can no longer activate any gear that has 2+ Strength. This injury is permanent and can be recorded once. Gain 1 bleeding token.',
        'name': 'Destroyed back',
        "bleeding_tokens": 1,
        'cannot_activate_two_plus_str_gear': True,
    },
    'destroyed_genitals': {
        'desc': 'You cannot be nominated for the Intimacy story event. This injury is permanent and can be recorded once. Gain a random disorder. You are knocked down. Gazing upwards, you wonder at the futility of your struggle. Gain +3 insanity. Gain 1 bleeding token.',
        'name': 'Destroyed genitals',
        'cannot_be_nominated_for_intimacy': True,
        "bleeding_tokens": 1,
    },
    'destroyed_tooth': {
        'desc': 'If you have 3+ courage, you boldly spit the tooth out and gain +2 insanity! Otherwise. the blow sends you sprawling and you are knocked down.',
        'name': 'Destroyed tooth',
        'max': False,
    },
    'disemboweled': {
        'desc': 'Your movement is reduced to 1 until the showdown ends. Gain 1 bleeding token. Skip the next hunt. If you suffer <b>disemboweled</b> during a showdown, at least one other survivor must live to the end of the showdown to carry you back to the settlement. Otherwise, at the end of the showdown, you are lost. Dead.',
        'name': 'Disemboweled',
        'skip_next_hunt': True,
        'max': False,
        "bleeding_tokens": 1,
    },
    'dislocated_shoulder': {
        'desc': 'Pop! You cannot activate two-handed or <b>paired</b> weapons or use <b>block</b> until showdown ends. Gain 1 bleeding token.',
        'name': 'Dislocated shoulder',
        'max': False,
        "bleeding_tokens": 1,
    },
    'dismembered_arm': {
        'desc': 'Lose an arm. You can no longer activate two-handed weapons. This injury is permanent, and can be recorded twice. A survivor with two <b>dismembered arm</b> severe injuries cannot activate any weapons. Gain 1 bleeding token.',
        'max': 2,
        'name': 'Dismembered Arm',
        "bleeding_tokens": 1,
        'cannot_activate_two_handed_weapons': True,
    },
    'dismembered_leg': {
        'Movement': -2,
        'desc': 'Lose a leg. You suffer -2 permanent movement, and can no longer <b>dash</b>. This injury is permanent and can be recorded twice. A survivor with two <b>dismembered leg</b> severe injuries has lost both of their legs and must retire at the end of the next showdown or settlement phase. Gain 1 bleeding token.',
        'max': 2,
        'name': 'Dismembered leg',
        'survival_actions': {
            'disable': ['dash'],
        },
        "bleeding_tokens": 1,
    },
    'gaping_chest_wound': {
        'Strength': -1,
        'desc': 'Suffer -1 permanent Strength. This injury is permanent and can be recorded multiple times. Gain 1 bleeding token.',
        'name': 'Gaping chest wound',
        'max': False,
        "bleeding_tokens": 1,
    },
    'hamstrung': {
        'cannot_use_fighting_arts': True,
        'desc': 'A painful rip. The leg is unusable. You can no longer use any fighting arts or abilities. This injury is permanent and can be recorded once. Gain 1 bleeding token.',
        'name': 'Hamstrung',
        "bleeding_tokens": 1,
    },
    'intestinal_prolapse': {
        'desc': 'Your gut is gravely injured. You can no longer equip any gear on your waist, as it is too painful to wear. This injury is permanent, and can be recorded once. Gain 1 bleeding token.',
        'disable_locations': ['Waist'],
        'name': 'Intestinal prolapse',
        "bleeding_tokens": 1,
    },
    "intracranial_hemorrhage": {
        "name": "Intracranial hemorrhage",
        "desc": "You can no longer use or gain any survival. This injury is permanent and can be recorded once. Gain 1 bleeding token.",
        "cannot_gain_survival": True,
        "cannot_spend_survival": True,
        "bleeding_tokens": 1,
    },
    'ruptured_muscle': {
        'cannot_use_fighting_arts': True,
        'desc': 'A painful rip. The arm hangs limp. You can no longer activate fighting arts. This injury is permanent and can be recorded once. Gain 1 bleeding token.',
        'name': 'Ruptured muscle',
        "bleeding_tokens": 1,
    },
    'ruptured_spleen': {
        'desc': 'A vicious body blow. Skip the next hunt. Gain 2 bleeding tokens.',
        'name': 'Ruptured spleen',
        'skip_next_hunt': True,
        'max': False,
        "bleeding_tokens": 2,
    },
    'shattered_jaw': {
        'desc': 'You drink your meat through a straw. You can no longer <b>consume</b> or be affected by events requiring you to <b>consume</b>. You can no longer <b>encourage</b>. This injury is permanent and can be recorded once. Gain 1 bleeding token.',
        'name': 'Shattered jaw',
        'survival_actions': {
            'disable': ['encourage'],
        },
        "bleeding_tokens": 1,
        'cannot_consume': True,
    },
    'slashed_back': {
        'desc': 'Making sudden movement is excruciatingly painful. You cannot <b>surge</b> until showdown ends. Gain 1 bleeding token.',
        'name': 'Slashed back',
        'type': 'severe_injury',
        'max': False,
        "bleeding_tokens": 1,
    },
    'spiral_fracture': {
        'desc': 'Your arm twists unnaturally. Gain -2 strength tokens. Skip the next hunt. Gain 1 bleeding token.',
        'name': 'Spiral fracture',
        'skip_next_hunt': True,
        'max': False,
        "bleeding_tokens": 1,
    },
    'torn_achilles_tendon': {
        'desc': 'Your leg cannot bear your weight. Until the end of the showdown, whenever you suffer light, heavy, or severe injury, you are also knocked down. Skip the next hunt. Gain 1 bleeding token.',
        'name': 'Torn Achilles Tendon',
        'skip_next_hunt': True,
        'max': False,
        "bleeding_tokens": 1,
    },
    'torn_muscle': {
        'desc': 'Your quadriceps is ripped to shreds. You cannot <b>dash</b> until he showdown ends. Skip the next hunt. Gain 1 bleeding token.',
        'name': 'Torn muscle',
        'skip_next_hunt': True,
        'max': False,
        "bleeding_tokens": 1,
    },
    'warped_pelvis': {
        'Luck': -1,
        'desc': 'Your pelvis is disfigured. Suffer -1 permanent luck. This injury is permanent and can be recorded multiple times. Gain 1 bleeding token.',
        'name': 'Warped Pelvis',
        'max': False,
        "bleeding_tokens": 1,
    },


}

expansion_ai = {

    # beta challenge scenarios
    'blue_glow': {
        'desc': '<font class="kdm_font">a</font> Move a Portal terrain tile on the showdown board to Snow\'s space. If there are less than 2 Portals on the board, add one to Snow\'s space instead.',
        'expansion': 'beta_challenge_scenarios',
        'max': 1,
        'name': 'Blue Glow',
        'type': 'ability',
    },
    'green_glow': {
        'desc': '<font class="kdm_font">a</font> Add <font class="inline_shield">1</font> to all hit locations.',
        'expansion': 'beta_challenge_scenarios',
        'max': 1,
        'name': 'Green Glow',
        'type': 'ability'
    },
    'red_glow': {
        'desc': '<font class="kdm_font">a</font> Make a melee attack with speed 3, accuracy 7+, and strength 5.',
        'expansion': 'beta_challenge_scenarios',
        'max': 1,
        'name': 'Red Glow',
        'type': 'ability'
    },
    'solid': {
        'desc': 'If you would be knocked down, roll 1d10. On a 4+, you are not knocked down.',
        'expansion': 'beta_challenge_scenarios',
        'max': 1,
        'name': 'Solid',
        'type': 'ability'
    },
    'twilight_succession': {
        'desc': 'If you die during the showdown and have a Twilight Sword, nominate another survivor on the showdown board to gain the Twilight Sword and this ability.',
        'expansion': 'beta_challenge_scenarios',
        'max': 1,
        'name': 'Twilight Succession',
        'type': 'ability'
    },

    # lonely tree
    'nightmare_blood': {
        'desc': 'Whenever you gain a bleeding token, add <font class="inline_shield">1</font> to all hit locations.',
        'expansion': 'lonely_tree',
        'max': 1,
        'name': 'Nightmare Blood',
        'type': 'ability'
    },
    'nightmare_membrane': {
        'desc': 'You may spend <font class="kdm_font">a c</font> to exchange any 1 of your tokens for a +1 strength token.',
        'expansion': 'lonely_tree',
        'max': 1,
        'name': 'Nightmare Membrane',
        'type': 'ability'
    },
    'nightmare_spurs': {
        'desc': 'Once per showdown, you may spend all your survival (at least 1) to lose all your +1 strength tokens and gain that many +1 luck tokens.',
        'expansion': 'lonely_tree',
        'max': 1,
        'name': 'Nightmare Spurs',
        'type': 'ability'
    },
    'super_hair': {
        'desc': 'You may spend <font class="kdm_font">a</font> to freely exchange any tokens with adjacent survivors who have <b>Super Hair</b>.',
        'expansion': 'lonely_tree',
        'max': 1,
        'name': 'Super Hair',
        'type': 'ability'
    },

    # spidicules
    "rivals_scar": {
        "name": "Rival's Scar",
        "type": "ability",
        "expansion": "spidicules",
        "desc":"Gain +1 permanent strength and -1 permanent evasion.",
        "max": 1,
        "epithet": "rivals_scar",
        "Strength": 1,
        "Evasion": -1,
    },

    # flower knight
    "sleeping_virus_flower": {
        "name": "Sleeping Virus Flower",
        "expansion": "flower_knight",
        "desc": 'When you die, a flower blooms from your corpse. Add <font class="kdm_font">g</font> <b>A Warm Virus</b> to the timeline next year. You are the guest.',
        "epithet": "host",
        "max": 1,
        "Luck": 1,
    },


    # lion knight
    "hideous_disguise": {
        "name": "Hideous Disguise",
        "expansion": "lion_knight",
        "desc": "At the start of the showdown, if you are fighting the Lion Knight, choose your Role card.",
        "epithet": "hideous",
        "max": 1,
    },

    # lion god
    'death_mehndi': {
        'desc': 'On a <b>Perfect hit</b>, gain 1d10 insanity. -4 to all brain trauma rolls.',
        'expansion': 'lion_god',
        'max': 1,
        'name': 'Death Mehndi',
        'type': 'curse'
    },

    # sunstalker
    'reflection': {
        'desc': '<ul><li>Your complete affinities and incomplete affinity halves count as all colors.</li><li>You may dodge at any time and as many times as you like each round.</li><li>When you attack from a blind spot, add +1d10 to all wound attempts for that attack.</li></ul>',
        'expansion': 'sunstalker',
        'max': 1,
        'name': 'Reflection',
        'type': 'ability'
    },
    'refraction': {
        'desc': '<ul><li>Your complete affinities and incomplete affinity halves count as all colors.</li><li>During the Showdown, after you perform a survival action, gain +1 survival.</li></ul>',
        'expansion': 'sunstalker',
        'max': 1,
        'name': 'Refraction',
        'type': 'ability'
    },

    # slenderman
    "forgettable": {
        "name": "Forgettable",
        "type": "ability",
        "max": 1,
        "expansion": "slenderman",
        "desc": "Gain +2 permanent evasion. Forgettable survivors cannot be encouraged.",
        "Evasion": 2,
    },

    # gorm
    'acid_palms_gorm': {
        'desc': 'Add 1d10 strength to your wound attempts when attacking with Fist & Tooth.',
        'expansion': 'gorm',
        'max': 1,
        'name': 'Acid Palms',
        'type': 'ability'
    },

    # dragon king
    'acid_palms_dk': {
        'desc': 'Add 1d10 strength to your wound attempts when attacking with Fist & Tooth.',
        'expansion': 'dragon_king',
        'max': 1,
        'name': 'Acid Palms',
        'type': 'ability'
    },
    'heart_of_the_sword': {
        'desc': 'If you gain weapon proficiency during the Aftermath, gain +3 additional ranks. You cough up a hunk of your own solidified blood and gain +1 <b>Iron</b> strange resource.',
        'expansion': 'dragon_king',
        'max': 1,
        'name': 'Heart of the Sword',
        'type': 'ability'
    },
    'iridescent_hide': {
        'constellation': {'horizontal': 'Absolute', 'vertical': 'Storm'},
        'desc': 'Gain +<font class="inline_shield">1</font> to all hit locations for each different-colored affinity in your gear grid.',
        'expansion': 'dragon_king',
        'max': 1,
        'name': 'Iridescent Hide',
        'type': 'ability'
    },
    'limb_maker': {
        'desc': 'Once per settlement phase, spend 2 <font class="kdm_font">d</font> to carve a prosthetic limb. Remove a survivor\'s <b>dismembered</b> injury and add 1 bone to the settlement\'s storage.',
        'expansion': 'dragon_king',
        'max': 1,
        'name': 'Limb-maker',
        'type': 'ability',
        'endeavors': ['limb_maker'],
    },
    "oracles_eye": {
        'constellation': {'horizontal': 'Goblin','vertical': 'Witch'},
        'desc': 'At the start of the showdown, look through the AI deck then shuffle.',
        'expansion': 'dragon_king',
        'max': 1,
        'name': "Oracle's Eye",
        'type': 'ability'
    },
    'presage': {
        'desc': 'Each time you attack, before drawing hit locations, loudly say a name. You lightly bite the eye in your cheek to see what it sees. If you draw any hit locations with that name, gain +3 insanity and +10 strength when attempting to wound them.',
        'expansion': 'dragon_king',
        'max': 1,
        'name': 'Presage',
        'type': 'ability'
    },
    'pristine': {
        'constellation': {'horizontal': 'Gambler', 'vertical': 'Reaper'},
        'desc': 'When you suffer a <b>dismembered</b> severe injury, ignore it and gain 1 bleeding token instead.',
        'expansion': 'dragon_king',
        'max': 1,
        'name': 'Pristine',
        'type': 'ability'
    },
    'psychovore': {
        'desc': "Once per showdown, you may eat an adjacent survivor's disorder. If you do, remove the disorder. They gain 1 bleeding token and you gain +1 permanent strength. At the end of the showdown, if you haven't eaten a disorder, you die.",
        'expansion': 'dragon_king',
        'max': 1,
        'name': 'Psychovore',
        'type': 'ability'
    },
    'rooted_to_all': {
        'desc': 'If you are standing at the start of your act, reveal the top 2 cards of the AI deck and put them back in any order.',
        'expansion': 'dragon_king',
        'max': 1,
        'name': 'Rooted to All',
        'type': 'ability'
    },
    'twelve_fingers': {
        'desc': 'You cannot carry two-handed gear. On a Perfect hit, your right hand pulses. Gain +5 insanity and +1 luck for the attack. However, for each natural 1 rolled when attempting to hit, your left hand shakes. Suffer 5 brain damage and -1 luck for the attack.',
        'expansion': 'dragon_king',
        'max': 1,
        'name': 'Twelve Fingers',
        'type': 'ability',
        'cannot_activate_two_handed_weapons': True,
    },
    'way_of_the_rust': {
        'desc': 'Your bleeding tokens are also +1 evasion tokens.',
        'expansion': 'dragon_king',
        'max': 1,
        'name': 'Way of the Rust',
        'type': 'ability',
    },

    # white box
    'gender_swap': {
        'desc': 'You own the <b>Belt of Gender Swap</b>, it will always take one space in your gear grid and while it is there, your gender is reversed.',
        'epithet': 'gender_swap',
        'expansion': 'white_box',
        'max': 1,
        'name': 'Gender Swap',
        'reverse_sex': True,
        'type': 'curse'
    },

}


#   p.43
# When a survivor reaches a weapon mastery,
# it is permanently added to your settlement as an
# innovation. The survivor's command of the weapon
# is so extensive that all current and future survivors
# of that settlement gain that weapon's specialization
# ability in addition to their own weapon proficiencies.
# The master will keep the full benefits of the mastery,
# so long as the innovation remains in the settlement. 

weapon_mastery = {
    "mastery_club": {
        "name": "Mastery - Club",
        "desc": "When a Club Master attacks with a club, if a successful wound attempt total is greater than or equal to twice the monster's toughness, inflict an additional wound.",
        "weapon_proficiency": "club",
        "weapon_name": "club",
        "current_survivor": {"abilities_and_impairments": ["club_specialization"]},
        "new_survivor": {"abilities_and_impairments": ["club_specialization"]},
        'epithet': 'club_master',
    },
    "mastery_scythe": {
        "name": "Mastery - Scythe",
        "desc": "When you critically wound with a scythe, roll 1d10. On a 6+, shuffle the hit location deck (do not shuffle unresolved hit locations).<br/>Limit, once per round.",
        "expansion": "dragon_king",
        "weapon_proficiency": "scythe",
        "weapon_name": "scythe",
        "current_survivor": {"abilities_and_impairments": ["scythe_specialization"]},
        "new_survivor": {"abilities_and_impairments": ["scythe_specialization"]},
        'epithet': 'scythe_master',
    },
    "mastery_katana": {
        "name": "Mastery - Katana",
        "desc": "When a survivor reaches Katana Mastery, they leave the settlement forever, heeding the call of the storm to hone their art.<br/>Before the master leaves, you may nominate a survivor. Set that survivor's weapon type to Katana and their weapon proficiency level to 1.",
        "expansion": "sunstalker",
        "add_to_innovations": False,
        "weapon_proficiency": "katana",
        "weapon_name": "katana",
        'epithet': 'katana_master',
    },
    "mastery_katar": {
        "name": "Mastery - Katar",
        "desc": "If you are a Katar Master, gain a <i>+1 evasion</i> token on a <b>perfect hit</b> with a katar. When you are knocked down, remove all +1 evasion tokens.",
        "weapon_proficiency": "katar",
        "weapon_name": "katar",
        "current_survivor": {"abilities_and_impairments": ["katar_specialization"]},
        "new_survivor": {"abilities_and_impairments": ["katar_specialization"]},
        'epithet': 'katar_master',
    },
    "mastery_bow": {
        "name": "Mastery - Bow",
        "desc": "If you are a Bow Master, all bows in your gear grid gain <b>Deadly 2</b>. In addition, ignore <b>cumbersome</b> on all Bows.",
        "weapon_proficiency": "bow",
        "weapon_name": "bow",
        "current_survivor": {"abilities_and_impairments": ["bow_specialization"]},
        "new_survivor": {"abilities_and_impairments": ["bow_specialization"]},
        'epithet': 'bow_master',
    },
    "mastery_twilight_sword": {
        "name": "Mastery - Twilight Sword",
        "desc": "Any Survivor who attains Twilight Sword Mastery leaves the settlement forever in pursuit of a higher purpose. Remove them from the settlement's population. You may place the master's Twilight Sword in another survivor's gear grid or archive it.",
        "excluded_campaigns": ["people_of_the_stars","people_of_the_sun"],
        "weapon_proficiency": "twilight_sword",
        "weapon_name": "Twilight Sword",
        "current_survivor": {"abilities_and_impairments": ["twilight_sword_specialization"]},
        "new_survivor": {"abilities_and_impairments": ["twilight_sword_specialization"]},
        'epithet': 'twilight_sword_master',
    },
    "mastery_axe": {
        "name": "Mastery - Axe",
        "desc": "When an Axe Master wounds a monster with an axe at a location with a persistent injury, that wound becomes a critical wound.",
        "weapon_proficiency": "axe",
        "weapon_name": "axe",
        "current_survivor": {"abilities_and_impairments": ["axe_specialization"]},
        "new_survivor": {"abilities_and_impairments": ["axe_specialization"]},
        'epithet': 'axe_master',
    },
    "mastery_spear": {
        "name": "Mastery - Spear",
        "desc": "Whenever a Spear Master hits a monster with a Separ, they may spend 1 survival to gain the Priority Target token. If they made the hit from directly behind another survivor, that survivor gains the Priority Target token instead.",
        "weapon_proficiency": "spear",
        "weapon_name": "spear",
        "current_survivor": {"abilities_and_impairments": ["spear_specialization"]},
        "new_survivor": {"abilities_and_impairments": ["spear_specialization"]},
        'epithet': 'spear_master',
    },
# 1.3
#    "mastery_club": {
#        "name": "Mastery - Club",
#        "desc": "If you are a Club Master, all Clubs in your gear grid gain <b>Savage</b>. On a <b>Perfect hit</b> with a Club, gain <i>+3 strength</i> until the end of the attack.",
#        "weapon_proficiency": "club",
#        "weapon_name": "club",
#        "current_survivor": {"abilities_and_impairments": ["club_specialization"]},
#        "new_survivor": {"abilities_and_impairments": ["club_specialization"]},
#        'epithet': 'club_master',
#    },
    "mastery_fist_and_tooth": {
        "name": "Mastery - Fist & Tooth",
        "desc": "While a survivor is a Fist & Tooth Master, they gain <i>+2 permanent accuracy</i> and <i>+2 permanent strength</i> (they receive this bonus even when not attacking with Fist and Tooth).",
        "weapon_proficiency": "fist_and_tooth",
        "weapon_name": "fist & tooth",
        "current_survivor": {"abilities_and_impairments": ["fist_and_tooth_specialization"]},
        "new_survivor": {"abilities_and_impairments": ["fist_and_tooth_specialization"]},
        'epithet': 'fist_and_tooth_master',
    },
    "mastery_grand_weapon": {
        "name": "Mastery - Grand Weapon",
        "desc": "When a Grand Weapon Master perfectly hits with a grand weapon, cancel all reactions for that attack.",
        "weapon_proficiency": "grand_weapon",
        "weapon_name": "grand weapon",
        "current_survivor": {"abilities_and_impairments": ["grand_weapon_specialization"]},
        "new_survivor": {"abilities_and_impairments": ["grand_weapon_specialization"]},
        'epithet': 'grand_weapon_master',
    },
    "mastery_whip": {
        "name": "Mastery - Whip",
        "desc": "Whip Masters gain <i>+5 strength</i> when attacking with a Whip.",
        "weapon_proficiency": "whip",
        "weapon_name": "whip",
        "current_survivor": {"abilities_and_impairments": ["whip_specialization"]},
        "new_survivor": {"abilities_and_impairments": ["whip_specialization"]},
        'epithet': 'whip_master',
    },
    "mastery_shield": {
        "name": "Mastery - Shield",
        "desc": "When a Shield Master is adjacent to a survivor that is targeted by a monster, they may swap spaces on the baord with the survivor and become the target instead. The master must have a shield to perform this.",
        "weapon_proficiency": "shield",
        "weapon_name": "shield",
        "current_survivor": {"abilities_and_impairments": ["shield_specialization"]},
        "new_survivor": {"abilities_and_impairments": ["shield_specialization"]},
        'epithet': 'shield_master',
    },
    "mastery_dagger": {
        "name": "Mastery - Dagger",
        "desc": "After a wounded hit location is discarded, a Dagger Master who is adjacent to the attacker and the wounded monster may spend 1 survival to re-draw the wounded hit location and attempt to wound with a dagger. Treat monster reactions on the re-drawn hit location card normally.",
        "weapon_proficiency": "dagger",
        "weapon_name": "dagger",
        "current_survivor": {"abilities_and_impairments": ["dagger_specialization"]},
        "new_survivor": {"abilities_and_impairments": ["dagger_specialization"]},
        'epithet': 'dagger_master',
    },
    "mastery_sword": {
        "name": "Mastery - Sword",
        "desc": "A Sword master gains +1 accuracy, +1 strength, and +1 speed when attacking with a Sword.",
        "weapon_proficiency": "sword",
        "weapon_name": "sword",
        "current_survivor": {"abilities_and_impairments": ["sword_specialization"]},
        "new_survivor": {"abilities_and_impairments": ["sword_specialization"]},
        'epithet': 'sword_master',
    },
}

weapon_specializations = {
    "club_specialization": {
        "name": "Specialization - Club",
        "desc": "When attacking with a club, on a <b>perfect hit</b>, double your wound attempt total on the first selected hit location.<br/>Limit, once per attack.",
    },
# 1.3
#    "club_specialization": {
#        "name": "Specialization - Club",
#        "desc": "All clubs in your gear grid gain <b>paired</b>. Cannot use this with two-handed clubs.",
#    },
    "twilight_sword_specialization": {
        "name": "Specialization - Twilight Sword",
        "desc": "This sentient sword improves as it's used. Gain the effect as proficiency rank increases. Rank 2: Ignore <b>Cumbersome</b> on Twilight Sword. Rank 4: When attacking with the Twilight Sword, ignore <b>slow</b> and gain +2 speed. Rank 6: Twilight Sword gains <b>Deadly</b>.",
        "excluded_campaigns": ["people_of_the_stars","people_of_the_sun"],
    },
    "axe_specialization": {
        "name": "Specialization - Axe",
        "desc":  "When attacking with an axe, if your wound attempt fails, you may ignore it and attempt to wound the selected hit location again. Limit, once per attack.",
    },
    "spear_specialization": {
        "name": "Specialization - Spear",
        "desc": "When attacking with a spear, if you draw a <b>trap</b>, roll 1d10. On a 7+, cancel the <b>trap</b>. Discard it, then reshuffle the hit location discard into the hit location deck and draw a new card. Limit, once per round.",
    },
    "fist_and_tooth_specialization": {
        "name": "Specialization - Fist & Tooth",
        "desc":  "You may stand (if knocked down) at the start of the monster's turn or the survivor's turn. Limit once per round.",
    },
    "grand_weapon_specialization": {
        "name": "Specialization - Grand Weapon",
        "desc": "When attacking with a grand weapon, gain <i>+1 accuracy</i>.",
    },
    "whip_specialization": {
        "name": "Specialization - Whip",
        "desc": "When you wound with a whip, instead of moving the top card of the AI deck into the wound stack, you may move the top card of the AI discard pile. Limit once per attack.",
    },
    "shield_specialization": {
        "name": "Specialization - Shield",
        "desc": 'While a shield is in your gear grid, you are no longer knocked down after <b>collision</b> with a monster. While a shield is in your gear grid, add <font class="inline_shield">1</font> to all hit locations.',
    },
    "sword_specialization": {
        "name": "Specialization - Sword",
        "desc": "When attacking with a sword, after drawing hit locations, make a wound attempt and then select a hit location to resolve with that result. Limit, once per attack.",
    },
    "dagger_specialization": {
        "name": "Specialization - Dagger",
        "desc": "When attacking with a Dagger, if a wound attempt fails, after performing any reactions, you may discard another drawn hit location card to attempt to wound that hit location again. Limit, once per attack.",
    },
    "katana_specialization": {
        "name": "Specialization - Katana",
        "desc": "You may not select this as your weapon type.<br/>If you are <b>blind</b> and have 4+ levels of Katana proficiency, gain the following:<br/>On your first <b>Perfect Hit</b> each attack with a Katana, do not draw a hit location. The monster suffers 1 wound.",
        "expansion": "sunstalker",
     },
    "scythe_specialization": {
        "name": "Specialization - Scythe",
        "desc": "When you critically wound with a scythe, roll 1d10. On a 6+, shuffle the hit location deck (do not shuffle unresolved hit locations).<br/>Limit, once per round.",
        "expansion": "dragon_king",
     },
    "bow_specialization": {
        "name": "Specialization - Bow",
        "desc": "When attacking with a bow, you may reroll any misses once. Limit, once per attack.",
    },
    "katar_specialization": {
        "name": "Specialization - Katar",
        "desc": "When attacking with a Katar, cancel reactions on the first selected hit location.",
    },
}

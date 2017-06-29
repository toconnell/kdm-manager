#!/usr/bin/python


abilities_and_impairments = {
    'ageless': {
        'desc': 'You may hunt if you are retired. When you gain Hunt XP, you may decide not to gain it.',
        'max': 1,
        'name': 'Ageless',
        'type': 'ability'
    },
    'analyze': {
        'desc': "At the start of the Survivors' turn, if you are adjacent to the monster, reveal the top AI card, then place back on top of the deck.",
        'max': 1,
        'name': 'Analyze',
        'type': 'ability'
    },
    'bitter_frenzy': {
        'desc': 'You may spend survival and use fighting arts, weapon specialization, and weapon mastery while Frenzied.',
        'max': 1,
        'name': 'Bitter Frenzy',
        'type': 'ability'
    },
    'blue_life_exchange': {
        'desc': 'In the <b>Aftermath</b>, gain 3 additional Hunt XP. You may not place <b>other</b> gear in your grid. Gain +1 permanent luck with each <b>Age</b> milestone. When you retire, you cease to exist.',
        'selectable': False,
        'max': 1,
        'name': 'Blue Life Exchange',
        'related': ['dream_of_the_lantern', 'lucernae'],
        'type': 'ability'
    },
    'bone_witch_scarred_eyes':{
        'Accuracy': -4,
        'Strength': 4,
        'desc': 'Suffer -4 permanent Accuracy and gain +4 permanent strength.',
        'max': 1,
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
    'cancerous_illness': {
        'desc': 'You cannot gain survival.',
        'max': 1,
        'name': 'Cancerous Illness',
        'type': 'impairment',
        'cannot_gain_survival': True,
    },
    'caratosis': {
        'desc': 'For each <font class="affinity_red"> &nbsp; red &nbsp;</font> affinity you have, 1 of your attack rolls hits automatically each attack.',
        'selectable': False,
        'max': 1,
        'name': 'Caratosis',
        'related': ['dream_of_the_beast', 'red_life_exchange'],
        'type': 'ability'
    },
    'crystal_skin': {
        'desc': 'You cannot place armor in your gear grid. When you <b>depart</b>, gain <font class="inline_shield">2</font> to all hit locations. Suffer -1 to the result of all severe injury rolls.',
        'max': 1,
        'name': 'Crystal Skin',
        'type': 'ability'
    },
    'dormenatus': {
        'desc': 'When you <b>depart</b>, gain +1 to every hit location for each <font class="affinity_green"> &nbsp; green &nbsp;</font> affinity you have.',
        'selectable': False,
        'max': 1,
        'name': 'Dormenatus',
        'related': ['dream_of_the_crown', 'green_life_exchange'],
        'type': 'ability'
    },
    'dream_of_the_beast': {
        'affinities': {'red': 1},
        'desc': '1 permanent red affinity.',
        'epithet': 'red_savior',
        'selectable': False,
        'max': 1,
        'name': 'Dream of the Beast',
        'related': ['caratosis', 'red_life_exchange'],
        'type': 'ability'
    },
    'dream_of_the_crown': {
        'affinities': {'green': 1},
        'desc': '1 permanent green affinity.',
        'epithet': 'green_savior',
        'selectable': False,
        'max': 1,
        'name': 'Dream of the Crown',
        'related': ['dormenatus', 'green_life_exchange'],
        'type': 'ability'
    },
    'dream_of_the_lantern': {
        'affinities': {'blue': 1},
        'desc': '1 permanent blue affinity.',
        'epithet': 'blue_savior',
        'selectable': False,
        'max': 1,
        'name': 'Dream of the Lantern',
        'related': ['Lucernae', 'blue_life_exchange'],
        'type': 'ability'
    },
    'endless_babble': {
        'desc': 'When you <b>depart</b>, <b>departing survivors</b> gain +1 insanity. You may not encourage.',
        'max': 1,
        'name': 'Endless Babble',
        'survival_actions': {
            'disable': ['encourage'],
        },
        'type': 'impairment'
    },
    'explore': {
        'desc': 'When you roll on an investigate table, add +2 to your roll result.',
        'max': 1,
        'name': 'Explore',
        'type': 'ability'
    },
    'fated_battle': {
        'desc': 'At the start of a showdown with the picked monster, gain +1 speed token.',
        'name': 'Fated Battle',
        'type': 'ability'
    },
    'forgettable': {
        'Evasion': 2,
        'desc': 'Gain +2 permanent evasion. Forgettable survivors cannot be encouraged.',
        'expansion': 'slenderman',
        'epithet': 'forgettable',
        'max': 1,
        'name': 'Forgettable',
        'type': 'ability'
    },
    'green_life_exchange': {
        'desc': 'In the <b>Aftermath</b>, gain 3 additional Hunt XP. You may not place <b>other</b> gear in your grid. Gain +1 permanent evasion with each <b>Age</b> milestone. When you retire, you cease to exist.',
         'selectable': False,
         'max': 1,
         'name': 'Green Life Exchange',
         'related': ['dream_of_the_crown', 'dormenatus'],
         'type': 'ability'
    },
    "homing_instinct": {
        "name": "Homing Instinct",
        "type": "ability",
        "desc": "Add +5 to your rolls on the Run Away story event."
    },
    "kings_curse": {
        'desc': 'At the Aftermath, <font class="kdm_font">g</font> <b>King\'s Curse</b>.',
        'epithet': "kings_curse",
        'max': 1,
        'name': "King's Curse",
        'type': 'curse'
    },
    'legendcaller': {
        'desc': 'Once a lifetime, on a hunt board space after <b>Overwhelming Darkness</b>, in place of rolling a random hunt event, use "53" as your result.',
        'epithet': 'legendcaller',
        'max': 1,
        'name': 'Legendcaller',
        'type': 'ability'
    },
    'leprosy': {
        'desc': 'Reduce all damage suffered by 1 to a minimum of 1. When rolling on the severe injury table, -2 to any result.',
        'epithet': 'leper',
        'max': 1,
        'name': 'Leprosy',
        'type': 'impairment'
    },
    'leyline_walker': {
        'desc': 'While there is no armor or accessory gear in your grid, gain +3 evasion.',
        'epithet': 'leyline_walker',
        'max': 1,
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
        'desc': 'For every <font class="affinity_blue"> &nbsp; blue &nbsp;</font> affinity you have, your ranged weapons gain this amount of <b>range</b> and your melee weapons gain this amount of <b>reach</b>.',
        'selectable': False,
        'max': 1,
        'name': 'Lucernae',
        'related': ['dream_of_the_lantern', 'blue_life_exchange'],
        'type': 'ability'
    },
    'marrow_hunger': {
        'desc': 'When the Murder or Skull Eater settlement events are drawn, this survivor is nominated.',
        'epithet': 'skull_Eater',
        'max': 1,
        'name': 'Marrow Hunger',
        'type': 'impairment'
    },
    'matchmaker': {
        'desc': 'When you are a returning survivor, once per year you may spend 1 Endeavor to trigger Intimacy (story event).',
        'max': 1,
        'name': 'Matchmaker',
        'type': 'ability'
    },
    'metal_maw': {
        'desc': 'Your Fist & Tooth gains <b>Sharp</b>. (Add 1d10 strength to each wound attempt using this gear. This d10 is not a wound roll, and cannot cause critical wounds.)',
        'max': 1,
        'name': 'Metal Maw',
        'type': 'ability'
    },
    'partner': {
        'desc': 'When you both <b>depart</b>, gain +2 survival. While adjacent to your partner, gain +1 strength. Partners may only nominate each other for <b><font class="kdm_font">g</font> Intimacy</b>. When a partner dies, the remaining partner gains a random disorder and loses this ability.',
        'name': 'Partner',
        'type': 'ability'
    },
    'peerless': {
        'desc': 'When you gain insanity, you may gain an equal amount of survival.',
        'max': 1,
        'name': 'Peerless',
        'type': 'ability'
    },
    'possessed': {
        'Accuracy': 1,
        'Strength': 2,
        'cannot_use_fighting_arts': True,
        'desc': 'Cannot use weapon specialization, weapon mastery, or fighting arts.',
        'max': 1,
        'name': 'Possessed',
        'type': 'ability',
    },
    'prepared': {
        'desc': 'When rolling to determine a straggler, add your hunt experience to your roll result.',
        'max': 1,
        'name': 'Prepared',
        'type': 'ability'
    },
    'red_life_exchange': {
        'desc': 'In the <b>Aftermath</b>, gain 3 additional Hunt XP. You may not place <b>other</b> gear in your grid. Gain +1 permanent strength with each <b>Age</b> milestone. When you retire, you cease to exist.',
        'selectable': False,
        'max': 1,
        'name': 'Red Life Exchange',
        'related': ['caratosis', 'dream_of_the_beast'],
        'type': 'ability'
    },
    'sour_death': {
        'desc': 'When you are knocked down, you may encourage yourself. If you do, gain +1 strength token.',
        'max': 1,
        'name': 'Sour Death',
        'type': 'ability'
    },
    'stalwart': {
        'desc': 'Ignore being knocked down by brain trauma and intimidation actions.',
        'max': 1,
        'name': 'Stalwart',
        'type': 'ability'
    },
    'story_of_the_forsaker': {
        'desc': 'You cannot be knocked down during a showdown with a nemesis monster.',
        'max': 1,
        'name': 'Story of the Forsaker',
        'type': 'ability'
    },
    'story_of_the_goblin': {
        'desc': 'Once per showdown you may...roll 1d10. On a 3+, gain the priority target token and the monster gains +1 damage token.',
        'max': 1,
        'name': 'Story of the Goblin',
        'type': 'ability'
    },
    'story_of_the_young_hero': {
        'desc': 'At the start of your act, you may...[g]ain 2 bleeding tokens and +1 survival.',
        'max': 1,
        'name': 'Story of the Young Hero',
        'type': 'ability'
    },
    'sweet_battle': {
        'desc': 'You may surge without spending survival. If you do, the Activation must be used to activate a weapon.',
        'max': 1,
        'name': 'Sweet Battle',
        'type': 'ability',
        'survival_actions': {
            'enable': ['surge'],
        },
    },
    'thundercaller': {
        'desc': 'Once a lifetime, on a hunt board space after <b>Overwhelming Darkness</b>, in place of rolling a random hunt event, use "100" as your result.',
        'epithet': 'thundercaller',
        'max': 1,
        'name': 'Thundercaller',
        'type': 'ability'
    },
    'tinker': {
        'desc': 'When you are a returning survivor, gain +1 Endeavor to use this settlement phase.',
        'max': 1,
        'name': 'Tinker',
        'type': 'ability'
    },
    'twilight_sword': {
        'desc': 'You may select <b>Twilight Sword</b> as a weapon proficiency type. This weapon may not be removed from your great grid for any reason. When you die, archive your <b>Twilight Sword</b> card.',
        'epithet': 'twilight_sword',
        'max': 1,
        'name': 'Twilight Sword',
        'type': 'curse'
    },
}

severe_injury = {
    'bleeding_kidneys': {
        'desc': 'Gain 2 bleeding tokens.',
        'name': 'Bleeding kidneys',
    },
    'blind': {
        'Accuracy': -1,
        'desc': 'Lose an eye. Suffer -1 permanent Accuracy. This injury is permanent and can be recorded twice. A survivor with two <b>blind</b> severe injuries suffers -4 permanent accuracy and retires at the end of the next showdown or settlement phase, having lost all sight. Gain 1 bleeding token.',
        'epithet': 'The Blind',
        'max': 2,
        'name': 'Blind',
    },
    'broken_arm': {
        'Accuracy': -1,
        'Strength': -1,
        'desc': 'An ear-shattering crunch. Suffer -1 permanent Accuracy and -1 permanent Strength. This injury is permanent and can be recorded twice. Gain 1 bleeding token.',
        'max': 2,
        'name': 'Broken arm',
    },
    'broken_hip': {
        'Movement': -1,
        'desc': 'Your hip is dislocated. You can no longer <b>dodge</b>. Suffer -1 permanent movement. This injury is permanent and can be recorded once. Gain 1 bleeding token.',
        'max': 1,
        'name': 'Broken hip',
        'survival_actions': {
            'disable': ['dodge'],
        }
    },
    'broken_leg': {
        'Movement': -1,
        'desc': 'An ear-shattering crunch! Adjacent survivors suffer 1 brain damage. Suffer -1 permanent movement. This injury is permanent, and can be recorded twice. Gain 1 bleeding token.',
        'max': 2,
        'name': 'Broken leg',
    },
    'broken_rib': {
        'Speed': -1,
        'desc': 'It even hurts to breathe. Suffer -1 permanent speed. This injury is permanent, and can be recorded multiple times. Gain 1 bleeding token.',
        'name': 'Broken rib',
    },
    'bruised_tailbone': {
        'desc': 'The base of your spine is in agony. You cannot <b>dash</b> until showdown ends. You are knocked down. Gain 1 bleeding token.',
        'name': 'Bruised tailbone',
    },
    'collapsed_lung': {
        'desc': "You can't catch a breath. Gain -1 movement token. Gain 1 bleeding token.",
        'name': 'Collapsed Lung',
    },
    'concussion': {
        'desc': 'Your brain is scrambled like an egg. Gain a random disorder. Gain 1 bleeding token.',
        'name': 'Concussion',
    },
    'contracture': {
        'Accuracy': -1,
        'desc': 'The arm will never be the same. Suffer -1 permanent Accuracy. This injury is permanent and can be recorded multiple times. Gain 1 bleeding token.',
        'name': 'Contracture',
    },
    'deaf': {
        'Evasion': -1,
        'desc': 'Suffer -1 permanent Evasion. This injury is permanent and can be recorded once.',
        'max': 1,
        'name': 'Deaf',
    },
    'destroyed_back': {
        'Movement': -2,
        'desc': 'A sharp cracking noise. Suffer -2 permanent movement. You can no longer activate any gear that has 2+ Strength. This injury is permanent and can be recorded once. Gain 1 bleeding token.',
        'max': 1,
        'name': 'Destroyed back',
    },
    'destroyed_genitals': {
        'desc': 'You cannot be nominated for the Intimacy story event. This injury is permanent and can be recorded once. Gain a random disorder. You are knocked down. Gazing upwards, you wonder at the futility of your struggle. Gain +3 insanity. Gain 1 bleeding token.',
        'max': 1,
        'name': 'Destroyed genitals',
        'cannot_be_nominated_for_intimacy': True,
    },
    'destroyed_tooth': {
        'desc': 'If you have 3+ courage, you boldly spit the tooth out and gain +2 insanity! Otherwise. the blow sends you sprawling and you are knocked down.',
        'name': 'Destroyed tooth',
    },
    'disemboweled': {
        'desc': 'Your movement is reduced to 1 until the showdown ends. Gain 1 bleeding token. Skip the next hunt. If you suffer <b>disemboweled</b> during a showdown, at least one other survivor must live to the end of the showdown to carry you back to the settlement. Otherwise, at the end of the showdown, you are lost. Dead.',
        'name': 'Disemboweled',
        'skip_next_hunt': True,
    },
    'dislocated_shoulder': {
        'desc': 'Pop! You cannot activate two-handed or <b>paired</b> weapons or use <b>block</b> until showdown ends. Gain 1 bleeding token.',
        'name': 'Dislocated shoulder',
    },
    'dismembered_arm': {
        'desc': 'Lose an arm. You can no longer activate two-handed weapons. This injury is permanent, and can be recorded twice. A survivor with two <b>dismembered arm</b> severe injuries cannot activate any weapons. Gain 1 bleeding token.',
        'max': 2,
        'name': 'Dismembered Arm',
    },
    'dismembered_leg': {
        'Movement': -2,
        'desc': 'Lose a leg. You suffer -2 permanent movement, and can no longer <b>dash</b>. This injury is permanent and can be recorded twice. A survivor with two <b>dismembered leg</b> severe injuries has lost both of their legs and must retire at the end of the next showdown or settlement phase. Gain 1 bleeding token.',
        'max': 2,
        'name': 'Dismembered leg',
        'survival_actions': {
            'disable': ['dash'],
        }
    },
    'gaping_chest_wound': {
        'Strength': -1,
        'desc': 'Suffer -1 permanent Strength. This injury is permanent and can be recorded multiple times. Gain 1 bleeding token.',
        'name': 'Gaping chest wound',
    },
    'hamstrung': {
        'cannot_use_fighting_arts': True,
        'desc': 'A painful rip. The leg is unusable. You can no longer use any fighting arts or abilities. This injury is permanent and can be recorded once. Gain 1 bleeding token.',
        'max': 1,
        'name': 'Hamstrung',
    },
    'intestinal_prolapse': {
        'desc': 'Your gut is gravely injured. You can no longer equip any gear on your waist, as it is too painful to wear. This injury is permanent, and can be recorded once. Gain 1 bleeding token.',
        'max': 1,
        'name': 'Intestinal prolapse',
    },
    "intracranial_hemorrhage": {
        "name": "Intracranial hemorrhage",
        "desc": "You can no longer use or gain any survival. This injury is permanent and can be recorded once. Gain 1 bleeding token.",
        "cannot_gain_survival": True,
        "cannot_spend_survival": True,
        "max": 1,
    },
    'ruptured_muscle': {
        'cannot_use_fighting_arts': True,
        'desc': 'A painful rip. The arm hangs limp. You can no longer activate fighting arts. This injury is permanent and can be recorded once. Gain 1 bleeding token.',
        'max': 1,
        'name': 'Ruptured muscle',
    },
    'ruptured_spleen': {
        'desc': 'A vicious body blow. Skip the next hunt. Gain 2 bleeding tokens.',
        'name': 'Ruptured spleen',
        'skip_next_hunt': True,
    },
    'shattered_jaw': {
        'desc': 'You drink your meat through a straw. You can no longer <b>consume</b> or be affected by events requiring you to <b>consume</b>. You can no longer <b>encourage</b>. This injury is permanent and can be recorded once. Gain 1 bleeding token.',
        'max': 1,
        'name': 'Shattered jaw',
        'survival_actions': {
            'disable': ['encourage'],
        }
    },
    'slashed_back': {
        'desc': 'Making sudden movement is excruciatingly painful. You cannot <b>surge</b> until showdown ends. Gain 1 bleeding token.',
        'name': 'Slashed back',
        'type': 'severe_injury'
    },
    'spiral_fracture': {
        'desc': 'Your arm twists unnaturally. Gain -2 strength tokens. Skip the next hunt. Gain 1 bleeding token.',
        'name': 'Spiral fracture',
        'skip_next_hunt': True,
    },
    'torn_achilles_tendon': {
        'desc': 'Your leg cannot bear your weight. Until the end of the showdown, whenever you suffer light, heavy, or severe injury, you are also knocked down. Skip the next hunt. Gain 1 bleeding token.',
        'name': 'Torn Achilles Tendon',
        'skip_next_hunt': True,
    },
    'torn_muscle': {
        'desc': 'Your quadriceps is ripped to shreds. You cannot <b>dash</b> until he showdown ends. Skip the next hunt. Gain 1 bleeding token.',
        'name': 'Torn muscle',
        'skip_next_hunt': True,
    },
    'warped_pelvis': {
        'Luck': -1,
        'desc': 'Your pelvis is disfigured. Suffer -1 permanent luck. This injury is permanent and can be recorded multiple times. Gain 1 bleeding token.',
        'name': 'Warped Pelvis',
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
        "expansion": "Spidicules",
        "desc":"Gain +1 permanent strength and +1 permanent evasion.",
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

    # dragon king
    'acid_palms': {
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
        'type': 'ability'
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
        'epithet': 'Gender Swap',
        'expansion': 'white_box',
        'max': 1,
        'name': 'Gender Swap',
        'reverse_sex': True,
        'type': 'curse'
    },

}


weapon_masteries = {
    "mastery_scythe": {
        "name": "Mastery - Scythe",
        "desc": "When you critically wound with a scythe, roll 1d10. On a 6+, shuffle the hit location deck (do not shuffle unresolved hit locations).<br/>Limit, once per round.",
        "expansion": "dragon_king",
        "weapon": "scythe",
    },
    "mastery_katana": {
        "name": "Mastery - Katana",
        "desc": "When a survivor reaches Katana Mastery, they leave the settlement forever, heeding the call of the sstorm to hone their art.<br/>Before the master leaves, you may nominate a survivor. Set that survivor's weapon type to Katana and their weapon proficiency level to 1.",
        "expansion": "sunstalker",
        "add_to_innovations": False,
        "weapon": "katana",
    },
    "mastery_katar": {
        "name": "Mastery - Katar",
        "desc": "If you are a Katar Master, gain a <i>+1 evasion</i> token on a <b>perfect hit</b> with a katar. When you are knocked down, remove all +1 evasion tokens.",
        "weapon": "katar",
    },
    "mastery_bow": {
        "name": "Mastery - Bow",
        "desc": "If you are a Bow Master, all bows in your gear grid gain <b>Deadly 2</b>. In addition, ignore <b>cumbersome</b> on all Bows.",
        "weapon": "bow",
    },
    "mastery_twilight_sword": {
        "name": "Mastery - Twilight Sword",
        "desc": "Any Survivor who attains Twilight Sword Mastery leaves the settlement forever in pursuit of a higher purpose. Remove them from the settlement's population. You may place the master's Twilight Sword in another survivor's gear grid or archive it.",
        "excluded_campaigns": ["People of the Stars","People of the Sun"],
        "weapon": "Twilight Sword",
    },
    "mastery_axe": {
        "name": "Mastery - Axe",
        "desc": "When an Axe Master wounds a monster with an axe at a location with a persistent injury, that wound becomes a critical wound.",
        "weapon": "axe",
    },
    "mastery_spear": {
        "name": "Mastery - Spear",
        "desc": "Whenever a Spear Master hits a monster with a Separ, they may spend 1 survival to gain the Priority Target token. If they made the hit from directly behind another survivor, that survivor gains the Priority Target token instead.",
        "weapon": "spear",
    },
    "mastery_club": {
        "name": "Mastery - Club",
        "desc": "If you are a Club Master, all Clubs in your gear grid gain <b>Savage</b>. On a <b>Perfect hit</b> with a Club, gain <i>+3 strength</i> until the end of the attack.",
        "weapon": "club",
    },
    "mastery_fist_and_tooth": {
        "name": "Mastery - Fist & Tooth",
        "desc": "While a survivor is a Fist & Tooth Master, they gain <i>+2 permanent accuracy</i> and <i>+2 permanent strength</i> (they receive this bonus even when not attacking with Fist and Tooth).",
        "weapon": "fist & tooth",
    },
    "mastery_grand_weapon": {
        "name": "Mastery - Grand Weapon",
        "desc": "When a Grand Weapon Master perfectly hits with a grand weapon, cancel all reactions for that attack.",
        "weapon": "grand weapon",
    },
    "mastery_whip": {
        "name": "Mastery - Whip",
        "desc": "Whip Masters gain <i>+5 strength</i> when attacking with a Whip.",
        "weapon": "whip",
    },
    "mastery_shield": {
        "name": "Mastery - Shield",
        "desc": "When a Shield Master is adjacent to a survivor that is targeted by a monster, they may swap spaces on the baord with the survivor and become the target instead. The master must have a shield to perform this.",
        "weapon": "shield",
    },
    "mastery_dagger": {
        "name": "Mastery - Dagger",
        "desc": "After a wounded hit location is discarded, a Dagger Master who is adjacent to the attacker and the wounded monster may spend 1 survival to re-draw the wounded hit location and attempt to wound with a dagger. Treat monster reactions on the re-drawn hit location card normally.",
        "weapon": "dagger",
    },
    "mastery_sword": {
        "name": "Mastery - Sword",
        "desc": "A Sword master gains +1 accuracy, +1 strength, and +1 speed when attacking with a Sword.",
        "weapon": "sword",
    },
}

weapon_specializations = {
    "twilight_sword_specialization": {
        "name": "Specialization - Twilight Sword",
        "desc": "This sentient sword improves as it's used. Gain the effect as proficiency rank increases. Rank 2: Ignore <b>Cumbersome</b> on Twilight Sword. Rank 4: When attacking with the Twilight Sword, ignore <b>slow</b> and gain +2 speed. Rank 6: Twilight Sword gains <b>Deadly</b>.",
        "excluded_campaigns": ["People of the Stars","People of the Sun"],
    },
    "axe_specialization": {
        "name": "Specialization - Axe",
        "desc":  "When attacking with an axe, if your wound attempt fails, you may ignore it and attempt to wound the selected hit location again. Limit, once per attack.",
    },
    "spear_specialization": {
        "name": "Specialization - Spear",
        "desc": "When attacking with a spear, if you draw a <b>trap</b>, roll 1d10. On a 7+, cancel the <b>trap</b>. Discard it, then reshuffle the hit location discard into the hit location deck and draw a new card. Limit, once per round.",
    },
    "club_specialization": {
        "name": "Specialization - Club",
        "desc": "All clubs in your gear grid gain <b>paired</b>. Cannot use this with two-handed clubs.",
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

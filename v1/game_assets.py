#!/usr/bin/env python

#
#   Only game_asset dictionaries belong in this file. Do not add any methods or
#       other helpers here. Those all belong in models.py
#



#
#   Abilities and Impairments
#

abilities_and_impairments = {
    "Acid Palms": {
        "type": "ability",
        "expansion": "Dragon King",
        "max": 1,
        "desc": "Add 1d10 strength to your wound attempts when attacking with Fist & Tooth.",
    },
    "Heart of the Sword": {
        "type": "ability",
        "expansion": "Dragon King",
        "max": 1,
        "desc": "If you gain weapon proficiency during the Aftermath, gain +3 additional ranks. You cough up a hunk of your own solidified blood and gain +1 <b>Iron</b> strange resource.",
    },
    "Oracle's Eye": {
        "type": "ability",
        "expansion": "Dragon King",
        "max": 1,
        "desc": "At the start of the showdown, look through the AI deck then shuffle.",
        "constellation": {
            "horizontal": "Goblin",
            "vertical": "Witch",
        },
    },
    "Iridescent Hide": {
        "type": "ability",
        "expansion": "Dragon King",
        "max": 1,
        "desc": 'Gain +<font class="inline_shield">1</font> to all hit locations for each different-colored affinity in your gear grid.',
        "constellation": {
            "horizontal": "Absolute",
            "vertical": "Storm",
        },
    },
    "Limb-maker": {
        "type": "ability",
        "expansion": "Dragon King",
        "max": 1,
        "desc": """Once per settlement phase, spend 2 <font class="kdm_font">d</font> to carve a prosthetic limb. Remove a survivor's <b>dismembered</b> injury and add 1 bone to the settlement's storage.""",
    },
    "Presage": {
        "type": "ability",
        "expansion": "Dragon King",
        "max": 1,
        "desc": "Each time you attack, before drawing hit locations, loudly say a name. You lightly bite the eye in your cheek to see what it sees. If you draw any hit locations with that name, gain +3 insanity and +10 strength when attempting to wound them.",
    },
    "Pristine": {
        "type": "ability",
        "expansion": "Dragon King",
        "desc": "When you suffer a <b>dismembered</b> severe injury, ignore it and gain 1 bleeding token instead.",
        "max": 1,
        "constellation": {
            "horizontal": "Gambler",
            "vertical": "Reaper",
        },
    },
    "Psychovore": {
        "type": "ability",
        "expansion": "Dragon King",
        "max": 1,
        "desc": "Once per showdown, you may eat an adjacent survivor's disorder. If you do, remove the disorder. They gain 1 bleeding token and you gain +1 permanent strength. At the end of the showdown, if you haven't eaten a disorder, you die.",
    },
    "Rooted to All": {
        "type": "ability",
        "expansion": "Dragon King",
        "max": 1,
        "desc": "If you are standing at the start of your act, reveal the top 2 cards of the AI deck and put them back in any order.",
    },
    "Twelve Fingers": {
        "type": "ability",
        "expansion": "Dragon King",
        "max": 1,
        "desc": "You cannot carry two-handed gear. On a Perfect hit, your right hand pulses. Gain +5 insanity and +1 luck for the attack. However, for each natural 1 rolled when attempting to hit, your left hand shakes. Suffer 5 brain damage and -1 luck for the attack.",
    },
    "Way of the Rust": {
        "type": "ability",
        "expansion": "Dragon King",
        "max": 1,
        "desc": "Your bleeding tokens are also +1 evasion tokens.",
    },
    "Lovelorn Rock": {
        "type": "impairment",
        "desc": "Forever in love, the straggler loses one gear slot permanently to the rock. This survivor must always leave one gear space empty to hold their rock. The rock can be lost like normal gear.",
    },
    "Sleeping Virus Flower": {
        "expansion": "Flower Knight",
        "type": "curse",
        "desc": 'When you die, a flower blooms from your corpse. Add <font class="kdm_font">g</font> <b>A Warm Virus</b> to the timeline next year. You are the guest.',
        "epithet": "Host",
        "max": 1,
        "Luck": 1,
    },
    "Nightmare Blood": {
        "expansion": "Lonely Tree",
        "type": "ability",
        "desc": 'Whenever you gain a bleeding token, add <font class="inline_shield">1</font> to all hit locations.',
        "max": 1,
    },
    "Nightmare Membrane": {
        "expansion": "Lonely Tree",
        "type": "ability",
        "desc": 'You may spend <font class="kdm_font">a c</font> to exchange any 1 of your tokens for a +1 strength token.',
        "max": 1,
    },
    "Nightmare Spurs": {
        "expansion": "Lonely Tree",
        "type": "ability",
        "desc": "Once per showdown, you may spend all your survival (at least 1) to lose all your +1 strength tokens and gain that many +1 luck tokens.",
        "max": 1,
    },
    "Super Hair": {
        "expansion": "Lonely Tree",
        "type": "ability",
        "desc": 'You may spend <font class="kdm_font">a</font> to freely exchange any tokens with adjacent survivors who have <b>Super Hair</b>.',
        "max": 1,
    },
    "Reflection": {
        "expansion": "Sunstalker",
        "type": "ability",
        "desc": "<ul><li>Your complete affinities and incomplete affinity halves count as all colors.</li><li>You may dodge at any time and as many times as you like each round.</li><li>When you attack from a blind spot, add +1d10 to all wound attempts for that attack.</li></ul>",
        "max": 1,
    },
    "Refraction": {
        "expansion": "Sunstalker",
        "type": "ability",
        "desc": "<ul><li>Your complete affinities and incomplete affinity halves count as all colors.</li><li>During the Showdown, after you perform a survival action, gain +1 survival.</li></ul>",
        "max": 1,
    },
    "Red Glow": {
        "expansion": "Beta Challenge Scenarios",
        "type": "ability",
        "max": 1,
        "desc": '<font class="kdm_font">a</font> Make a melee attack with speed 3, accuracy 7+, and strength 5.',
    },
    "Blue Glow": {
        "expansion": "Beta Challenge Scenarios",
        "type": "ability",
        "max": 1,
        "desc": """<font class="kdm_font">a</font> Move a Portal terrain tile on the showdown board to Snow's space. If there are less than 2 Portals on the board, add one to Snow's space instead.""",
    },
    "Green Glow": {
        "expansion": "Beta Challenge Scenarios",
        "type": "ability",
        "max": 1,
        "desc": '<font class="kdm_font">a</font> Add <font class="inline_shield">1</font> to all hit locations.',
    },
    "Solid": {
        "expansion": "Beta Challenge Scenarios",
        "type": "ability",
        "max": 1,
        "desc": "If you would be knocked down, roll 1d10. On a 4+, you are not knocked down.",
    },
    "Twilight Sword": {
        "type": "curse",
        "desc": "You may select <b>Twilight Sword</b> as a weapon proficiency type. This weapon may not be removed from your great grid for any reason. When you die, archive your <b>Twilight Sword</b> card.",
        "max": 1,
        "epithet": "Twilight Sword",
    },
    "Twilight Succession": {
        "expansion": "Beta Challenge Scenarios",
        "type": "ability",
        "desc": "If you die during the showdown and have a Twilight Sword, nominate another survivor on the showdown board to gain the Twilight Sword and this ability.",
        "max": 1,
    },
	"Death Mehndi": {
		"expansion": "Lion God",
		"type": "curse",
		"desc": "On a <b>Perfect hit</b>, gain 1d10 insanity. -4 to all brain trauma rolls.",
		"max": 1,
	},
    "Hideous Disguise": {
		"expansion": "Lion Knight",
        "type": "curse",
        "desc": "At the start of the showdown, if you are fighting the Lion Knight, choose your Role card.",
        "max": 1,
    },
    "King's Curse": {
        "type": "curse",
        "epithet": "King\\'s Curse",
        "desc": """At the Aftermath, <font class="kdm_font">g</font> <b>King's Curse</b>.""",
        "max": 1,
    },
    "Gender Swap": {
        "expansion": "White Box",
        "type": "curse",
        "desc": "You own the <b>Belt of Gender Swap</b>, it will always take one space in your gear grid and while it is there, your gender is reversed.",
        "reverse_sex": True,
        "epithet": "Gender Swap",
        "max": 1,
    },
    "Crystal Skin": {
        "type": "ability",
        "desc": 'You cannot place armor in your gear grid. When you <b>depart</b>, gain <font class="inline_shield">2</font> to all hit locations. Suffer -1 to the result of all severe injury rolls.',
        "max": 1,
    },
    "Endless Babble": {
        "type": "impairment",
        "desc": "When you <b>depart</b>, <b>departing survivors</b> gain +1 insanity. You may not encourage.",
        "max": 1,
        "survival_actions_disabled": ["Encourage"],
    },
    "Fated Battle": {
        "type": "ability",
        "desc": "At the start of a showdown with the picked monster, gain +1 speed token."
    },
    "Metal Maw": {
        "type": "ability",
        "desc": "Your Fist & Tooth gains <b>Sharp</b>. (Add 1d10 strength to each wound attempt using this gear. This d10 is not a wound roll, and cannot cause critical wounds.)",
        "max": 1,
    },
    "Partner": {
        "type": "ability",
        "desc": 'When you both <b>depart</b>, gain +2 survival. While adjacent to your partner, gain +1 strength. Partners may only nominate each other for <b><font class="kdm_font">g</font> Intimacy</b>. When a partner dies, the remaining partner gains a random disorder and loses this ability.',
    },
    "Specialization - Scythe": {
        "type": "weapon_proficiency",
        "expansion": "Dragon King",
        "max": 1,
        "desc": "When you critically wound with a scythe, roll 1d10. On a 6+, shuffle the hit location deck (do not shuffle unresolved hit locations).<br/>Limit, once per round.",
    },
    "Mastery - Scythe": {
        "type": "weapon_proficiency",
        "expansion": "Dragon King",
        "max": 1,
        "desc": """At the start of a Scythe Master's act, if they are insane, they gain +1 <font class="kdm_font">a</font>, which they may only spend to activate scythes.""",
    },
    "Specialization - Katana": {
        "type": "weapon_proficiency",
        "expansion": "Sunstalker",
        "max": 1,
        "desc": "You may not select this as your weapon type.<br/>If you are <b>blind</b> and have 4+ levels of Katana proficiency, gain the following:<br/>On your first <b>Perfect Hit</b> each attack with a Katana, do not draw a hit location. The monster suffers 1 wound.",
    },
    "Mastery - Katana": {
        "type": "weapon_proficiency",
        "expansion": "Sunstalker",
        "max": 1,
        "desc": "When a survivor reaches Katana Mastery, they leave the settlement forever, heeding the call of the storm to hone their art.<br/>Before the master leaves, you may nominate a survivor. Set that survivor's weapon type to Katana and their weapon proficiency level to 1.",
    },
    "Specialization - Katar": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "When attacking with a Katar, cancel reactions on the first selected hit location.",
    },
    "Mastery - Katar": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "If you are a Katar Master, gain a <i>+1 evasion</i> token on a <b>perfect hit</b> with a katar. When you are knocked down, remove all +1 evasion tokens.",
    },
    "Specialization - Bow": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "When attacking with a bow, you may reroll any misses once. Limit, once per attack",
    },
    "Mastery - Bow": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "If you are a Bow Master, all Bows in your gear grid gain <b>Deadly 2</b>. In addition, ignore <b>cumbersome</b> on all Bows.",
    },
    "Specialization - Twilight Sword": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "This sentient sword improves as it's used. Gain the effect as proficiency rank increases. Rank 2: Ignore <b>Cumbersome</b> on Twilight Sword. Rank 4: When attacking with the Twilight Sword, ignore <b>slow</b> and gain +2 speed. Rank 6: Twilight Sword gains <b>Deadly</b>.",
    },
    "Mastery - Twilight Sword": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "Any Survivor who attains Twilight Sword Mastery leaves the settlement forever in pursuit of a higher purpose. Remove them from the settlement's population. You may place the master's Twilight Sword in another survivor's gear grid or archive it.",
    },
    "Specialization - Axe": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "When attacking with an axe, if your wound attempt fails, you may ignore it and attempt to wound the selected hit location again. Limit, once per attack.",
    },
    "Mastery - Axe": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "When an Axe Master wounds a monster with an axe at a location with a persistent injury, that wound becomes a critical wound.",
    },
    "Specialization - Spear": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "When attacking with a spear, if you draw a <b>trap</b>, roll 1d10. On a 7+, cancel the <b>trap</b>. Discard it, then reshuffle the hit location discard into the hit location deck and draw a new card. Limit, once per round.",
    },
    "Mastery - Spear": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "Whenever a Spear Master hits a monster with a Separ, they may spend 1 survival to gain the Priority Target token. If they made the hit from directly behind another survivor, that survivor gains the Priority Target token instead.",
    },
    "Specialization - Club": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "All clubs in your gear grid gain <b>paired</b>. Cannot use this with two-handed clubs.",
    },
    "Mastery - Club": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "If you are a Club Master, all Clubs in your gear grid gain <b>Savage</b>. On a <b>Perfect hit</b> with a Club, gain <i>+3 strength</i> until the end of the attack.",
    },
    "Specialization - Fist & Tooth": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "You may stand (if knocked down) at the start of the monster's turn or the survivor's turn. Limit once per round.",
    },
    "Mastery - Fist & Tooth": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "While a survivor is a Fist & Tooth Master, they gain <i>+2 permanent accuracy</i> and <i>+2 permanent strength</i> (they receive this bonus even when not attacking with Fist and Tooth).",
    },
    "Specialization - Grand Weapon": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "When attacking with a grand weapon, gain <i>+1 accuracy</i>.",
    },
    "Mastery - Grand Weapon": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "When a Grand Weapon Master perfectly hits with a grand weapon, cancel all reactions for that attack.",
    },
    "Specialization - Whip": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "When you wound with a whip, instead of moving the top card of the AI deck into the wound stack, you may move the top card of the AI discard pile. Limit once per attack.",
    },
    "Mastery - Whip": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "Whip Masters gain <i>+5 strength</i> when attacking with a Whip.",
    },
    "Mastery - Shield": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "When a Shield Master is adjacent to a survivor that is targeted by a monster, they may swap spaces on the baord with the survivor and become the target instead. The master must have a shield to perform this.",
    },
    "Specialization - Shield": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": 'While a shield is in your gear grid, you are no longer knocked down after <b>collision</b> with a monster. While a shield is in your gear grid, add <font class="inline_shield">1</font> to all hit locations.',
    },
    "Specialization - Dagger": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "When attacking with a Dagger, if a wound attempt fails, after performing any reactions, you may discard another drawn hit location card to attempt to wound that hit location again. Limit, once per attack.",
    },
    "Mastery - Dagger": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "After a wounded hit location is discarded, a Dagger Master who is adjacent to the attacker and the wounded monster may spend 1 survival to re-draw the wounded hit location and attempt to wound with a dagger. Treat monster reactions on the re-drawn hit location card normally.",
    },
    "Specialization - Sword": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "When attacking with a sword, after drawing hit locations, make a wound attempt and then select a hit location to resolve with that result. Limit, once per attack.",
    },
    "Mastery - Sword": {
        "type": "weapon_proficiency",
        "max": 1,
        "desc": "A Sword master gains +1 accuracy, +1 strength, and +1 speed when attacking with a Sword."
    },
    "Thundercaller": {
        "type": "ability",
        "desc": 'Once a lifetime, on a hunt board space after <b>Overwhelming Darkness</b>, in place of rolling a random hunt event, use "100" as your result.',
        "max": 1,
        "epithet": "Thundercaller",
    },
    "Legendcaller": {
        "type": "ability",
        "desc": 'Once a lifetime, on a hunt board space after <b>Overwhelming Darkness</b>, in place of rolling a random hunt event, use "53" as your result.',
        "max": 1,
        "epithet": "Legendcaller",
    },
    "Analyze": {
        "type": "ability",
        "desc": "At the start of the Survivors' turn, if you are adjacent to the monster, reveal the top AI card, then place back on top of the deck.",
        "max": 1,
    },
    "Explore": {
        "type": "ability",
        "desc": "When you roll on an investigate table, add +2 to your roll result.",
        "max": 1,
    },
    "Tinker": {
        "type": "ability",
        "desc": "When you are a returning survivor, gain +1 Endeavor to use this settlement phase.",
        "max": 1,
    },
    "Stalwart": {
        "type": "ability",
        "desc": "Ignore being knocked down by brain trauma and intimidation actions.",
        "max": 1,
    },
    "Prepared": {
        "type": "ability",
        "desc": "When rolling to determine a straggler, add your hunt experience to your roll result.",
        "max": 1,
    },
    "Matchmaker": {
        "type": "ability",
        "desc": "When you are a returning survivor, once per year you may spend 1 Endeavor to trigger Intimacy (story event).",
        "max": 1,
    },
    "Leprosy": {
        "type": "impairment",
        "desc": "Reduce all damage suffered by 1 to a minimum of 1. When rolling on the severe injury table, -2 to any result.",
        "max": 1,
        "epithet": "Leper",
    },
    "Cancerous Illness": {
        "type": "impairment",
        "desc": "You cannot gain survival.",
        "max": 1,
    },
    "Marrow Hunger": {
        "type": "impairment",
        "desc": "When the Murder or Skull Eater settlement events are drawn, this survivor is nominated.",
        "max": 1,
        "epithet": "Skull Eater",
    },
    "Sweet Battle": {
        "type": "ability",
        "desc": "You may surge without spending survival. If you do, the Activation must be used to activate a weapon.",
        "max": 1,
    },
    "Bitter Frenzy": {
        "type": "ability",
        "desc": "You may spend survival and use fighting arts, weapon specialization, and weapon mastery while Frenzied.",
        "max": 1,
    },
    "Sour Death": {
        "type": "ability",
        "desc": "When you are knocked down, you may encourage yourself. If you do, gain +1 strength token.",
        "max": 1,
    },
    "Ageless": {
        "type": "ability",
        "desc": "You may hunt if you are retired. When you gain Hunt XP, you may decide not to gain it.",
        "max": 1,
    },
    "Peerless": {
        "type": "ability",
        "desc": "When you gain insanity, you may gain an equal amount of survival.",
        "max": 1,
    },
    "Leyline Walker": {
        "type": "ability",
        "desc": "While there is no armor or accessory gear in your grid, gain +3 evasion.",
        "max": 1,
        "epithetp": "Leyline Walker",
    },
    "Story of the Goblin": {
        "type": "ability",
        "desc": "Once per showdown you may...roll 1d10. On a 3+, gain the priority target token and the monster gains +1 damage token.",
        "max": 1,
    },
    "Story of the Forsaker": {
        "type": "ability",
        "desc": "You cannot be knocked down during a showdown with a nemesis monster.",
        "max": 1,
    },
    "Story of the Young Hero": {
        "type": "ability",
        "desc": "At the start of your act, you may...[g]ain 2 bleeding tokens and +1 survival.",
        "max": 1,
    },
    "Possessed": {
        "type": "ability",
        "desc": "Cannot use weapon specialization, weapon mastery, or fighting arts.",
        "cannot_use_fighting_arts": True,
        "Strength": 2,
        "Accuracy": 1,
        "max": 1,
    },
    "Bone Witch - Scarred Eyes": {
        "type": "impairment",
        "desc": "Suffer -4 permanent Accuracy and gain +4 permanent strength (p.109).",
        "Accuracy": -4,
        "Strength": 4,
        "max": 1,
    },
    "Bone Witch - Wounds": {
        "type": "impairment",
        "desc": "Suffer -1 permanent strength, -1 permanent accuracy and skip the next hunt (p.109).",
        "skip_next_hunt": True,
        "Accuracy": -1,
        "Strength": -1,
    },
    "Homing Instinct": {
        "type": "ability",
        "desc": "Add +5 to your rolls on the Run Away story event."
    },
    # Severe Injuries start here! severe injuries
    "Intracranial hemmorhage": {
        "type": "severe_injury",
        "desc": "You can no longer use or gain any survival. This injury is permanent and can be recorded once. Gain 1 bleeding token.",
        "cannot_gain_survival": True,
        "cannot_spend_survival": True,
        "max": 1,
    },
    "Deaf": {
        "type": "severe_injury",
        "desc": "Suffer -1 permanent Evasion. This injury is permanent and can be recorded once.",
        "Evasion": -1,
        "max": 1,
    },
    "Blind": {
        "type": "severe_injury",
        "desc": "Lose an eye. Suffer -1 permanent Accuracy. This injury is permanent and can be recorded twice. A survivor with two <b>blind</b> severe injuries suffers -4 permanent accuracy and retires at the end of the next showdown or settlement phase, having lost all sight. Gain 1 bleeding token.",
        "Accuracy": -1,
        "max": 2,
        "epithet": "The Blind",
    },
    "Concussion": {
        "type": "severe_injury",
        "desc": "Your brain is scrambled like an egg. Gain a random disorder. Gain 1 bleeding token.",
    },
    "Shattered jaw": {
        "type": "severe_injury",
        "desc": "You drink your meat through a straw. You can no longer <b>consume</b> or be affected by events requiring you to <b>consume</b>. You can no longer <b>encourage</b>. This injury is permanent and can be recorded once. Gain 1 bleeding token.",
        "survival_actions_disabled": ["Encourage"],
        "max": 1,
    },
    "Destroyed tooth": {
        "type": "severe_injury",
        "desc": "If you have 3+ courage, you boldly spit the tooth out and gain +2 insanity! Otherwise. the blow sends you sprawling and you are knocked down.",
    },
    "Dismembered Arm": {
        "type": "severe_injury",
        "desc": "Lose an arm. You can no longer activate two-handed weapons. This injury is permanent, and can be recorded twice. A survivor with two <b>dismembered arm</b> severe injuries cannot activate any weapons. Gain 1 bleeding token.",
        "max": 2,
    },
    "Ruptured muscle": {
        "type": "severe_injury",
        "desc": "A painful rip. The arm hangs limp. You can no longer activate fighting arts. This injury is permanent and can be recorded once. Gain 1 bleeding token.",
        "cannot_use_fighting_arts": True,
        "max": 1,
    },
    "Contracture": {
        "type": "severe_injury",
        "desc": "The arm will never be the same. Suffer -1 permanent Accuracy. This injury is permanent and can be recorded multiple times. Gain 1 bleeding token.",
        "Accuracy": -1,
    },
    "Broken arm": {
        "type": "severe_injury",
        "desc": "An ear-shattering crunch. Suffer -1 permanent Accuracy and -1 permanent Strength. This injury is permanent and can be recorded twice. Gain 1 bleeding token.",
        "Accuracy": -1,
        "Strength": -1,
        "max": 2,
    },
    "Spiral fracture": {
        "type": "severe_injury",
        "desc": "Your arm twists unnaturally. Gain -2 strength tokens. Skip the next hunt. Gain 1 bleeding token.",
        "skip_next_hunt": True,
    },
    "Dislocated shoulder": {
        "type": "severe_injury",
        "desc": "Pop! You cannot activate two-handed or <b>paired</b> weapons or use <b>block</b> until showdown ends. Gain 1 bleeding token.",
    },
    "Gaping chest wound": {
        "type": "severe_injury",
        "desc": "Suffer -1 permanent Strength. This injury is permanent and can be recorded multiple times. Gain 1 bleeding token.",
        "Strength": -1,
    },
    "Destroyed back": {
        "type": "severe_injury",
        "desc": "A sharp cracking noise. Suffer -2 permanent movement. You can no longer activate any gear that has 2+ Strength. This injury is permanent and can be recorded once. Gain 1 bleeding token.",
        "Movement": -2,
        "max": 1,
    },
    "Disemboweled": {
        "type": "severe_injury",
        "desc": "Your movement is reduced to 1 until the showdown ends. Gain 1 bleeding token. Skip the next hunt. If you suffer <b>disemboweled</b> during a showdown, at least one other survivor must live to the end of the showdown to carry you back to the settlement. Otherwise, at the end of the showdown, you are lost. Dead.",
        "skip_next_hunt": True,
    },
    "Ruptured spleen": {
        "type": "severe_injury",
        "desc": "A vicious body blow. Skip the next hunt. Gain 2 bleeding tokens.",
        "skip_next_hunt": True,
    },
    "Broken rib": {
        "type": "severe_injury",
        "desc": "It even hurts to breathe. Suffer -1 permanent speed. This injury is permanent, and can be recorded multiple times. Gain 1 bleeding token.",
        "Speed": -1,
    },
    "Collapsed Lung": {
        "type": "severe_injury",
        "desc": "You can't catch a breath. Gain -1 movement token. Gain 1 bleeding token.",
    },
    "Intestinal prolapse": {
        "type": "severe_injury",
        "desc": "Your guy is gravely injured. You can no longer equip any gear on your waist, as it is too painful to wear. This injury is permanent, and can be recorded once. Gain 1 bleeding token.",
        "max": 1,
    },
    "Warped Pelvis": {
        "type": "severe_injury",
        "desc": "Your pelvis is disfigured. Suffer -1 permanent luck. This injury is permanent and can be recorded multiple times. Gain 1 bleeding token.",
        "Luck": -1,
    },
    "Destroyed genitals": {
        "type": "severe_injury",
        "desc": "You cannot be nominated for the Intimacy story event. This injury is permanent and can be recorded once. Gain a random disorder. You are knocked down. Gazing upwards, you wonder at the futility of your struggle. Gain +3 insanity. Gain 1 bleeding token.",
        "max": 1,
    },
    "Broken hip": {
        "type": "severe_injury",
        "desc": "Your hip is dislocated. You can no longer <b>dodge</b>. Suffer -1 permanent movement. This injury is permanent and can be recorded once. Gain 1 bleeding token.",
        "Movement": -1,
        "max": 1,
        "survival_actions_disabled": ["Dodge"],
    },
    "Slashed back": {
        "type": "severe_injury",
        "desc": "Making sudden movement is excruciatingly painful. You cannot <b>surge</b> until showdown ends. Gain 1 bleeding token.",
    },
    "Bruised tailbone": {
        "type": "severe_injury",
        "desc": "The base of your spine is in agony. You cannot <b>dash</b> until showdown ends. You are knocked down. Gain 1 bleeding token.",
    },
    "Dismembered leg": {
        "type": "severe_injury",
        "desc": "Lose a leg. You suffer -2 permanent movement, and can no longer <b>dash</b>. This injury is permanent and can be recorded twice. A survivor with two <b>dismembered leg</b> severe injuries has lost both of their legs and must retire at the end of the next showdown or settlement phase. Gain 1 bleeding token.",
        "survival_actions_disabled": ["Dash"],
        "Movement": -2,
        "max": 2,
    },
    "Hamstrung": {
        "type": "severe_injury",
        "desc": "A painful rip. The leg is unusable. You can no longer use any fighting arts or abilities. This injury is permanent and can be recorded once. Gain 1 bleeding token.",
        "max": 1,
        "cannot_use_fighting_arts": True,
    },
    "Torn Achilles Tendon": {
        "type": "severe_injury",
        "desc": "Your leg cannot bear your weight. Until the end of the showdown, whenever you suffer light, heavy, or severe injury, you are also knocked down. Skip the next hunt. Gain 1 bleeding token.",
        "skip_next_hunt": True,
    },
    "Torn muscle": {
        "type": "severe_injury",
        "desc": "Your quadriceps is ripped to shreds. You cannot <b>dash</b> until he showdown ends. Skip the next hunt. Gain 1 bleeding token.",
        "skip_next_hunt": True,
    },
    "Broken leg": {
        "type": "severe_injury",
        "desc": "An ear-shattering crunch! Adjacent survivors suffer 1 brain damage. Suffer -1 permanent movement. This injury is permanent, and can be recorded twice. Gain 1 bleeding token.",
        "Movement": -1,
        "max": 2,
    },

    # savior A&I's. set to HIDDEN so they don't show up in any list
    "Dream of the Beast" : {
        "type": "ability",
        "expansion": "HIDDEN",
        "desc": "1 permanent red affinity.",
        "affinities": {"red": 1},
        "max": 1,
        "related": ["Caratosis", "Red Life Exchange"],
        "epithet": "Red Savior"
    },
    "Caratosis" : {
        "type": "ability",
        "expansion": "HIDDEN",
        "desc": 'For each <font class="affinity_red"> &nbsp; red &nbsp;</font> affinity you have, 1 of your attack rolls hits automatically each attack.',
        "max": 1,
        "related": ["Dream of the Beast", "Red Life Exchange"],
    },
    "Red Life Exchange" : {
        "type": "ability",
        "expansion": "HIDDEN",
        "desc": "In the <b>Aftermath</b>, gain 3 additional Hunt XP. You may not place <b>other</b> gear in your grid. Gain +1 permanent strength with each <b>Age</b> milestone. When you retire, you cease to exist.",
        "max": 1,
        "related": ["Caratosis", "Dream of the Beast"],
    },
    "Dream of the Crown" : {
        "type": "ability",
        "expansion": "HIDDEN",
        "desc": "1 permanent green affinity.",
        "affinities": {"green": 1},
        "max": 1,
        "related": ["Dormenatus", "Green Life Exchange"],
        "epithet": "Green Savior"
    },
    "Dormenatus" : {
        "type": "ability",
        "expansion": "HIDDEN",
        "desc": 'When you <b>depart</b>, gain +1 to every hit location for each <font class="affinity_green"> &nbsp; green &nbsp;</font> affinity you have.',
        "max": 1,
        "related": ["Dream of the Crown", "Green Life Exchange"],
    },
    "Green Life Exchange" : {
        "type": "ability",
        "expansion": "HIDDEN",
        "desc": "In the <b>Aftermath</b>, gain 3 additional Hunt XP. You may not place <b>other</b> gear in your grid. Gain +1 permanent evasion with each <b>Age</b> milestone. When you retire, you cease to exist.",
        "max": 1,
        "related": ["Dream of the Crown", "Dormenatus"],
    },
    "Dream of the Lantern" : {
        "type": "ability",
        "expansion": "HIDDEN",
        "desc": "1 permanent blue affinity.",
        "affinities": {"blue": 1},
        "max": 1,
        "related": ["Lucernae", "Blue Life Exchange"],
        "epithet": "Blue Savior"
    },
    "Lucernae" : {
        "expansion": "HIDDEN",
        "type": "ability",
        "desc": 'For every <font class="affinity_blue"> &nbsp; blue &nbsp;</font> affinity you have, your ranged weapons gain this amount of <b>range</b> and your melee weapons gain this amount of <b>reach</b>.',
        "max": 1,
        "related": ["Dream of the Lantern", "Blue Life Exchange"],
    },
    "Blue Life Exchange" : {
        "expansion": "HIDDEN",
        "type": "ability",
        "desc": "In the <b>Aftermath</b>, gain 3 additional Hunt XP. You may not place <b>other</b> gear in your grid. Gain +1 permanent luck with each <b>Age</b> milestone. When you retire, you cease to exist.",
        "max": 1,
        "related": ["Dream of the Lantern", "Lucernae"],
    },
}



#
#   Disorders
#

disorders = {
    "Superstitious": {
        "expansion": "Dragon King",
        "flavor_text": "Evil magic will be your undoing. You do not believe in abusing the other.",
        "survivor_effect": "You cannot activate or <b>depart</b> with other gear in your gear grid.",
    },
    "Arithmophilia": {
        "expansion": "Dragon King",
        "flavor_text": "You love numbers. Your life must exist in perfect arithmetical harmony.",
        "survivor_effect": "When you gain this disorder, roll 1d5. Your movement is that number.<br/>Ignore all other movement modifiers.",
    },
    "Performance Anxiety": {
        "expansion": "Dragon King",
        "flavor_text": "You're not ready to love.",
        "survivor_effect": "You cannot be nominated for <b>Intimacy</b>.<br/>Cure this disorder if you have 8+ courage.",
    },
    "Destined": {
        "expansion": "Dragon King",
        "flavor_text": "You have a grand destiny that you must fulfill.",
        "survivor_effect": "If you do not <b>depart</b>, lose all survival and insanity.",
        "constellation": {
            "vertical": "Rust",
            "horizontal": "Gambler",
        },
    },
    "Flower Addiction": {
        "expansion": "Flower Knight",
        "flavor_text": "An insatiable hunger has bloomed in you, delicate and sickeningly sweet.",
        "survivor_effect": "You may only <b>depart</b> to hunt the Flower Knight.<br/>After you <b>depart</b>, cure this disorder.",
    },
    "Ghostly Beauty": {
        "expansion": "Flower Knight",
        "flavor_text": "You cannot experience fear if you do not exist.",
        "survivor_effect": "Double all insanity you gain.<br/>Double all survival you spend.",
    },
    "Narcissistic": {
        "expansion": "Flower Knight",
        "flavor_text": "There is nothing in the world more beautiful than yourself.",
        "survivor_effect": "You may not wear armor at the head location. If you are wearing armor at the head location when you gain this disorder, archive it.",
    },
    "Overprotective" :{
        "expansion": "Sunstalker",
        "flavor_text": "You love the feeling of being needed.",
        "survivor_effect": "When an adjacent survivor is knocked down, you are also knocked down as you rush to their aid.",
    },
    "Sun-Drunk" :{
        "expansion": "Sunstalker",
        "flavor_text": "When your emotions rise, you can only think of violence.",
        "survivor_effect": 'When you have any +1 strength tokens, you cannot <b>dash</b>, <b>dodge</b> or <font class="kdm_font">g</font> <b>Run Away</b>.',
    },
    "Emotionless" :{
        "expansion": "Sunstalker",
        "flavor_text": "You don't have any emotions. You've hidden this from everyone by mimicking their social interactions.",
        "survivor_effect": "You cannot gain +1 strength tokens.",
    },
    "Sworn Enemy": {
        "expansion": "Beta Challenge Scenarios",
        "survivor_effect": "When you gain this, choose a monster. You may only depart to face the chosen monster. Your attacks against the chosen monster gain +1 speed and +1 strength.",
    },
	"Delicious": {
		"expansion": "Lion God",
		"flavor_text": "Predators of all shapes and sizes find your scent irresistible.",
		"survivor_effect": "You are still considered a threat when you are knocked down (unless you use an effect that says otherwise).",
	},
	"Enfeebled": {
		"expansion": "Lion God",
		"flavor_text": "You are delicate flower, wilting in the darkness.",
		"survivor_effect": "It takes one less bleeding token to kill you.",
	},
	"Stark Raving": {
		"expansion": "Lion God",
		"flavor_text": "Freedom awaits those pushed this far beyond the breaking point.",
		"survivor_effect": "You are always <b>insane</b>, regardless of your insanity.",
	},
	"Tunnel Vision": {
		"expansion": "Lion God",
		"flavor_text": "If you're not killing something, you're wasting your time.",
		"survivor_effect": 'When you spend <font class="kdm_font">a</font>, you may only activate weapons.',
	},
    "Stage Fright": {
        "expansion": "Lion Knight",
        "flavor_text": "You hate being the center of attention.",
        "survivor_effect": "Whenever you become <b>doomed</b> or gain the <b>priority target</b> token, lose 1 survival.",
    },
    "Shallow Lungs": {
        "expansion": "Lion Knight",
        "flavor_text": "Yelling makes you feel light-headed.",
        "survivor_effect": "When you <b>encourage</b>, you are knocked down.",
    },
    "Primma Donna": {
        "expansion": "Lion Knight",
        "flavor_text": "The double-edged sword of fame is the only weapon you require.",
        "survivor_effect": "Each survivor turn, you must take your act first (roll off each turn if multiple survivors have this disorder).",
    },
    "Unlucky": {
        "expansion": "Lion Knight",
        "flavor_text": "Your mother always said you were born under a bad sign.",
        "survivor_effect": "You cannot critically wound.",
    },
    "Vermin Obsession": {
        "expansion": "Dung Beetle Knight",
        "flavor_text": "You love insects.",
        "survivor_effect": "While there is a <b>Bug Spot</b> terrain tile on the showdown board, you are so overwhelmed that you are <b>doomed</b>.",
    },
    "Motion Sickness": {
        "expansion": "Dung Beetle Knight",
        "flavor_text": "Moving quickly makes you vomit.",
        "survivor_effect": "Whenever you suffer <b>knockback</b>, gain 1 bleeding token.",
    },
    "Megalophobia": {
        "expansion": "Gorm",
        "flavor_text": "Even large, looming shadows make you jumpy.",
        "survivor_effect": "You may not <b>depart</b> for hunts or showdowns with monsters that occupy more than 4 spaces on the showdown board.",
    },
    "Absent Seizures": {
        "expansion": "Gorm",
        "flavor_text": "No one knows where your mind goes when you're gone, not even you.",
        "survivor_effect": "The first time you would suffer a brain trauma each showdown, you are instead knocked down and forget a fighting art (erase it).",
    },
    "Fear of the Dark": {
        "flavor_text": "You cannot bear the oppressive darkness any longer.",
        "survivor_effect": "You retire.<br/>If you gain this disorder during a hunt or showdown, you put on a brave face until you return to the settlement, vowing never to leave the Lantern Hoard again.",
        "retire": True,
    },
    "Hoarder": {
        "flavor_text": "You compulsively collect and stash anything you can get your hands on. Every little bit you add to your secret hoard makes your existence feel more real.",
        "survivor_effect": "Whenever you are a <b>returning</b> survivor, archive 1 resource gained from the last showdown and gain +1 courage.",
    },
    "Binge Eating Disorder": {
        "flavor_text": "Eating is the only thing that helps you escape your miserable life.",
        "survivor_effect": "You cannot <b>depart</b> unless you have <b>consumable</b> gear in your gear grid. You must <b>consume</b> if a choice to <b>consume</b> arises.",
    },
    "Squeamish": {
        "flavor_text": "You can't handle bad smells.",
        "survivor_effect": "You cannot <b>depart</b> with any <b>stinky</b> gear in your gear grid. If a status or effect would cause you to become stinky, lose all your survival.",
    },
    "Secretive": {
        "flavor_text": "You love secrets. So much, in fact, that you pretend to have many.",
        "survivor_effect": "When you are a <b>returning survivor</b>, you quickly become preoccuiped with your own affairs. You must skip the next hunt to deal with them.",
        "on_return": {
            "skip_next_hunt": "checked",
        },
    },
    "Seizures": {
        "flavor_text": "Lingering damage from your head injuries has caused you to experience period of of uncontrollable shaking and absence of thought.",
        "survivor_effect": "During the showdown, whenever you suffer damage to your head location, you are knocked down.",
    },
    "Immortal": {
        "flavor_text": "You are immortal! You will live forever and cannot be killed.",
        "survivor_effect": "While you are insane, convert all damage dealt to your hit locations to brain damage.<br/>You are so busy reveling in your own glory that you cannot spend survival while insane.",
    },
    "Coprolalia": {
        "flavor_text": "You have compulsive tics in the form of sporadic muttering, cursing, whimpering, and screaming.",
        "survivor_effect": "All your gear is <b>noisy</b>. You are always a threat unless you are knocked down, even if an effect says otherwise.",
    },
    "Prey": {
        "flavor_text": "You are prey. All there is for you is death.",
        "survivor_effect": "You may not spend survival unless you are insane.",
    },
    "Honorable": {
        "flavor_text": "You believe in honor and fairness when conducting yourself on the battlefield. It is these strong principles that have kept you alive, and you will not abandon them under any circumstances.",
        "survivor_effect": "You cannot attack a monster from its blind spot or if it is knocked down.",
    },
    "Apathetic": {
        "flavor_text": "You've given up. Nothing seems to matter. You have no concern for your own wellbeing.",
        "survivor_effect": "You cannot use or gain survival. You cannot gain courage. Cure this disorder if you have 8+ understanding.",
    },
    "Weak Spot": {
        "flavor_text": "You have an imaginary infirmity.",
        "survivor_effect": "When you gain this disorder, roll a random hit location and record it. You cannot <b>depart</b> unless you have armor at this hit location.",
    },
    "Hyperactive": {
        "flavor_text": "Whether you are running, fiddling with your gear, or pacing, you are always moving.",
        "survivor_effect": "During the showdown, you must move at least 1 space every round.",
    },
    "Aichmophobia": {
        "flavor_text": "Sharp things make you uncomfortable. It's just a matter of time before someone cuts themselves.",
        "survivor_effect": "You cannot activate or <b>depart</b> with axes, swords, spears, daggers, scythes, or katars in your gear grid.",
    },
    "Hemophobia": {
        "flavor_text": "The mere sight of blood makes you lightheaded, and serious gore can knock you out!",
        "survivor_effect": "During the showdown, whenever a survivor (including you) gains a bleeding token, you are knocked down.",
    },
    "Vestiphobia": {
        "flavor_text": "Even the lightest armor rubs harshly against your skin and constricts your ability to move.",
        "survivor_effect": "You cannot wear armor at the body location. If you are wearing armor at the body location when you gain this disorder, archive it as you tear it off your person!",
    },
    "Traumatized": {
        "flavor_text": "Your experiences have left you shaken and paralyzed by fear.",
        "survivor_effect": "Whenever you end your act adjacent to a monster, you are knocked down.",
    },
    "Monster Panic": {
        "flavor_text": "Monsters make you feel bad. Really, really bad.",
        "survivor_effect": "Whenever you suffer brain damage from an <b>Intimidate</b> action, suffer 1 additional brain damage.",
    },
    "Post-Traumatic Stress": {
        "flavor_text": "The last hunt was harrowing. All you can do is cower and relive the trauma. Only time can heal your wounds.",
        "survivor_effect": "Next settlement phase, you do not contribute or participate in any endeavors. Skip the next hunt to recover.",
        "skip_next_hunt": True,
    },
    "Rageholic": {
        "flavor_text": "Your rage boils out of control, causing you to see red at the slightest provocation.",
        "survivor_effect": "Whenever you suffer a severe injury, also suffer the <b>frenzy</b> brain trauma.",
    },
    "Indecision": {
        "flavor_text": "Past decisions haunt you ceaselessly. You are crippled by indecision, and even the most trivial choices grip you with terror.",
        "survivor_effect": "If you are the event revealer of hunt events that call on you to make a roll, roll twice and use the lower result.",
    },
    "Anxiety": {
        "flavor_text": "You are afraid of being afraid. You're a nervous wreck, and monsters can smell this in your scent.",
        "survivor_effect": "At the start of each showdown, gain the <b>priority target</b> token unless you have <b>stinky</b> gear in your gear grid.",
    },
    "Quixotic": {
        "flavor_text": "You carry the weight of your settlement on your shoudlers. Everyone is counting on you to save them, and you will rise to the challenge.",
        "survivor_effect": "If you are insane when you <b>depart</b>, gain +1 survival and +1 Strength token.",
    },
}




fighting_arts = {
    "Eternal Will": {
        "expansion": "Manhunter",
        "desc": "Gain +1 accuracy and +1 strength for each permanent injury you have.<br/>You may always <b>depart</b>, even when retired.",
        "secret": True,
    },
    "Abyssal Sadist": {
        "expansion": "Manhunter",
        "desc": "The first time you wound the monster each attack, gain +1 survival and +1 insanity.<br/>Ignore the effects of the <b>Fear of the Dark</b> and <b>Prey</b> disorders.",
        "epithet": "Sadist",
    },
    "Seasoned Hunter": {
        "expansion": "Manhunter",
        "desc": "Whenever a random hunt event result is:<br/>11, 22, 33, 44, 55, 66, 77, 88, 99 or 100,<br/>the event revealer gains +1 understanding and +1 courage.",
    },
    "Trailblazer": {
        "expansion": "Manhunter",
        "desc": "The hunting party may start the hunt phase 1 space closer to the monster.<br/>At the start of the showdown, all survivors gain +1 survival and up to +1 insanity.",
    },
    "Transcended Masochist": {
        "expansion": "Manhunter",
        "desc": "When you gain a bleeding token, gain +1 survival and +1 insanity.<br/>Ignore the effects of the <b>Aichmophobia</b> and <b>Apathetic</b> disorders.",
    },
    "Champion's Rite": {
        "expansion": "Dragon King",
        "desc": "Before making an attack, you may add your understanding to your accuracy attribute for that attack.<br/>Limit, once per showdown.",
        "constellation": {
            "horizontal": "Absolute",
            "vertical": "Reaper",
        },
    },
    "Unbreakable": {
        "expansion": "Dragon King",
        "desc": "Once per lantern year, you may ignore one of your severe injury roll results. If you do, gain a random disorder.",
        "constellation": {
            "horizontal": "Goblin",
            "vertical": "Rust",
        },
    },
    "Fated Blow": {
        "expansion": "Dragon King",
        "desc": "Once per showdown, you may give your next wound attempt +2 strength and <b>Devastating 1</b>.",
        "constellation": {
            "horizontal": "Gambler",
            "vertical": "Storm",
        },
    },
    "Acrobatics": {
        "expansion": "Dragon King",
        "desc": 'When you are adjacent to the monster, you may spend <font class="kdm_font">c</font> to place your survivor on any other space adjacent to the monster.',
    },
    "Frozen Star": {
        "expansion": "Dragon King",
        "secret": True,
        "desc": "Once per round, you may spend 1 survival to freeze a monster's brain. They gain -2 accuracy until the end of the round.<br/>Once per round, you may spend 1 survival to freeze a survivor's brain, killing them instantly. They die.",
        "constellation": {
            "horizontal": "Absolute",
            "vertical": "Rust",
        },
    },
    "Altered Destiny": {
        "expansion": "Dragon King",
        "secret": True,
        "desc": "If you would gain a negative attribute token, gain a positive attribute token of that type instead."
    },
    "Fencing": {
        "expansion": "Flower Knight",
        "secret": True,
        "desc": "Ignore <b>Parry</b> when attempting to wound hit locations. (Attempt to wound these locations normally.)<br/>When a monster attacks you, roll 1d10. On a 6+, ignore 1 hit. Limit, once per round.",
    },
    "True Blade": {
        "expansion": "Flower Knight",
        "secret": True,
        "desc": "All swords in your gear grid gain <b>deadly</b>.<br/>Gain +3 luck when attacking with a sword if you have the <b>Ghostly Beauty</b> and <b>Narcissistic</b> disorders.",
    },
    "Acanthus Doctor": {
        "expansion": "Flower Knight",
        "secret": True,
        "desc": 'You may wear up to 3 <b>Satchel</b> gear cards.<br/>When you <b>depart</b>, if you are not wearing any armor, for each <font id="Dormenatus">&#x02588;</font> you have, gain +1 strength token and add <font class="inline_shield">1</font> to all hit locations.<br/>Spend <font class="kdm_font">a</font> and a Flower or <b>Fresh Acanthus</b> resource to heal a permanent injury you or an adjacent survivor suffered this showdown.',
    },
    "Otherworldly Luck": {
        "expansion": "Flower Knight",
        "desc": "During the Hunt and Settlement phase, whenever you roll on a table, you may add +1 to the roll result. This may not exceed the highest possible result of that table.<br/>(This includes Hunt Events, Story Events, Endeavors, Settlement Events, etc.)",
    },
    "Black Guard Style": {
        "expansion": "White Box",
        "secret": True,
        "desc": 'Swords in your gear grid gain <b>Block 1</b>.<br/>When you block a hit with a sword, your next attack that round with a sword gains +2 accuracy, +2 strength, +2 speed. Limit, once per round.<br/> During the settlement phase you may spend <font class="kdm_font">d</font> to train a survivor. They gain the <b>Black Guard Style</b> secret fighting art. You lose it and suffer the <b>broken arm</b> severe injury.',
    },
    "Sneak Attack": {
        "expansion": "Sunstalker",
        "desc": "When you attack a monster from its blind spot, gain +4 strength for that attack.",
    },
    "Purpose": {
        "expansion": "Sunstalker",
        "desc": "Your comrades make you strong enough to exceed the limits of death itself.<br/>During the showdown, if you would gain a lethal number of bleeding tokens while there are any other standing survivors, roll 1d10. On a 6+, you live but are knocked down. You will not bleed to death until you gain another bleeding token.",
    },
    "Burning Ambition": {
        "expansion": "Sunstalker",
        "desc": 'When you are instructed to <b>Skip the Next Hunt</b>, ignore it. The "Skip Next Hunt" box on your survivor record sheet cannot be filled in.',
    },
    "Trick Attack": {
        "expansion": "Sunstalker",
        "desc": "Once per showdown, when you wound a monster from its blind spot, a survivor adjacent to you may gain the <b>priority target</b> token.",
    },
    "Defender": {
        "expansion": "Sunstalker",
        "desc": "When a survivor adjacent to you is knocked down, you may spend 1 survival. If you do, they stand and gain +1 survival from your words of encouragement.<br/>You cannot use this if you have a <b>broken jaw</b>.",
    },
    "Hellfire": {
        "secret": True,
        "expansion": "Sunstalker",
        "desc": 'You cannot lose or remove this fighting art.<br/>Gain +1 strength for each <font id="Caratosis">&#x02588;</font> you have. You cannot be nominated for <b>Intimacy</b>. You ignore <b>Extreme Heat</b>.<br/>At the start of your act, lose 1 survival. At the end of your act, if your survival is 0 or you have any +1 strength tokens, your organs cook themselves and you die.',
    },
    "Sun Eater": {
        "secret": True,
        "expansion": "Sunstalker",
        "desc": "Your body mysteriously absorbs light. At the start of the showdown, gain survival up to the settlement's Survival Limit.<br/>If you have any +1 strength tokens, you may spend them all to perform the <b>Surge</b> survival action (following all of its normal rules and restrictions).",
    },
    "Suppressed Shadow": {
        "secret": True,
        "expansion": "Sunstalker",
        "desc": "You no longer cast a shadow and you never hesitate. Ignore First Strike.<br/>On a <b>Perfect Hit</b>, your first wound attempt of the attack automatically succeeds and inflicts a critical wound.<br/>If you die during the showdown, place a Shade minion in the space you occupied.",
    },
	"Necromancer": {
		"secret": True,
		"expansion": "Lion God",
		"desc": 'When you <b>depart</b>, gain <font class="inline_shield">1</font> to all hit locations for each gear card in your grid with the <i>symbol</i> keyword.<br/>If you would roll on the severe injury table, roll on the <b>Worm Trauma</b> table on the other side of this card instead.<br/>When you die or forget this, the settlement gains the <b>Knowledge Worm</b> innovation.',
	},
	"Unrelenting": {
		"expansion": "Lion God",
		"desc": "If all of your attack rolls in an attack miss, you may spend 1 survival to re-roll all attack rolls.",
	},
	"Ruthless": {
		"expansion": "Lion God",
		"desc": "Whenever a survivor dies during the showdown, roll 1d10. On a 7+, gain a <b>Skull</b> basic resource.",
	},
	"Heroic": {
		"expansion": "Lion God",
		"desc": "Once per showdown, if you are standing adjacent to the monster and have 3+ survival, you may spend all of your survival for one automatic hit that inflicts a critical wound.",
	},
	"Burning Focus": {
		"expansion": "Lion God",
		"desc": "If you have 0 survival at the start of your act, gain 1 survival.",
	},
    "Wardrobe Expert": {
        "expansion": "Lion Knight",
        "desc": "When you suffer a severe injury at a hit location, you may archive a gear worn at that location to ignore it and gain +1 survival.",
    },
    "Tenacious": {
        "expansion": "Lion Knight",
        "desc": "When your wound attempt on a hit location is a failure, you may put that hit location back on top of the deck instead of in the discard pile.<br/>Limit, once per round.",
    },
    "Headliner": {
        "expansion": "Lion Knight",
        "desc": "When you become <b>doomed</b> or gain the <b>priority target</b> token, you may choose to gain +1 survival or +1 strength token.",
    },
    "Courtly Screenwriter": {
        "secret": True,
        "expansion": "Lion Knight",
        "desc": "At the start of the showdown, secretly write down on a scrap of paper which survivors will live and who will deal the killing blow. During the aftermath, if your predictions were correct, raise the settlement's Survival Limit by 1.",
    },
    "Ageless Apprentice": {
        "secret": True,
        "expansion": "Lion Knight",
        "desc": "When yu gain Hunt XP, you may decide not to gain it.<br/>When you <b>depart</b>, you may rotate up to 3 gear cards in your gear grid. This changes the location of their affinities and arrows. Otherwise, the gear functions normally.",
    },
    "Beetle Strength": {
        "secret": True,
        "expansion": "Dung Beetle Knight",
        "desc": 'Once per showdown, you may spend <font class="kdm_font">a</font> to shove an adjacent obstacle terrain. If you do, move the train directly away from you in a straight line until it encounters a board edge or another obstacle terrain. Any monsters the train passes over suffer a wound, and any survivors it <b>collides</b> with suffer <b>knockback 7</b>.<br/>The display of strength is so exhausting it ages you. You are knocked down and gain +1 Hunt XP.',
    },
    "Propulsion Drive": {
        "expansion": "Dung Beetle Knight",
        "desc": "At the start of a showdown, gain the <b>Momentum</b> survivor status card.<br/> When you attack, if you have 5+ momentum tokens, remove them all and roll 1d10. Gain that amount of luck and strength when attempting to wound the first selected hit location for this attack.",
    },
    "Carapace of Will": {
        "expansion": "Dung Beetle Knight",
        "desc": "At the start of the showdown, gain the <b>Steadfast</b> survivor status card.<br/> When you are attacked, if you have 2+ steadfast tokens, ignore a hit and remove all your steadfast tokens.",
    },
    "Mammoth Hunting": {
        "expansion": "Gorm",
        "desc": "Gain +1 strength when attacking from adjacent spaces outside the monster's facing and blind spot.",
    },
    "Lure Epilepsy": {
        "expansion": "Gorm",
        "desc": 'Once per showdown, you may spend <font class="kdm_font">a</font> to give yourself a seizure. You suffer a random brain trauma and are knocked down.',
    },
    "Immovable Object": {
        "secret": True,
        "expansion": "Gorm",
        "desc": "If you are on an unoccupied space, you stand firm in the face of any force. You cannot be knocked down and may ignore <b>knockback</b>. (If you occupy the same space as a monster, impassable terrain tile, or another survivor, you are knocked down and suffer <b>knockback</b>.)",
    },
    "Red Fist": {
        "secret": True,
        "desc": "At the start of each showdown, each survivor gains +1 Strength token. Survivors may spend +1 Strength tokens in place of survival.",
    },
    "King of a Thousand Battles": {
        "secret": True,
        "desc": "Gain +2 Accuracy, +2 Strength, +2 Evasion. You may dodge any number of times in a rount. Only 1 survivor may have this Secret Fighting Art.",
    },
    "King's Step": {
        "secret": True,
        "desc": "Whenever you attack, you may discard any number of Battle Pressure hit locations drawn and draw an equal number of new hit locations. Whenever you attack, after drawing hit locations, but before rolling to wound, you may choose one hit location drawn and discard it to draw a new hit location. Traps will cancel these effects.",
    },
    "Legendary Lungs": {
        "secret": True,
        "desc": "Once per attack, for each successful hit, make an additional attack roll.",
    },
    "Zero Presence": {
        "secret": True,
        "desc": "Gain +1 Strength when attacking a monster from its blind spot. Whenever you attack a monster, you are always considered to be in its blind spot.",
    },
    "Swordsman's Promise": {
        "secret": True,
        "desc": "At the start of each showdown, gain survival up to your settlement's survival limit if you have a sword in your gear grid.",
    },
    "Orator of Death": {
        "desc": 'Once per showdown, you may spend <font class="kdm_font">a</font> to have all non-deaf survivors gain +2 insanity.<br/>When you die, you <b>encourage</b> all survivors with your last words.',
    },
    "Leader": {
        "desc": "Whenever you <b>encourage</b> a survivor they gain +1 speed token until the end of the round.",
    },
    "Combo Master": {
        "desc": "On a <b>perfect hit</b>, make 1 additional attack roll.",
    },
    "Double Dash": {
        "desc": 'During your act, once per round, you may spend <font class="kdm_font">a</font> to gain <font class="kdm_font">c</font>.',
    },
    "Timeless Eye": {
        "desc": "Your attack roll is a <b>perfect hit</b> on a result of a 9 or 10.<br/>You cannot use Timeless Eye if you have the <b>blind</b> severe head injury.",
    },
    "Mighty Strike": {
        "desc": "On a <b>Perfect hit</b>, gain +2 Strength until the end of the attack.",
    },
    "Berserker": {
        "desc": 'Once per showdown, you may spend <font class="kdm_font">a</font> to suffer <b>bash</b> and the <b>frenzy</b> brain trauma.',
    },
    "Thrill Seeker": {
        "desc": "Whenever you gain survival during the showdown phase, gain 1 additional survival.",
    },
    "Tough": {
        "desc": "When rolling on a severe injury table, unless you roll a 1, add +1 to the result. (This does not include brain trauma. The result total cannot exceed 10.)",
    },
    "Rhythm Chaser": {
        "desc": "Gain +1 Evasion token the first time you critically wound during a showdown.<br/>Rhythm Chaser cannot be used if there are any shields or <i>heavy</i> gear in your grid.",
    },
    "Last Man Standing": {
        "desc": "While you are the only survivor on the showdown board, you may not gain bleeding tokens or be knocked down.",
    },
    "Crossarm Block": {
        "desc": "Whenever you are hit, after hit locations are rolled, you may change 1 result to the arms hit location.",
    },
    "Clutch Fighter": {
        "desc": "While you have 3 or more blood tokens, gain +1 Strength and +1 Accuracy.",
    },
    "Crazed": {
        "desc": "On a <b>Perfect hit</b>, gain +1 insanity.",
    },
    "Unconscious Fighter": {
        "desc": "It takes 7 bleeding tokens to kill you.",
    },
    "Ambidexterous": {
        "desc": "All melee weapons in your gear grid gain <b>paired</b> (add the speed of the second weapon when attacking with the first).<br/>Ambidexterous cannot be used if there are any shields, two-handed or heavy gear in your gear grid.",
    },
    "Strategist": {
        "desc": "During the showdown setup, after placing terrain, you may add a <b>Giant Stone Face</b> or a <b>Toppled Pillar</b> terrain card to the showdown board.",
    },
    "Monster Claw Style": {
        "desc": "Your <b>Fist & Tooth</b> attacks gain +1 Accuracy, +1 Strength and <b>Savage</b> (after the first critical wound in an attack, savage weapons cause 1 additional wound. This rule does not trigger on Impervious hit locations).",
    },
    "Tumble": {
        "desc": "When something would <b>collide</b> with you, roll 1d10. On a result of 6+, you successfully tumble out of harm's way. Instead, place your survivor standing on the closest free space outside of the collision path.",
    },
    "Extra Sense": {
        "desc": "You may <b>dodge</b> 1 additional time per round.",
    },
}

defeated_monsters = {
    "White Lion (First Story)": {
        "always_vailable": True,
    }
}

locations = {
    "Manhunter Gear":{
        "color": "000",
        "font_color": "f00",
    },
    "Dragon Armory":{
        "color": "6A1B9A",
        "font_color": "FFF",
    },
    "Sense Memory": {
        "color": "145314",
        "font_color": "FFF",
    },
    "Rare Gear": {
        "color": "9DC209",
    },
    "Promo": {
        "color": "3BB9FF",
    },
    "Gear Recipe": {
        "color": "333",
        "font_color": "FFF",
    },
    "Ivory Carver": {
        "color": "FFFFF0",
    },
    "Unique Items": {
        "font_color": "FFF",
        "color": "FF00FF",
    },
    "Throne": {
        "consequences": ["Bone Smith", "Skinnery", "Organ Grinder", "Catarium", "Plumery", "Mask Maker"],
        "endeavors": {
            "Innovate": {"cost": 1, "desc": "Once per settlement phase, you may spend the listed resources (1 Endeavor, 1 Bone, 1 Organ, 1 Hide) to draw 2 innovation cards. Keep 1 and return the other to the deck."},
            "Fear and Trembling": {"cost": 1, "desc": 'Once per settlement phase, a survivor may spend <font class="kdm_font">d</font> to approach the throne and roll 1d10.'},
            "Build": {"cost":1, "desc": "Bone Smith", "remove_after": "Bone Smith"},
            " Build": {"cost":1, "desc": "Skinnery", "remove_after": "Skinnery"},
            "  Build": {"cost":1, "desc": "Organ Grinder", "remove_after": "Organ Grinder"},
        },
    },
    "Lantern Hoard": {
        "consequences": ["Bone Smith", "Skinnery", "Organ Grinder", "Catarium", "Plumery", "Exhausted Lantern Hoard", "Mask Maker"],
        "endeavors": {
            "Innovate": {"cost": 1, "desc": "Once per settlement phase, you may spend the listed resources (1 Endeavor, 1 Bone, 1 Organ, 1 Hide) to draw 2 innovation cards. Keep 1 and return the other to the deck."},
            "Shared Experience": {
                "cost": 1,
                "requires": ["Symposium"],
                "desc": "Nominate a survivor that has 2 or more Hunt XP than yourself. They describe illuminating details of their desired death. If you are not deaf, gain +1 Hunt XP from their story.  If the nominated survivor has a broken jaw, instead gain +1 insanity.",
            },
            "Build": {"cost":1, "desc": "Bone Smith", "remove_after": "Bone Smith"},
            " Build": {"cost":1, "desc": "Skinnery", "remove_after": "Skinnery"},     # hacks!
            "  Build": {"cost":1, "desc": "Organ Grinder", "remove_after": "Organ Grinder"},    # craaaazzzzzyyy hacks!
        },
    },
    "Bone Smith": {
        "color": "e3dac9",
        "consequences": ["Weapon Crafter"],
        "endeavors": {
            "Build": {"cost": 1, "desc": "Weapon Crafter (3 x bone, 1 x hide)", "remove_after": "Weapon Crafter"},
        },
    },
    "Skinnery": {
        "color": "FFCBA4",
        "consequences": ["Leather Worker"],
        "endeavors": {
            "Build": {"cost": 1, "desc": "Leather Worker (3 x hide, 1 x organ)", "remove_after": "Leather Worker"},
        },
    },
    "Organ Grinder": {
        "color": "B58AA5",
        "consequences": ["Stone Circle"],
        "endeavors": {
            "Augury": {"cost": 1},
            "Build": {"cost": 1, "desc": "Stone Circle (3 x organ, 1 x hide)", "remove_after": "Stone Circle"},
        },
    },
    "Blacksmith": {
        "requires": ("innovations", "Scrap Smelting"),
        "color": "625D5D",
        "font_color": "FFF",
    },
    "Stone Circle": {
        "color": "835C3B",
        "font_color": "FFF",
        "endeavors": {
            "Harvest Ritual": {"cost": 1, "desc": "Spend any number of monster resources to draw an equal number of basic resources."},
        },
    },
    "Leather Worker": {
        "color": "7F462C",
        "font_color": "FFF",
        "endeavors": {
            "Leather-Making": {
                "cost": 1,
                "desc": "Spend any number of hide to add an equal number of leather strange resources to the settlement storage.",
                "requires": ["Ammonia"],
                },
        },
    },
    "Weapon Crafter": {
        "color": "E1D4C0",
        "endeavors": {
            "Scrap Scavenge": {"cost": 1, },
            "Special Innovate": {"cost": 1, "desc": "Scrap Smelting (2 x scrap, 5 x bone, 5 x organ)", "remove_after": "Scrap Smelting"},
        },
    },
    "Barber Surgeon": {
        "requires": ("innovations", "Pottery"),
        "color": "E55451",
        "font_color": "FFF",
    },
    "Plumery": {
        "color": "FF5EAA",
        "consequences": [],
    },
    "Mask Maker": {
        "color": "FFD700",
        "endeavors": {
            "White Lion Mask": {"cost": 1, "desc": "You may hunt the Great Golden Cat."},
            "Antelope Mask": {"cost": 1, "desc": "You may hunt the Mad Steed."},
            "Phoenix Mask": {"cost": 1, "desc": "You may hunt the Golden Eyed King."},
        },
    },
    "Exhausted Lantern Hoard": {
        "color": "ddd",
        "consequences": [],
    },
    "Catarium": {
        "color": "BA8B02",
        "consequences": [],
    },
    "Gormchymist": {
        "color": "8C001A",
        "font_color": "FFF",
        "consequences": [],
        "expansion": "Gorm",
        "endeavors": {
            "Special Innovate": {"cost": 1, "desc": "Gain the next Gormchymy innovation (1 x strange resource, 1 x gorm brain)"},
        },
    },
    "Gormery": {
        "color": "600313",
        "font_color": "FFF",
        "consequences": [],
        "expansion": "Gorm",
    },
    "Black Harvest": {
        "color": "333",
        "font_color": "FFF",
        "expansion": "Dung Beetle Knight",
    },
    "Wet Resin Crafter": {
        "expansion": "Dung Beetle Knight",
        "color": "C9CE62",
    },
    "The Sun": {
        "expansion": "Sunstalker",
        "consequences": ["Bone Smith", "Skinnery", "Organ Grinder", "Catarium", "Plumery", "Mask Maker", "Skyreef Sanctuary", "Sacred Pool"],
        "endeavors": {
            "Innovate": {"cost": 1, "desc": "Once per settlement phase, you may spend the listed resources (1 Bone, 1 Organ, 1 Hide) to draw 2 innovation cards. Keep 1 and return the other to the deck."},
            "Build": {"cost":1, "desc": "Bone Smith", "remove_after": "Bone Smith"},
            " Build": {"cost":1, "desc": "Skinnery", "remove_after": "Skinnery"},     # hacks!
            "  Build": {"cost":1, "desc": "Organ Grinder", "remove_after": "Organ Grinder"},    # craaaazzzzzyyy hacks!
        },
        "special_rules": [
            {"name": "Extreme Heat", "desc": "Survivors cannot wear heavy gear.", "bg_color": "DD3300", "font_color": "FFF"},
            {"name": "Supernova", "desc": 'If you suffer defeat against a nemesis monster, the sun cleanses the settlement, instantly killing everyone. <font class="kdm_font">g</font> <b>Game Over</b>', "bg_color": "990000", "font_color": "FFF"},
        ],
    },
    "Sacred Pool": {
        "expansion": "Sunstalker",
        "levels": 3,
        "endeavors": {
            "Sacred Water": {"cost": 1, "desc": 'Once per settlement phase, the settlement drinks the oil that builds up on the surface of the pool. <font class="kdm_font">g</font> <b>Intimacy</b>.'},
            "Purification Ceremony": {"cost": 2, "desc": "You may endeavor here once per lifetime. Your body is infused with sacred water and <b>Purified</b> (record this). You cannot <b>depart</b> this year. Gain the <b>Protective</b> disorder and roll 1d10. On 8+, gain +1 permanent attribute of your choice. Otherwise, gain +1 permanent strength or accuracy."},
            "Sun Sealing": {"requires": ["Sauna Shrine"], "cost": 1, "desc": "You sit for a year, in the boiling darkness of the Shrine. Gain the <b>Hellfire</b> secret fighting art. You cannot <b>depart</b> this year."},
        },
        "color": "eee541",
    },
    "Skyreef Sanctuary": {
        "expansion": "Sunstalker",
        "color": "FFF541",
        "consequences": [],
    },
}


# boy, this is a really good example of why you don't try to make dictionary
# keys out of your raw asset values. Fuck you, Poots: next time I'm using bson
# object keys or some shit
item_normalization_exceptions = {
    ("Belt Of Gender Swap", "Belt of Gender Swap"),
    ("Quiver And Sunstring", "Quiver and Sunstring"),
    ("Sun Lure And Hook", "Sun Lure and Hook"),
	("Arm Of The First Tree", "Arm of the First Tree"),
    ("Dbk Errant Badge", "DBK Errant Badge"),
    ("Finger Of God", "Finger of God"),
    ("Eye Of Cat", "Eye of Cat"),
}



items = {
    "Black Friday Lantern": {
        "expansion": "White Box",
        "location": "Promo",
        "desc": "On <b>Arrival</b> (at the start of the showdown), you may archive this and Ambush the monster. Limit, once per campaign.",
        "attributes": {"Evasion": 1},
        "type": ["item","lantern","other"],
    },
    "Jack O' Lantern": {
        "expansion": "White Box",
        "location": "Gear Recipe",
    },
    "Nightmare Breast Pump": {
        "expansion": "White Box",
        "location": "Promo",
    },
    "Dragon Vestments": {
        "expansion": "Dragon King",
        "location": "Rare Gear",
    },
    "Celestial Spear": {
        "expansion": "Dragon King",
        "location": "Rare Gear",
    },
    "Hazmat Shield": {
        "expansion": "Dragon King",
        "location": "Rare Gear",
    },
    "Husk of Destiny": {
        "expansion": "Dragon King",
        "location": "Rare Gear",
    },
    "Red Power Core": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Blue Power Core": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Nuclear Knife": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Nuclear Scythe": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Blast Shield": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Shielded Quiver": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Dragon Bite Bolt": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Dragon Belt": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Dragon Chakram": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Regal Edge": {
        "expansion": "Dragon King",
        "location": "Rare Gear",
    },
    "Dragon Boots": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Dragonskull Helm": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Talon Knife": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Dragon Gloves": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Dragon Mantle": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Dragon Armor Set": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Blast Sword": {
        "expansion": "Dragon King",
        "location": "Dragon Armory",
    },
    "Horn Fragment": {
        "expansion": "Dragon King",
        "location": "Dragon King Resources",
        "resource_family": ["bone"],
    },
    "King's Claws": {
        "expansion": "Dragon King",
        "location": "Dragon King Resources",
        "resource_family": ["bone"],
    },
    "Husk": {
        "expansion": "Dragon King",
        "location": "Dragon King Resources",
        "resource_family": ["hide"],
    },
    "Veined Wing": {
        "expansion": "Dragon King",
        "location": "Dragon King Resources",
        "resource_family": ["hide"],
    },
    "Dragon Iron": {
        "expansion": "Dragon King",
        "location": "Dragon King Resources",
        "resource_family": ["scrap","iron"],
    },
    "King's Tongue": {
        "expansion": "Dragon King",
        "location": "Dragon King Resources",
        "resource_family": ["hide"],
    },
    "Hardened Ribs": {
        "expansion": "Dragon King",
        "location": "Dragon King Resources",
        "resource_family": ["bone"],
    },
    "Cabled Vein": {
        "expansion": "Dragon King",
        "location": "Dragon King Resources",
        "resource_family": ["organ"],
    },
    "Radioactive Dung": {
        "expansion": "Dragon King",
        "location": "Dragon King Resources",
        "resource_family": ["organ","scrap"],
    },
    "Vespertine Foil": {
        "expansion": "Flower Knight",
        "location": "Sense Memory",
    },
    "Vespertine Bow": {
        "expansion": "Flower Knight",
        "location": "Sense Memory",
    },
    "Vespertine Cello": {
        "expansion": "Flower Knight",
        "location": "Sense Memory",
    },
    "Satchel": {
        "expansion": "Flower Knight",
        "location": "Sense Memory",
    },
    "Vespertine Arrow": {
        "expansion": "Flower Knight",
        "location": "Sense Memory",
    },
    "Flower Knight Badge": {
        "expansion": "Flower Knight",
        "location": "Sense Memory",
    },
    "Flower Knight Helm": {
        "expansion": "Flower Knight",
        "location": "Rare Gear",
    },
    "Replica Flower Sword": {
        "expansion": "Flower Knight",
        "location": "Rare Gear",
    },
    "Sleeping Virus Flower": {
        "expansion": "Flower Knight",
        "location": "Rare Gear",
    },
    "Cycloid Scale Hood": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Cycloid Scale Sleeves": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Cycloid Scale Jacket": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Cycloid Scale Skirt": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Cycloid Scale Shoes": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Cycloid Scale Armor": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Sunspot Dart": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Sunshark Bow": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Sunshark Arrows": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Denticle Axe": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Skleaver": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Ink Sword": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Sunspot Lantern": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Quiver and Sunstring": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Shadow Saliva Shawl": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Sun Lure and Hook": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Sky Harpoon": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Ink Blood Bow": {
        "expansion": "Sunstalker",
        "location": "Skyreef Sanctuary",
    },
    "Sun Vestments": {
        "expansion": "Sunstalker",
        "location": "Sacred Pool",
    },
    "Sunring Bow": {
        "expansion": "Sunstalker",
        "location": "Sacred Pool",
    },
    "Apostle Crown": {
        "expansion": "Sunstalker",
        "location": "Sacred Pool",
    },
    "Prism Mace": {
        "expansion": "Sunstalker",
        "location": "Sacred Pool",
    },
    "God's String": {
        "expansion": "Sunstalker",
        "location": "Rare Gear",
    },
    "Eye Patch": {
        "expansion": "Sunstalker",
        "location": "Rare Gear",
    },
    "Riot Mace": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Rib Blade": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Regeneration Suit": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Pulse Lantern": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Knuckle Shield": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Greater Gaxe": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Gorn": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Gaxe": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Black Sword": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Gorment Mask": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Gorment Suit": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Gorment Sleeves": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Gorment Boots": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Armor Spikes": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Acid Tooth Dagger": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Gorment Armor Set": {
        "expansion": "Gorm",
        "location": "Gormery",
    },
    "Healing Potion": {
        "location": "Gormchymist",
    },
    "Wisdom Potion": {
        "location": "Gormchymist",
    },
    "Steadfast Potion": {
        "location": "Gormchymist",
    },
    "Power Potion": {
        "location": "Gormchymist",
    },
    "Life Elixir": {
        "location": "Gormchymist",
    },
    "First Aid Kit" : {
        "location": "Barber Surgeon",
    },
    "Brain Mint" : {
        "location": "Barber Surgeon",
    },
    "Elder Earrings" : {
        "location": "Barber Surgeon",
    },
    "Musk Bomb" : {
        "location": "Barber Surgeon",
    },
    "Scavenger Kit" : {
        "location": "Barber Surgeon",
    },
    "Bug Trap" : {
        "location": "Barber Surgeon",
    },
    "Speed Powder" : {
        "location": "Barber Surgeon",
    },
    "Almanac" : {
        "location": "Barber Surgeon",
    },
    "God Mask" : {
        "location": "Mask Maker",
    },
    "Phoenix Mask" : {
        "location": "Mask Maker",
    },
    "Man Mask" : {
        "location": "Mask Maker",
    },
    "White Lion Mask" : {
        "location": "Mask Maker",
    },
    "Antelope Mask" : {
        "location": "Mask Maker",
    },
    "Death Mask" : {
        "location": "Mask Maker",
    },
    "Phoenix Armor Set": {
        "location": "Plumery",
    },
    "Arc Bow": {
        "location": "Plumery",
    },
    "Hollowpoint Arrow": {
        "location": "Plumery",
    },
    "Hollow Sword": {
        "location": "Plumery",
    },
    "Feather Shield": {
        "location": "Plumery",
    },
    "Phoenix Faulds": {
        "location": "Plumery",
    },
    "Sonic Tomahawk": {
        "location": "Plumery",
    },
    "Crest Crown": {
        "location": "Plumery",
    },
    "Phoenix Helm": {
        "location": "Plumery",
    },
    "Phoenix Greaves": {
        "location": "Plumery",
    },
    "Hours Ring": {
        "location": "Plumery",
    },
    "Bird Bread": {
        "location": "Plumery",
    },
    "Phoenix Plackart": {
        "location": "Plumery",
    },
    "Bloom Sphere": {
        "location": "Plumery",
    },
    "Phoenix Gauntlet": {
        "location": "Plumery",
    },
    "Feather Mantle": {
        "location": "Plumery",
    },
    "Scrap Shield" : {
        "location": "Blacksmith",
    },
    "Dragon Slayer" : {
        "location": "Blacksmith",
    },
    "Lantern Armor Set": {
        "location": "Blacksmith",
    },
    "Lantern Cuirass" : {
        "location": "Blacksmith",
    },
    "Lantern Gauntlets" : {
        "location": "Blacksmith",
    },
    "Perfect Slayer" : {
        "location": "Blacksmith",
    },
    "Lantern Greaves" : {
        "location": "Blacksmith",
    },
    "Lantern Helm" : {
        "location": "Blacksmith",
    },
    "Beacon Shield" : {
        "location": "Blacksmith",
    },
    "Lantern Mail" : {
        "location": "Blacksmith",
    },
    "Ring Whip" : {
        "location": "Blacksmith",
    },
    "Lantern Sword" : {
        "location": "Blacksmith",
    },
    "Lantern Glaive" : {
        "location": "Blacksmith",
    },
    "Lantern Dagger" : {
        "location": "Blacksmith",
    },
    "Leather Armor Set": {
        "location": "Leather Worker",
    },
    "Leather Bracers": {
        "location": "Leather Worker",
    },
    "Leather Cuirass": {
        "location": "Leather Worker",
    },
    "Leather Mask": {
        "location": "Leather Worker",
    },
    "Leather Skirt": {
        "location": "Leather Worker",
    },
    "Hunter Whip": {
        "location": "Leather Worker",
    },
    "Round Leather Shield": {
        "location": "Leather Worker",
    },
    "Leather Boots": {
        "location": "Leather Worker",
    },
    "Portcullis Key": {
        "location": "Unique Items",
    },
    "Love Juice": {
        "location": "Basic Resources",
        "resource_family": ["organ"],
        "consumable": True,
    },
    "Skull": {
        "location": "Basic Resources",
        "resource_family": ["bone"],
    },
    "???": {
        "location": "Basic Resources",
        "resource_family": ["organ","hide","bone"],
        "consumable": True,
    },
    "Monster Bone": {
        "location": "Basic Resources",
        "resource_family": ["bone"],
    },
    "Monster Organ": {
        "location": "Basic Resources",
        "resource_family": ["organ"],
        "consumable": True,
    },
    "Monster Hide": {
        "location": "Basic Resources",
        "resource_family": ["hide"],
    },
    "Scrap": {
        "location": "Basic Resources",
        "resource_family": ["scrap"],
    },
    "Broken Lantern": {
        "location": "Basic Resources",
        "resource_family": ["scrap"],
    },
    "Iron": {
        "location": "Strange Resources",
        "resource_family": ["scrap"],
    },
    "Leather": {
        "location": "Strange Resources",
        "resource_family": ["hide"],
    },
    "Elder Cat Teeth": {
        "location": "Strange Resources",
        "resource_family": ["bone"],
    },
    "Phoenix Crest": {
        "location": "Strange Resources",
        "resource_family": ["organ"],
    },
    "Second Heart": {
        "location": "Strange Resources",
        "resource_family": ["organ","bone"],
    },
    "Perfect Crucible": {
        "location": "Strange Resources",
    },
    "Legendary Horns": {
        "location": "Strange Resources",
        "resource_family": ["bone","scrap"],
    },
    "Gormite": {
        "location": "Strange Resources",
        "resource_family": ["scrap"],
        "expansion": "Gorm",
    },
    "Pure Bulb": {
        "location": "Strange Resources",
        "resource_family": ["organ"],
        "expansion": "Gorm",
    },
    "Stomach Lining": {
        "location": "Strange Resources",
        "resource_family": ["organ"],
        "expansion": "Gorm",
    },
    "Active Thyroid": {
        "location": "Strange Resources",
        "resource_family": ["organ"],
        "expansion": "Gorm",
    },
    "Fresh Acanthus": {
        "location": "Strange Resources",
    },
    "White Fur": {
        "location": "White Lion Resources",
        "resource_family": ["hide"],
    },
    "Lion Claw": {
        "location": "White Lion Resources",
        "resource_family": ["bone"],
    },
    "Eye of Cat": {
        "location": "White Lion Resources",
        "resource_family": ["organ"],
        "consumable": True,
    },
    "Great Cat Bones": {
        "location": "White Lion Resources",
        "resource_family": ["bone"],
    },
    "Shimmering Mane": {
        "location": "White Lion Resources",
        "resource_family": ["hide"],
    },
    "Lion Tail": {
        "location": "White Lion Resources",
        "resource_family": ["hide"],
    },
    "Curious Hand": {
        "location": "White Lion Resources",
        "resource_family": ["hide"],
    },
    "Golden Whiskers": {
        "location": "White Lion Resources",
        "resource_family": ["organ"],
    },
    "Sinew": {
        "location": "White Lion Resources",
        "resource_family": ["organ"],
    },
    "Lion Testes": {
        "location": "White Lion Resources",
        "resource_family": ["organ"],
    },
    "Pelt": {
        "location": "Screaming Antelope Resources",
        "resource_family": ["hide"],
    },
    "Shank Bone": {
        "location": "Screaming Antelope Resources",
        "resource_family": ["bone"],
    },
    "Large Flat Tooth": {
        "location": "Screaming Antelope Resources",
        "resource_family": ["bone"],
    },
    "Beast Steak": {
        "location": "Screaming Antelope Resources",
        "resource_family": ["organ"],
        "consumable": True,
    },
    "Muscly Gums": {
        "location": "Screaming Antelope Resources",
        "resource_family": ["organ"],
        "consumable": True,
    },
    "Spiral Horn": {
        "location": "Screaming Antelope Resources",
        "resource_family": ["bone"],
    },
    "Bladder": {
        "location": "Screaming Antelope Resources",
        "resource_family": ["organ"],
        "consumable": True,
    },
    "Screaming Brain": {
        "location": "Screaming Antelope Resources",
        "resource_family": ["organ"],
        "consumable": True,
    },
    "Tail Feathers": {
        "location": "Phoenix Resources",
        "resource_family": ["hide"],
    },
    "Phoenix Eye": {
        "location": "Phoenix Resources",
        "resource_family": ["organ", "scrap"],
    },
    "Phoenix Whisker": {
        "location": "Phoenix Resources",
        "resource_family": ["hide"],
    },
    "Pustules": {
        "location": "Phoenix Resources",
        "resource_family": ["organ"],
        "consumable": True,
    },
    "Small Feathers": {
        "location": "Phoenix Resources",
        "resource_family": ["hide"],
    },
    "Muculent Droppings": {
        "location": "Phoenix Resources",
        "resource_family": ["organ"],
    },
    "Wishbone": {
        "location": "Phoenix Resources",
        "resource_family": ["bone"],
    },
    "Shimmering Halo": {
        "location": "Phoenix Resources",
        "resource_family": ["organ"],
    },
    "Bird Beak": {
        "location": "Phoenix Resources",
        "resource_family": ["bone"],
    },
    "Black Skull": {
        "location": "Phoenix Resources",
        "resource_family": ["scrap","bone"],
    },
    "Small Hand Parasites": {
        "location": "Phoenix Resources",
        "resource_family": ["organ"],
    },
    "Phoenix Finger": {
        "location": "Phoenix Resources",
        "resource_family": ["bone"],
    },
    "Hollow Wing Bones": {
        "location": "Phoenix Resources",
        "resource_family": ["bone"],
    },
    "Rainbow Droppings": {
        "location": "Phoenix Resources",
        "resource_family": ["organ"],
        "consumable": True,
    },
    "White Lion Armor Set": {
        "location": "Catarium",
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
    "White Lion Gauntlets": {
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
        "type": "gear",
        "location": "Starting Gear",
    },
    "Cloth": {
        "type": "gear",
        "location": "Starting Gear",
    },
    "Rawhide Armor Set": {
        "location": "Skinnery",
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
    "Regal Gauntlet": {
        "location": "Rare Gear",
    },
    "Regal Plackart": {
        "location": "Rare Gear",
    },
    "Regal Greaves": {
        "location": "Rare Gear",
    },
    "Regal Helm": {
        "location": "Rare Gear",
    },
    "Regal Faulds": {
        "location": "Rare Gear",
    },
    "Forsaker Mask": {
        "location": "Rare Gear",
    },
    "Adventure Sword": {
        "location": "Rare Gear",
    },
    "Steel Shield": {
        "location": "Rare Gear",
    },
    "Steel Sword": {
        "location": "Rare Gear",
    },
    "Twilight Sword": {
        "location": "Rare Gear",
    },
    "Butcher Cleaver": {
        "location": "Rare Gear",
    },
    "Lantern Halberd": {
        "location": "Rare Gear",
    },
    "Muramasa": {
        "location": "Rare Gear",
    },
    "Thunder Maul": {
        "location": "Rare Gear",
    },
    "Screaming Armor Set": {
        "location": "Stone Circle",
    },
    "Screaming Bracers": {
        "location": "Stone Circle",
    },
    "Screaming Horns": {
        "location": "Stone Circle",
    },
    "Screaming Leg Warmers": {
        "location": "Stone Circle",
    },
    "Screaming Skirt": {
        "location": "Stone Circle",
    },
    "Screaming Coat": {
        "location": "Stone Circle",
    },
    "Beast Knuckle": {
        "location": "Stone Circle",
    },
    "Lance Of Longinus": {
        "location": "Stone Circle",
    },
    "Boss Mehndi": {
        "location": "Stone Circle",
    },
    "Green Charm": {
        "location": "Stone Circle",
    },
    "Red Charm": {
        "location": "Stone Circle",
    },
    "Blue Charm": {
        "location": "Stone Circle",
    },
    "Blood Paint": {
        "location": "Stone Circle",
    },
    "Bone Earrings": {
        "location": "Stone Circle",
    },
    "Zanbato": {
        "location": "Weapon Crafter",
    },
    "Counterweighted Axe": {
        "location": "Weapon Crafter",
    },
    "Scrap Sword": {
        "location": "Weapon Crafter",
    },
    "Scrap Dagger": {
        "location": "Weapon Crafter",
    },
    "Skullcap Hammer": {
        "location": "Weapon Crafter",
    },
    "Whistling Mace": {
        "location": "Weapon Crafter",
    },
    "Finger of God": {
        "location": "Weapon Crafter",
    },
    "Rainbow Katana": {
        "location": "Weapon Crafter",
    },
    "Blood Sheath": {
        "location": "Weapon Crafter",
    },
    "Nightmare Tick" : {
        "location": "Vermin",
    },
    "Lonely Ant" : {
        "location": "Vermin",
    },
    "Crab Spider" : {
        "location": "Vermin",
    },
    "Hissing Cockroach" : {
        "location": "Vermin",
    },
    "Sword Beetle" : {
        "location": "Vermin",
    },
    "Cyclops Fly" : {
        "location": "Vermin",
    },
    "Fairy Bottle": {
        "attribs": ["item","fragile","other"],
        "location": "Rare Gear",
		"expansion": "Beta Challenge Scenarios",
    },
    "Scout's Tunic": {
        "attribs": ["armor","set","leather"],
        "location": "Rare Gear",
		"expansion": "Beta Challenge Scenarios",
    },
    "Aya's Sword": {
        "attribs": ["weapon","melee","sword"],
        "location": "Rare Gear",
		"expansion": "Beta Challenge Scenarios",
    },
    "Aya's Spear": {
        "attribs": ["weapon","melee","spear"],
        "location": "Rare Gear",
		"expansion": "Beta Challenge Scenarios",
    },
    "Arm of the First Tree": {
        "attribs": ["weapon","melee","club"],
        "location": "Rare Gear",
		"expansion": "Beta Challenge Scenarios",
    },
    "Stone Arm": {
        "attribs": ["item","stone","heavy"],
        "location": "Rare Gear",
		"expansion": "Beta Challenge Scenarios",
    },
    "Giant Stone Face": {
        "attribs": ["weapon","melee","grand","heavy","two-handed","stone"],
        "location": "Rare Gear",
		"expansion": "Beta Challenge Scenarios",
    },
    "Petal Lantern": {
        "attribs": ["item","lantern","other"],
        "location": "Rare Gear",
		"expansion": "Beta Challenge Scenarios",
    },
    "Piranha Helm": {
        "attribs": ["armor","set","rawhide"],
        "location": "Rare Gear",
		"expansion": "Beta Challenge Scenarios",
    },
    "Cola Bottle Lantern": {
        "attribs": ["item","fragile","other"],
        "location": "Rare Gear",
		"expansion": "Beta Challenge Scenarios",
    },
    "Mammoth Hand": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["bone","hide","organ"],
    },
    "Jiggling Lard": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["hide","organ"],
    },
    "Stout Kidney": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["organ"],
        "consumable": True,
    },
    "Stout Heart": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["organ"],
    },
    "Stout Hide": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["hide"],
    },
    "Stout Vertebrae": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["bone"],
    },
    "Handed Skull": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["bone"],
    },
    "Dense Bone": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["bone"],
    },
    "Milky Eye": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["organ"],
    },
    "Gorm Brain": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["organ"],
    },
    "Acid Gland": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["organ"],
    },
    "Meaty Rib": {
        "expansion": "Gorm",
        "location": "Gorm Resources",
        "resource_family": ["bone","organ"],
    },
    "Preserved Caustic Dung": {
        "expansion": "Dung Beetle Knight",
        "location": "Strange Resources",
        "resource_family": ["organ"],
    },
    "Scell": {
        "expansion": "Dung Beetle Knight",
        "location": "Strange Resources",
        "resource_family": ["organ"],
    },
    "Beetle Horn": {
        "expansion": "Dung Beetle Knight",
        "location": "Dung Beetle Knight Resources",
        "resource_family": ["bone"],
    },
    "Century Fingernails": {
        "expansion": "Dung Beetle Knight",
        "location": "Dung Beetle Knight Resources",
        "resource_family": ["bone"],
    },
    "Century Shell": {
        "expansion": "Dung Beetle Knight",
        "location": "Dung Beetle Knight Resources",
        "resource_family": ["hide","scrap"],
    },
    "Compound Eye": {
        "expansion": "Dung Beetle Knight",
        "location": "Dung Beetle Knight Resources",
        "resource_family": ["organ"],
    },
    "Elytra": {
        "expansion": "Dung Beetle Knight",
        "location": "Dung Beetle Knight Resources",
        "resource_family": ["bone","hide","organ"],
    },
    "Scarab Shell": {
        "expansion": "Dung Beetle Knight",
        "location": "Dung Beetle Knight Resources",
        "resource_family": ["hide"],
    },
    "Scarab Wing": {
        "expansion": "Dung Beetle Knight",
        "location": "Dung Beetle Knight Resources",
        "resource_family": ["organ"],
    },
    "Underplate Fungus": {
        "expansion": "Dung Beetle Knight",
        "location": "Dung Beetle Knight Resources",
        "resource_family": ["hide"],
    },
    "Rolling Armor Set": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "DBK Errant Badge": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "Rainbow Wing Belt": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "Rubber Bone Harness": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "Scarab Circlet": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "Seasoned Monster Meat": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "The Beetle Bomb": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "Seasoned Monster Meat": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "Century Greaves": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "Century Shoulder Pads": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "Digging Claw": {
        "expansion": "Dung Beetle Knight",
        "location": "Wet Resin Crafter",
    },
    "Calcified Zanbato": {
        "expansion": "Dung Beetle Knight",
        "location": "Black Harvest",
    },
    "Calcified Digging Claw": {
        "expansion": "Dung Beetle Knight",
        "location": "Black Harvest",
    },
    "Calcified Shoulder Pads": {
        "expansion": "Dung Beetle Knight",
        "location": "Black Harvest",
    },
    "Calcified Greaves": {
        "expansion": "Dung Beetle Knight",
        "location": "Black Harvest",
    },
    "Hidden Crimson Jewel": {
        "expansion": "Dung Beetle Knight",
        "location": "Rare Gear",
    },
    "Trash Crown": {
        "expansion": "Dung Beetle Knight",
        "location": "Rare Gear",
    },
    "Regenerating Blade": {
        "expansion": "Dung Beetle Knight",
        "location": "Rare Gear",
    },
    "Calcified Juggernaut Blade": {
        "expansion": "Dung Beetle Knight",
        "location": "Rare Gear",
    },
    "Hideous Disguise": {
        "expansion": "Lion Knight",
        "location": "Rare Gear",
    },
    "Lion Knight Badge": {
        "expansion": "Lion Knight",
        "location": "Rare Gear",
    },
    "Lion Knight's Left Claw": {
        "expansion": "Lion Knight",
        "location": "Rare Gear",
    },
    "Lion Knight's Right claw": {
        "expansion": "Lion Knight",
        "location": "Rare Gear",
    },
	"Ancient Lion Claws": {
		"expansion": "Lion God",
		"location": "Rare Gear",
	},
	"Golden Plate": {
		"expansion": "Lion God",
		"location": "Rare Gear",
	},
	"Lion God Statue": {
		"expansion": "Lion God",
		"location": "Rare Gear",
	},
	"Bone Witch Mehndi": {
		"expansion": "Lion God",
		"location": "Rare Gear",
	},
	"Butcher's Blood": {
		"expansion": "Lion God",
		"location": "Rare Gear",
	},
	"Glyph of Solitude": {
		"expansion": "Lion God",
		"location": "Rare Gear",
	},
	"Lantern Mehndi": {
		"expansion": "Lion God",
		"location": "Rare Gear",
	},
	"Death Mehndi": {
		"expansion": "Lion God",
		"location": "Rare Gear",
	},
	"Necromancer's Eye": {
		"expansion": "Lion God",
		"location": "Rare Gear",
	},
    "Canopic Jar": {
        "expansion": "Lion God",
        "location": "Strange Resources",
        "resource_family": ["organ","scrap"],
    },
    "Old Blue Box": {
        "expansion": "Lion God",
        "location": "Strange Resources",
        "resource_family": ["scrap"],
    },
    "Sarcophagus": {
        "expansion": "Lion God",
        "location": "Strange Resources",
        "resource_family": ["scrap"],
    },
    "Silver urn": {
        "expansion": "Lion God",
        "location": "Strange Resources",
        "resource_family": ["bone","scrap"],
    },
    "Triptych": {
        "expansion": "Lion God",
        "location": "Strange Resources",
        "resource_family": ["hide","scrap"],
    },
    "Jowls": {
        "expansion": "Sunstalker",
        "location": "Strange Resources",
        "resource_family": ["iron","scrap"],
    },
    "Hagfish": {
        "expansion": "Sunstalker",
        "location": "Strange Resources",
        "resource_family": ["bone","hide"],
    },
    "Bugfish": {
        "expansion": "Sunstalker",
        "location": "Strange Resources",
        "resource_family": ["organ"],
    },
    "Salt": {
        "expansion": "Sunstalker",
        "location": "Strange Resources",
    },
    "Sun Stones": {
        "expansion": "Sunstalker",
        "location": "Strange Resources",
        "resource_family": ["bone"],
    },
    "1,000 Year Sunspot": {
        "expansion": "Sunstalker",
        "location": "Strange Resources",
        "resource_family": ["bone","organ"],
    },
    "3,000 Year Sunspot": {
        "expansion": "Sunstalker",
        "location": "Strange Resources",
        "resource_family": ["bone","organ","scrap"],
    },
    "Lonely Fruit": {
        "expansion": "Lonely Tree",
        "location": "Strange Resources",
    },
    "Drifting Dream Fruit": {
        "expansion": "Lonely Tree",
        "location": "Strange Resources",
    },
    "Jagged Marrow Fruit": {
        "expansion": "Lonely Tree",
        "location": "Strange Resources",
        "resource_family": ["bone","scrap"],
    },
    "Blistering Plasma Fruit": {
        "expansion": "Lonely Tree",
        "location": "Strange Resources",
        "resource_family": ["organ"],
    },
    "Blue Lantern": {
        "expansion": "White Box",
        "location": "Rare Gear",
    },
    "Dormant Twilight Cloak": {
        "expansion": "White Box",
        "location": "Rare Gear",
    },
    "Sword of Silence": {
        "expansion": "White Box",
        "location": "Rare Gear",
    },
    "Belt of Gender Swap": {
        "expansion": "White Box",
        "location": "Promo",
    },
    "Blood Plasma Gun": {
        "expansion": "White Box",
        "location": "Promo",
    },
    "Blood Plasma Katana": {
        "expansion": "White Box",
        "location": "Promo",
    },
    "Twilight Thong": {
        "expansion": "White Box",
        "location": "Promo",
    },
    "Bloodskin": {
        "expansion": "White Box",
        "location": "Rare Gear",
    },
    "Speaker Cult Knife": {
        "expansion": "White Box",
        "location": "Rare Gear",
    },
    "Vibrant Lantern": {
        "expansion": "White Box",
        "location": "Promo",
    },
    "Dying Lantern": {
        "expansion": "White Box",
        "location": "Promo",
    },
    "Prismatic Lantern": {
        "expansion": "White Box",
        "location": "Promo",
    },
    "Cloth Leggings": {
        "expansion": "White Box",
        "location": "Gear Recipe",
    },
    "Hard Breastplate": {
        "expansion": "White Box",
        "location": "Gear Recipe",
    },
    "Vagabond Armor Set": {
        "expansion": "White Box",
        "location": "Gear Recipe",
    },
    "Tabard": {
        "expansion": "White Box",
        "location": "Gear Recipe",
    },
    "White Dragon Gauntlets": {
        "expansion": "White Box",
        "location": "Ivory Carver",
    },
    "Radiant Heart": {
        "expansion": "Dragon King",
        "location": "Strange Resources",
        "resource_family": ["organ"],
    },
    "Pituitary Gland": {
        "expansion": "Dragon King",
        "location": "Strange Resources",
        "resource_family": ["organ"],
    },
    "Shining Liver": {
        "expansion": "Dragon King",
        "location": "Strange Resources",
        "resource_family": ["organ"],
    },
    "Red Vial": {
        "expansion": "Manhunter",
        "location": "Strange Resources",
    },
    "Crimson Vial": {
        "expansion": "Manhunter",
        "location": "Strange Resources",
        "resource_family": ["scrap","iron"],
    },
    "Hunter's Heart": {
        "expansion": "Manhunter",
        "location": "Manhunter Gear",
    },
    "Tool Belt": {
        "expansion": "Manhunter",
        "location": "Manhunter Gear",
    },
    "Manhunter's Hat": {
        "expansion": "Manhunter",
        "location": "Manhunter Gear",
    },
    "Deathpact": {
        "expansion": "Manhunter",
        "location": "Manhunter Gear",
    },
    "Reverberating Lantern": {
        "expansion": "Manhunter",
        "location": "Manhunter Gear",
    },

}



#
#   Innovations
#

innovations = {
    "Settlement Watch": {
        "type": "home",
        "expansion": "Manhunter",
        "survivor_buff": "<b>Departing Survivors</b> gain +2 survival when they depart for a Nemesis Encounter or a Special Showdown.",
        "endeavors": {
            "New Recruits": {"cost": 1, "type": "home",},
        },
    },
    "War Room": {
        "type": "education",
        "expansion": "Manhunter",
        "survival_limit": 1,
        "endeavors": {
            "Hunt Plan": {
                "hide_name": True,
                "type": "education",
                "desc": 'The hunt team makes a plan. The group may reroll 1 <b>Hunt Event Table</b> result (d100) this lantern year. They must reroll before performing the event.',
                "cost": 1
            },
        },
    },
    "Crimson Candy": {
        "type": "science",
        "expansion": "Manhunter",
        "survivor_buff": "At the start of the showdown, each survivor gains &#9733; survival.",
        "endeavors": {
            "Crimson Cannibalism": {"cost": 1, "type": "science"},
        },
    },
    "Dragon Speech": {
        "type": "starting innovation",
        "expansion": "Dragon King",
        "survival_limit": 1,
        "survival_action": "Encourage",
        "consequences": ["Hovel", "Inner Lantern", "Drums", "Paint", "Symposium", "Ammonia"],
    },
    "Arena": {
        "type": "education",
        "expansion": "Dragon King",
        "endeavors": {
            "Spar": {"cost": 1, "type": "education"},
        },
    },
    "Empire": {
        "type": "home",
        "expansion": "Dragon King",
        "survivor_buff": 'Newborn survivors are born with +1 permanent strength and the <font class="maroon_text">Pristine</font> ability.',
        "newborn_survivor": {"Strength": 1, "abilities_and_impairments": "Pristine"},
    },
    "Bloodline": {
        "type": "home",
        "expansion": "Dragon King",
        "consequences": ["Empire",],
        "survivor_buff": """Newborn survivors inherit the following from their parents:<ul><li>The <font class="maroon_text">Oracle's Eye</font>, <font class="maroon_text">Iridescent Hide</font>, or <font class="maroon_text">Pristine</font> ability (choose 1)</li><li>1 <b>Surname</b></li><li>Half of one parent's weapon proficiency levels (rounded up)</li></ul>""",
    },
    "Radiating Orb": {
        "type": "science",
        "expansion": "Dragon King",
        "settlement_buff": "<b>Departing Survivors</b> and newborn survivors gain +1 survival.<br/><b>Departing survivors</b> with a constellation gain +1 survival.",
        "consequences": ["Cooking", "Scrap Smelting"],
        "newborn_survivor": {"survival": 1},
    },
    "Petal Spiral": {
        "type": "music",
        "expansion": "Flower Knight",
        "endeavors": {
            "Trace Petals": {"cost": 1, "type": "music"},
        },
    },
    "Sun Language": {
        "expansion": "Sunstalker",
        "type": "starting innovation",
        "survival_limit": 1,
        "survival_action": "Embolden",
        "consequences": ["Ammonia", "Drums", "Hovel", "Paint", "Symposium", "Hands of the Sun"],
    },
    "Hands of the Sun" : {
        "expansion": "Sunstalker",
        "type": "faith",
        "survival_action": "Overcharge",
        "consequences": ["Aquarobics", "Sauna Shrine"],
    },
    "Aquarobics" : {
        "expansion": "Sunstalker",
        "type": "faith",
        "survival_limit": 1,
        "endeavors": {
            "Underwater Train": {"cost": 1, "type": "faith"},
        },
    },
    "Sauna Shrine" : {
        "expansion": "Sunstalker",
        "type": "faith",
        "endeavors": {
            "Tribute": {"cost": 1, "type": "faith"},
        },
        "departure_buff": "When survivors <b>depart</b> for a Nemesis Encounter or Special Showdown, they gain +10 survival.",
    },
    "Umbilical Bank" : {
        "expansion": "Sunstalker",
        "consequences": ["Pottery"],
        "type": "science",
        "settlement_buff": "When a survivor is born, you may add 1 <b>Life String</b> strange resource to storage.",
        "endeavors": {
            '<font class="kdm_font">g</font> Umbilical Symbiosis': {"cost": 1, "type": "science"},
            "Special Innovate": {"cost": 1, "desc": "Pottery (3 x organ)", "remove_after": "Pottery"},
        },
    },
    "Filleting Table" : {
        "expansion": "Sunstalker",
        "type": "science",
        "settlement_buff": "Once per settlement phase, if the <b>returning survivors</b> are victorious, gain 1 random basic resource.",
        "endeavors": {
            "Advanced Cutting": {"cost": 1, "type": "science"},
        },
    },
    "Shadow Dancing" : {
        "expansion": "Sunstalker",
        "type": "home",
        "endeavors": {
            "Final Dance": {"cost": 1, "type": "home"},
        },
    },
	"The Knowledge Worm" :{
		"type": "other",
		"expansion": "Lion God",
		"settlement_buff": 'At the start of each settlement phase, add 1 scrap to settlement storage.<br/><b>Departing Survivors</b> gain +3 survival and +3 insanity. If any of those survivors have 10+ insanity, <font class="kdm_font">g</font> <b>A Gracious Host</b>.',
	},
    "Stoic Statue" : {
        "consequences": ["Black Mask", "White Mask"],
        "expansion": "Lion Knight",
        "type": "other",
        "endeavors": {
            "Worship the monster": {"cost": 1, "type": "other"}
        },
    },
    "Black Mask" : {
        "consequences": ["White Mask"],
        "expansion": "Lion Knight",
        "type": "other",
        "endeavors": {
            "Visit the retinue": {"cost": 1, "type": "other"},
            "Face the monster": {"cost": 2, "type": "other"},
        },
    },
    "White Mask" : {
        "consequences": ["Black Mask"],
        "expansion": "Lion Knight",
        "type": "other",
        "endeavors": {
            "Visit the retinue": {"cost": 1, "type": "other"},
            "Leave the monster an offering": {"cost": 1, "type": "other"},
        },
    },
    "Subterranean Agriculture": {
        "expansion": "Dung Beetle Knight",
        "type": "science",
        "endeavors": {
            "Build": {"cost": 1, "desc": "Wet Resin Crafter (2 x organ, 2 x bone)", "remove_after": "Wet Resin Crafter"},
            "Underground Sow": {
                "hide_name": True,
                "type": "science",
                "desc": 'If <b>Black Harvest</b> is not on the timeline, <font class="kdm_font">g</font> <b>Underground Sow</b>.',
                "cost": 1
            },
           "Underground Fertilize": {
                "hide_name": True,
                "type": "science",
                "desc": 'If <b>Black Harvest</b> is on the timeline, you may spend 1 Preserved Caustic Dung to increase its rank by 1 to a maximum rank of 3. Limit, once per settlement phase.',
                "cost": 1,
            },
        },
    },
    "Round Stone Training": {
        "expansion": "Dung Beetle Knight",
        "type": "education",
        "endeavors": {
            "Train": {"cost": 1, "type": "education"},
        },
    },
    "Nigredo": {
        "expansion": "Gorm",
        "type": "science",
        "survival_limit": 1,
        "consequences": ["Albedo"],
        "endeavors": {
            "Nigredo": {"cost": 1, "type": "science"},
        },
    },
    "Albedo": {
        "expansion": "Gorm",
        "type": "science",
        "consequences": ["Citrinitas"],
        "endeavors": {
            "Albedo": {"cost": 2, "type": "science"},
        },
    },
    "Citrinitas": {
        "expansion": "Gorm",
        "type": "science",
        "survival_limit": 1,
        "consequences": ["Rubedo"],
        "endeavors": {
            "Citrinitas": {"cost": 3, "type": "science"},
        },
    },
    "Rubedo": {
        "expansion": "Gorm",
        "type": "science",
        "endeavors": {
            "Rubedo": {"cost": 4, "type": "science"},
        },
    },
    "Graves": {
        "type": "principle",
        "milestone": "First time death count is updated",
        "settlement_buff": 'All new survivors gain +1 understanding.<br/>When a survivor dies during the hunt or showdown phase, gain +2 <font class="kdm_font">d</font>.<br/>When a survivor dies during the settlement phase, gain +1 <font class="kdm_font">d</font>.',
        "survivor_buff": "All new survivors gain +1 understanding.",
        "new_survivor": {"Understanding": 1},
    },
    "Cannibalize": {
        "type": "principle",
        "milestone": "First time death count is updated",
        "survival_limit": 1,
        "settlement_buff": "Whenever a survivor dies, draw one basic resource and add it to the settlement storage.",
    },
    "Barbaric": {
        "type": "principle",
        "survival_limit": 1,
        "survivor_buff": "All current and newborn survivors gain +1 permanent Strength.",
        "current_survivor": {"Strength": 1},
        "newborn_survivor": {"Strength": 1},
    },
    "Romantic": {
        "type": "principle",
        "survival_limit": 1,
        "settlement_buff": "You may innovate one additional time during the settlement phase. In addition, all current and newborn survivors gain +1 understanding.",
        "survivor_buff": "All current and newborn survivors gain +1 understanding.",
        "current_survivor": {"Understanding": 1},
        "newborn_survivor": {"Understanding": 1},
    },
    "Collective Toil": {
        "type": "principle",
        "milestone": "Population reaches 15",
        "settlement_buff": "At the start of the settlement phase, gain +1 Endeavor for every 10 population.",
    },
    "Accept Darkness": {
        "type": "principle",
        "milestone": "Population reaches 15",
        "survivor_buff": "Add +2 to all Brain Trauma Rolls.",
    },
    "Protect the Young": {
        "type": "principle",
        "milestone": "First child is born",
        "settlement_buff": "When rolling on the Intimacy story event, roll twice and pick one result.",
    },
    "Survival of the Fittest": {
        "type": "principle",
        "milestone": "First child is born",
        "survival_limit": 1,
        "settlement_buff": "When rolling on the Intimacy story event, roll twice and pick the lowest result. All current and newborn survivors gain +1 strength and evasion.<br/>Once per lifetime, a survivor may reroll a single roll result. They must keep this new result.",
        "survivor_buff": "All current and newborn survivors gain +1 strength and evasion.",
        "current_survivor": {"Strength": 1, "Evasion": 1},
        "newborn_survivor": {"Strength": 1, "Evasion": 1},
    },
    "Clan of Death": {
        "type": "home",
        "survivor_buff": "All newborn survivors gain <b>+1 Accuracy</b>, <b>+1 Strength</b> and <b>+1 Evasion</b>.",
        "newborn_survivor": {"Strength": 1, "Accuracy": 1, "Evasion": 1},
    },
    "Sacrifice": {
        "type": "faith",
        "endeavors": {
            "Death Ritual": {"type": "faith", "cost": 1,},
        },
    },
    "Scarification": {
        "type": "faith",
        "endeavors": {
            "Initiation": {"cost": 1, "type": "faith"},
        },
    },
    "Records": {
        "type": "education",
        "endeavors": {
            "Knowledge": {"cost": 2, "type": "education"},
        },
    },
    "Shrine": {
        "type": "faith",
        "consequences": ["Sacrifice"],
        "endeavors": {
            "Armor Ritual": {"cost": 1, "type": "faith"},
        },
    },
    "Scrap Smelting": {
        "type": "science",
        "special_innovate": ("locations","Weapon Crafter"),
        "endeavors": {
            "Purification": {"cost": 1, "type": "science"},
            "Build": {"cost": 1, "desc": "Blacksmith (6 x bone, 3 x scrap)", "remove_after": "Blacksmith"},
        },
    },
    "Cooking": {
        "type": "science",
        "survival_limit": 1,
        "endeavors": {
            "Culinary Inspiration": {"cost": 1, "type": "science"},
        },
    },
    "Drums": {
        "type": "music",
        "consequences": ["Song of the Brave", "Forbidden Dance"],
        "endeavors": {
            "Bone Beats": {"cost": 1, "type": "music"},
        },
    },
    "Inner Lantern": {
        "type": "faith",
        "consequences": ["Shrine", "Scarification"],
        "survival_action": "Surge",
    },
    "Symposium": {
        "type": "education",
        "consequences": ["Nightmare Training", "Storytelling",],
        "survival_limit": 1,
        "settlement_buff": "When a survivor innovates, draw an additional 2 Innovation Cards to choose from.",
    },
    "Hovel": {
        "type": "home",
        "consequences": ["Partnership", "Family", "Bed", "Shadow Dancing","Bloodline","Settlement Watch"],
        "departure_buff": "Departing survivors gain +1 survival.",
        "survival_limit": 1,
    },
    "Storytelling": {
        "type": "education",
        "consequences": ["Records","War Room"],
        "survival_limit": 1,
        "endeavors": {
            "Tale as Old as Time": {"cost": 2, "type": "education"},
        },
    },
    "Nightmare Training": {
        "type": "education",
        "consequences": ["Round Stone Training"],
        "endeavors": {
            "Train": {"cost": 1, "type": "education"},
        },
    },
    "Momento Mori": {
        "type": "art",
        "endeavors": {
            "Momento Mori": {"cost": 1, "type": "art"},
        },
    },
    "Face Painting": {
        "type": "art",
        "endeavors": {
            "Battle Paint": {"cost": 1, "type": "art"},
            "Founder's Eye": {"cost": 1, "type": "art"},
        },
    },
    "Pottery": {
        "type": "art",
        "survival_limit": 1,
        "settlement_buff": "If the settlement loses all its resources, you may select up to two resources and keep them.",
        "endeavors": {
            "Build": {"cost": 1, "desc": "Barber Surgeon (3 x organ, 1 x scrap)", "remove_after": "Barber Surgeon"},
        },
    },
    "Sculpture": {
        "type": "art",
        "consequences": ["Pottery"],
        "survival_limit": 1,
        "departure_buff": "Departing survivors gain +2 survival when they depart for a Nemesis Encounter.",
    },
    "Paint": {
        "type": "art",
        "consequences": ["Pictograph", "Sculpture", "Face Painting"],
        "survival_action": "Dash",
    },
    "Pictograph": {
        "type": "art",
        "consequences": ["Momento Mori"],
        "survivor_buff": 'Anytime during the hunt or showdown phase, a survivor may <font class="kdm_font">g</font> <b>Run Away</b>.',
    },
    "Heart Flute": {
        "type": "music",
        "endeavors": {
            "Devil's Melody": {"cost": 1, "type": "music"},
        },
    },
    "Forbidden Dance": {
        "type": "music",
        "consequences": ["Petal Spiral"],
        "endeavors": {
            "Fever Dance": {"cost": 1, "type": "music"},
        },
    },
    "Bed": {
        "type": "home",
        "survival_limit": 1,
        "endeavors": {
            "Rest": {"cost": 1, "type": "home"},
        },
    },
    "Bloodletting": {
        "type": "science",
        "endeavors": {
            "Breathing a Vein": {"cost": 1, "type": "science"},
        },
    },
    "Saga": {
        "type": "music",
        "survivor_buff": "All newborn survivors gain +2 hunt experience and +2 survival from knowing the epic.",
        "newborn_survivor": {"hunt_xp": 2, "survival": 2},
    },
    "Family": {
        "type": "home",
        "consequences": ["Clan of Death"],
        "departure_buff": "Departing survivors gain +1 survival.",
        "settlement_buff": "Survivors nominated for intimacy may give themselves a surname if they do not have one. A newborn survivor inherits the surname of one parent, their weapon type and half (rounded down) of their weapon proficiency levels.",
    },
    "Song of the Brave": {
        "type": "music",
        "consequences": ["Saga",],
        "survivor_buff": "All non-deaf survivors add +1 to their roll results on the Overwhelming Darkness story event.",
    },
    "Language": {
        "type": "starting innovation",
        "consequences": ["Hovel", "Inner Lantern", "Drums", "Paint", "Symposium", "Ammonia"],
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
        "always_available": True,
    },
    "Final Fighting Art": {
        "type": "education",
        "survival_limit": 1,
        "always_available": True,
    },
    "Ultimate Weapon": {
        "type": "science",
        "survival_limit": 1,
        "always_available": True,
    },
    "Guidepost": {
        "type": "other",
        "departure_buff": "Departing survivors gain +1 survival.",
        "always_available": True,
    },
    "Partnership": {
        "always_available": True,
        "type": "home",
        "endeavors": {
            "Partner": {"cost": 2, "type": "home"},
        },
    },
}


#
#   Pre-fab Survivors (available on new campaign view)
#

survivors = {
    "Adam": {
        "attribs": {
            "survival": 4,
            "Insanity": 4,
            "Courage": 6,
            "Understanding": 3,
            "Weapon Proficiency": 3,
            "Strength": 1,
            "weapon_proficiency_type": "Sword",
            "fighting_arts": ["Timeless Eye"],
            "abilities_and_impairments": ["Partner", "Specialization - Sword"],
            "ability_customizations": {"Partner": "Partner: Anna"},
        },
    },
    "Anna": {
        "attribs": {
            "sex": "F",
            "survival": 4,
            "Insanity": 4,
            "Courage": 3,
            "Understanding": 6,
            "Weapon Proficiency": 3,
            "Evasion": 1,
            "weapon_proficiency_type": "Spear",
            "fighting_arts": ["Leader"],
            "abilities_and_impairments": ["Partner", "Specialization - Spear"],
            "ability_customizations": {"Partner": "Partner: Adam"},
        },
    },
    "Paul the Survivor": {
        "attribs": {
            "name": "Paul",
            "survival": 5,
            "Insanity": 9,
            "Courage": 3,
            "Understanding": 3,
            "fighting_arts": ["Thrill Seeker","Clutch Fighter","Extra Sense"],
            "disorders": ["Rageholic","Sworn Enemy"],
            "abilities_and_impairments": ["Sworn Enemy"],
            "ability_customizations": {"Sworn Enemy": "Halberdless Man"},
        },
    },
    "Candy & Cola": {
        "attribs": {"Movement": 6, "disorders": ["Hyperactive"], "sex": "F"},
    },
    "Kara Black": {
        "attribs": {"survival": 3, "Strength": 1, "fighting_arts": ["Leader","Tough"], "sex": "F"},
    },
    "Messenger of the First Story": {
        "attribs": {"sex": "F", "survival": 6, "Insanity": 6, "Courage": 6, "Strength": 1, "Evasion": 1, "Speed": 1, "fighting_arts": ["Last Man Standing"], },
    },
    "Messenger of Courage": {
        "attribs": {"sex": "F", "survival": 6, "Insanity": 9, "Courage":  9, "Understanding": 5, "Strength": 1, "Evasion": 2, "Speed": 2, "hunt_xp": 2, "Weapon Proficiency": 5, "weapon_proficiency_type": "Twilight Sword", "fighting_arts": ["Last Man Standing"], "abilities_and_impairments": ["Specialization - Twilight Sword"]},
    },
    "Messenger of Humanity": {
        "attribs": {"survival": 10, "abilities_and_impairments": ["Bitter Frenzy", "Solid", "Specialization - Grand Weapon"], "fighting_arts": ["Berserker", "Crossarm Block", "Unconscious Fighter"], "disorders": ["Rageholic"]},
    },
    "Snow the Savior": {
        "attribs": {"name": "Snow", "sex": "F", "survival": 6, "Insanity": 8, "Courage": 5, "Understanding": 5, "fighting_arts": ["Unconscious Fighter"], "abilities_and_impairments": ["Red Glow", "Blue Glow", "Green Glow"]},
    },
}



#
#   Monster assets
#

quarries = {
    "White Lion":               {"sort_order": 1, },
    "Gorm":                     {"sort_order": 2, "expansion": "Gorm"},
    "Screaming Antelope":       {"sort_order": 3, },
    "Flower Knight":            {"sort_order": 4, "expansion": "Flower Knight"},
    "Phoenix":                  {"sort_order": 5, },
    "Sunstalker":               {"sort_order": 6, "expansion": "Sunstalker"},
    "Dragon King":              {"sort_order": 7, "expansion": "Dragon King"},
    "Dung Beetle Knight":       {"sort_order": 7, "expansion": "Dung Beetle Knight"},
	"Lion God":                 {"sort_order": 8, "expansion": "Lion God"},
    "Beast Of Sorrow":          {"sort_order": 10, "no_levels": True, },
    "Great Golden Cat":         {"sort_order": 11, "no_levels": True, },
    "Mad Steed":                {"sort_order": 12, "no_levels": True, },
    "Golden Eyed King":         {"sort_order": 13, "no_levels": True, },
    "Old Master":               {"sort_order": 14, "no_levels": True, "expansion": "Dung Beetle Knight"},
}

nemeses = {
    "Lonely Tree":          {"sort_order": 20, "expansion": "Lonely Tree", "exclude_from_picker": True,},
    "Butcher":              {"sort_order": 21, },
    "The Tyrant":           {"sort_order": 22, "expansion": "Dragon King", "exclude_from_picker": True,},
    "Manhunter":            {"sort_order": 23, "expansion": "Manhunter", "exclude_from_picker": True, "levels": 4,},
    "King's Man":           {"sort_order": 24, },
    "Lion Knight":          {"sort_order": 25, "expansion": "Lion Knight"},
    "The Hand":             {"sort_order": 26, },
    "Ancient Sunstalker":   {"sort_order": 30, "no_levels": True, "expansion": "Sunstalker", "add_to_timeline_controls_at": 25, "campaign": "People of the Sun"},
    "Watcher":              {"sort_order": 31, "no_levels": True, "add_to_timeline_controls_at": 20, "campaign": "People of the Lantern"},
}




#
#   Settlement Sheet assets
#

story_events = {
    "Bold": {"page": 106, "book": "core"},
    "Insight": {"page": 122, "book": "core"},
    "The Pool and the Sun": {"page": 15, "book": "Sunstalker"},
    "Endless Screams": {"page": 115, "book": "core"},
    "Sun Dipping": {"page": 19, "book": "Sunstalker"},
    "The Great Sky Gift": {"page": 21, "book": "Sunstalker"},
    "Phoenix Feather": {"page": 139, "book": "core"},
    "Promise Under the sun": {"page": 4, "book": "Sunstalker"},
    "Birth of Color": {"page": 23, "book": "Sunstalker"},
    "Principle: Conviction": {"page": 141, "book": "core"},
    "Principle: Death": {"page": 143, "book": "core"},
    "Principle: New Life": {"page": 145, "book": "core"},
    "Principle: Society": {"page": 147, "book": "core"},
    "Final Gift": {"page": 25, "book": "Sunstalker"},
    "The Great Devourer": {"page": 33, "book": "Sunstalker"},
    "Game Over": {"page": 179, "book": "core"},
    "Edged Tonometry": {"page": 29, "book": "Sunstalker"},
    "Hooded Knight": {"page": 121, "book": "core"},
    "The Lonely Lady": {"page": 2, "book": "Lonely Tree"},
    "A Crone's Tale": {"page": 4, "book": "Flower Knight"},
    "The Forest Wants What It Wants": {"page": 12, "book": "Flower Knight"},
    "Breakthrough": {"page": 14, "book": "Flower Knight"},
    "Sense Memory": {"page": 16, "book": "Flower Knight"},
    "A Warm Virus": {"page": 18, "book": "Flower Knight"},
    "Necrotoxic Mistletoe": {"page": 20, "book": "Flower Knight"},
    "Glowing Crater": {"page": 4, "book": "Dragon King"},
    "Meltdown": {"page": 8, "book": "Dragon King"},
    "Foundlings": {"page": 10, "book": "Dragon King"},
    "Intimacy (People of the Stars)": {"page": 12, "book": "Dragon King"},
    "Midnight's Children": {"page": 14, "book": "Dragon King"},
    "Awake": {"page": 16, "book": "Dragon King"},
    "Unveil the Sky": {"page": 18, "book": "Dragon King"},
    "Faces in the Sky": {"page": 20, "book": "Dragon King"},
    "The Tomb": {"page": 22, "book": "Dragon King"},
    "Death of the Dragon King": {"page": 27, "book": "Dragon King"},
    "The Hanged Man": {"page": 3, "book": "Manhunter"},
    "Lottery": {"page": 11, "book": "Manhunter"},
    "Death Pit": {"page": 13, "book": "Manhunter"},
    "Sonorous Rest": {"page": 15, "book": "Manhunter"},
    "Bleeding Heart": {"page": 17, "book": "Manhunter"},
    "Tools of War": {"page": 19, "book": "Manhunter"},
}

resources = {
    "White Lion Resources": {
        "color": "FFCC66",
    },
    "Screaming Antelope Resources": {
        "color": "FFCC66",
    },
    "Phoenix Resources": {
        "color": "FFCC66",
    },
    "Gorm Resources": {
        "expansion": "Gorm",
        "color": "FFCC66",
    },
    "Dung Beetle Knight Resources": {
        "expansion": "Dung Beetle Knight",
        "color": "FFCC66",
    },
    "Dragon King Resources": {
        "expansion": "Dragon King",
        "color": "FFCC66",
    },
    "Basic Resources": {
        "color": "B1FB17",
    },
    "Vermin": {
        "color": "99CC66",
    },
    "Strange Resources": {
        "color": "9DC209",
    },
    "Starting Gear": {
        "color": "CCC",
    },
}




#
#   Survivor Sheet assets
#

survival_actions = {
    "Dodge": {"sort_order": 0},
    "Encourage": {"sort_order": 1},
    "Embolden": {"sort_order": 2, "expansion": "Sunstalker"},
    "Dash": {"sort_order": 3},
    "Surge": {"sort_order": 4},
    "Overcharge": {"sort_order": 5, "expansion": "Sunstalker"},
    }

survivor_attributes = ["Movement", "Accuracy", "Strength", "Evasion", "Luck", "Speed"]

weapon_proficiencies = {
    "Scythe": {"expansion": "Dragon King"},
    "Katana": {"expansion": "Sunstalker", "auto-apply_specialization": False},
    "Bow": {},
    "Katar": {},
    "Sword": {},
    "Dagger": {},
    "Shield": {},
    "Whip": {},
    "Grand Weapon": { },
    "Fist & Tooth": { },
    "Club": {},
    "Spear": {},
    "Axe": {},
    "Twilight Sword": {},
}


epithets = {
    # manhunter
    "Recruit": {"expansion": "Manhunter"},
    "Settlement Watch": {"expansion": "Manhunter"},
    "Tuned": {"expansion": "Manhunter", "bgcolor": "1C99CD", "color": "FFF"},
    "Rested": {"expansion": "Manhunter", "bgcolor": "4CB848", "color": "FFF"},
    "Slave": {"expansion": "Manhunter", "bgcolor": "000", "color": "f00"},
    "Sadist": {"expansion": "Manhunter", "bgcolor": "000", "color": "f00"},
    "Masochist": {"expansion": "Manhunter", "bgcolor": "000", "color": "f00"},
    "Manhunter": {"expansion": "Manhunter", "bgcolor": "000", "color": "f00"},
    "Warborn": {"expansion": "Manhunter", "bgcolor": "000", "color": "f00"},
    "Crimson Confectioner": {"expansion": "Manhunter", "bgcolor": "c00", "color": "fff"},
    "Sweet Tooth": {"expansion": "Manhunter", },
    "Deranged": {"expansion": "Manhunter", "bgcolor": "000", "color": "f00"},
    "Deranged Expression": {"expansion": "Manhunter", "bgcolor": "000", "color": "f00"},
    # Dragon King
    "The Witch": {"expansion": "HIDDEN", "bgcolor":"4527A0", "color":"FFF",},
    "The Rust": {"expansion": "HIDDEN", "bgcolor":"4527A0", "color":"FFF",},
    "The Storm": {"expansion": "HIDDEN", "bgcolor":"4527A0", "color":"FFF",},
    "The Reaper": {"expansion": "HIDDEN", "bgcolor":"4527A0", "color":"FFF",},
    "The Gambler": {"expansion": "HIDDEN", "bgcolor":"4527A0", "color":"FFF",},
    "The Absolute": {"expansion": "HIDDEN", "bgcolor":"4527A0", "color":"FFF",},
    "The Sculptor": {"expansion": "HIDDEN", "bgcolor":"4527A0", "color":"FFF",},
    "The Goblin": {"expansion": "HIDDEN", "bgcolor":"4527A0", "color":"FFF",},
    "Imago Tyrannis": {"expansion": "Dragon King"},
    "Molded by the Tyrant": {"expansion": "Dragon King"},
    "Approached the Throne": {"expansion": "Dragon King"},
    "Foundling": {"expansion": "Dragon King", "bgcolor": "FFC107"},
    "Successor": {"expansion": "Dragon King"},
    "Husk": {"expansion": "Dragon King"},
    "Tyrant": {"expansion": "Dragon King"},
    "Molded by the Tyrant": {"expansion": "Dragon King"},
    "Sweetmeat Eater": {"expansion": "Dragon King"},
    "Held the Radiant Heart": {"expansion": "Dragon King"},
    "Numerologist": {"expansion": "Dragon King"},
    "Gladiator": {"expansion": "Dragon King"},
    "Nuclear Warrior": {"expansion": "Dragon King"},
    "Atomic Heart": {"expansion": "Dragon King"},
    "Star Gazer": {"expansion": "Dragon King"},
    "Starbound": {"expansion": "Dragon King"},
    "Dragonkin": {"expansion": "Dragon King"},
    "Consumer of Sins": {"expansion": "Dragon King"},
    "Consumer of Lies": {"expansion": "Dragon King"},
    "Peered into Destiny": {"expansion": "Dragon King"},
    "Noble": {"expansion": "Dragon King"},
    "Reincarnated": {"expansion": "Dragon King"},

    # flower knight
    "Vespertine": {"expansion": "Flower Knight"},
    "Host": {"expansion": "Flower Knight", "bgcolor": "116E17", "color": "0f0"},
    "Guest": {"expansion": "Flower Knight", "bgcolor": "116E17", "color": "0f0"},
    "The First Host": {"expansion": "Flower Knight", "bgcolor": "116E17", "color": "0f0"},
    "The First Guest": {"expansion": "Flower Knight", "bgcolor": "116E17", "color": "0f0"},
    "Flower Addict": {"expansion": "Flower Knight"},

    # Sunstalker
    "Child of the Sun": {"expansion": "Sunstalker", "bgcolor": "FFEB3B"},
    "Purified": {"expansion": "Sunstalker"},
    "Sun Eater": {"expansion": "Sunstalker", "bgcolor": "FFEB3B"},
    "Triplet": {"expansion": "Sunstalker"},
    "Eye Patch Badass": {"expansion": "Sunstalker"},

    # Lion God
    "Necromancer": {"expansion": "Lion God"},
    "Worm Bait": {"expansion": "Lion God"},

    # Lion Knight
    "Hideous": {"expansion": "Lion Knight"},
    "Warlord": {"expansion": "Lion Knight"},
    "Dancer": {"expansion": "Lion Knight"},
    "Brawler": {"expansion": "Lion Knight"},
    "Monster Worshipper": {"expansion": "Lion Knight"},

    # DBK
    "Spelunker of Death": {"expansion": "Dung Beetle Knight"},
    "Farmer": {"expansion": "Dung Beetle Knight"},
    "Bug Man": {"expansion": "Dung Beetle Knight"},
    "Met the Bug Man": {"expansion": "Dung Beetle Knight"},
    "Entomophile": {"expansion": "Dung Beetle Knight"},
    "Beetle-kin": {"expansion": "Dung Beetle Knight"},
    "Beetle-brain": {"expansion": "Dung Beetle Knight"},
    "Round Stone Trainer": {"expansion": "Dung Beetle Knight"},

    # gorm
    "Vomit-soaked": {"expansion": "Gorm"},
    "Gorm Bait": {"expansion": "Gorm",},
    "Digested": {"expansion": "Gorm"},
    "Braved the Storm": {"expansion": "Gorm"},
    "Living Sacrifice": {"expansion": "Gorm"},

    #
    #   Generic/core epithets
    #

    # showdown
    "Vomit-soaked": {},
    "Masticated": {},

    # endeavor
    "Sacrificed": {},
    "Forbidden Dancer": {},

    # severe injury
    "Scarred": {},
    "Destroyed Genitals": {},
    "One-eyed": {},
    "The Blind": {},
    "The Dead": {},

    # hunt phase
    "Hunter": {},
    "Straggler": {},
    "Ate the Fruit": {},
    "Wanderer": {},

    # fun/general
    "Gender Swap": {"bgcolor": "FF4081", "color": "fff"},
    "Twilight Knight": {"color": "fff", "bgcolor": "546E7A"},
    "Twilight Sword": {"color": "fff", "bgcolor": "546E7A"},
    "Twilight Lineage": {"color": "fff", "bgcolor": "546E7A"},
    "Dreamer": {},
    "Cursed": {},
    "Monster": {},
    "Fast Runner": {},
    "The Doomed": {},
    "The Brave": {},
    "The Insane": {},
    "The Mad": {},
    "The Silent": {},

    # combat / prowess
    "Slayer": {},
    "Sniper": {},
    "Forsaker": {},
    "Berserker": {},
    "Iron Fist": {},
    "Thunderer": {},
    "Swift-footed": {},

    # settlement event
    "Bewitched": {},
    "Witness": {},
    "Plague-bearer": {},
    "Infected": {},
    "White-haired":{},
    "Monster Teeth": {},
    "Rival": {},
    "Branded by the Lantern": {},
    "Maw Runner": {},
    "Triathlete":{},
    "Undisputed boss of the settlement": {},
    "Coward": {},
    "Foolish": {},
    "Shining": {},
    "Hero": {},
    "Metal Jaw": {},
    "Haunted": {},
    "Skull Eater": {},
    "Dimmed by the Lantern": {},
    "Murderer": {},
    "Endless Arguer": {},

    # story event
    "Speaker of the First Words": {},
    "Father of Words": {},
    "Silence Breaker": {},
    "Broke the Silence": {},
    "The Chef": {},
    "Death Taster": {},
    "Pure Warrior": {},
    "Swamp Explorer": {},
    "Lantern Experimenter": {},
    "Experimented with Lanterns": {},
    "Voice of Reason": {},
    "Bone Witch": {"color": "FFF", "bgcolor": "212121"},
    "Leader of the Settlement": {},

    # lineage/ancestry/etc.
    "Breeder": {},
    "The Fertile": {},
    "Founder": {"bgcolor": "FFC107"},
    "First Son": {},
    "First Daughter": {},
    "First Father": {},
    "First Mother": {},
    "Twin": {},

    # saviors
    "Caratosis": {"color": "FFF", "bgcolor": "CD2027", "expansion": "HIDDEN",},
    "Lucernae": {"color": "FFF", "bgcolor": "1C99CD", "expansion": "HIDDEN",},
    "Dormenatus": {"color": "FFF", "bgcolor": "4CB848", "expansion": "HIDDEN",},
    "Savior": {},
    "Red Savior": {"color": "FFF", "bgcolor": "CD2027", "expansion": "HIDDEN"},
    "Blue Savior": {"color": "FFF", "bgcolor": "1C99CD", "expansion": "HIDDEN"},
    "Green Savior": {"color": "FFF", "bgcolor": "4CB848", "expansion": "HIDDEN"},
}


#
#   constellation map (People of the Stars)
#

potstars_constellation = {
    "map": {
        "9 Understanding (max)": "A1",
        "Destined disorder": "B1",
        "Fated Blow fighting art": "C1",
        "Pristine ability": "D1",
        "Reincarnated surname": "A2",
        "Frozen Star secret fighting art": "B2",
        "Iridescent Hide ability": "C2",
        "Champion's Rite fighting art": "D2",
        "Scar": "A3",
        "Noble surname": "B3",
        "Weapon Mastery": "C3",
        "1+ Accuracy attribute": "D3",
        "Oracle's Eye ability": "A4",
        "Unbreakable fighting art": "B4",
        "3+ Strength attribute": "C4",
        "9 Courage (max)": "D4",
    },
    "formulae": {
        "Witch": ["A1","A2","A3","A4"],
        "Rust": ["B1","B2","B3","B4"],
        "Storm": ["C1","C2","C3","C4"],
        "Reaper": ["D1","D2","D3","D4"],
        "Gambler": ["A1","B1","C1","D1"],
        "Absolute": ["A2","B2","C2","D2"],
        "Sculptor": ["A3","B3","C3","D3"],
        "Goblin": ["A4","B4","C4","D4"],
    },
}



#
#   Expansion assets and definitions
#

expansions = {
    "Beta Challenge Scenarios": {
        "subtitle": "Enables abilities & impairments, disorders, items etc. included in the Beta Challenge Scenarios.",
        "enforce_survival_limit": False,
        "special_rules": [
        {"name": "Survival Limit Warning!", "desc": "Survival Limit is not automatically enforced by the Manager when Beta Challenge Scenarios content is enabled.", "bg_color": "F87217", "font_color": "FFF"},
        ],
    },
    "Dragon King": {
        "always_available": ["Dragon Armory"],
        "timeline_add": [
            {"ly": 8, "type": "story_event", "name": "Glowing Crater", "excluded_campaign": "People of the Stars"},
        ],
    },
    "Gorm": {
        "always_available": ["Gormery", "Gormchymist", "Nigredo"],
        "timeline_add": [
            {"ly": 1, "type": "story_event", "name": "The Approaching Storm"},
            {"ly": 2, "type": "settlement_event", "name": "Gorm Climate"},
        ],
    },
    "Manhunter": {
        "always_available": ["War Room", "Settlement Watch", "Crimson Candy"],
        "always_available_nemesis": "Manhunter",
        "timeline_add": [
            {"ly": 5, "type": "story_event", "name": "The Hanged Man"},
            {"ly": 10, "type": "nemesis_encounter", "name": "Special Showdown - Manhunter"},
            {"ly": 16, "type": "nemesis_encounter", "name": "Special Showdown - Manhunter"},
            {"ly": 22, "type": "nemesis_encounter", "name": "Special Showdown - Manhunter"},
        ],
    },
    "Dung Beetle Knight": {
        "always_available": ["Wet Resin Crafter","Subterranean Agriculture"],
        "timeline_add": [
            {"ly": 8, "type": "story_event", "name": "Rumbling in the Dark"},
        ],
    },
    "Lion Knight": {
        "always_available": ["Stoic Statue"],
        "timeline_add": [
            {"ly": 6, "type": "story_event", "name": "An Uninvited Guest"},
            {"ly": 8, "type": "story_event", "name": "Places, Everyone!"},
            {"ly": 12, "type": "story_event", "name": "Places, Everyone!"},
            {"ly": 16, "type": "story_event", "name": "Places, Everyone!"},
        ],
    },
    "Lion God": {
        "always_available": ["The Knowledge Worm"],
        "timeline_add": [
            {"ly": 13, "type": "story_event", "name": "The Silver City"},
        ],
    },
    "Sunstalker": {
        "always_available": ["The Sun", "Sun Language", "Umbilical Bank"],
        "timeline_add": [
            {"ly": 8, "type": "story_event", "name": "Promise Under the Sun", "excluded_campaign": "People of the Sun"},
        ],
    },
    "Lonely Tree": {
        "always_available_nemesis": "Lonely Tree",
    },
    "White Box": {
        "subtitle": "Enables promo and early-release items and abilities & impairments included in the so-called 'White Box' collection of survivor minis (released at Gen Con 2016).",
    },
    "Flower Knight": {
        "timeline_add": [{"ly": 5, "type": "story_event", "name": "A Crone's Tale", "excluded_campaign": "The Bloom People"}],
    },
}




#
#   Campaign assets and definitions
#

default_timeline = [
    {"year": 0, "settlement_event": ["First Day"]},
    {"year": 1, "story_event": ["Returning Survivors"]},
    {"year": 2, "story_event": ["Endless Screams"]},
    {"year": 3, },
    {"year": 4, "nemesis_encounter": ["Nemesis Encounter: Butcher"]},
    {"year": 5, "story_event": ["Hands of Heat"]},
    {"year": 6, "story_event": ["Armored Strangers"]},
    {"year": 7, "story_event": ["Phoenix Feather"]},
    {"year": 8, },
    {"year": 9, "nemesis_encounter": ["Nemesis Encounter: King's Man"]},
    {"year": 10, },
    {"year": 11, "story_event": ["Regal Visit"]},
    {"year": 12, "story_event": ["Principle: Conviction"]},
    {"year": 13, }, {"year": 14, }, {"year": 15, },
    {"year": 16, "nemesis_encounter": ["Nemesis Encounter"]},
    {"year": 17, }, {"year": 18, },
    {"year": 19, "nemesis_encounter": ["Nemesis Encounter"]},
    {"year": 20, "story_event": ["Watched"], },
    {"year": 21, }, {"year": 22, },
    {"year": 23, "nemesis_encounter": ["Nemesis Encounter: Level 3"]},
    {"year": 24, }, {"year": 25, },
    {"year": 26, "nemesis_encounter": ["Nemesis Encounter: Watcher"]},
    {"year": 27, }, {"year": 28, }, {"year": 29, }, {"year": 30, }, {"year": 31, },
    {"year": 32, }, {"year": 33, }, {"year": 34, }, {"year": 35, }, {"year": 36, },
    {"year": 37, }, {"year": 38, }, {"year": 39, }, {"year": 40, },
]

# this is a collection of milestones that might or might not be used in a given
#   campaign. Campaign assets don't default for this stuff, so you've got to
#   reference all required milestones when defining the asset below
milestones = {
    "first_child": {
        "sort_order": 0,
        "story_event": "Principle: New Life",
    },
    "first_death": {
        "sort_order": 1,
        "story_event": "Principle: Death",
        "add_to_timeline": 'int(self.settlement["death_count"]) >= 1',
    },
    "pop_15": {
        "sort_order": 2,
        "story_event": "Principle: Society",
        "add_to_timeline": 'int(self.settlement["population"]) >= 15',
    },
    "innovations_5": {
        "sort_order": 3,
        "story_event": "Hooded Knight",
        "add_to_timeline": 'len(self.settlement["innovations"]) >= 5',
    },
    "innovations_8": {
        "sort_order": 2,
        "story_event": "Edged Tonometry",
        "add_to_timeline": 'len(self.settlement["innovations"]) >= 8',
    },
    "game_over": {
        "sort_order": 10,
        "story_event": "Game Over",
        "add_to_timeline": 'int(self.settlement["death_count"]) >= 1 and int(self.settlement["population"]) == 0 and int(self.settlement["lantern_year"]) >= 1',
    },
}

# create generic principle definitions here, just like milestones above
principles = {
    "new_life": {
        "sort_order": 0,
        "milestone": "First child is born",
        "show_controls": ['"First child is born" in self.settlement["milestone_story_events"]'], 
        "options": ["Protect the Young","Survival of the Fittest"],
    },
    "death": {
        "sort_order": 1,
        "milestone": "First time death count is updated",
        "show_controls": ['int(self.settlement["death_count"]) >= 1'],
        "options": ["Cannibalize","Graves"]
    },
    "society": {
        "sort_order": 2,
        "milestone": "Population reaches 15",
        "options": ["Collective Toil","Accept Darkness"],
        "show_controls": ['int(self.settlement["population"]) >= 15'],
    },
    "conviction": {
        "sort_order": 3,
        "options": ["Barbaric","Romantic"],
        "show_controls": ['int(self.settlement["lantern_year"]) >= 12'],
    },
}

# define all campaign assets here
campaigns = {
    "People of the Lantern": {
        "default": True,
        "always_available": ["Lantern Hoard", "Language", "Exhausted Lantern Hoard"],
        "forbidden": ["The Sun","Throne","Dragon Speech","Sun Language"],
        "saviors": "1.3.1",
        "principles": {
            "New Life": principles["new_life"],
            "Death": principles["death"],
            "Society": principles["society"],
            "Conviction": principles["conviction"],
        },
        "milestones": {
            "First child is born": milestones["first_child"],
            "First time death count is updated": milestones["first_death"],
            "Population reaches 15": milestones["pop_15"],
            "Settlement has 5 innovations": milestones["innovations_5"],
            "Population reaches 0": milestones["game_over"],
        },
    },

    "People of the Skull": {
        "always_available": ["Lantern Hoard", "Language"],
        "forbidden": ["The Sun","Throne","Dragon Speech","Sun Language"],
        "saviors": "1.3.1",
        "special_rules": [
            {"name": "People of the Skull",
             "desc": "Survivors can only place weapons and armor with the <b>bone</b> keyword in their gear grid. The people of the skull ignore the <b>Frail</b> rule.",
             "bg_color": "E3DAC9",
             "font_color": "333"},
            {"name": "People of the Skull",
             "desc": "When you name a survivor, if they have the word bone or skull in their name, in addition to +1 survival, players choose to gain +1 permanent accuracy, evasion, strength, luck or speed.",
             "bg_color": "E3DAC9",
             "font_color": "333"},
            {"name": "Black Skull",
             "desc": "If a weapon or armor is made with the Black Skull resource, a survivor may place it in their gear grid despite being iron.",
             "bg_color": "333",
             "font_color": "efefef"},
        ],
        "endeavors": {
            "Skull Ritual": {"cost": 1, "desc": "Costs one Skull resource. Nominate up to four survivors to consume the skull. They gain a permanent +1 to all their attributes."},
        },
        "principles": {
            "New Life": principles["new_life"],
            "Death": principles["death"],
            "Society": principles["society"],
            "Conviction": principles["conviction"],
        },
        "milestones": {
            "First child is born": milestones["first_child"],
            "First time death count is updated": milestones["first_death"],
            "Population reaches 15": milestones["pop_15"],
            "Settlement has 5 innovations": milestones["innovations_5"],
            "Population reaches 0": milestones["game_over"],
        },
    },

    "The Bloom People": {
        "always_available": ["Lantern Hoard", "Language"],
        "expansions": ["Flower Knight"],
        "saviors": "1.3.1",
        "storage": ["Sleeping Virus Flower"],
        "forbidden": ["The Sun", "Throne" "Flower Addiction", "Flower Knight"],
        "milestones": {
            "First child is born": milestones["first_child"],
            "First time death count is updated": milestones["first_death"],
            "Population reaches 15": milestones["pop_15"],
            "Settlement has 5 innovations": milestones["innovations_5"],
            "Population reaches 0": milestones["game_over"],
        },
        "principles": {
            "New Life": principles["new_life"],
            "Death": principles["death"],
            "Society": principles["society"],
            "Conviction": principles["conviction"],
        },
        "endeavors": {
            "Forest Run": {"cost": 1, "desc": "You may exchange any number of monster resources for that number of random Flower resources."},
        },
        "settlement_buff": "All survivors are born with +1 permanent luck, +1 permanent green affinity and -2 permanent red affinities.",
        "newborn_survivor": {
            "affinities": {"red": -2, "green": 1,},
            "Luck": 1,
        },
    },

    "People of the Sun": {
        "expansions": ["Sunstalker"],
        "survivor_attribs": ["Purified","Sun Eater","Child of the Sun"],
        "always_available": ["Sun Language","The Sun"],
        "forbidden": ["Leader", "Lantern Hoard", "Exhausted Lantern Hoard"],
        "principles": {
            # custom new life principle
            "New Life": {
                "sort_order": 0,
                "show_controls": ["True"],
                "options": ["Survival of the Fittest"]
            },
            "Death": principles["death"],
            "Society": principles["society"],
            "Conviction": principles["conviction"],
        },
        "milestones": {
            "First time death count is updated": milestones["first_death"],
            "Population reaches 15": milestones["pop_15"],
            "Settlement has 8 innovations": milestones["innovations_8"],
            "Population reaches 0": milestones["game_over"],
            "Not Victorious against Nemesis": {"sort_order": 4, "story_event": "Game Over"},
        },
        "nemesis_monsters": {"Butcher": [u'Lvl 1'], },
        "timeline": [
            {"year": 0, "settlement_event": ["First Day"]},
            {"year": 1, "story_event": ["The Pool and the Sun"]},
            {"year": 2, "story_event": ["Endless Screams"]},
            {"year": 3, },
            {"year": 4, "story_event": ["Sun Dipping"]},
            {"year": 5, "story_event": ["The Great Sky Gift"]},
            {"year": 6, },
            {"year": 7, "story_event": ["Phoenix Feather"]},
            {"year": 8, }, {"year": 9, },
            {"year": 10, "story_event": ["Birth of Color"]},
            {"year": 11, "story_event": ["Principle: Conviction"]},
            {"year": 12, "story_event": ["Sun Dipping"]},
            {"year": 13, "story_event": ["The Great Sky Gift"]},
            {"year": 14, }, {"year": 15, }, {"year": 16, }, {"year": 17, }, {"year": 18, },
            {"year": 19, "story_event": ["Sun Dipping"]},
            {"year": 20, "story_event": ["Final Gift"]},
            {"year": 21, "nemesis_encounter": ["Nemesis Encounter: Kings Man Level 2"]},
            {"year": 22, "nemesis_encounter": ["Nemesis Encounter: Butcher Level 3"]},
            {"year": 23, "nemesis_encounter": ["Nemesis Encounter: Kings Man Level 3"]},
            {"year": 24, "nemesis_encounter": ["Nemesis Encounter: The Hand Level 3"]},
            {"year": 25, "story_event": ["The Great Devourer"]},
            {"year": 26, }, {"year": 27, }, {"year": 28, }, {"year": 29, }, {"year": 30, }, {"year": 31, },
            {"year": 32, }, {"year": 33, }, {"year": 34, }, {"year": 35, }, {"year": 36, },
            {"year": 37, }, {"year": 38, }, {"year": 39, }, {"year": 40, },
        ],
    },

    "People of the Stars": {
        "expansions": ["Dragon King"],
        "always_available": ["Throne","Dragon Speech","Radiating Orb"],
        "forbidden": ["Lantern Hoard", "Language","Lantern Oven","Clan of Death","Family", "Dragon Armory"],
        "always_available_nemesis": "The Tyrant",
        "founder_epithet": "Foundling",
        "replaced_story_events": {
            "Bold": "Awake",
            "Insight": "Awake",
        },
        "new_survivor_additional_attribs": {
            "constellation": None,
            "constellation_traits": [],
        },
        "survivor_attribs": ["Scar","Noble surname","Reincarnated surname"],
        "special_rules": [
            {"name": "Removed Story Events", "desc": "If an event or card would cause you to add/trigger <b>Hands of Heat</b>, <b>Regal Visit</b>, <b>Armored Strangers</b>, <b>Watched</b>, or <b>Nemesis Encounter - Watcher</b>, do nothing instead.", "bg_color": "673AB7", "font_color": "FFF"},
#            {"name": "Removed Innovations", "desc": "Remove the following innovations from the pool of possible innovations: <b>Language</b>, <b>Lantern Oven</b>, <b>Family</b>, and <b>Clan of Death</b>.", "bg_color": "4527A0", "font_color": "FFF"},
        ],
        "principles": {
            # custom new life principle
            "New Life": principles["new_life"],
            "Death": principles["death"],
            "Society": principles["society"],
            "Conviction": principles["conviction"],
        },
        "milestones": {
            "First child is born": milestones["first_child"],
            "First time death count is updated": milestones["first_death"],
            "Population reaches 15": milestones["pop_15"],
            "Population reaches 0": milestones["game_over"],
        },
        "nemesis_monsters": {"Butcher": [u'Lvl 1'], "King's Man": [u'Lvl 1'], "The Hand": [u'Lvl 1'],},
        "timeline": [
            {"year": 0, "settlement_event": ["First Day"]},
            {"year": 1, "story_event": ["The Foundlings"]},
            {"year": 2, "story_event": ["Endless Screams"]},
            {"year": 3, },
            {"year": 4, "nemesis_encounter": ["Nemesis Encounter - Dragon King Human Lvl 1"]},
            {"year": 5, "story_event": ["Midnight's Children"]},
            {"year": 6, },
            {"year": 7, "story_event": ["Phoenix Feather"]},
            {"year": 8, },
            {"year": 9, "nemesis_encounter": ["Nemesis Encounter - Dragon King Human Lvl 2"]},
            {"year": 10, "story_event": ["Unveil the Sky"]},
            {"year": 11, },
            {"year": 12, "story_event": ["Principle: Conviction"]},
            {"year": 13, "nemesis_encounter": ["Nemesis Encounter - Butcher Lvl 2"]},
            {"year": 14, }, {"year": 15, },
            {"year": 16, "nemesis_encounter": ["Nemesis Encounter - Lvl 2"]},
            {"year": 17, }, {"year": 18, },
            {"year": 19, "nemesis_encounter": ["Nemesis Encounter - Dragon King Human Lvl 3"]},
            {"year": 20, "story_event": ["The Dragon's tomb"]},
            {"year": 21, }, {"year": 22, },
            {"year": 23, "nemesis_encounter": ["Nemesis Encounter - Lvl 3"]},
            {"year": 24, },
            {"year": 25, "nemesis_encounter": ["Nemesis Encounter - Death of the Dragon King"]},
            {"year": 26, }, {"year": 27, }, {"year": 28, }, {"year": 29, }, {"year": 30, }, {"year": 31, },
            {"year": 32, }, {"year": 33, }, {"year": 34, }, {"year": 35, }, {"year": 36, },
            {"year": 37, }, {"year": 38, }, {"year": 39, }, {"year": 40, },
        ],
    },
}


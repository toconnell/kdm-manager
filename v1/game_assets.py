#!/usr/bin/env python

#
#   Only game_asset dictionaries belong in this file. Do not add any methods or
#       other helpers here. Those all belong in models.py
#

abilities_and_impairments = {
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
    "Permanent Red Affinity": {
        "expansion": "Sunstalker",
        "type": "ability",
        "desc": '<font id="Caratosis">&#x02588;</font>',
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
        "desc": """At the Aftermath, <font class="kdm_font">g</font> <b>King's Curse</b>.""",
        "max": 1,
    },
    "Twilight Sword": {
        "type": "curse",
        "desc": "You may select <b>Twilight Sword</b> as a weapon proficiency type. This weapon may not be removed from your great grid for any reason. When you die, archive your <b>Twilight Sword</b> card.",
        "max": 1,
    },
    "Gender Swap": {
        "type": "curse",
        "desc": "You own the <b>Belt of Gender Swap</b>, it will always take one space in your gear grid and while it is there, your gender is reversed.",
        "reverse_sex": True,
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
        "desc": 'When you both <b>depart</b>, gain +2 survival. While adjacent to your partner, gain +1 strength. Partners may only nominate each other for <img class="icon" src="http://media.kdm-manager.com/icons/trigger_story_event.png" /> <b>Intimacy</b>. When a partner dies, the remaining partner gains a random disorder and loses this ability.',
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
    },
    "Legendcaller": {
        "type": "ability",
        "desc": 'Once a lifetime, on a hunt board space after <b>Overwhelming Darkness</b>, in place of rolling a random hunt event, use "53" as your result.',
        "max": 1,
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
    },
    "Cancerous Illness": {
        "type": "impairment",
        "desc": "You cannot gain survival.",
        "max": 1,
    },
    "Dream of the Beast" : {
        "type": "ability",
        "desc": "1 permanent red affinity.",
        "max": 1,
        "related": ["Caratosis", "Red Life Exchange"],
    },
    "Caratosis" : {
        "type": "ability",
        "desc": 'For each <font color="red">red</font> affinity you have, 1 of your attack rolls hits automatically each attack.',
        "max": 1,
        "related": ["Dream of the Beast", "Red Life Exchange"],
    },
    "Red Life Exchange" : {
        "type": "ability",
        "desc": "In the <b>Aftermath</b>, gain 3 additional Hunt XP. You may not place <b>other</b> gear in your grid. Gain +1 permanent strength with each <b>Age</b> milestone. When you retire, you cease to exist.",
        "max": 1,
        "related": ["Caratosis", "Dream of the Beast"],
    },
    "Dream of the Crown" : {
        "type": "ability",
        "desc": "1 permanent green affinity.",
        "max": 1,
        "related": ["Dormenatus", "Green Life Exchange"],
    },
    "Dormenatus" : {
        "type": "ability",
        "desc": 'When you <b>depart</b>, gain +1 to every hit location for each <font color="green">green</font> affinity you have.',
        "max": 1,
        "related": ["Dream of the Crown", "Green Life Exchange"],
    },
    "Green Life Exchange" : {
        "type": "ability",
        "desc": "In the <b>Aftermath</b>, gain 3 additional Hunt XP. You may not place <b>other</b> gear in your grid. Gain +1 permanent evasion with each <b>Age</b> milestone. When you retire, you cease to exist.",
        "max": 1,
        "related": ["Dream of the Crown", "Dormenatus"],
    },
    "Dream of the Lantern" : {
        "type": "ability",
        "desc": "1 permanent blue affinity.",
        "max": 1,
        "related": ["Lucernae", "Blue Life Exchange"],
    },
    "Lucernae" : {
        "type": "ability",
        "desc": 'For every <font color="blue">blue</font> affinity you have, your ranged weapons gain this amount of <b>range</b> and your melee weapons gain this amount of <b>reach</b>.',
        "max": 1,
        "related": ["Dream of the Lantern", "Blue Life Exchange"],
    },
    "Blue Life Exchange" : {
        "type": "ability",
        "desc": "In the <b>Aftermath</b>, gain 3 additional Hunt XP. You may not place <b>other</b> gear in your grid. Gain +1 permanent luck with each <b>Age</b> milestone. When you retire, you cease to exist.",
        "max": 1,
        "related": ["Dream of the Lantern", "Lucernae"],
    },
    "Marrow Hunger": {
        "type": "impairment",
        "desc": "When the Murder or Skull Eater settlement events are drawn, this survivor is nominated.",
        "max": 1,
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
}


disorders = {
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


epithets = {
    "Eye Patch Badass": {},
    "Scarred": {},
    "Plague-bearer": {},
    "Infected": {},
    "Sun Eater": {},
    "Child of the Sun": {},
    "Purified": {},
    "Lord of War": {},
    "Warlord": {},
    "Dancer": {},
    "Brawler": {},
    "Monster Worshipper": {},
    "Twin": {},
    "Spelunker of Death": {},
    "Farmer": {},
    "Maw Runner": {},
    "Bug Man": {},
    "Met the Bug Man": {},
    "Vomit-soaked": {},
    "Coward": {},
    "Foolish": {},
    "Shining": {},
    "Hero": {},
    "Entomophile": {},
    "Beetle-kin": {},
    "Beetle-brain": {},
    "Round Stone Trainer": {},
    "Bewitched": {},
    "Witness": {},
    "Gorm Bait": {},
    "Digested": {},
    "Braved the Storm": {},
    "White-haired":{},
    "White Wolf":{},
    "The White":{},
    "The Black":{},
    "Eunuch": {},
    "Broke the Silence": {},
    "Triathlete":{},
    "Undisputed boss of the settlement": {},
    "The Fertile": {},
    "Defiled": {},
    "Occult": {},
    "Living Sacrifice": {},
    "Sacrificed": {},
    "Corpsegrinder": {},
    "Ate the Fruit": {},
    "Silence Breaker": {},
    "The Silent": {},
    "Father of Words": {},
    "Forsaker": {},
    "Forbidden Dancer": {},
    "Endless Arguer": {},
    "Monster Teeth": {},
    "Metal Jaw": {},
    "Haunted": {},
    "Skull Eater": {},
    "Rival": {},
    "Warborn": {},
    "Shape Shifter": {},
    "The Wanderer": {},
    "One-eyed": {},
    "The Blind": {},
    "The Dead": {},
    "Berserker": {},
    "The Wolf": {},
    "Thunderer": {},
    "Swift-footed": {},
    "The Chef": {},
    "Iron-hearted": {},
    "Man-slaying": {},
    "Fast Runner": {},
    "The Doomed": {},
    "The Brave": {},
    "The Insane": {},
    "The Mad": {},
    "Huntress": {"sex": "F", },
    "Branded by the Lantern": {},
    "Hunter": {},
    "Straggler": {},
    "Dreamer": {},
    "Monster": {},
    "The Destroyer": {},
    "Patriarch": {"sex": "M", },
    "Matriarch": {"sex": "F", },
    "Experimented with Lanterns": {},
    "Dimmed by the Lantern": {},
    "Masticated": {},
    "Death Taster": {},
    "Pure Warrior": {},
    "Cursed": {},
    "Twilight Knight": {},
    "Swamp Explorer": {},
    "Lantern Experimenter": {},
    "Speaker of the First Words": {},
    "Voice of Reason": {},
    "Bone Witch": {},
    "Murdered": {"sex": "F", },
    "Murderer": {},
    "Lucernae": {},
    "Caratosis": {},
    "Dormenatus": {},
}


fighting_arts = {
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
    "Rare Gear": {
        "color": "9DC209",
    },
    "Unique Items": {
        "font_color": "FFF",
        "color": "FF00FF",
    },
    "Lantern Hoard": {
        "consequences": ["Bone Smith", "Skinnery", "Organ Grinder", "Catarium", "Plumery", "Exhausted Lantern Hoard", "Mask Maker"],
        "endeavors": {
            "Innovate": {"cost": 1, "desc": "Once per settlement phase, you may spend the listed resources (1 Bone, 1 Organ, 1 Hide) to draw 2 innovation cards. Keep 1 and return the other to the deck."},
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
    ("Quiver And Sunstring", "Quiver and Sunstring"),
    ("Sun Lure And Hook", "Sun Lure and Hook"),
	("Arm Of The First Tree", "Arm of the First Tree"),
    ("Dbk Errant Badge", "DBK Errant Badge"),
    ("Finger Of God", "Finger of God"),
    ("Eye Of Cat", "Eye of Cat"),
}

cursed_items = {
    "Belt of Gender Swap": {"ability": "Gender Swap"},
    "Real Helm": {"ability": "King's Curse",},
    "Real Faulds": {"ability": "King's Curse",},
    "Real Gauntlets": {"ability": "King's Curse",},
    "Real Greaves": {"ability": "King's Curse",},
    "Real Plackart": {"ability": "King's Curse",},
    "Thunder Maul": {},
    "Twilight Sword": {"ability": "Twilight Sword"},
    "Hideous Disguise": {"expansion": "Lion Knight", "ability": "Hideous Disguise"},
	"Death Mehndi": {"expansion": "Lion God", "ability": "Death Mehndi"}
}

items = {
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
    "Belt Of Gender Swap": {
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
    "Vibrant Lantern": {
        "location": "Rare Gear",
    },
    "Dying Lantern": {
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
        "resource_family": ["iron"],
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
}


innovations = {
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
        "new_survivor": {"Strength": 1},
    },
    "Romantic": {
        "type": "principle",
        "survival_limit": 1,
        "settlement_buff": "You may innovate one additional time during the settlement phase. In addition, all current and newborn survivors gain +1 understanding.",
        "survivor_buff": "All current and newborn survivors gain +1 understanding.",
        "new_survivor": {"Understanding": 1},
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
        "settlement_buff": "When rolling on the Intimacy story event, roll twice and pick the lowest result. All newborn survivors gain +1 Strength.",
        "survivor_buff": "All newborn survivors gain +1 Strength.",
        "new_survivor": {"Strength": 1},
    },
    "Clan of Death": {
        "type": "home",
        "survivor_buff": "All newborn survivors gain <b>+1 Accuracy</b>, <b>+1 Strength</b> and <b>+1 Evasion</b>.",
        "new_survivor": {"Strength": 1, "Accuracy": 1, "Evasion": 1},
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
        "consequences": ["Nightmare Training", "Storytelling", ],
        "survival_limit": 1,
        "settlement_buff": "When a survivor innovates, draw an additional 2 Innovation Cards to choose from.",
    },
    "Hovel": {
        "type": "home",
        "consequences": ["Partnership", "Family", "Bed", "Shadow Dancing"],
        "departure_buff": "Departing survivors gain +1 survival.",
        "survival_limit": 1,
    },
    "Storytelling": {
        "type": "education",
        "consequences": ["Records"],
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
        "new_survivor": {"hunt_xp": 2, "survival": 2},
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

# pre-fab survivors
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
        "attribs": {"Movement": 1, "disorders": ["Hyperactive"], "sex": "F"},
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


# Monster assets

quarries = {
    "White Lion":               {"sort_order": 1, "tokens": ["LION","WHITE"]},
    "Gorm":                     {"sort_order": 2, "tokens": ["GORM"], "expansion": "Gorm"},
    "Screaming Antelope":       {"sort_order": 3, "tokens": ["ANTELOPE","SCREAMING"]},
    "Phoenix":                  {"sort_order": 4, "tokens": ["PHOENIX","PHONIEX"]},
    "Sunstalker":               {"sort_order": 5, "tokens": ["STALKER","SUNSTALKER"], "expansion": "Sunstalker"},
    "Dung Beetle Knight":       {"sort_order": 6, "tokens": ["DUNG","BEETLE","DBK"], "expansion": "Dung Beetle Knight"},
	"Lion God":                 {"sort_order": 7, "tokens": ["LIONGOD","GOD"], "expansion": "Lion God"},
    "Beast Of Sorrow":          {"sort_order": 10, "no_levels": True, "tokens": ["SORROW","BEAST"]},
    "Great Golden Cat":         {"sort_order": 11, "no_levels": True, "tokens": ["CAT"]},
    "Mad Steed":                {"sort_order": 12, "no_levels": True, "tokens": ["MAD","STEED"]},
    "Golden Eyed King":         {"sort_order": 13, "no_levels": True, "tokens": ["GOLDEN","EYED"]},
    "Old Master":               {"sort_order": 14, "no_levels": True, "tokens": ["MASTER"], "expansion": "Dung Beetle Knight"},
}

nemeses = {
    "Butcher":              {"sort_order": 20, "tokens": ["BUTCHER","BUTCHEE"]},
    "King's Man":           {"sort_order": 21, "tokens": ["KINGSMAN","KINGS", "KING'S"]},
    "Lion Knight":          {"sort_order": 22, "tokens": ["LK"], "expansion": "Lion Knight"},
    "The Hand":             {"sort_order": 23, "tokens": ["HAND"]},
    "Ancient Sunstalker":   {"sort_order": 30, "no_levels": True, "tokens": ["ANCIENT"], "expansion": "Sunstalker", "add_to_timeline_controls_at": 25, "campaign": "People of the Sun"},
    "Watcher":              {"sort_order": 31, "no_levels": True, "tokens": ["WATCHER"], "add_to_timeline_controls_at": 20, "campaign": "People of the Lantern"},
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
    "Katana": {"expansion": "Sunstalker"},
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

expansions = {
    "Beta Challenge Scenarios": {
        "special_rules": [
        {"name": "Survival Limit Warning!", "desc": "Survival Limit is not automatically enforced by the Manager when Beta Challenge Scenarios content is enabled.", "bg_color": "F87217", "font_color": "FFF"},
        ],
    },
    "Gorm": {
        "always_available": ["Gormery", "Gormchymist", "Nigredo"],
        "timeline_add": [
            {"ly": 1, "type": "story_event", "name": "The Approaching Storm"},
            {"ly": 2, "type": "settlement_event", "name": "Gorm Climate"},
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
        "nickname": "lk",
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
        "existing_campaign_only": True,
        "timeline_add": [
            {"ly": 8, "type": "story_event", "name": "Promise Under the Sun"},
        ],
        "survivor_attribs": ["Purified","Sun Eater","Child of the Sun"],
    },
}

campaigns = {
    "People of the Lantern": {
        "default": True,
        "expansions": [],
        "always_available": ["Lantern Hoard", "Language"],
        "principles": {
            "New Life":     {"sort_order": 0, "show_controls": ['"First child is born" in self.settlement["milestone_story_events"]'], "milestone": "First child is born", "options": ["Protect the Young","Survival of the Fittest"]},
            "Death":        {"sort_order": 1, "show_controls": ['int(self.settlement["death_count"]) >= 1'], "milestone": "First time death count is updated", "options": ["Cannibalize","Graves"]},
            "Society":      {
                "sort_order": 2,
                "milestone": "Population reaches 15",
                "options": ["Collective Toil","Accept Darkness"],
                "show_controls": ['int(self.settlement["population"]) >= 15'],
            },
            "Conviction":   {"sort_order": 3, "options": ["Barbaric","Romantic"], "show_controls": ['int(self.settlement["lantern_year"]) >= 12'],},
        },
        "milestones": {
            "First child is born": {
                "sort_order": 0,
                "story_event": "Principle: New Life",
            },
            "First time death count is updated": {
                "sort_order": 1,
                "story_event": "Principle: Death",
                "add_to_timeline": 'int(self.settlement["death_count"]) >= 1',
            },
            "Population reaches 15": {
                "sort_order": 2,
                "story_event": "Principle: Society",
                "add_to_timeline": 'int(self.settlement["population"]) >= 15',
            },
            "Settlement has 5 innovations": {
                "sort_order": 3,
                "story_event": "Hooded Knight",
                "add_to_timeline": 'len(self.settlement["innovations"]) >= 5',
            },
            "Population reaches 0": {
                "sort_order": 4,
                "story_event": "Game Over",
                "add_to_timeline": 'int(self.settlement["population"]) == 0 and int(self.settlement["lantern_year"]) >= 1',
            },
        },
        "timeline": [
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
        ],
        "nemesis_monsters": {"Butcher": [], },
    },
    "People of the Sun": {
        "expansions": ["Sunstalker"],
        "forbidden": ["Leader"],
        "principles": {
            "New Life":     {"sort_order": 0, "show_controls": ["True"], "options": ["Survival of the Fittest"]},
            "Death":        {"sort_order": 1, "show_controls": ['int(self.settlement["death_count"]) >= 1'], "milestone": "First time death count is updated", "options": ["Cannibalize","Graves"]},
            "Society":      {
                "sort_order": 2,
                "milestone": "Population reaches 15",
                "options": ["Collective Toil","Accept Darkness"],
                "show_controls": ['int(self.settlement["population"]) >= 15'],
            },
            "Conviction":   {"sort_order": 3, "options": ["Barbaric","Romantic"], "show_controls": ['int(self.settlement["lantern_year"]) >= 11'],},
        },
        "milestones": {
            "First time death count is updated": {
                "sort_order": 0,
                "story_event": "Principle: Death",
                "add_to_timeline": 'int(self.settlement["death_count"]) >= 1',
                "principle": {
                    "desc": "Death Principle",
                    "options": ["Cannibalize","Graves"],
                },
            },
            "Population reaches 15": {
                "sort_order": 1,
                "story_event": "Principle: Society",
                "add_to_timeline": 'int(self.settlement["population"]) >= 15',
                "principle": {
                    "desc": "Society Principle",
                    "options": "",
                },
            },
            "Settlement has 8 innovations": {
                "sort_order": 2,
                "story_event": "Edged Tonometry",
                "add_to_timeline": 'len(self.settlement["innovations"]) >= 8',
            },
            "Population reaches 0": {
                "sort_order": 3,
                "story_event": "Game Over",
                "add_to_timeline": 'int(self.settlement["population"]) == 0 and int(self.settlement["lantern_year"]) >= 1',
            },
            "Not Victorious against Nemesis": {"sort_order": 4, "story_event": "Game Over"},
        },
        "timeline": [
            {"year": 0, "settlement_event": ["First Day"]},
            {"year": 1, "story_event": ["The Pool and the Sun"]},
            {"year": 2, "story_event": ["Endless Screams"]},
            {"year": 3, },
            {"year": 4, "story_event": ["Sun Dipping"]},
            {"year": 5, "story_event": ["The Great Sky Gift"]},
            {"year": 6, },
            {"year": 7, "story_event": ["Phoenix Feather"]},
            {"year": 8, "story_event": ["Promise Under the Sun"]},
            {"year": 9, },
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
        "nemesis_monsters": {"Butcher": [u'Lvl 1'], },
    },
}

story_events = {
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
}


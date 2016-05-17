#!/usr/bin/env python

#
#   Only game_asset dictionaries belong in this file. Do not add any methods or
#       other helpers here. Those all belong in models.py
#

abilities_and_impairments = {
    "King's Curse": {
        "type": "impairment",
        "desc": """At the Aftermath, <font class="kdm_font">g</font> <b>King's Curse</b>.""",
    },
    "Crystal Skin": {
        "type": "ability",
        "desc": "You cannot place armor in your gear grid. When you <b>depart</b>, gain <b>2</b> to all hit locations. Suffer -1 to the result of all severe injury rolls.",
    },
    "Twilight Sword": {
        "type": "impairment",
        "desc": "You may select <b>Twilight Sword</b> as a weapon proficiency type. This weapon may not be removed from your great grid for any reason. When you die, archive your <b>Twilight Sword</b> card.",
        "max": 1,
    },
    "Gender Swap": {
        "type": "impairment",
        "desc": "You own the <b>Belt of Gender Swap</b>, it will always take one space in your gear grid and while it is there, your gender is reversed.",
        "reverse_sex": True,
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
    "Specialization - Katar": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "When attacking with a Katar, cancel reactions on the first selected hit location.",
    },
    "Mastery - Katar": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "If you are a Katar Master, gain a <i>+1 evasion</i> token on a <b>perfect hit</b> with a katar. When you are knocked down, remove all +1 evasion tokens.",
    },
    "Specialization - Bow": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "When attacking with a bow, you may reroll any misses once. Limit, once per attack",
    },
    "Mastery - Bow": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "If you are a Bow Master, all Bows in your gear grid gain <b>Deadly 2</b>. In addition, ignore <b>cumbersome</b> on all Bows.",
    },
    "Specialization - Twilight Sword": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "This sentient sword improves as it's used. Gain the effect as proficiency rank increases. Rank 2: Ignore <b>Cumbersome</b> on Twilight Sword. Rank 4: When attacking with the Twilight Sword, ignore <b>slow</b> and gain +2 speed. Rank 6: Twilight Sword gains <b>Deadly</b>.",
    },
    "Mastery - Twilight Sword": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "Any Survivor who attains Twilight Sword Mastery leaves the settlement forever in pursuit of a higher purpose. Remove them from the settlement's population. You may place the master's Twilight Sword in another survivor's gear grid or archive it.",
    },
    "Specialization - Axe": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "When attacking with an axe, if your wound attempt fails, you may ignore it and attempt to wound the selected hit location again. Limit, once per attack.",
    },
    "Mastery - Axe": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "When an Axe Master wounds a monster with an axe at a location with a persistent injury, that wound becomes a critical wound.",
    },
    "Specialization - Spear": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "When attacking with a spear, if you draw a <b>trap</b>, roll 1d10. On a 7+, cancel the <b>trap</b>. Discard it, then reshuffle the hit location discard into the hit location deck and draw a new card. Limit, once per round.",
    },
    "Mastery - Spear": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "Whenever a Spear Master hits a monster with a Separ, they may spend 1 survival to gain the Priority Target token. If they made the hit from directly behind another survivor, that survivor gains the Priority Target token instead.",
    },
    "Specialization - Club": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "All clubs in your gear grid gain <b>paired</b>. Cannot use this with two-handed clubs.",
    },
    "Mastery - Club": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "If you are a Club Master, all Clubs in your gear grid gain <b>Savage</b>. On a <b>Perfect hit</b> with a Club, gain <i>+3 strength</i> until the end of the attack.",
    },
    "Specialization - Fist & Tooth": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "You may stand (if knocked down) at the start of the monster's turn or the survivor's turn. Limit once per round.",
    },
    "Mastery - Fist & Tooth": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "While a survivor is a Fist & Tooth Master, they gain <i>+2 permanent accuracy</i> and <i>+2 permanent strength</i> (they receive this bonus even when not attacking with Fist and Tooth).",
    },
    "Specialization - Grand Weapon": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "When attacking with a grand weapon, gain <i>+1 accuracy</i>.",
    },
    "Mastery - Grand Weapon": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "When a Grand Weapon Master perfectly hits with a grand weapon, cancel all reactions for that attack.",
    },
    "Specialization - Whip": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "When you wound with a whip, instead of moving the top card of the AI deck into the wound stack, you may move the top card of the AI discard pile. Limit once per attack.",
    },
    "Mastery - Whip": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "Whip Masters gain <i>+5 strength</i> when attacking with a Whip.",
    },
    "Mastery - Shield": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "When a Shield Master is adjacent to a survivor that is targeted by a monster, they may swap spaces on the baord with the survivor and become the target instead. The master must have a shield to perform this.",
    },
    "Specialization - Shield": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "While a shield is in your gear grid, you are no longer knocked down after <b>collision</b> with a monster. While a shield is in your gear grid, add <b>1</b> to all hit locations.",
    },
    "Specialization - Dagger": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "When attacking with a Dagger, if a wound attempt fails, after performing any reactions, you may discard another drawn hit location card to attempt to wound that hit location again. Limit, once per attack.",
    },
    "Mastery - Dagger": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "After a wounded hit location is discarded, a Dagger Master who is adjacent to the attacker and the wounded monster may spend 1 survival to re-draw the wounded hit location and attempt to wound with a dagger. Treat monster reactions on the re-drawn hit location card normally.",
    },
    "Specialization - Sword": {
        "type": "weapon proficiency",
        "max": 1,
        "desc": "When attacking with a sword, after drawing hit locations, make a wound attempt and then select a hit location to resolve with that result. Limit, once per attack.",
    },
    "Mastery - Sword": {
        "type": "weapon proficiency",
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
    "Intracranial hemmorhage": {
        "type": "impairment",
        "desc": "You can no longer use or gain any survival. This injury is permanent and can be recorded once.",
        "cannot_spend_survival": True,
        "max": 1,
    },
    "Deaf": {
        "type": "impairment",
        "desc": "Suffer -1 permanent Evasion. This injury is permanent and can be recorded once.",
        "Evasion": -1,
        "max": 1,
    },
    "Blind": {
        "type": "impairment",
        "desc": "Suffer -1 permanent Accuracy. This injury is permanent and can be recorded twice.",
        "Accuracy": -1,
        "max": 2,
    },
    "Concussion": {
        "type": "impairment",
        "desc": "Your brain is scrambled like an egg. Gain a random disorder.",
    },
    "Shattered jaw": {
        "type": "impairment",
        "desc": "You can no longer <b>consume</b> or be affected by events requiring you to <b>consume</b>. You can no longer <b>encourage</b>. This injury is permanent and can be recorded once.",
        "survival_actions_disabled": ["Encourage"],
        "max": 1,
    },
    "Dismembered Arm": {
        "type": "impairment",
        "desc": "You can no longer activate two-handed weapons. This injury is permanent, and can be recorded twice. A survivor with two <b>dismembered arm</b> severe injuries cannot activate any weapons.",
        "max": 2,
    },
    "Ruptured muscle": {
        "type": "impairment",
        "desc": "You can no longer activate fighting arts. This injury is permanent and can be recorded once.",
        "cannot_use_fighting_arts": True,
        "max": 1,
    },
    "Contracture": {
        "type": "impairment",
        "desc": "Suffer -1 permanent Accuracy. This injury is permanent and can be recorded multiple times.",
        "Accuracy": -1,
    },
    "Broken arm": {
        "type": "impairment",
        "desc": "Suffer -1 permanent Accuracy and -1 permanent Strength. This injury is permanent and can be recorded twice.",
        "Accuracy": -1,
        "Strength": -1,
        "max": 2,
    },
    "Spiral fracture": {
        "type": "impairment",
        "desc": "Skip the next hunt.",
        "skip_next_hunt": True,
    },
    "Dislocated shoulder": {
        "type": "impairment",
        "desc": "You cannot activate two-handed or <b>paired</b> weapons or use <b>block</b> until showdown ends.",
    },
    "Gaping chest wound": {
        "type": "impairment",
        "desc": "Suffer -1 permanent Strength. This injury is permanent and can be recorded multiple times.",
        "Strength": -1,
    },
    "Disemboweled": {
        "type": "impairment",
        "desc": "Skip the next hunt. If you suffer <b>disemboweled</b> during a showdown, at least one other survivor must live to the end of the showdown to carry you back to the settlement. Otherwise, at the end of the showdown, you are lost. Dead.",
        "skip_next_hunt": True,
    },
    "Ruptured spleen": {
        "type": "impairment",
        "desc": "Skip the next hunt.",
        "skip_next_hunt": True,
    },
    "Destroyed back": {
        "type": "impairment",
        "desc": "Suffer -2 permanent movement. You can no longer activate any gear that has 2+ Strength. This injury is permanent and can be recorded once.",
        "Movement": -2,
        "max": 1,
    },
    "Broken rib": {
        "type": "impairment",
        "desc": "Suffer -1 permanent speed. This injury is permanent, and can be recorded multiple times.",
        "Speed": -1,
    },
    "Intestinal prolapse": {
        "type": "impairment",
        "desc": "You can no longer equip any gear on your waist, as it is too painful to wear. This injury is permanent, and can be recorded once.",
    },
    "Warped Pelvis": {
        "type": "impairment",
        "desc": "Suffer -1 permanent luck. This injury is permanent and can be recorded multiple times.",
        "Luck": -1,
    },
    "Destroyed genitals": {
        "type": "impairment",
        "desc": "You cannot be nominated for the Intimacy story event. This injury is permanent and can be recorded once.",
    },
    "Slashed back": {
        "type": "impairment",
        "desc": "You cannot <b>surge</b> until showdown ends.",
    },
    "Broken hip": {
        "type": "impairment",
        "desc": "You can no longer <b>dodge</b>. Suffer -1 permanent movement. This injury is permanent and can be recorded once.",
        "Movement": -1,
        "max": 1,
        "survival_actions_disabled": ["Dodge"],
    },
    "Bruised tailbone": {
        "type": "impairment",
        "desc": "You cannot <b>dash</b> until showdown ends.",
    },
    "Dismembered leg": {
        "type": "impairment",
        "desc": "You suffer -2 permanent movement, and can no longer <b>dash</b>. This injury is permanent and can be recorded twice. A survivor with two <b>dismembered leg</b> severe injuries has lost both of their legs and must retire at the end of the next showdown or settlement phase.",
        "survival_actions_disabled": ["Dash"],
        "Movement": -2,
        "max": 2,
    },
    "Torn Achilles Tendon": {
        "type": "impairment",
        "desc": "Until the end of the showdown, whenever you suffer light, heavy, or severe injury, you are also knocked down. Skip the next hunt.",
        "skip_next_hunt": True,
    },
    "Torn muscle": {
        "type": "impairment",
        "desc": "You cannot <b>dash</b> until he showdown ends. Skip the next hunt.",
        "skip_next_hunt": True,
    },
    "Hamstrung": {
        "type": "impairment",
        "desc": "You can no longer use any fighting arts or abilities. This injury is permanent and can be recorded once.",
        "max": 1,
        "cannot_use_fighting_arts": True,
    },
    "Broken leg": {
        "type": "impairment",
        "desc": "Suffer -1 permanent movement. This injury is permanent, and can be recorded twice.",
        "Movement": -1,
        "max": 2,
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
    }
}


disorders = {
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
    "Brawler": {},
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
        "desc": "Whenever you attack, you may discard any number of Battle Pressure hit locations drawn and draw an equal number of new hit locations. Whenever you attack, after drawing hit locations, but before rolling to wound, you may choose one hit location drawn and disacrd it to draw a new hit location. Traps will cancel these effects.",
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
        "always_available": True,
        "consequences": ["Bone Smith", "Skinnery", "Organ Grinder", "Catarium", "Plumery", "Exhausted Lantern Hoard", "Mask Maker","Gormery","Gormchymist"],
    },
    "Bone Smith": {
        "color": "e3dac9",
        "consequences": ["Weapon Crafter"],
    },
    "Skinnery": {
        "color": "FFCBA4",
        "consequences": ["Leather Worker"],
    },
    "Organ Grinder": {
        "color": "B58AA5",
        "consequences": ["Stone Circle"],
    },
    "Blacksmith": {
        "requires": ("innovations", "Scrap Smelting"),
        "color": "625D5D",
        "font_color": "FFF",
        "consequences": [],
    },
    "Stone Circle": {
        "color": "835C3B",
        "font_color": "FFF",
    },
    "Leather Worker": {
        "color": "7F462C",
        "font_color": "FFF",
        "consequences": [],
    },
    "Weapon Crafter": {
        "color": "E1D4C0",
        "consequences": [],
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
        "consequences": [],
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
        "always_available": True,
        "color": "C9CE62",
    },
}

# boy, this is a really good example of why you don't try to make dictionary
# keys out of your raw asset values. Fuck you, Poots: next time I'm using bson
# object keys or some shit
item_normalization_exceptions = {
    ("Dbk Errant Badge", "DBK Errant Badge"),
    ("Finger Of God", "Finger of God"),
    ("Eye Of Cat", "Eye of Cat"),
}

items = {
    "Riot Mace": {
        "location": "Gormery",
    },
    "Rib Blade": {
        "location": "Gormery",
    },
    "Regeneration Suit": {
        "location": "Gormery",
    },
    "Pulse Lantern": {
        "location": "Gormery",
    },
    "Knuckle Shield": {
        "location": "Gormery",
    },
    "Greater Gaxe": {
        "location": "Gormery",
    },
    "Gorn": {
        "location": "Gormery",
    },
    "Gaxe": {
        "location": "Gormery",
    },
    "Black Sword": {
        "location": "Gormery",
    },
    "Gorment Mask": {
        "location": "Gormery",
    },
    "Gorment Suit": {
        "location": "Gormery",
    },
    "Gorment Sleeves": {
        "location": "Gormery",
    },
    "Gorment Boots": {
        "location": "Gormery",
    },
    "Armor Spikes": {
        "location": "Gormery",
    },
    "Acid Tooth Dagger": {
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
    "Fairy Bottle": {
        "attribs": ["item","fragile","other"],
        "location": "Rare Gear",
    },
    "Scout's Tunic": {
        "attribs": ["armor","set","leather"],
        "location": "Rare Gear",
    },
    "Aya's Sword": {
        "attribs": ["weapon","melee","sword"],
        "location": "Rare Gear",
    },
    "Aya's Spear": {
        "attribs": ["weapon","melee","spear"],
        "location": "Rare Gear",
    },
    "Arm Of The First Tree": {
        "attribs": ["weapon","melee","club"],
        "location": "Rare Gear",
    },
    "Stone Arm": {
        "attribs": ["item","stone","heavy"],
        "location": "Rare Gear",
    },
    "Giant Stone Face": {
        "attribs": ["weapon","melee","grand","heavy","two-handed","stone"],
        "location": "Rare Gear",
    },
    "Petal Lantern": {
        "attribs": ["item","lantern","other"],
        "location": "Rare Gear",
    },
    "Piranha Helm": {
        "attribs": ["armor","set","rawhide"],
        "location": "Rare Gear",
    },
    "Cola Bottle Lantern": {
        "attribs": ["item","fragile","other"],
        "location": "Rare Gear",
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

}


innovations = {
    "Subterranean Agriculture": {
        "expansion": "Dung Beetle Knight",
        "type": "science",
        "endeavors": {
            'If <b>Black Harvest</b> is not on the timeline, <font class="kdm_font">g</font> <b>Underground Sow</b>.': 1,
            'If <b>Black Harvest</b> is on the timeline, you may spend 1 Preserved Caustic Dung to increase its rank by 1 to a maximum rank of 3. Limit, once per settlement phase.': 1,
        },
        "always_available": True,
    },
    "Round Stone Training": {
        "expansion": "Dung Beetle Knight",
        "type": "education",
        "endeavors": {"Train": 1},
        "always_available": True,
    },
    "Nigredo": {
        "expansion": "Gorm",
        "type": "science",
        "survival_limit": 1,
        "consequences": ["Albedo"],
        "endeavors": {"Nigredo": 1},
        "always_available": True,
    },
    "Albedo": {
        "expansion": "Gorm",
        "type": "science",
        "consequences": ["Citrinitas"],
        "endeavors": {"Albedo": 2},
    },
    "Citrinitas": {
        "expansion": "Gorm",
        "type": "science",
        "survival_limit": 1,
        "consequences": ["Rubedo"],
        "endeavors": {"Citrinitas": 3},
    },
    "Rubedo": {
        "expansion": "Gorm",
        "type": "science",
        "endeavors": {"Rubedo": 4},
    },
    "Graves": {
        "type": "principle",
        "milestone": "First time death count is updated",
        "settlement_buff": "All new survivors gain +1 understanding. When a survivor dies during the hunt or showdown phase, gain +2 Endeavors. When a survivor dies during the settlement phase, gain +1 Endeavor.",
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
        "endeavors": {"Death Ritual": 1},
    },
    "Scarification": {
        "type": "faith",
        "endeavors": {"Initiation": 1},
    },
    "Records": {
        "type": "education",
        "endeavors": {"Knowledge": 2},
    },
    "Shrine": {
        "type": "faith",
        "consequences": ["Sacrifice"],
        "endeavors": {"Armor Ritual": 1},
    },
    "Scrap Smelting": {
        "type": "science",
        "endeavors": {"Purification": 1},
    },
    "Cooking": {
        "type": "science",
        "consequences": [],
        "survival_limit": 1,
        "endeavors": {"Culinary Inspiration": 1},
    },
    "Paint": {
        "type": "art",
        "consequences": ["Pictograph", "Sculpture", "Face Painting"],
        "survival_action": "Dash",
    },
    "Drums": {
        "type": "music",
        "consequences": ["Song of the Brave", "Forbidden Dance"],
        "endeavors": {"Bone Beats": 1},
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
        "consequences": ["Partnership", "Family", "Bed"],
        "departure_buff": "Departing survivors gain +1 survival.",
        "survival_limit": 1,
    },
    "Storytelling": {
        "type": "education",
        "consequences": ["Records"],
        "survival_limit": 1,
        "endeavors": {"Tale as Old as Time": 2},
    },
    "Nightmare Training": {
        "type": "education",
        "endeavors": {"Train": 1},
        "consequences": ["Round Stone Training"],
    },
    "Momento Mori": {
        "type": "art",
        "endeavors": {"Momento Mori": 1},
    },
    "Face Painting": {
        "type": "art",
        "endeavors": {"Battle Paint": 1, "Founder's Eye": 1},
    },
    "Sculpture": {
        "type": "art",
        "consequences": ["Pottery"],
        "survival_limit": 1,
        "departure_buff": "Departing survivors gain +2 survival when they depart for a Nemesis Encounter.",
    },
    "Pictograph": {
        "type": "art",
        "consequences": ["Momento Mori"],
        "survivor_buff": "Anytime during the hunt or showdown phase, a survivor may <b>Run Away</b>.",
    },
    "Pottery": {
        "type": "art",
        "survival_limit": 1,
        "settlement_buff": "If the settlement loses all its resources, you may select up to two resources and keep them.",
    },
    "Heart Flute": {
        "type": "music",
        "endeavors": {"Devil's Melody": 1},
    },
    "Saga": {
        "type": "music",
        "survivor_buff": "All newborn survivors gain +2 hunt experience and +2 survival from knowing the epic.",
        "new_survivor": {"hunt_xp": 2, "survival": 2},
    },
    "Forbidden Dance": {
        "type": "music",
        "endeavors": {"Fever Dance": 1},
    },
    "Bed": {
        "type": "home",
        "survival_limit": 1,
        "endeavors": {"Rest": 1},
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
    "Partnership": {
        "type": "home",
        "always_available": True,
        "endeavors": {"Partner": 2},
    },
    "Bloodletting": {
        "type": "science",
        "endeavors": {"Breathing a Vein": 1},
    },
    "Language": {
        "type": "starting",
        "consequences": ["Hovel", "Inner Lantern", "Drums", "Paint", "Symposium", "Ammonia"],
        "survival_limit": 1,
        "survival_action": "Encourage",
        "always_available": True,
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
}


# Monster assets

quarries = {
    "White Lion":           {"sort_order": 1, "tokens": ["LION","WHITE"]},
    "Gorm":                 {"sort_order": 2, "tokens": ["GORM"], "expansion": "Gorm"},
    "Screaming Antelope":   {"sort_order": 3, "tokens": ["ANTELOPE","SCREAMING"]},
    "Dung Beetle Knight":   {"sort_order": 4, "tokens": ["DUNG","BEETLE","DBK"], "expansion": "Dung Beetle Knight"},
    "Old Master":           {"sort_order": 5, "tokens": ["MASTER"], "expansion": "Dung Beetle Knight"},
    "Phoenix":              {"sort_order": 6, "tokens": ["PHOENIX","PHONIEX"]},
    "Beast Of Sorrow":      {"sort_order": 7, "no_levels": True, "tokens": ["SORROW","BEAST"]},
    "Great Golden Cat":     {"sort_order": 8, "no_levels": True, "tokens": ["GOLDEN","CAT"]},
    "Mad Steed":            {"sort_order": 9, "no_levels": True, "tokens": ["MAD","STEED"]},
    "Golden Eyed King":     {"sort_order": 10, "no_levels": True, "tokens": ["GOLDEN","EYED","KING"]},
}

nemeses = {
    "Butcher":      {"sort_order": 15, "tokens": ["BUTCHER","BUTCHEE"]},
    "King's Man":   {"sort_order": 16, "tokens": ["MAN","KINGSMAN"]},
    "The Hand":     {"sort_order": 17, "tokens": ["HAND"]},
    "Watcher":      {"sort_order": 30, "no_levels": True, "tokens": ["WATCHER"]},
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


survival_actions = ["Dodge", "Encourage", "Surge", "Dash"]
survivor_attributes = ["Movement", "Accuracy", "Strength", "Evasion", "Luck", "Speed"]


weapon_proficiencies = {
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
    "Gorm": {"nickname": "gorm"},
    "Dung Beetle Knight": {"nickname": "dbk"},
}

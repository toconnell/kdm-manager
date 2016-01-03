#!/usr/bin/env python

#
#   Only game_asset dictionaries belong in this file. Do not add any methods or
#       other helpers here. Those all belong in models.py
#

abilities_and_impairments = {
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
        "desc": "While a shield is in your gear grid, you are no longer knocked down after <b>collision</b> with a monster. Whil a shield is in your gear grid, add <b>1</b> to all hit locations.",
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
        "desc": 'Once a lifetime, on a hunt board space after Overwhelming Darkness, in place of rolling a random hunt event, use "53" as your result.',
        "max": 1,
    },
    "Legendcaller": {
        "type": "ability",
        "desc": 'Once a lifetime, on a hunt board space after Overwhelming Darkness, in place of rolling a random hunt event, use "100" as your result.',
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
    "Shattered jaw": {
        "type": "impairment",
        "desc": "You can no longer consume or be affected by events requiring you to consume. You can no longer encourage. This injury is permanent and can be recorded once.",
        "max": 1,
    },
    "Dismembered Arm": {
        "type": "impairment",
        "desc": "You can no longer activate two-handed weapons. This injury is permanent, and can be recorded twice. A survivor with two dismembered arm severe injuries cannot activate any weapons.",
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
    "Gaping chest wound": {
        "type": "impairment",
        "desc": "Suffer -1 permanent Strength. This injury is permanent and can be recorded multiple times.",
        "Strength": -1,
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
    "Broken hip": {
        "type": "impairment",
        "desc": "You can no longer dodge. Suffer -1 permanent movement. This injury is permanent and can be recorded once.",
        "Movement": -1,
    },
    "Dismembered leg": {
        "type": "impairment",
        "desc": "You suffer -2 permanent movement, and can no longer dash. This injury is permanent and can be recorded twice.",
        "Movement": -2,
        "max": 2,
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
    "Fear of the Dark": {
        "survivor_effect": "You retire.",
    },
    "Hoarder": {
        "survivor_effect": "Whenever you are a returning survivor, archive 1 resource gained from the last showdown and gain +1 courage.",
    },
    "Binge Eating Disorder": {
        "survivor_effect": "You cannot <b>depart</b> unless you have <b>consumable</b> gear in your gear grid. You must <b>consume</b> if a choice to <b>consume</b> arises.",
    },
    "Squeamish": {
        "survivor_effect": "You cannot <b>depart</b> with any stinky gear in your gear grid. If a status or effect would cause you to become stinky, lose all your survival.",
    },
    "Secretive": {
        "survivor_effect": "When you are a returning survivor, you quickly become preoccuiped with your own affairs. You must skip the next hunt to deal with them.",
        "on_return": {
            "skip_next_hunt": "checked",
        },
    },
    "Seizures": {
        "survivor_effect": "During the showdown, whenever you suffer damage to your head location, you are knocked down.",
    },
    "Immortal": {
        "survivor_effect": "While you are insane, convert all damage dealt to your hit locations to brain damage. You are so busy reveling in your own glory that you cannot spend survival while insane.",
    },
    "Corprolalia": {
        "survivor_effect": "All your gear is noisy. You are always a threat unless you are knocked down, even if an effect says otherwise.",
    },
    "Prey": {
        "survivor_effect": "You may not spend survival unless you are insane.",
    },
    "Honorable": {
        "survivor_effect": "You cannot attack a monster from its blind spot or if it is knocked down.",
    },
    "Apathetic": {
        "survivor_effect": "You cannot use or gain survival. You cannot gain courage. Cure this disorder if you have 8+ understanding.",
    },
    "Weak Spot": {
        "survivor_effect": "When you gain this disorder, roll a random hit location and record it. You cannot depart unless you have armor at this hit location.",
    },
    "Hyperactive": {
        "survivor_effect": "During the showdown, you must move at least 1 space every round.",
    },
    "Aichmophobia": {
        "survivor_effect": "You cannot activate or depart with axes, swords, spears, daggers, scythes, or katars in your gear grid.",
    },
    "Hemophobia": {
        "survivor_effect": "During the showdown, whenever a survivor (including you) gains a bleeding token, you are knocked down.",
    },
    "Vestiphobia": {
        "survivor_effect": "You cannot wear armor at the body location. If you are wearing armor at the body location when you gain this disorder, archive it as you tear it off your person!",
    },
    "Traumatized": {
        "survivor_effect": "Whenever you end your act adjacent to a monster, you are knocked down.",
    },
    "Monster Panic": {
        "survivor_effect": "Whenever you suffer brain damage from an Intimidate action, suffer 1 additional brain damage.",
    },
    "Post-Traumatic Stress": {
        "survivor_effect": "Next settlement phase, you do not contribute or participate in any endeavors. Skip the next hunt to recover.",
        "skip_next_hunt": True,
    },
    "Rageholic": {
        "survivor_effect": "Whenever you suffer a severe injury, also suffer the frenzy brain trauma.",
    },
    "Indecision": {
        "survivor_effect": "If you are the event revealer of hunt events that call on you to make a roll, roll twice and use the lower result.",
    },
    "Anxiety": {
        "survivor_effect": "At the start of each showdown, gain the priority target token unless you have stinky gear in your gear grid.",
    },
    "Quixotic": {
        "survivor_effect": "If you are insane when you depart, gain +1 survival and +1 Strength token.",
    },
}


epithets = {
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
        "desc": "Once per showdown, you may spend Activation to have all non-deaf survivors gain +2 insanity. When you die, you encourage all survivors with your last words.",
    },
    "Leader": {
        "desc": "Whenever you encourage a survivor they gain +1 speed token until the end of the round.",
    },
    "Combo Master": {
        "desc": "On a perfect hit, make 1 additional attack roll.",
    },
    "Double Dash": {
        "desc": "During your act, once per round, you may spend Activation to gain Movement.",
    },
    "Timeless Eye": {
        "desc": "Your attack roll is a perfect hit on a result of a 9 or 10. You cannot use Timeless Eye if you have the blind severe head injury.",
    },
    "Mighty Strike": {
        "desc": "On a Perfect hit, gain +2 Strength until the end of the attack.",
    },
    "Berserker": {
        "desc": "Once per showdown, you may spend Activation to suffer bash and the frenzy brain trauma.",
    },
    "Thrill Seeker": {
        "desc": "Whenever you gain survival during the showdown phase, gain 1 additional survival.",
    },
    "Tough": {
        "desc": "When rolling on a severe injury table, unless you roll a 1, add +1 to the result. (This does not include brain trauma. The result total cannot exceed 10.)",
    },
    "Rhythm Chaser": {
        "desc": "Gain +1 Evasion token the first time you critically wound during a showdown. Rhythm Chaser cannot be used if there are any shields or <i>heavy</i> gear in your grid.",
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
        "desc": "On a Perfect hit, gain +1 insanity.",
    },
    "Unconscious Fighter": {
        "desc": "It takes 7 bleeding tokens to kill you.",
    },
    "Ambidexterous": {
        "desc": "All melee weapons in your gear grid gain paired (add the speed of the second weapon when attacking with the first). Ambidexterous cannot be used if there are any shields, two-handed or heavy gear in your gear grid.",
    },
    "Strategist": {
        "desc": "During the showdown setup, after placing terrain, you may add a Giant Stone Face or a Toppled Pillar terrain card to the showdown board.",
    },
    "Monster Claw Style": {
        "desc": "Your Fist & Tooth attacks gain +1 Accuracy, +1 Strength and Savage (after the first critical wound in an attack, savage weapons cause 1 additional wound. This rule does not trigger on Impervious hit locations).",
    },
    "Tumble": {
        "desc": "When something would collide with you, roll 1d10. On a result of 6+, you successfully tumble out of harm's way. Instead, please your survivor standing on the closest free space outside of the collision path.",
    },
    "Extra Sense": {
        "desc": "You may dodge 1 additional time per round.",
    },
}


locations = {
    "Lantern Hoard": {
        "always_available": True,
        "consequences": ["Bone Smith", "Skinnery", "Organ Grinder", "Catarium", "Plumery", "Exhausted Lantern Hoard", "Mask Maker"],
    },
    "Bone Smith": {
        "color": "E5DDD3",
        "consequences": ["Weapon Crafter"],
    },
    "Skinnery": {
        "color": "A89166",
        "consequences": ["Leather Worker"],
    },
    "Organ Grinder": {
        "color": "B58AA5",
        "consequences": ["Stone Circle"],
    },
    "Blacksmith": {
        "requires": ("innovations", "Scrap Smelting"),
        "color": "9DAFBC",
        "consequences": [],
    },
    "Stone Circle": {
        "color": "84596B",
        "consequences": [],
    },
    "Leather Worker": {
        "color": "927B51",
        "consequences": [],
    },
    "Weapon Crafter": {
        "color": "E1D4C0",
        "consequences": [],
    },
    "Barber Surgeon": {
        "requires": ("innovations", "Pottery"),
        "color": "F5F1DE",
        "consequences": [],
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
}


items = {
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
    "Hours Ring": {
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
    "Eye Of Cat": {
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
    "Tall Feathers": {
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
        "type": "gear",
    },
    "Regal Plackart": {
        "location": "Rare Gear",
        "type": "gear",
    },
    "Regal Greaves": {
        "location": "Rare Gear",
        "type": "gear",
    },
    "Regal Helm": {
        "location": "Rare Gear",
        "type": "gear",
    },
    "Regal Faulds": {
        "location": "Rare Gear",
        "type": "gear",
    },
    "Forsaker Mask": {
        "location": "Rare Gear",
        "type": "gear",
    },
    "Adventure Sword": {
        "location": "Rare Gear",
        "type": "gear",
    },
    "Steel Shield": {
        "location": "Rare Gear",
        "type": "gear",
    },
    "Steel Sword": {
        "location": "Rare Gear",
        "type": "gear",
    },
    "Twilight Sword": {
        "location": "Rare Gear",
        "type": "gear",
    },
    "Butcher Cleaver": {
        "location": "Rare Gear",
        "type": "gear",
    },
    "Lantern Halberd": {
        "location": "Rare Gear",
        "type": "gear",
    },
    "Muramasa": {
        "location": "Rare Gear",
        "type": "gear",
    },
    "Thunder Maul": {
        "location": "Rare Gear",
        "type": "gear",
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
    "Lance of Longinus": {
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
}


innovations = {
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
        "survivor_buff": "When rolling on the Intimacy story event, roll twice and pick one result.",
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
    "Sacrifice": { "type": "faith", },
    "Scarification": { "type": "faith", },
    "Records": { "type": "education", },
    "Shrine": {
        "type": "faith",
        "consequences": ["Sacrifice"],
    },
    "Scrap Smelting": {"type": "science"},
    "Cooking": {
        "type": "science",
        "consequences": [],
        "survival_limit": 1,
    },
    "Paint": {
        "type": "art",
        "consequences": ["Pictograph", "Sculpture", "Face Painting"],
        "survival_action": "Dash",
    },
    "Drums": {
        "type": "music",
        "consequences": ["Song of the Brave", "Forbidden Dance"],
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
    },
    "Nightmare Training": {"type": "education"},
    "Momento Mori": {"type": "art"},
    "Face Painting": {"type": "art"},
    "Sculpture": {
        "type": "art",
        "consequences": ["Pottery"],
        "survival_limit": 1,
        "departure_buff": "Departing survivors gain +2 survival when they depart for a Nemesis Encounter.",
    },
    "Pictograph": {
        "type": "art",
        "consequences": ["Momento Mori"],
        "survivor_buff": "Anytime during the hunt or showdown phase, a survivor may Run Away (story event).",
    },
    "Pottery": {
        "type": "art",
        "survival_limit": 1,
        "settlement_buff": "If the settlement loses all its resources, you may select up to two resources and keep them.",
    },
    "Heart Flute": {"type": "music"},
    "Saga": {
        "type": "music",
        "survivor_buff": "All newborn survivors gain +2 hunt experience and +2 survival from knowing the epic.",
        "new_survivor": {"hunt_xp": 2, "survival": 2},
    },
    "Forbidden Dance": {"type": "music"},
    "Bed": {
        "type": "home",
        "survival_limit": 1,
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
    },
    "Bloodletting": {"type": "science"},
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



quarries = {
    "White Lion": {    },
    "Screaming Antelope": {    },
    "Phoenix": {    },
}

nemeses = {
    "Butcher": {},
    "King's Man": {},
    "The Hand": {},
}

resources = {
    "Rare Gear": {
        "color": "43C6DB",
    },
    "Unique Items": {
        "color": "7E6FF3",
    },
    "White Lion Resources": {
        "color": "FFCC66",
    },
    "Screaming Antelope Resources": {
        "color": "FFCC66",
    },
    "Phoenix Resources": {
        "color": "FFCC66",
    },
    "Basic Resources": {
        "color": "51C327",
    },
    "Vermin": {
        "color": "99CC66",
    },
    "Strange Resources": {
        "color": "B9FAC4",
    },
    "Starting Gear": {
        "color": "CCC",
    },
}

resource_decks = {
    "White Lion": [ "White Fur", "White Fur", "White Fur", "White Fur", "Lion Claw", "Lion Claw", "Lion Claw", "Eye of Cat", "Great Cat Bones", "Great Cat Bones", "Great Cat Bones", "Great Cat Bones", "Shimmering Mane", "Lion Tail", "Curious Hand", "Golden Whiskers", "Sinew", "Sinew", "Lion Testes" ],
    "Screaming Antelope": ["Pelt", "Pelt", "Pelt", "Pelt", "Shank Bone", "Shank Bone", "Shank Bone", "Shank Bone", "Large Flat Tooth", "Large Flat Tooth", "Beast Steak", "Beast Steak", "Muscly Gums", "Spiral Horn", "Bladder", "Screaming Brain"],
    "Phoenix": ["Tall Feathers", "Tall Feathers", "Tall Feathers", "Phoenix Eye", "Phoenix Whisker", "Pustules", "Pustules", "Small Feathers", "Small Feathers", "Small Feathers", "Muculent Droppings", "Muculent Droppings", "Muculent Droppings", "Wishbone", "Shimmering Halo", "Bird Beak", "Black Skull", "Small Hand Parasites", "Phoenix Finger", "Phoenix Finger", "Hollow Wing Bones", "Hollow Wing Bones", "Hollow Wing Bones", "Rainbow Droppings"],
    "Basic Resources": ["???", "???", "Skull", "Broken Lantern", "Broken Lantern", "Monster Bone", "Monster Bone", "Monster Bone", "Monster Bone", "Love Juice", "Love Juice", "Monster Organ", "Monster Organ", "Monster Organ", "Monster Hide", "Monster Hide", "Monster Hide", "Monster Hide", "Monster Hide", "Monster Hide", "Monster Hide"]
}

survival_actions = ["Dodge", "Encourage", "Surge", "Dash"]
survivor_attributes = ["Movement", "Accuracy", "Strength", "Evasion", "Luck", "Speed"]


weapon_proficiencies = {
    "Bow": {},
    "Katar": {},
    "Sword": { },
    "Dagger": { },
    "Shield": { },
    "Whip": {},
    "Grand Weapon": { },
    "Fist & Tooth": { },
    "Club": {},
    "Spear": {},
    "Axe": {},
    "Twilight Sword": {},
}

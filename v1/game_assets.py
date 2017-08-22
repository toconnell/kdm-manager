#!/usr/bin/env python


#
#   Disorders
#

disorders = {
    "Spiral Ganglia": {
        "expansion": "Slenderman",
        "flavor_text": "The roads in your mind cross and reveal a strange new path.",
        "survivor_effect": "At the start of the showdown, gain the <b>Darkness Awareness</b> survivor status card.",
    },
    "Hyper-Sensitivity": {
        "expansion": "Slenderman",
        "flavor_text": "Your will to survive has become indefatigable",
        "survivor_effect": "You may <b>dodge</b> one additional time per round.<br/>Whenever you are hit by an attack, you must <b>dodge</b> at least once, if possible.",
    },
    "Tiny Arachnophobia": {
        "expansion": "Spidicules",
        "flavor_text": "You are irrationally scared by tiny spiders and the things they produce.",
        "survivor_effect": 'You cannot carry any gear with the amber keyword. You cannot gain any resources with the silk keyword.',
    },
    "Controlophobia": {
        "expansion": "Spidicules",
        "flavor_text": "You are deeply afraid of being the monster controller.",
        "survivor_effect": 'While you are the monster controller, double any damage you suffer.',
    },
    "Revenge": {
        "expansion": "Spidicules",
        "flavor_text": "When a fellow hunter perishes you lose control.",
        "survivor_effect": 'When a survivors dies during the showdown, suffer the <b>Frenzy</b> brain trauma.',
    },
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
        "flavor_text": "Lingering damage from your head injuries has caused you to experience periods of uncontrollable shaking and absence of thought.",
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
    "Blotted Out": {
        "expansion": "Slenderman",
        "desc": "When you suffer a brain trauma, gain a bleeding token.",
        "epithet": "Blotted Out",
    },
    "Phantom Friend": {
        "expansion": "Slenderman",
        "desc": "The first time you gain a resource during a showdown, you may feed it to your phantom friend. If you do, archive the resources and gain +1 evasion token.<br/>Lose this token if you are <b>deaf</b> or become <b>deaf</b> during the showdown."
    },
    "Clarity of Darkness": {
        "expansion": "Slenderman",
        "desc": "At the start of the showdown, gain the <b>Path of Gloom</b> survivor status card.<br/>There is a deadly, otherworldly presence about you. Other survivors cannot voluntarily end their movement adjacent to you.",
        "secret": True,
    },
    "Death Touch": {
        "expansion": "Spidicules",
        "desc": "Gain +1 accuracy when attacking with Fist & Tooth.<br/>When you wound a monster, it gains -1 toughness until the end of your attack.<br/>You cannot use this if you are male.",
        "secret": True,
        "epithet": "Black Widow"
    },
    "Silk Surgeon": {
        "expansion": "Spidicules",
        "desc": "",
        "secret": True,
        "epithet": "Silk Surgeon",
        "levels": {
            0: "",
            1: 'You may spend <font class="kdm_font">a</font> while adjacent to another survivor to add <font class="inline_shield">2</font> to one of their hit locations.',
            2: "While all armor in your gear grid is silk and all jewelry is amber, gain +2 evasion.",
            3: "During the aftermath, roll 1d10 for each other survivor that died during the showdown. On a 7+, revive them.",
        },
    },
    "Vengeance": {
        "expansion": "Spidicules",
        "desc": "When a survivor dies during the showdown, gain +4 survival and +1 strength token.",
    },
    "Harvestman": {
        "expansion": "Spidicules",
        "desc": "Gain +3 movement. Whenever you are knocked down, gain -1 movement token.<br/>If you have the <b>Tiny Arachnophobia</b> disorder, you are too scared of spiders to imitate them and you cannot use this fighting art.",
        "epithet": "Harvestman",
        "Movement": 3,
    },
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


locations = {
    "Light-Forging": {
        "color": "570A75",
        "font_color": "fff",
    },
    "Green Knight Armor": {
        "color": "42AB59",
        "font_color": "fff",
    },
    "Silk Mill":{
        "color": "C0CA33",
        "font_color": "000",
    },
    "Manhunter Gear":{
        "color": "000",
        "font_color": "F50057",
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
        "consequences": [
            "Bone Smith",
            "Skinnery",
            "Organ Grinder",
            "Catarium",
            "Plumery",
            "Mask Maker",
            "Sacred Pool"
        ],
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
    "Gloom Hammer": {
        "expansion": "Slenderman",
        "location": "Light-Forging",
    },
    "Gloom Katana": {
        "expansion": "Slenderman",
        "location": "Light-Forging",
    },
    "Gloom Sheath": {
        "expansion": "Slenderman",
        "location": "Light-Forging",
    },
    "Gloom Bracelets": {
        "expansion": "Slenderman",
        "location": "Light-Forging",
    },
    "Gloom-Coated Arrow": {
        "expansion": "Slenderman",
        "location": "Light-Forging",
    },
    "Gloom Mehndi": {
        "expansion": "Slenderman",
        "location": "Light-Forging",
    },
    "Dark Water Vial": {
        "expansion": "Slenderman",
        "location": "Light-Forging",
    },
    "Raptor-Worm Collar": {
        "expansion": "Slenderman",
        "location": "Light-Forging",
    },
    "Gloom Cream": {
        "expansion": "Slenderman",
        "location": "Light-Forging",
    },
    "Slender Ovule": {
        "expansion": "Slenderman",
        "location": "Light-Forging",
    },
    "Crystal Sword Mold": {
        "expansion": "Slenderman",
        "location": "Strange Resources",
    },
    "Dark Water": {
        "expansion": "Slenderman",
        "location": "Strange Resources",
    },
    "Green Boots" : {
        "expansion": "Green Knight Armor",
        "location": "Green Knight Armor",
    },
    "Green Plate" : {
        "expansion": "Green Knight Armor",
        "location": "Green Knight Armor",
    },
    "Green Gloves" : {
        "expansion": "Green Knight Armor",
        "location": "Green Knight Armor",
    },
    "Green Helm" : {
        "expansion": "Green Knight Armor",
        "location": "Green Knight Armor",
    },
    "Green Faulds" : {
        "expansion": "Green Knight Armor",
        "location": "Green Knight Armor",
    },
    "Fetorsaurus" : {
        "expansion": "Green Knight Armor",
        "location": "Green Knight Armor",
    },
    "Griswaldo" : {
        "expansion": "Green Knight Armor",
        "location": "Green Knight Armor",
    },
    "Venom Sac": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["organ",],
    },
    "Arachnid Heart": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["organ",],
    },
    "Serrated Fangs": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["bone",],
        "endeavors": {
            "Razor Push-ups": {"cost": 1, "type": "education",},
        },
    },
    "Eyeballs": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["organ",],
    },
    "Unlaid Eggs": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["organ",],
    },
    "Large Appendage": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["bone",],
    },
    "Exoskeleton": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["hide",],
    },
    "Chitin": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["hide",],
    },
    "Small Appendages": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["hide",],
    },
    "Stomach": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["organ",],
    },
    "Spinnerets": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["organ","scrap"],
    },
    "Thick Web Silk": {
        "expansion": "Spidicules",
        "location": "Spidicules Resources",
        "resource_family": ["hide"],
    },
    "Silken Nervous System": {
        "expansion": "Spidicules",
        "location": "Strange Resources",
        "resource_family": ["organ"],
    },
    "Web Silk": {
        "expansion": "Spidicules",
        "location": "Strange Resources",
    },
    "Silk Armor Set": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Throwing Knife": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Hooded Scrap Katar": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Silk Wraps": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Silk Whip": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Silk Turban": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Silk Sash": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Silk robes": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Silk Boots": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Silk Bomb": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Silk Body Suit": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Green Ring": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Red Ring": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Blue Ring": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Amber Poleaxe": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Amber Edge": {
        "expansion": "Spidicules",
        "location": "Silk Mill",
    },
    "Grinning Visage": {
        "expansion": "Spidicules",
        "location": "Rare Gear",
        "desc": 'When you wound with this shield, you may spend 1 survival to add <font class="inline_shield">1</font> to all hit locations.<br/>Limit, once per attack.',
        "type": ["weapon","melee","shield"],
    },
    "The Weaver": {
        "expansion": "Spidicules",
        "location": "Rare Gear",
        "desc": 'When you wound a monster, add <font class="inline_shield">1</font> to a random hit location.',
        "type": ["weapon","melee","sword","amber"],
    },
    "Detective Cap": {
        "expansion": "white_box",
        "location": "Promo",
    },
    "Twilight Revolver": {
        "expansion": "white_box",
        "location": "Promo",
    },
    "Xmaxe": {
        "expansion": "white_box",
        "location": "Promo",
    },
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
        "resource_family": ["scrap"],
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
    "Lantern Bloom": {
        "expansion": "Flower Knight",
        "location": "Flower Knight Resources",
        "resource_family": ["hide",],
    },
    "Sighing Bloom": {
        "expansion": "Flower Knight",
        "location": "Flower Knight Resources",
        "resource_family": ["organ",],
    },
    "Osseous Bloom": {
        "expansion": "Flower Knight",
        "location": "Flower Knight Resources",
        "resource_family": ["bone",],
    },
    "Lantern Bud": {
        "expansion": "Flower Knight",
        "location": "Flower Knight Resources",
        "resource_family": ["scrap",],
    },
    "Warbling Bloom": {
        "expansion": "Flower Knight",
        "location": "Flower Knight Resources",
        "resource_family": ["hide",],
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
    "Huge Sunteeth": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["bone"],
    },
    "Small Sunteeth": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["bone"],
    },
    "Shadow Tentacles": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["organ","hide"],
    },
    "Shark Tongue": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["organ"],
    },
    "Cycloid Scales": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["hide"],
    },
    "Inner Shadow Skin": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["hide"],
    },
    "Prismatic Gills": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["organ"],
    },
    "Sunshark Fin": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["bone","hide"],
    },
    "Sunshark Bone": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["bone"],
    },
    "Stink Lung": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["organ"],
    },
    "Brain Root": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["organ"],
    },
    "Fertility Tentacle": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["organ"],
    },
    "Shadow Ink Gland": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["organ"],
    },
    "Sunshark Blubber": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["organ"],
    },
    "Black Lens": {
        "expansion": "Sunstalker",
        "location": "Sunstalker Resources",
        "resource_family": ["organ"],
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
        "resource_family": ["scrap"],
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
        "resource_family": ["scrap"],
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
    "Choreia": {
        "type": "music",
        "expansion": "Spidicules",
        "endeavors": {
            "Spider Dance": {"cost": 1, "type": "music", "desc": "Nominate a male and a female survivor and roll 1d10."},
        },
    },
    "Silk-Refining": {
        "expansion": "Spidicules",
        "type": "other",
        "survival_limit": 1,
        "endeavors": {
            "end_0": {
                "hide_name": True,
                "type": "other",
                "desc": '<font class="kdm_font">g</font> <b>Silk Surgery</b>.',
                "cost": 1,
            },
           "end_1": {
                "hide_name": True,
                "type": "other",
                "desc": 'Convert 1 silk resource into 1 hide basic resource.',
                "cost": 1,
            },
           "end_2": {
                "hide_name": True,
                "type": "other",
                "desc": 'Spend 2 silk, 1 bone, and 1 organ to build the <b>Silk Mill</b> settlement location.',
                "remove_after": "Silk Mill",
                "cost": 1,
            },
        },
    },
    "Legless Ball": {
        "expansion": "Spidicules",
        "type": "other",
        "survivor_buff": '<b>Departing survivors</b> gain +2 insanity.',
        "subhead": 'Spend only 1 <font class="kdm_font">d</font> here per settlement phase.',
        "endeavors": {
            "end_0": {
                "hide_name": True,
                "type": "other",
                "desc": 'Add 1 <b>Web Silk</b> strange resource to settlement storage.',
                "cost": 1,
            },
           "end_1": {
                "hide_name": True,
                "type": "other",
                "desc": 'A survivor with 10+ insanity may put the Spidicules out of its misery. Gain the <b>Grinning Visage</b> rare gear and lose this innovation. (Archive this card.)',
                "cost": 1,
            },
        },
    },

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

    "Dark Water Research": {
        "type": "science",
        "expansion": "Slenderman",
        "endeavors": {
            '<font class="kdm_font">g</font> Light-Forging': {"cost": 2, "type": "science"},
            "end_0": {
                "hide_name": True,
                "type": "science",
                "desc": 'Spend 2x resources and 2x Dark Water to increase the level of <b>Dark Water Research</b> by 1, to a maximum of 3. (Update your settlement record sheet.)',
                "cost": 1,
            },
        },
        "levels": 3,
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
#        "survivor_buff": 'Anytime during the hunt or showdown phase, a survivor may <font class="kdm_font">g</font> <b>Run Away</b>.',
        "survivor_buff": 'At the start of a standing survivor\'s act, they may trigger the <font class="kdm_font">g</font> <b>Run Away</b> story event. Limit, once per act.',
    },
    "Heart Flute": {
        "type": "music",
        "endeavors": {
            "Devil's Melody": {"cost": 1, "type": "music"},
        },
    },
    "Forbidden Dance": {
        "type": "music",
        "consequences": ["Petal Spiral", "Choreia"],
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
#   Settlement Sheet assets
#

resources = {
    "White Lion Resources": {
        "color": "DCD900",
    },
    "Screaming Antelope Resources": {
        "color": "DCD900",
    },
    "Phoenix Resources": {
        "color": "DCD900",
    },
    "Spidicules Resources": {
        "color": "DCD900",
    },
    "Flower Knight Resources": {
        "expansion": "Flower Knight",
        "color": "DCD900",
    },
    "Gorm Resources": {
        "expansion": "Gorm",
        "color": "DCD900",
    },
    "Sunstalker Resources": {
        "expansion": "Sunstalker",
        "color": "DCD900",
    },
    "Dung Beetle Knight Resources": {
        "expansion": "Dung Beetle Knight",
        "color": "DCD900",
    },
    "Dragon King Resources": {
        "expansion": "Dragon King",
        "color": "DCD900",
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

survivor_attributes = ["Movement", "Accuracy", "Strength", "Evasion", "Luck", "Speed"]


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
    "Green Knight Armor": {
        "always_available": ["Green Knight Armor"],
    },
    "Slenderman": {
        "always_available": ["Dark Water Research"],
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
            {"ly": 10, "type": "special_showdown", "name": "Special Showdown - Manhunter"},
            {"ly": 16, "type": "special_showdown", "name": "Special Showdown - Manhunter"},
            {"ly": 22, "type": "special_showdown", "name": "Special Showdown - Manhunter"},
        ],
    },
    "Spidicules": {
        "always_available": ["Legless Ball","Silk Mill","Silk-Refining"],
        "timeline_add": [
            {"ly": 2, "type": "story_event", "name": "Young Rivals"},
        ],
        "timeline_rm": [
            {"ly": 2, "type": "story_event", "name": "Endless Screams"},
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
        "always_available": ["The Sun", "Sun Language", "Umbilical Bank","Skyreef Sanctuary"],
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
        "sort_order": 4,
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


# temporary/transitional lookup table for campaign names
campaign_look_up = {
    "people_of_the_sun": "People of the Sun",
    "people_of_the_lantern": "People of the Lantern",
    "people_of_the_skull": "People of the Skull",
    "people_of_the_stars": "People of the Stars",
    "the_bloom_people": "The Bloom People",
    "the_green_knight": "The Green Knight",
    "People of the Sun": "People of the Sun",
    "People of the Lantern": "People of the Lantern",
    "People of the Skull": "People of the Skull",
    "People of the Stars": "People of the Stars",
    "The Bloom People": "The Bloom People",
    "The Green Knight": "The Green Knight",
}



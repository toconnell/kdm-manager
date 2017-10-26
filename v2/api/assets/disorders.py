core = {
    'aichmophobia': {
        'flavor_text': "Sharp things make you uncomfortable. It's just a matter of time before someone cuts themselves.",
        'name': 'Aichmophobia',
        'survivor_effect': 'You cannot activate or <b>depart</b> with axes, swords, spears, daggers, scythes, or katars in your gear grid.'
        },
    'anxiety': {
        'flavor_text': "You are afraid of being afraid. You're a nervous wreck, and monsters can smell this in your scent.",
        'name': 'Anxiety',
        'survivor_effect': 'At the start of each showdown, gain the <b>priority target</b> token unless you have <b>stinky</b> gear in your gear grid.'
    },
    'apathetic': {
        'flavor_text': "You've given up. Nothing seems to matter. You have no concern for your own wellbeing.",
        'name': 'Apathetic',
        'survivor_effect': 'You cannot use or gain survival. You cannot gain courage. Cure this disorder if you have 8+ understanding.'
    },
    'binge_eating_disorder': {
        'flavor_text': 'Eating is the only thing that helps you escape your miserable life.',
        'name': 'Binge Eating',
        'survivor_effect': 'You cannot <b>depart</b> unless you have <b>consumable</b> gear in your gear grid. You must <b>consume</b> if a choice to <b>consume</b> arises.'
    },
    'coprolalia': {
        'flavor_text': 'You have compulsive tics in the form of sporadic muttering, cursing, whimpering, and screaming.',
        'name': 'Coprolalia',
        'survivor_effect': 'All your gear is <b>noisy</b>. You are always a threat unless you are knocked down, even if an effect says otherwise.'
    },
    'fear_of_the_dark': {
        'flavor_text': 'You cannot bear the oppressive darkness any longer.',
        'name': 'Fear of the Dark',
        'retire': True,
        'survivor_effect': 'You retire.<br/>If you gain this disorder during a hunt or showdown, you put on a brave face until you return to the settlement, vowing never to leave the Lantern Hoard again.'
    },
    'hemophobia': {
        'flavor_text': 'The mere sight of blood makes you lightheaded, and serious gore can knock you out!',
        'name': 'Hemophobia',
        'survivor_effect': 'During the showdown, whenever a survivor (including you) gains a bleeding token, you are knocked down.'
    },
    'hoarder': {
        'flavor_text': 'You compulsively collect and stash anything you can get your hands on. Every little bit you add to your secret hoard makes your existence feel more real.',
        'name': 'Hoarder',
        'survivor_effect': 'Whenever you are a <b>returning</b> survivor, archive 1 resource gained from the last showdown and gain +1 courage.'
    },
    'honorable': {
        'flavor_text': 'You believe in honor and fairness when conducting yourself on the battlefield. It is these strong principles that have kept you alive, and you will not abandon them under any circumstances.',
        'name': 'Honorable',
        'survivor_effect': 'You cannot attack a monster from its blind spot or if it is knocked down.'
    },
    'hyperactive': {
        'flavor_text': 'Whether you are running, fiddling with your gear, or pacing, you are always moving.',
        'name': 'Hyperactive',
        'survivor_effect': 'During the showdown, you must move at least 1 space every round.'
    },
    'immortal': {
        'flavor_text': 'You are immortal! You will live forever and cannot be killed.',
        'name': 'Immortal',
        'survivor_effect': 'While you are insane, convert all damage dealt to your hit locations to brain damage.<br/>You are so busy reveling in your own glory that you cannot spend survival while insane.'
    },
    'indecision': {
        'flavor_text': 'Past decisions haunt you ceaselessly. You are crippled by indecision, and even the most trivial choices grip you with terror.',
        'name': 'Indecision',
        'survivor_effect': 'If you are the event revealer of hunt events that call on you to make a roll, roll twice and use the lower result.'
    },
    'monster_panic': {
        'flavor_text': 'Monsters make you feel bad. Really, really bad.',
        'name': 'Monster Panic',
        'survivor_effect': 'Whenever you suffer brain damage from an <b>Intimidate</b> action, suffer 1 additional brain damage.'
    },
    'post_traumatic_stress': {
        'flavor_text': 'The last hunt was harrowing. All you can do is cower and relive the trauma. Only time can heal your wounds.',
        'name': 'Post-Traumatic Stress',
        'skip_next_hunt': True,
        'survivor_effect': 'Next settlement phase, you do not contribute or participate in any endeavors. Skip the next hunt to recover.'
    },
    'prey': {
        'flavor_text': 'You are prey. All there is for you is death.',
        'name': 'Prey',
        'survivor_effect': 'You may not spend survival unless you are insane.'
    },
    'quixotic': {
        'flavor_text': 'You carry the weight of your settlement on your shoudlers. Everyone is counting on you to save them, and you will rise to the challenge.',
        'name': 'Quixotic',
        'survivor_effect': 'If you are insane when you <b>depart</b>, gain +1 survival and +1 Strength token.'
    },
    'rageholic': {
        'flavor_text': 'Your rage boils out of control, causing you to see red at the slightest provocation.',
        'name': 'Rageholic',
        'survivor_effect': 'Whenever you suffer a severe injury, also suffer the <b>frenzy</b> brain trauma.'
    },
    'secretive': {
        'flavor_text': 'You love secrets. So much, in fact, that you pretend to have many.',
        'name': 'Secretive',
        'on_return': {
            'skip_next_hunt': True,
        },
        'survivor_effect': 'When you are a <b>returning survivor</b>, you quickly become preoccuiped with your own affairs. You must skip the next hunt to deal with them.'
        },
    'seizures': {
        'flavor_text': 'Lingering damage from your head injuries has caused you to experience periods of uncontrollable shaking and absence of thought.',
        'name': 'Seizures',
        'survivor_effect': 'During the showdown, whenever you suffer damage to your head location, you are knocked down.'
    },
    'squeamish': {
        'flavor_text': "You can't handle bad smells.",
        'name': 'Squeamish',
        'survivor_effect': 'You cannot <b>depart</b> with any <b>stinky</b> gear in your gear grid. If a status or effect would cause you to become stinky, lose all your survival.'
    },
    'traumatized': {
        'flavor_text': 'Your experiences have left you shaken and paralyzed by fear.',
        'name': 'Traumatized',
        'survivor_effect': 'Whenever you end your act adjacent to a monster, you are knocked down.'
    },
    'vestiphobia': {
        'flavor_text': 'Even the lightest armor rubs harshly against your skin and constricts your ability to move.',
        'name': 'Vestiphobia',
        'survivor_effect': 'You cannot wear armor at the body location. If you are wearing armor at the body location when you gain this disorder, archive it as you tear it off your person!'
    },
    'weak_spot': {
        'flavor_text': 'You have an imaginary infirmity.',
        'name': 'Weak Spot',
        'survivor_effect': 'When you gain this disorder, roll a random hit location and record it. You cannot <b>depart</b> unless you have armor at this hit location.'
    },

}

expansions = {

    # gorm
    'absent_seizures': {
        'expansion': 'gorm',
        'flavor_text': "No one knows where your mind goes when you're gone, not even you.",
        'name': 'Absent Seizures',
        'survivor_effect': 'The first time you would suffer a brain trauma each showdown, you are instead knocked down and forget a fighting art (erase it).'
    },
    'megalophobia': {
        'expansion': 'gorm',
        'flavor_text': 'Even large, looming shadows make you jumpy.',
        'name': 'Megalophobia',
        'survivor_effect': 'You may not <b>depart</b> for hunts or showdowns with monsters that occupy more than 4 spaces on the showdown board.'
    },

    # spidicules
    'controlophobia': {
        'expansion': 'spidicules',
        'flavor_text': 'You are deeply afraid of being the monster controller.',
        'name': 'Controlophobia',
        'survivor_effect': 'While you are the monster controller, double any damage you suffer.'
    },
    'revenge': {
        'expansion': 'spidicules',
        'flavor_text': 'When a fellow hunter perishes you lose control.',
        'name': 'Revenge',
        'survivor_effect': 'When a survivors dies during the showdown, suffer the <b>Frenzy</b> brain trauma.'
    },
    'tiny_arachnophobia': {
        'expansion': 'spidicules',
        'flavor_text': 'You are irrationally scared by tiny spiders and the things they produce.',
        'name': 'Tiny Arachnophobia',
        'survivor_effect': 'You cannot carry any gear with the amber keyword. You cannot gain any resources with the silk keyword.'
    },

    # dragon king
    'arithmophilia': {
        'expansion': 'dragon_king',
        'flavor_text': 'You love numbers. Your life must exist in perfect arithmetical harmony.',
        'name': 'Arithmophilia',
        'survivor_effect': 'When you gain this disorder, roll 1d5. Your movement is that number.<br/>Ignore all other movement modifiers.'
    },
    'destined': {
        'constellation': {'horizontal': 'Gambler', 'vertical': 'Rust'},
        'expansion': 'dragon_king',
        'flavor_text': 'You have a grand destiny that you must fulfill.',
        'name': 'Destined',
        'survivor_effect': 'If you do not <b>depart</b>, lose all survival and insanity.'
    },
    'performance_anxiety': {
        'expansion': 'dragon_king',
        'flavor_text': "You're not ready to love.",
        'name': 'Performance Anxiety',
        'survivor_effect': 'You cannot be nominated for <b>Intimacy</b>.<br/>Cure this disorder if you have 8+ courage.'
    },
    'superstitious': {
        'expansion': 'dragon_king',
        'flavor_text': 'Evil magic will be your undoing. You do not believe in abusing the other.',
        'name': 'Superstitious',
        'survivor_effect': 'You cannot activate or <b>depart</b> with other gear in your gear grid.'
    },

    # lion god
    'delicious': {
        'expansion': 'lion_god',
        'flavor_text': 'Predators of all shapes and sizes find your scent irresistible.',
        'name': 'Delicious',
        'survivor_effect': 'You are still considered a threat when you are knocked down (unless you use an effect that says otherwise).'
    },
    'enfeebled': {
        'expansion': 'lion_god',
        'flavor_text': 'You are delicate flower, wilting in the darkness.',
        'name': 'Enfeebled',
        'survivor_effect': 'It takes one less bleeding token to kill you.'
    },
    'stark_raving': {
        'expansion': 'lion_god',
        'flavor_text': 'Freedom awaits those pushed this far beyond the breaking point.',
        'name': 'Stark Raving',
        'survivor_effect': 'You are always <b>insane</b>, regardless of your insanity.'
    },
    'tunnel_vision': {
        'expansion': 'lion_god',
        'flavor_text': "If you're not killing something, you're wasting your time.",
        'name': 'Tunnel Vision',
        'survivor_effect': 'When you spend <font class="kdm_font">a</font>, you may only activate weapons.'
    },

    # sunstalker
    'emotionless': {
        'expansion': 'sunstalker',
        'flavor_text': "You don't have any emotions. You've hidden this from everyone by mimicking their social interactions.",
        'name': 'Emotionless',
        'survivor_effect': 'You cannot gain +1 strength tokens.',
    },
    'overprotective': {
        'expansion': 'sunstalker',
        'flavor_text': 'You love the feeling of being needed.',
        'name': 'Overprotective',
        'survivor_effect': 'When an adjacent survivor is knocked down, you are also knocked down as you rush to their aid.',
    },
    'sun_drunk': {
        'expansion': 'sunstalker',
        'flavor_text': 'When your emotions rise, you can only think of violence.',
        'name': 'Sun-Drunk',
        'survivor_effect': 'When you have any +1 strength tokens, you cannot <b>dash</b>, <b>dodge</b> or <font class="kdm_font">g</font> <b>Run Away</b>.'
        },

    # flower knight
    'flower_addiction': {
        'expansion': 'flower_knight',
        'flavor_text': 'An insatiable hunger has bloomed in you, delicate and sickeningly sweet.',
        'name': 'Flower Addiction',
        'survivor_effect': 'You may only <b>depart</b> to hunt the Flower Knight.<br/>After you <b>depart</b>, cure this disorder.'
    },
    'ghostly_beauty': {
        'expansion': 'flower_knight',
        'flavor_text': 'You cannot experience fear if you do not exist.',
        'name': 'Ghostly Beauty',
        'survivor_effect': 'Double all insanity you gain.<br/>Double all survival you spend.'
    },
    'narcissistic': {
        'expansion': 'flower_knight',
        'flavor_text': 'There is nothing in the world more beautiful than yourself.',
        'name': 'Narcissistic',
        'survivor_effect': 'You may not wear armor at the head location. If you are wearing armor at the head location when you gain this disorder, archive it.'
    },

    # slenderman
    'hyper_sensitivity': {
        'expansion': 'slenderman',
        'flavor_text': 'Your will to survive has become indefatigable',
        'name': 'Hyper-Sensitivity',
        'survivor_effect': 'You may <b>dodge</b> one additional time per round.<br/>Whenever you are hit by an attack, you must <b>dodge</b> at least once, if possible.'
    },
    'spiral_ganglia': {
        'expansion': 'slenderman',
        'flavor_text': 'The roads in your mind cross and reveal a strange new path.',
        'name': 'Spiral Ganglia',
        'survivor_effect': 'At the start of the showdown, gain the <b>Darkness Awareness</b> survivor status card.'
    },

    # dung beetle knight
    'motion_sickness': {
        'expansion': 'dung_beetle_knight',
        'flavor_text': 'Moving quickly makes you vomit.',
        'name': 'Motion Sickness',
        'survivor_effect': 'Whenever you suffer <b>knockback</b>, gain 1 bleeding token.'
    },
    'vermin_obsession': {
        'expansion': 'dung_beetle_knight',
        'flavor_text': 'You love insects.',
        'name': 'Vermin Obsession',
        'survivor_effect': 'While there is a <b>Bug Spot</b> terrain tile on the showdown board, you are so overwhelmed that you are <b>doomed</b>.'
    },

    # lion knight
    'primma_donna': {
        'expansion': 'lion_knight',
        'flavor_text': 'The double-edged sword of fame is the only weapon you require.',
        'name': 'Primma Donna',
        'survivor_effect': 'Each survivor turn, you must take your act first (roll off each turn if multiple survivors have this disorder).'
    },
    'shallow_lungs': {
        'expansion': 'lion_knight',
        'flavor_text': 'Yelling makes you feel light-headed.',
        'name': 'Shallow Lungs',
        'survivor_effect': 'When you <b>encourage</b>, you are knocked down.'
    },
    'stage_fright': {
        'expansion': 'lion_knight',
        'flavor_text': 'You hate being the center of attention.',
        'name': 'Stage Fright',
        'survivor_effect': 'Whenever you become <b>doomed</b> or gain the <b>priority target</b> token, lose 1 survival.'
    },
    'unlucky': {
        'expansion': 'lion_knight',
        'flavor_text': 'Your mother always said you were born under a bad sign.',
        'name': 'Unlucky',
        'survivor_effect': 'You cannot critically wound.'
    },

    # beta challenge scenarios
    'sworn_enemy': {
        'expansion': 'beta_challenge_scenarios',
        'name': 'Sworn Enemy',
        'survivor_effect': 'When you gain this, choose a monster. You may only depart to face the chosen monster. Your attacks against the chosen monster gain +1 speed and +1 strength.'
    },

}

#!/usr/bin/python


weapon_masteries = {
    "scythe_master": {
        "name": "Mastery - Scythe",
        "desc": "When you critically wound with a scythe, roll 1d10. On a 6+, shuffle the hit location deck (do not shuffle unresolved hit locations).<br/>Limit, once per round.",
        "expansion": "Dragon King",
    },
    "katana_mastery": {
        "name": "Mastery - Katana",
        "desc": "When a survivor reaches Katana Mastery, they leave the settlement forever, heeding the call of the sstorm to hone their art.<br/>Before the master leaves, you may nominate a survivor. Set that survivor's weapon type to Katana and their weapon proficiency level to 1.",
        "expansion": "Sunstalker",
    },
    "katar_mastery": {
        "name": "Mastery - Katar",
        "desc": "If you are a Katar Master, gain a <i>+1 evasion</i> token on a <b>perfect hit</b> with a katar. When you are knocked down, remove all +1 evasion tokens.",
    },
    "bow_mastery": {
        "name": "Mastery - Bow",
        "desc": "If you are a Bow Master, all bows in your gear grid gain <b>Deadly 2</b>. In addition, ignore <b>cumbersome</b> on all Bows.",
    },
    "twilight_sword_mastery": {
        "name": "Mastery - Twilight Sword",
        "desc": "Any Survivor who attains Twilight Sword Mastery leaves the settlement forever in pursuit of a higher purpose. Remove them from the settlement's population. You may place the master's Twilight Sword in another survivor's gear grid or archive it.",
        "excluded_campaigns": ["People of the Stars","People of the Sun"],
    },
    "axe_mastery": {
        "name": "Mastery - Axe",
        "desc": "When an Axe Master wounds a monster with an axe at a location with a persistent injury, that wound becomes a critical wound.",
    },
    "spear_mastery": {
        "name": "Mastery - Spear",
        "desc": "Whenever a Spear Master hits a monster with a Separ, they may spend 1 survival to gain the Priority Target token. If they made the hit from directly behind another survivor, that survivor gains the Priority Target token instead.",
    },
    "club_mastery": {
        "name": "Mastery - Club",
        "desc": "If you are a Club Master, all Clubs in your gear grid gain <b>Savage</b>. On a <b>Perfect hit</b> with a Club, gain <i>+3 strength</i> until the end of the attack.",
    },
    "fist_and_tooth_mastery": {
        "name": "Mastery - Fist & Tooth",
        "desc": "While a survivor is a Fist & Tooth Master, they gain <i>+2 permanent accuracy</i> and <i>+2 permanent strength</i> (they receive this bonus even when not attacking with Fist and Tooth).",
    },
    "grand_weapon_mastery": {
        "name": "Mastery - Grand Weapon",
        "desc": "When a Grand Weapon Master perfectly hits with a grand weapon, cancel all reactions for that attack.",
    },
    "whip_mastery": {
        "name": "Mastery - Whip",
        "desc": "Whip Masters gain <i>+5 strength</i> when attacking with a Whip.",
    },
    "shield_mastery": {
        "name": "Mastery - Shield",
        "desc": "When a Shield Master is adjacent to a survivor that is targeted by a monster, they may swap spaces on the baord with the survivor and become the target instead. The master must have a shield to perform this.",
    },
    "dagger_mastery": {
        "name": "Mastery - Dagger",
        "desc": "After a wounded hit location is discarded, a Dagger Master who is adjacent to the attacker and the wounded monster may spend 1 survival to re-draw the wounded hit location and attempt to wound with a dagger. Treat monster reactions on the re-drawn hit location card normally.",
    },
    "sword_mastery": {
        "name": "Mastery - Sword",
        "desc": "A Sword master gains +1 accuracy, +1 strength, and +1 speed when attacking with a Sword.",
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
        "expansion": "Sunstalker",
     },
    "scythe_specialization": {
        "name": "Specialization - Scythe",
        "desc": "When you critically wound with a scythe, roll 1d10. On a 6+, shuffle the hit location deck (do not shuffle unresolved hit locations).<br/>Limit, once per round.",
        "expansion": "Dragon King",
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

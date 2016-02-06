#!/usr/bin/env python

import assets
from models import Items

import xlwt

big_style = xlwt.easyxf("font: height 320; align: horiz centre, vert centre")
bold_style = xlwt.easyxf("font: bold on")
bold_big_style = xlwt.easyxf("font: bold on, height 320; align: horiz centre, vert centre")
caption_style = xlwt.easyxf("align: horiz centre, vert centre")
small_caption_style = xlwt.easyxf("font: height 170; align: horiz centre, vert centre")
bold_caption_style = xlwt.easyxf("font: bold on; align: horiz centre, vert centre")
bold_title_style = xlwt.easyxf("font: bold on, height 300; align: horiz centre, vert centre")
settlement_name_style = xlwt.easyxf("font: bold on, height 420; align: horiz centre, vert centre")
border_bottom_style = xlwt.easyxf("borders: bottom thin")

def add_generic_settlement_summary(sh, settlement):
    """ Updates a sheet (use the 'sh' arg) to include settlement info. """

    # column controls
    sh.col(0).width = 256 * 2
    sh.col(1).width = 256 * 8
    sh.col(2).width = 256 * 15
    sh.col(6).width = 256 * 2
    sh.col(7).width = 256 * 12
    sh.col(8).width = 256 * 12
    sh.col(9).width = 256 * 13
    sh.col(10).width = 256 * 13
    sh.col(11).width = 256 * 2
    sh.col(12).width = 256 * 18
    sh.col(13).width = 256 * 2
    sh.col(14).width = 256 * 6
    sh.col(15).width = 256 * 2
    sh.col(16).width = 256 * 6
    sh.col(17).width = 256 * 2
    sh.col(18).width = 256 * 6

    # sheet.write_merge(top_row, bottom_row, left_column, right_column, 'Long Cell')

    # survival limit
    sh.write_merge(1, 3, 1, 1, settlement["survival_limit"], bold_big_style)
    sh.write(2, 2, "Survival Limit", bold_caption_style)

    # settlement name
    sh.write_merge(0, 2, 4, 9, settlement["name"], settlement_name_style)

    # pop and death count
    sh.write_merge(5, 7, 1, 1, settlement["population"], big_style)
    sh.write(6, 2, "Population", caption_style)
    sh.write_merge(9, 11, 1, 1, settlement["death_count"], big_style)
    sh.write(10, 2, "Death Count", caption_style)

    # lost settlements
    sh.write_merge(13, 15, 1, 1, settlement["lost_settlements"], big_style)
    sh.write(14, 2, "Lost Settlements", caption_style)

    # milestones
    sh.write_merge(17, 18, 1, 5, "Milestone Story Events", bold_title_style)
    sh.write_merge(19, 19, 1, 5, "Trigger these story events when the millestone condition is met.", caption_style)

    m_text = "First child is born"
    sh.write_merge(21,21,2,3, m_text)
    sh.write_merge(21,21,4,5, "Principle: New Life", bold_style)
    if m_text in settlement["milestone_story_events"]:
        sh.write(21,1, "X", bold_caption_style)

    m_text = "First time death count is updated"
    sh.write_merge(22,22,2,3, m_text)
    sh.write_merge(22,22,4,5, "Principle: Death", bold_style)
    if m_text in settlement["milestone_story_events"]:
        sh.write(22,1, "X", bold_caption_style)

    m_text = "Population reaches 15"
    sh.write_merge(23,23,2,3, m_text)
    sh.write_merge(23,23,4,5, "Principle: Society", bold_style)
    if m_text in settlement["milestone_story_events"]:
        sh.write(23,1, "X", bold_caption_style)

    m_text = "Settlement has 5 innovations"
    sh.write_merge(24,24,2,3, m_text)
    sh.write_merge(24,24,4,5, "Hooded Knight", bold_style)
    if m_text in settlement["milestone_story_events"]:
        sh.write(24,1, "X", bold_caption_style)

    m_text = "Population reaches 0"
    sh.write_merge(25,25,2,3, "Population reaches 0")
    sh.write_merge(25,25,4,5, "Game Over", bold_style)
    if m_text in settlement["milestone_story_events"]:
        sh.write(25,1, "X", bold_caption_style)


    # principles
    sh.write_merge(30, 31, 1, 5, "Principles", bold_title_style)
    sh.write_merge(32, 32, 1, 5, "The settlement's established principles", caption_style)

    sh.write_merge(34,34,1,2, "New Life", bold_style)
    for p in ["Survival of the Fittest","Protext the Young"]:
        if p in settlement["principles"]:
            sh.write_merge(34,34,3,4, p)
    sh.write_merge(35,35,1,2, "Death", bold_style)
    for p in ["Cannibalize","Graves"]:
        if p in settlement["principles"]:
            sh.write_merge(35,35,3,4, p)
    sh.write_merge(36,36,1,2, "Society", bold_style)
    for p in ["Collective Toil","Accept Darkness"]:
        if p in settlement["principles"]:
            sh.write_merge(36,36,3,4, p)
    sh.write_merge(37,37,1,2, "Conviction", bold_style)
    for p in ["Barbaric","Romantic"]:
        if p in settlement["principles"]:
            sh.write_merge(37,37,3,4, p)

    # innovations
    sh.write_merge(4,5,7,8, "Innovations", bold_title_style)
    row = 6
    for innovation in sorted(settlement["innovations"]):
        sh.write_merge(row,row,7,8,innovation)
        row += 1
    # locations
    sh.write_merge(4,5,9,10, "Locations", bold_title_style)
    row = 6
    for location in sorted(settlement["locations"]):
        sh.write_merge(row,row,9,10,location)
        row += 1
    # quarries
    sh.write_merge(30,31,7,8, "Quarries", bold_title_style)
    row=32
    for quarry in sorted(settlement["quarries"]):
        sh.write_merge(row,row,7,8,quarry)
        row += 1

    # defeated monsters
    sh.write_merge(30,31,9,10, "Defeated Monsters", bold_title_style)
    row=32
    monst_dict = {}
    for monst in sorted(settlement["defeated_monsters"]):
        if monst not in monst_dict.keys():
            monst_dict[monst] = 1
        else:
            monst_dict[monst] += 1
    pretty_monst_list = []
    for monst in sorted(monst_dict.keys()):
        if monst_dict[monst] == 1:
            pretty_monst_list.append("%s" % monst)
        else:
            pretty_monst_list.append("%s x%s" % (monst, monst_dict[monst]))
    for monst in pretty_monst_list:
        sh.write_merge(row,row,9,10,monst)
        row += 1

    # nemesis monsters
    sh.write_merge(4,5,12,18, "Nemesis Monsters", bold_title_style)
    row=6
    for nemesis in sorted(settlement["nemesis_monsters"].keys()):
        col=12
        sh.write(row,col,nemesis)
        for level in ["Lvl 1", "Lvl 2", "Lvl 3"]:
            col += 1
            if level in settlement["nemesis_monsters"][nemesis]:
                sh.write(row,col,"X",bold_caption_style)
            col += 1
            sh.write(row,col,level)
        row += 1

def add_fixed_position_storage(sh, storage):
    """ Creates a storage sheet with fixed positions for all locations. """

    storage_dict = {}
    for item_key in storage:
        if item_key not in storage_dict.keys():
            storage_dict[item_key] = 1
        else:
            storage_dict[item_key] += 1
    location_dict = {}
    for item_key in storage_dict.keys():
        item_location = "Custom"
        if item_key in Items.get_keys():
            item_dict = Items.get_asset(item_key)
            item_location = item_dict["location"]
        if item_location not in location_dict.keys():
            location_dict[item_location] = {item_key: storage_dict[item_key]}
        else:
            location_dict[item_location][item_key] = storage_dict[item_key]

    # column widths
    sh.col(0).width = 256 * 23
    sh.col(1).width = 256 * 3
    sh.col(2).width = 256 * 1
    sh.col(3).width = 256 * 23
    sh.col(4).width = 256 * 3
    sh.col(5).width = 256 * 1
    sh.col(6).width = 256 * 20
    sh.col(7).width = 256 * 3
    sh.col(8).width = 256 * 1
    sh.col(9).width = 256 * 22
    sh.col(10).width = 256 * 3
    sh.col(11).width = 256 * 1
    sh.col(12).width = 256 * 20
    sh.col(13).width = 256 * 3
    sh.col(14).width = 256 * 1
    sh.col(15).width = 256 * 20
    sh.col(16).width = 256 * 3
    sh.col(17).width = 256 * 1
    sh.col(18).width = 256 * 20
    sh.col(19).width = 256 * 3
    sh.col(20).width = 256 * 1


    loc_coords = {
        "Basic Resources": (0,1,0,1),
        "Strange Resources": (9,10,0,1),
        "Vermin": (20,21,0,1),
        "Unique Items": (29,30,0,1),
        "White Lion Resources": (0,1,3,4),
        "Screaming Antelope Resources": (12,13,3,4),
        "Phoenix Resources": (29,30,3,4),
        "Starting Gear": (0,1,6,7),
        "Bone Smith": (5,6,6,7),
        "Skinnery": (15,16,6,7),
        "Organ Grinder": (26,27,6,7),
        "Catarium": (0,1,9,10),          # 15 items
        "Weapon Crafter": (18,19,9,10),
        "Leather Worker": (29,30,9,10),
        "Stone Circle": (0,1,12,13),
        "Blacksmith": (16,17,12,13),
        "Mask Maker": (32,33,12,13),
        "Barber Surgeon": (0,1,15,16),
        "Plumery": (10,11,15,16),
        "Custom": (0,1,18,19),
    }

    for loc in loc_coords.keys():
        c = loc_coords[loc]
        pretty_loc = loc
        if loc == "White Lion Resources":
            pretty_loc = "WL Resources"
        elif loc == "Screaming Antelope Resources":
            pretty_loc = "SA Resrouces"
        sh.write_merge(c[0],c[1],c[2],c[3], pretty_loc, bold_title_style)
        row = c[1] + 1
        if loc in location_dict.keys():
            for item_key in sorted(location_dict[loc].keys()):
                sh.write(row,c[2], item_key)
                sh.write(row,c[2]+1, location_dict[loc][item_key], caption_style)
                row += 1


def add_generic_survivor(sh, survivor_object):
    """ """
    survivor = survivor_object.survivor

    sh.col(0).width = 256 * 2
    sh.col(1).width = 256 * 8
    sh.col(4).width = 256 * 8
    sh.col(5).width = 256 * 8
    sh.col(6).width = 256 * 8
    sh.col(7).width = 256 * 8
    sh.col(8).width = 256 * 8
    sh.col(9).width = 256 * 8
    sh.col(10).width = 256 * 8
    sh.col(11).width = 256 * 8
    sh.col(12).width = 256 * 8

    sh.write_merge(0, 2, 5, 10, "%s [%s]" % (survivor["name"], survivor["sex"]), settlement_name_style)
    sh.write_merge(3, 3, 5, 10, ", ".join(survivor["epithets"]), caption_style)

    # hunt xp
    sh.write_merge(1, 3, 12, 12, survivor["hunt_xp"], bold_big_style)
    sh.write(2, 13, "Hunt XP", bold_caption_style)

    sh.write_merge(5,5,13,14, "Weapon Proficiency:", bold_caption_style)
    sh.write_merge(6,6,13,14, survivor["weapon_proficiency_type"], caption_style)
    sh.write_merge(5,7,12,12, survivor["Weapon Proficiency"], big_style)

    # survival
    sh.write_merge(1, 3, 1, 1, survivor["survival"], bold_big_style)
    sh.write(2, 2, "Survival", bold_caption_style)

    if "cannot_spend_survival" in survivor.keys():
        sh.write(5,1, "X", bold_caption_style)
    sh.write_merge(5,5,2,3, "Cannot spend survival", caption_style)

    row=7
    for action in ["Dodge", "Encourage", "Surge", "Dash"]:
        if action in survivor_object.get_survival_actions():
            sh.write(row, 1, "X", bold_caption_style)
        sh.write(row,2, action)
        row += 1

    # stat boxes
    col=5
    for stat in ["Movement","Accuracy","Strength","Evasion","Luck","Speed"]:
        sh.write_merge(5,7,col,col, survivor[stat], bold_big_style)
        sh.write(8,col, stat, small_caption_style)
        col += 1

    # insanity, courage, understanding
    col=5
    for stat in ["Courage", "Understanding"]:
        sh.write_merge(10,12,col,col, survivor[stat], bold_big_style)
        sh.write_merge(13,13,col,col+1, stat, small_caption_style)
        col += 2

    # hit boxes (because why not?)
    sh.write_merge(13, 15, 1, 1, survivor["Insanity"], big_style)
    sh.write(14,2, "Brain", caption_style)
    sh.write(16, 1, "Insanity", small_caption_style)

    row=18
    for hit_box in ["Head", "Arms", "Body", "Waist", "Legs"]:
        sh.write_merge(row, row+2, 1,1, survivor[hit_box], big_style)
        sh.write(row+1, 2, hit_box, caption_style)
        row += 4

    #fa's, disorders, abilities/impairments
    row=17
    for t in [("Fighting Arts","fighting_arts"),("Disorders","disorders"),("Abilities & Impairments","abilities_and_impairments")]:
        pretty_name, asset = t
        sh.write_merge(row,row+1, 4,7, pretty_name, bold_title_style)
        asset_row = row+2
        for a in survivor[asset]:
            sh.write_merge(asset_row,asset_row,4,7, a)
            asset_row += 1
        row += 6

    row=17
    for misc_attrib in ["dead","retired","cannot_use_fighting_arts","skip_next_hunt"]:
        sh.write_merge(row,row,10,12, misc_attrib.replace("_"," ").capitalize())
        if misc_attrib in survivor.keys():
            sh.write(row,9,"X", bold_caption_style)
        row+=1


def add_timeline(sh, timeline):
    """ Creates a timeline worksheet. """

    sh.col(0).width = 256 * 5
    sh.col(1).width = 256 * 30
    sh.col(2).width = 256 * 30
    sh.col(3).width = 256 * 30
    sh.col(4).width = 256 * 30
    sh.col(5).width = 256 * 30

    # write the headline
    sh.write(0, 0, "LY", bold_title_style)
    sh.write(0, 1, "Quarries", bold_title_style)
    sh.write(0, 2, "Story Events", bold_title_style)
    sh.write(0, 3, "Settlement Events", bold_title_style)
    sh.write(0, 4, "Nemesis Encounter", bold_title_style)
    sh.write(0, 5, "Custom Events", bold_title_style)

    row = 1
    for year in timeline:
        sh.write(row, 0, year["year"])
        col = 1
        for event_type in ["quarry_event", "story_event", "settlement_event", "nemesis_encounter", "custom"]:
            if event_type not in year.keys():
                event_string = ""
            elif type(year[event_type]) == list:
                event_string = ", ".join(year[event_type])
            else:
                event_string = year[event_type]
            sh.write(row, col, event_string)
            col += 1
        row += 1


def xls(settlement, survivors=[], session_object=None):
    """ The export function for creating Excel spreadsheets. """

    book = xlwt.Workbook()
    settlement_ws = book.add_sheet(settlement["name"])
    add_generic_settlement_summary(settlement_ws, settlement)
    storage_ws = book.add_sheet("Storage")
    add_fixed_position_storage(storage_ws, settlement["storage"])
    timeline_ws = book.add_sheet("Timeline")
    add_timeline(timeline_ws, settlement["timeline"])
    tab_titles = {}
    for survivor in survivors:
        tab_title = "%s %s %s" % (survivor["sex"], survivor["name"], survivor["hunt_xp"])
        if tab_title in tab_titles.keys():
            tab_titles[tab_title] += 1
            tab_title = "%s (%s)" % (tab_title, tab_titles[tab_title]-1)
        else:
            tab_titles[tab_title] = 1
        survivor_ws = book.add_sheet(tab_title)
        add_generic_survivor(survivor_ws, assets.Survivor(survivor_id=survivor["_id"], session_object=session_object))


    return book

#!/usr/bin/env python

from bson.objectid import ObjectId
from optparse import OptionParser

import html
from utils import mdb
from models import Quarries, Nemeses

def kill_board(return_type=None, admin=False):
    """ Creates a dictionary showing kills by monster type. """
    kill_list = []
    all_settlements = mdb.settlements.find()
    for settlement in all_settlements:
        for m in settlement["defeated_monsters"]:
            kill_list.append(m)

    monsters = {"Other": {"sort_order": 99, "token": "OTHER", }}
    others = []
    for model in [Quarries, Nemeses]:
        monsters.update(model.game_assets)
    for m in monsters:
        monsters[m]["kills"] = 0
        monsters[m]["name"] = m

    for kill in kill_list:
        categorized = False
        k_tokenized = kill.upper().split()
        for monster in monsters.keys():
            if monsters[monster]["token"] in k_tokenized:
                categorized = True
                monsters[monster]["kills"] += 1
        if not categorized:
            others.append(kill)
            monsters["Other"]["kills"] += 1

    sorted_monsters = {}
    for m in monsters:
        sorted_monsters[monsters[m]["sort_order"]] = monsters[m]

    if return_type == "html_table_rows":
        output = ""
        for numerical_key in sorted(sorted_monsters.keys()):
            monst_dict = sorted_monsters[numerical_key]
            monst_html = html.dashboard.kill_board_row.safe_substitute(monster = monst_dict["name"], kills = monst_dict["kills"])
            output += monst_html
        if admin:
            output += html.dashboard.kill_board_foot.safe_substitute(other_list = ",".join(sorted(others)))
        return output

    return sorted_monsters

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-k", dest="kill_board", help="Run the kill_board func and print its contents.", default=False, action="store_true")
    (options, args) = parser.parse_args()

    if options.kill_board:
        print kill_board()

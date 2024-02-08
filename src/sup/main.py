"""
TODO: 
    special case: Liquid D-3 & MK-7 -- has d-3 and k-mk7
    special case: K Complex has K1, MK-4 and MK-7 in it
"""

import collections 
import json
import pathlib as pl
import tomllib


ORDERED_SUPPS_FP = pl.Path("inventory.json")
SUPP_CONSUMPTION_FP = pl.Path("supps.toml")


def load_config():
    return tomllib.loads(SUPP_CONSUMPTION_FP.read_text())


def load_ordered_supps(user_id: str) -> list[dict]:
    return json.loads(ORDERED_SUPPS_FP.read_text())


CONFIG = load_config()
ALIASES = CONFIG["product_aliases"]

ordered_supps = load_ordered_supps(user_id)

for i in CONFIG["supps"]:
    for ordered_supp in ordered_supps:
        if i["name"].lower() in ordered_supp["name"].lower():
            ALIASES[ordered_supp["name"]] = i["name"]

ALIASES_REV = {v: k for k, v in ALIASES.items()}


def load_inventory(user_id: str):
    inventory = collections.defaultdict(list)
    for s in load_ordered_supps(user_id):
        if s["name"] not in CONFIG["discontinued"]:
            inventory[ALIASES[s["name"]]].append(s)
    return inventory

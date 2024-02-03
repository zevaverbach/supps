import collections
from dataclasses import dataclass
import json
import pathlib as pl
import tomllib
import typing as t

from rich.pretty import pprint as print



def load_config():
    return tomllib.loads(pl.Path("supps.toml").read_text())


def load_ordered_supps():
    return json.loads(pl.Path('supps.json').read_text())


ALIASES = {
        'Naturally Sourced Vitamin E': "vitamin e",
        "Natural Vitamin K2 MK-7 with MenaQ7": "k2-mk7",
        "Liquid D-3 & MK-7": "d-3",
        "Calcium AKG Longevity": "ca-akg",
        "MK-7 Vitamin K-2": "k2-mk7",
        "Optimized Folate": "methyl folate",
        "Extend-Release Magnesium": "magnesium slow release",
        "Crucera-SGS": "broccomax",
        "B-50": "b complex",
        "Vitamin K2, MK-4 (Menatetrenone)": "k2-mk4",
        "Super K": "k1",
        "Ultimate Omega, Lemon": "epa/dha",
        }

ALIASES_REV = {v: k for k, v in ALIASES.items()}

class Missing(Exception):
    pass


def validate_matches() -> None:
    missing = []
    config = load_config()

    ordered_supp_names_lower = [i['name'].lower() for i in load_ordered_supps()]
    for i in config['supps']:
        if (
                not any(i['name'].lower() in ordered_supp_name for ordered_supp_name in ordered_supp_names_lower)
                and i['name'].lower() not in ALIASES_REV
                ):
            missing.append(i['name'])

    if missing:
        raise Missing(', '.join(missing))


@dataclass
class Supp:
    name: str
    morning: int | float = 0
    lunch: int | float = 0
    dinner: int | float = 0
    bedtime: int | float = 0
    per_week: int = 7
    units: t.Literal["caps", "mg", "g", "ml", "mcg", "iu"] = "mg"
    winter_only: bool = False


# special case: Liquid D-3 & MK-7 -- has d-3 and k-mk7
# special case: K Complex has K1, MK-4 and MK-7 in it

"""
{'orderDate': '2024-01-04T23:00:00.000Z',
  'name': 'Naturally Sourced Vitamin E',
  'quantity': 100,
  'quantityUnits': 'caps',
  'servingUnit': 'mg',
  'numUnitsInServing': 134,
  'numBottles': 2}]
"""

missing_names = validate_matches()

if missing_names:
    print(missing_names)

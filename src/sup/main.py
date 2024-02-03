"""
TODO: 
    special case: Liquid D-3 & MK-7 -- has d-3 and k-mk7
    special case: K Complex has K1, MK-4 and MK-7 in it
"""
from dataclasses import dataclass
import json
import pathlib as pl
import tomllib
import typing as t


ORDERED_SUPPS_FP = pl.Path("inventory.json")
SUPP_CONSUMPTION_FP = pl.Path("supps.toml")


def load_config():
    return tomllib.loads(SUPP_CONSUMPTION_FP.read_text())


def load_ordered_supps() -> list[dict]:
    return json.loads(ORDERED_SUPPS_FP.read_text())


CONFIG = load_config()
ALIASES = CONFIG["product_aliases"]

ordered_supps = load_ordered_supps()

for i in CONFIG["supps"]:
    for ordered_supp in ordered_supps:
        if i["name"].lower() in ordered_supp["name"].lower():
            ALIASES[ordered_supp["name"]] = i["name"]

ALIASES_REV = {v: k for k, v in ALIASES.items()}


def load_inventory():
    return {
        ALIASES[s["name"]]: s
        for s in load_ordered_supps()
        if s["name"] not in CONFIG["discontinued"]
    }


class Missing(Exception):
    pass


def validate_matches() -> None:
    missing = []

    ordered_supp_names_lower = [i["name"].lower() for i in load_ordered_supps()]
    for i in CONFIG["supps"]:
        if (
            not any(
                i["name"].lower() in ordered_supp_name
                for ordered_supp_name in ordered_supp_names_lower
            )
            and i["name"].lower() not in ALIASES_REV
        ):
            missing.append(i["name"])

    if missing:
        raise Missing(", ".join(missing))


@dataclass
class Supp:
    name: str
    morning: int | float = 0
    lunch: int | float = 0
    dinner: int | float = 0
    bedtime: int | float = 0
    days_per_week: int = 7
    units: t.Literal["caps", "mg", "g", "ml", "mcg", "iu"] = "mg"
    winter_only: bool = False

    def __mul__(self, other: int) -> float:
        return self.quantity_per_day * other

    @property
    def quantity_per_day(self) -> float:
        return (
            sum([self.morning, self.lunch, self.dinner, self.bedtime])
            * 7
            / self.days_per_week
        )


def main():
    missing_names = validate_matches()
    if missing_names:
        print(missing_names)


if __name__ == "__main__":
    main()

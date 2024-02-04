"""
{'orderDate': '2024-01-04T23:00:00.000Z',
  'name': 'Naturally Sourced Vitamin E',
  'quantity': 100,
  'quantityUnits': 'caps',
  'servingUnit': 'mg',
  'numUnitsInServing': 134,
  'numBottles': 2}]
"""

import datetime as dt
import json
import math
import toml
from typing_extensions import Annotated

import typer

from sup.main import (
    load_ordered_supps,
    ORDERED_SUPPS_FP,
    load_config,
    SUPP_CONSUMPTION_FP,
    load_inventory,
    Supp,
    CONFIG,
    ALIASES_REV,
)

app = typer.Typer()


class UnitMismatch(Exception):
    pass


class Missing(Exception):
    pass


def get_qty_inventory(supp: Supp, inventory: dict, next_fill_date: dt.date) -> int:
    inventory_order_date = dt.datetime.strptime(
        inventory["orderDate"][:10], "%Y-%m-%d"
    ).date()
    num_days_since_bought = (next_fill_date - inventory_order_date).days
    if inventory["servingUnit"] != supp.units:
        raise UnitMismatch(inventory, supp)

    inv = (
        inventory["quantity"] * inventory["numBottles"] * inventory["numUnitsInServing"]
    ) - (supp * num_days_since_bought)
    if inv < 0:
        return 0
    return inv


def get_num_winter_days_starting(num_days: int, starting: dt.date) -> int:
    # dec 21 to mar 20
    winter_starts = dt.date(starting.year, 12, 21)
    if starting <= winter_starts:
        num_days_til_winter = (winter_starts - starting).days
        if num_days_til_winter > num_days:
            return 0
        return num_days - num_days_til_winter

    winter_ends = dt.date(starting.year, 3, 2)
    if starting >= winter_ends:
        winter_starts = dt.date(starting.year + 1, 12, 21)
        num_days_til_winter = (winter_starts - starting).days
        if num_days_til_winter > num_days:
            return 0
        return num_days - num_days_til_winter

    winter_ends = dt.date(starting.year + 1, 3, 2)
    if starting <= winter_ends:
        num_days_til_winter_ends = (winter_ends - starting).days
        if num_days_til_winter_ends > num_days:
            return num_days
        return num_days_til_winter_ends
    raise Exception


@app.command()
def status():
    """
    check if there's enough inventory for the next fill-up; if not, what to order?

    TODO: this doesn't seem to sense pending orders which have been added to inventory.json
          maybe because the delivery date is in the present/future?
    """
    validate_matches()

    config = load_config()

    num_days_of_inventory_needed = config["FILL_EVERY_X_DAYS"]
    next_fill_date = config["LAST_FILL_DATE"] + dt.timedelta(
        num_days_of_inventory_needed
    )
    inventory = load_inventory()

    needs = []

    num_days_of_inventory_needed_winter = get_num_winter_days_starting(
        num_days_of_inventory_needed, next_fill_date
    )

    for sup in config["supps"]:
        sup_inst = Supp(**sup)
        if sup_inst.winter_only:
            qty_needed = sup_inst * num_days_of_inventory_needed_winter
        else:
            qty_needed = sup_inst * num_days_of_inventory_needed

        try:
            inv = inventory[sup_inst.name.lower()]
        except KeyError:
            print(f"no hit for key '{sup_inst.name}'")
            qty_of_inventory = 0
            needs.append((sup_inst.name, 0, float('inf')))
            continue

        qty_of_inventory = get_qty_inventory(sup_inst, inv, next_fill_date)
        print(sup_inst.name, int(qty_of_inventory / inv["numUnitsInServing"]))

        net_need = int(qty_needed - qty_of_inventory)
        if net_need > 0:
            num_units_needed = net_need / inv["numUnitsInServing"]  # type: ignore
            num_bottles_needed = int(math.ceil(num_units_needed / inv["quantity"]))  # type: ignore
            needs.append((sup_inst.name, int(num_units_needed), num_bottles_needed))

    if needs:
        print()
        print(f"The next fill-up is on {next_fill_date}, and you won't have enough of:")
        print()
        for name, units_needed, num_bottles in needs:
            bottle = "bottle" if num_bottles == 1 else "bottles"
            print(
                f"{name} (need {units_needed} units, which is {num_bottles} {bottle})"
            )
        print()


@app.command()
def fill():
    """reset 'next fill' clock"""
    validate_matches()
    config = load_config()
    today = dt.date.today()
    config["LAST_FILL_DATE"] = today.strftime("%Y-%m-%d")
    # TODO: make sure this toml library doesn't add quotes to this entry, it
    #       makes it so when reading it doesn't get parsed to a date
    fill_every_x_days = config["FILL_EVERY_X_DAYS"]
    save_config(config)
    print(
        f"Okay, next fill-up set to {today + dt.timedelta(days=fill_every_x_days)} (configured in `sup.toml`::FILL_EVERY_X_DAYS)"
    )


@app.command()
def add(
    name: Annotated[str, typer.Option(prompt=True)],
    quantity: Annotated[int, typer.Option(prompt=True)],
    serving_quantity: Annotated[int, typer.Option(prompt=True)],
    serving_unit: Annotated[str, typer.Option(prompt=True)] = "mg",
    quantity_unit: Annotated[str, typer.Option(prompt=True)] = "caps",
    date: (
        Annotated[dt.datetime, typer.Option(help="(today)", prompt=True)] | None
    ) = None,
    number_of_bottles: Annotated[int, typer.Option(prompt=True)] = 1,
) -> None:
    """add to inventory"""
    if date is None:
        date = dt.datetime.now().date()  # type: ignore
    else:
        date = date.date()  # type: ignore
    ordered_supps = load_ordered_supps()
    order_dict = dict(
        name=name,
        quantity=quantity,
        numUnitsInServing=serving_quantity,
        servingUnit=serving_unit,
        quantityUnit=quantity_unit,
        orderDate=date.strftime("%Y-%m-%d"),  # type: ignore
        numBottles=number_of_bottles,
    )
    ordered_supps.append(order_dict)
    save_ordered_supps(ordered_supps)
    print(f"added {order_dict} to {ORDERED_SUPPS_FP}")


def save_ordered_supps(ordered_supps: list[dict]) -> None:
    ORDERED_SUPPS_FP.write_text(json.dumps(ordered_supps, indent=2))


def save_config(config: dict) -> None:
    SUPP_CONSUMPTION_FP.write_text(toml.dumps(config))


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

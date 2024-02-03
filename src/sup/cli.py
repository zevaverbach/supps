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
)

app = typer.Typer()


class UnitMismatch(Exception):
    pass


def get_qty_inventory(supp: Supp, inventory: dict) -> int:
    inventory_order_date = dt.datetime.strptime(
        inventory["orderDate"][:10], "%Y-%m-%d"
    ).date()
    num_days_since_bought = (dt.date.today() - inventory_order_date).days
    if inventory["servingUnit"] != supp.units:
        raise UnitMismatch(inventory, supp)

    return (inventory["quantity"] * inventory["numBottles"]) - (
        supp * num_days_since_bought
    )


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
    """check if there's enough inventory for the next fill-up; if not, what to order?"""
    config = load_config()
    num_days_of_inventory_needed = config["FILL_EVERY_X_DAYS"]
    next_fill_date = config["LAST_FILL_DATE"] + dt.timedelta(
        num_days_of_inventory_needed
    )
    inventory = load_inventory()
    needs = []
    for sup in config["supps"]:
        sup_inst = Supp(**sup)
        if sup_inst.winter_only:
            num_days_of_inventory_needed = get_num_winter_days_starting(
                num_days_of_inventory_needed, next_fill_date
            )
        qty_needed = sup_inst * num_days_of_inventory_needed
        try:
            inv = inventory[sup_inst.name]
        except KeyError:
            qty_of_inventory = 0
        else:
            qty_of_inventory = get_qty_inventory(sup_inst, inv)
        net_need = qty_needed - qty_of_inventory
        if net_need > 0:
            needs.append((sup_inst.name, net_need, sup_inst.units))
    if needs:
        print(f"The next fill-up is on {next_fill_date}, and you won't have enough of:")
        for name, quant, units in needs:
            print(f"{name} (need {quant} {units})")


@app.command()
def fill():
    """reset 'next fill' clock"""
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
    date: Annotated[dt.datetime, typer.Option(help="(today)", prompt=True)]
    | None = None,
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

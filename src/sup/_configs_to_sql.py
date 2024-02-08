import collections
from dataclasses import asdict
import datetime as dt
import hashlib
import json
import pathlib as pl
import tomllib

from mysql.connector.errors import IntegrityError

from sup.commands import (
        add_user_supp_consumption, 
        add_inventory, 
        add_product, 
        add_alias,
        set_fill_every_x_days,
        set_last_fill_date,
        create_user,
)
from sup.models import Supp
from sup.queries import product_is_in_products_table, alias_exists, inventory_exists, consumption_exists
from sup.sql_funcs import commit

def load_config():
    return tomllib.loads(pl.Path('supps.toml').read_text())

CONFIG = load_config()


def transfer_inventory_to_sql():
    inventory = json.loads(pl.Path('inventory.json').read_text())
    for i in inventory:
        add_inventory(
            user_id='zev@averba.ch', 
            product_name=i['name'], 
            order_date=i['orderDate'][:10], 
            num_bottles=i['numBottles']
        )


def populate_products():
    inventory = json.loads(pl.Path('inventory.json').read_text())
    for i in inventory:
        try:
            add_product(
                name=i['name'],
                quantity=i['quantity'],
                num_units_in_serving=i['numUnitsInServing'],
                quantity_units=i['quantityUnits'],
                serving_units=i['servingUnit'],
            )
        except KeyError:
            print(i)
            raise
        except IntegrityError:
            print('already exists')
            continue
        commit()


def transfer_supps_consumption_toml_to_sql() -> None:
    aliases = {v: k for k, v in CONFIG['product_aliases'].items()}
    product_names = [i['name'] for i in json.loads(pl.Path('inventory.json').read_text())]
    for sup in CONFIG["supps"]:
        si = Supp(**sup)
        si_dict = asdict(si)
        _name = si_dict['name']
        del si_dict['name']
        name = None
        if _name.lower() in aliases:
            name = aliases[_name.lower()]
        else:
            for pn in product_names:
                if _name.lower() in pn.lower():
                    name = pn
                    break
        name = name or _name
        print(name)
        add_user_supp_consumption(name=name, user_id="zev@averba.ch", **si_dict)
    commit()


def transfer_config_to_sql():
    """fill every x days and last fill"""
    fill_every_x_days = CONFIG['FILL_EVERY_X_DAYS']
    last_fill_date = CONFIG['LAST_FILL_DATE']
    set_fill_every_x_days(value=fill_every_x_days, user_id="zev@averba.ch")
    set_last_fill_date(value=last_fill_date, user_id="zev@averba.ch")
    commit()


def transfer_aliases_to_sql():
    aliases = CONFIG['product_aliases']
    for name, alias in aliases.items():
        add_alias("zev@averba.ch", name, alias)
    commit()


def validate_products_against_toml():
    inventory = json.loads(pl.Path('inventory.json').read_text())
    for i in inventory:
        if not product_is_in_products_table(name=i['name'], q=round(i['quantity']), num_units=i['numUnitsInServing']):
            raise Exception


def do_create_user():
    email = "zev@averba.ch"
    pw = "@m_6Lwx.CjqvfwG@hmT"
    first_name = "Zev"
    last_name = "Averbach"
    pw_hash = hashlib.new("SHA256")
    pw_hash.update(pw.encode())
    create_user(email, pw_hash.hexdigest(), first_name, last_name, dt.date.today(), 30)
    commit()
    print("okay, created user")


def validate_product_aliases():
    aliases = CONFIG['product_aliases']
    for name, alias in aliases.items():
        if not alias_exists(name=name, alias=alias, user_id="zev@averba.ch"):
            raise Exception


def validate_inventory():
    inventory = json.loads(pl.Path('inventory.json').read_text())
    for i in inventory:
        if not inventory_exists(
                user_id="zev@averba.ch", 
                product_name=i['name'], 
                order_date=i['orderDate'][:10],
                quantity=i['quantity'],
                serving_q=i["numUnitsInServing"],
            ):
            raise Exception
            # PRIMARY KEY (user_id, product_id, order_date)

def validate_consumption():
    """
    Something is wrong here; several of the items in supps.toml are missing from
    the consumption table.
    """
    aliases = collections.defaultdict(list)
    for k, v in CONFIG['product_aliases'].items():
        aliases[v].append(k)
    product_names = [i['name'] for i in json.loads(pl.Path('inventory.json').read_text())]
    for sup in CONFIG["supps"]:
        si = Supp(**sup)
        si_dict = asdict(si)
        _name = si_dict['name']
        del si_dict['name']
        name = None
        names = None
        if _name in aliases:
            names = aliases[_name]
            print(f"{names=}")
        else:
            for pn in product_names:
                if _name.lower() in pn.lower():
                    name = pn
                    break
        if names:
            if not any(consumption_exists(name=n, user_id="zev@averba.ch", **si_dict) for n in names):
                raise Exception
        else:
            name = name or _name
            if not consumption_exists(name=name, user_id="zev@averba.ch", **si_dict):
                raise Exception


# do_create_user()
# populate_products()
# transfer_inventory_to_sql()
# transfer_aliases_to_sql()
# transfer_supps_consumption_toml_to_sql()
# transfer_config_to_sql()
# validate_products_against_toml()
# validate_product_aliases()
# validate_inventory()
# validate_consumption()

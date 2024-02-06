from dataclasses import asdict
import json
import pathlib as pl
import tomllib

from sup.commands import add_user_supp_consumption
from sup.models import Supp
from sup.queries import get_product_id_from_alias


def transfer_inventory_to_sql():
    ...


def transfer_supps_consumption_toml_to_sql():
    toml = tomllib.loads(pl.Path('supps.toml').read_text())
    for sup in toml["supps"]:
        si = Supp(**sup)
        si_dict = asdict(si)
        name = si_dict['name']
        del si_dict['name']
        product_id = get_product_id_from_alias(name)

        add_user_supp_consumption(**si_dict)


def transfer_config_to_sql():
    """fill every x days and last fill"""
    ...

def transfer_aliases_to_sql():
    ...


transfer_config_to_sql()
transfer_aliases_to_sql()
transfer_supps_consumption_toml_to_sql()
transfer_inventory_to_sql()

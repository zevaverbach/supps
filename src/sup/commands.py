import datetime as dt
import typing as t

from sup.sql_funcs import do_query


def set_fill_every_x_days(value: int, user_id: str) -> None:
    do_query(query=f"update users set fill_every_x_days = {value} where id = '{user_id}'")


def set_last_fill_date(value: int, user_id: str) -> None:
    do_query(query=f"update users set last_fill_date = '{value}' where id = '{user_id}'")


def create_user(email: str, pw_hash: str, first_name: str, last_name: str, last_fill_date: dt.date, fill_every_x_days=30):
    do_query(commit=True,
            query="insert into users (id, pw_hash, first_name, last_name, last_fill_date, fill_every_x_days) values "
            f"('{email}', '{pw_hash}', '{first_name}', '{last_name}', '{last_fill_date}', '{fill_every_x_days}')"
            )


def add_user_supp_consumption(user_id: str, name: str, morning: int, lunch: int, dinner: int, bedtime: int, days_per_week: int, units: str, winter_only: bool):
    do_query(
        "insert into user_supplements_consumption "
        "(user_id, product_id, morning, lunch, dinner, bedtime, days_per_week, units, winter_only) "
        f"select '{user_id}', id, {morning}, {lunch}, {dinner}, {bedtime}, {days_per_week}, '{units}', {winter_only} "
        f"from products where name = '{name}'"
    )


def add_inventory(user_id: str, product_name: str, order_date: str, num_bottles: int) -> None:
    do_query(
        "insert into user_supplements_orders (user_id, product_id, order_date, num_bottles) "
        f"select '{user_id}', id, '{order_date}', {num_bottles} "
        f"from products where name = '{product_name}'"
    )


def add_product(
        name: str, 
        quantity: int, 
        quantity_units: t.Literal['caps', 'mg', 'g', 'ml', 'mcg', 'iu'], 
        serving_units: t.Literal['caps', 'mg', 'g', 'ml', 'mcg', 'iu'],
        num_units_in_serving: int,
    ):
    query = (
        "insert into products (name, quantity, quantity_units, serving_units, num_units_in_serving) values ("        
        f"'{name}', {quantity}, '{quantity_units}', '{serving_units}', {num_units_in_serving}"
        ")"
    )
    do_query(query)


def add_alias(user_id: str, name: str, alias: str) -> None:
    query = (
        "insert into user_product_aliases (user_id, product_id, alias) "
        f"select '{user_id}', id, '{alias}' "
        f"from products where name = '{name}'"
    )
    do_query(query)

import datetime as dt

from sup.sql_funcs import do_query


def create_user(email: str, pw_hash: str, first_name: str, last_name: str, last_fill_date: dt.date, fill_every_x_days=30):
    do_query(
            "insert into users (id, pw_hash, first_name, last_name, last_fill_date, fill_every_x_days) values "
            f"('{email}', '{pw_hash}', '{first_name}', '{last_name}', '{last_fill_date}', '{fill_every_x_days}')"
            )


def add_user_supp_consumption(user_id: str, product_id: int, morning: int, lunch: int, dinner: int, bedtime: int, days_per_week: int, units: str, winter_only: bool):
    do_query(
        "insert into user_supplements_consumption "
        "(user_id, product_id, morning, lunch, dinner, bedtime, days_per_week, units, winter_only) values ("
        f"('{user_id}', {product_id}, {morning}, {lunch}, {dinner}, {bedtime}, {days_per_week}, '{units}', {winter_only}"
        ")"
    )

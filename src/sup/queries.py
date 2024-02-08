from sup.sql_funcs import do_query


def get_user(user_id: str):
    return do_query(f"select * from users where id = '{user_id}'", get_result=True, return_dict=True)[0] # type: ignore


def product_is_in_products_table(name: str, q: int, num_units: int) -> bool:
    query = f"select count(*) from products where name = '{name}' and quantity = {q} and num_units_in_serving = {num_units}"
    res = do_query(get_result=True, query=query)
    if res[0][0] != 1: # type: ignore
        print(res[0][0]) # type: ignore
        return False
    return True


def alias_exists(name: str, alias: str, user_id: str) -> bool:
    query = (
        f"select count(*) from user_product_aliases where user_id = '{user_id}' "
        f"and alias = '{alias}' and product_id = (select id from products where name = '{name}')"
    )
    res = do_query(get_result=True, query=query)
    if res[0][0] != 1: # type: ignore
        print(res[0][0]) # type: ignore
        return False
    return True


def inventory_exists(user_id: str, product_name: str, order_date: str, quantity: int, serving_q: int):
    query = (
        f"select count(*) from user_supplements_orders where user_id = '{user_id}' and order_date = '{order_date}' "
        "and product_id = ("
        f"select distinct id from products where name = '{product_name}' and quantity = {quantity} "
        f"and num_units_in_serving = {serving_q}"
        ")"
    )
    res = do_query(get_result=True, query=query)
    if res[0][0] != 1: # type: ignore
        print(res[0][0]) # type: ignore
        return False
    return True


def consumption_exists(name: str, user_id: str, morning: int, lunch: int, dinner: int, bedtime: int, days_per_week: int, units: str, winter_only: bool):
    name = name.lower()
    query = (
        f"select count(*) from user_supplements_consumption where user_id = '{user_id}' and morning = {morning} "
        f"and lunch = {lunch} and dinner = {dinner} and bedtime = {bedtime} and days_per_week = {days_per_week} "
        f"and units = '{units}' and winter_only = {winter_only} "
        f"and product_id = coalesce("
        f"(select id from products where name = '{name}' limit 1), "
        f"(select product_id from user_product_aliases where alias = '{name}' and user_id = '{user_id}' limit 1)"
        ")"
    )
    res = do_query(get_result=True, query=query)
    if res[0][0] != 1: # type: ignore
        print(res[0][0]) # type: ignore
        return False
    return True

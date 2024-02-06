from sup.sql_funcs import do_query


class NoResult(Exception):
    pass


def get_product_id_from_alias(alias: str):
    res = do_query(f"select
    raise NoResult(f"no product_id for alias '{alias}'")

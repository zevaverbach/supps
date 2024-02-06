import atexit
import os

import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv


load_dotenv()

DB_NAME = os.getenv("PLANETSCALE_DATABASE")

cnx = mysql.connector.connect(
      user=os.getenv("PLANETSCALE_USERNAME"), 
      password=os.getenv("PLANETSCALE_PW"),
      host=os.getenv("PLANETSCALE_HOST"),
      database=DB_NAME,
)
cursor = cnx.cursor()

def close_everything():
    cnx.close()
    cursor.close()

atexit.register(close_everything)


def do_query(create_statement: str) -> None:
    try:
        table_name = create_statement.lower().split("create table ")[1].split(" ")[0]
    except IndexError:
        table_name = create_statement.lower().split("drop table ")[1].split(" ")[0]
    print(f"{table_name=}")
    print(create_statement)
    try:
        cursor.execute(create_statement)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
        return
    print(f"created table '{table_name}'")


def create_table_users():
    query = ("""
        create table users (
            id VARCHAR(80) NOT NULL, 
            pw_hash VARCHAR(64) NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            fill_every_x_days INTEGER NOT NULL,
            last_fill_date DATE NOT NULL,
            CONSTRAINT pk_user PRIMARY KEY (id)
    )""").strip()
    do_query(query)


def create_table_products():
    query = ("""
        create table products (
            id INT NOT NULL AUTO_INCREMENT,
            name VARCHAR(150) NOT NULL,
            quantity INT NOT NULL,
            quantity_units ENUM('caps', 'mg', 'g', 'ml', 'mcg', 'iu'),
            serving_units ENUM('caps', 'mg', 'g', 'ml', 'mcg', 'iu'),
            num_units_in_serving INT NOT NULL,
            CONSTRAINT pk_product PRIMARY KEY (id)
    )""").strip()
    do_query(query)


def create_table_product_aliases():
    query = ("""
        create table user_product_aliases (
            user_id VARCHAR(80) NOT NULL,
            product_id INT NOT NULL,
            alias VARCHAR(30) NOT NULL,
            CONSTRAINT fk_product_alias_user_id FOREIGN KEY (user_id) REFERENCES users(id),
            CONSTRAINT fk_product_alias_product_id FOREIGN KEY (product_id) REFERENCES products(id),
            CONSTRAINT pk_user_product_alias PRIMARY KEY (user_id, product_id, alias)
    )""").strip()
    do_query(query)


def create_table_user_supplements_consumption():
    query = ("""
        create table user_supplements_consumption (
            user_id VARCHAR(80) NOT NULL,
            product_id INT NOT NULL,
            morning INT DEFAULT 0,
            lunch INT NULL,
            dinner INT NULL,
            bedtime INT NULL,
            days_per_week INT DEFAULT 7,
            units ENUM('caps', 'mg', 'g', 'ml', 'mcg', 'iu'),
            winter_only BOOL DEFAULT false,
            CONSTRAINT fk_user_id FOREIGN KEY (user_id) REFERENCES users(id),
            CONSTRAINT fk_product_id FOREIGN KEY (product_id) REFERENCES products(id),
            CONSTRAINT pk_user_supplement_consumption PRIMARY KEY (user_id, product_id, morning)
    )""").strip().replace("\n", "")
    do_query(query)


def create_table_user_supplements_inventory():
    query = ("""
        create table user_supplements_orders (
            user_id VARCHAR(80) NOT NULL,
            product_id INT NOT NULL,
            order_date DATE NOT NULL,
            num_bottles INT NOT NULL,
            CONSTRAINT fk_user_supplements_orders_user_id FOREIGN KEY (user_id) REFERENCES users(id),
            CONSTRAINT fk_user_supplements_orders_product_id FOREIGN KEY (product_id) REFERENCES products(id),
            CONSTRAINT pk_user_supplement_order PRIMARY KEY (user_id, product_id, order_date)
    )""").strip()
    do_query(query)



def create_tables1():
    try:
        create_table_users()
    except Exception:
        return
    try:
        create_table_products()
    except Exception:
        do_query("drop table users")
        return

def create_tables2():
    # try:
    #     create_table_user_supplements_consumption()
    # except Exception:
    #     return
    # create_table_user_supplements_inventory()
    create_table_product_aliases()

def drop_tables():
    do_query("drop table users")
    do_query("drop table products")
    do_query("drop table user_supplements_consumption")
    do_query("drop table user_supplements_orders")


# drop_tables()
create_tables2()

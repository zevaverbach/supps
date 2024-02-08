import atexit
import os

from dotenv import load_dotenv
import mysql.connector


load_dotenv()

DB_NAME = os.getenv("PLANETSCALE_DATABASE")

cnx = mysql.connector.connect(
      user=os.getenv("PLANETSCALE_USERNAME"), 
      password=os.getenv("PLANETSCALE_PW"),
      host=os.getenv("PLANETSCALE_HOST"),
      database=DB_NAME,
)
cursor = cnx.cursor(buffered=True)
dict_cursor = cnx.cursor(dictionary=True)

def close_everything():
    cnx.close()
    cursor.close()

atexit.register(close_everything)


def do_query(query: str, get_result: bool = False, commit: bool = False, return_dict: bool = False) -> list | None:
    print(query)
    c = cursor if not return_dict else dict_cursor
    try:
        c.execute(query)
    except mysql.connector.Error as err:
        print(err.msg)
        raise
    if commit:
        cnx.commit()
    if get_result:
        return cursor.fetchall()

def commit():
    cnx.commit()

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
cursor = cnx.cursor()

def close_everything():
    cnx.close()
    cursor.close()

atexit.register(close_everything)


def do_query(query: str) -> None:
    try:
        cursor.execute(query)
    except mysql.connector.Error as err:
        print(err.msg)
        raise
    # TODO: return something if appropriate


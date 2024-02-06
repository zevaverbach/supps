import datetime as dt
import hashlib

from sup.commands import create_user


if __name__ == "__main__":
    email = input('email? ')
    pw = input('pw? ')
    first_name = input('first name? ')
    last_name = input('last name? ')
    pw_hash = hashlib.new("SHA256")
    pw_hash.update(pw.encode())
    create_user(email, pw_hash.hexdigest(), first_name, last_name, dt.date.today(), 30)
    print("okay, created user")

import logging
from pathlib import Path
from dotenv import load_dotenv
import os
import sqlite3

load_dotenv()


class Config:
    quotes_api = os.getenv("quotes_api")
    horoscope_api = os.getenv("horoscope_api")
    token = os.getenv("token")
    path = Path(__file__).parents[0]
    db_path = f'file:{path}/database.db'

    logging.basicConfig(
        filename="app.log",
        filemode="a",
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%d-%m-%y %H:%M:%S",
    )


class Database:
    db = sqlite3.connect(Config.db_path, uri=True, check_same_thread=False)

    cursor = db.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users 
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_id INTEGER,
            user_first_name VARCHAR,
            user_last_name VARCHAR,
            user_name VARCHAR
        )               
        ;''')


    @classmethod
    def add_user(cls, user):
        if not cls.check_user_is_subscriber(user):
            cls.cursor.execute(f"""
                INSERT INTO users (user_id, user_first_name, user_last_name, user_name)
                VALUES ('{user.id}', '{user.first_name}', '{user.last_name}', '{user.username}') 
            ;""")
            cls.db.commit()

    @classmethod
    def check_user_is_subscriber(cls, user):
        query = cls.cursor.execute(f"SELECT {user.id} FROM users;").fetchall()
        return bool(query)

    @classmethod
    def delete_user(cls, user):
        if cls.check_user_is_subscriber(user):
            cls.cursor.execute(f"DELETE FROM users WHERE user_id='{user.id}';")
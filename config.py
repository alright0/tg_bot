import logging
from pathlib import Path
from dotenv import load_dotenv
import os
import sqlite3
import sys

load_dotenv()


class Config:
    quotes_api = os.getenv("quotes_api")
    horoscope_api = os.getenv("horoscope_api")
    token = os.getenv("token")

    path = Path(__file__).parents[0]
    db_path = f'file:{path}/database.db'
    logs_path = path / 'logs'

    logging.basicConfig(
        filename=logs_path / "app.log",
        filemode="a",
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%d-%m-%y %H:%M:%S",
    )
    sys.stderr = open(logs_path / 'stderr.log', 'a')


class Database:
    db = sqlite3.connect(Config.db_path, uri=True, check_same_thread=False)

    cursor = db.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users 
        (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_id INTEGER,
            chat_id INTEGER,
            user_first_name VARCHAR,
            user_last_name VARCHAR,
            user_name VARCHAR
        )               
        ;''')


    @classmethod
    def add_user(cls, message):
        user = message.from_user
        chat_id = message.chat.id

        if not cls.check_user_is_subscriber(user.id):
            cls.cursor.execute(f"""
                INSERT INTO users (user_id, chat_id, user_first_name, user_last_name, user_name)
                VALUES ('{user.id}', '{chat_id}', '{user.first_name}', '{user.last_name}', '{user.username}') 
            ;""")
            logging.info(f'user: {user.id} added to db')
            return
        logging.warning(f'user: {user.id} not added to db. Already exists.')

    @classmethod
    def delete_user(cls, user_id):
        if cls.check_user_is_subscriber(user_id):
            cls.cursor.execute(f"DELETE FROM users WHERE user_id='{user_id}';")
            logging.info(f'user: {user_id} deleted from db')
            return
        logging.info(f'user: {user_id} not deleted from db. Not found in db.')

    @classmethod
    def check_user_is_subscriber(cls, user_id):
        query = cls.cursor.execute(f"SELECT * FROM users where user_id='{user_id}';").fetchall()
        return bool(query)

    @classmethod
    def get_all_subscribers(cls):
        return cls.cursor.execute('SELECT chat_id from users;').fetchall()
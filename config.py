import logging
from pathlib import Path
from dotenv import load_dotenv
import os


load_dotenv()


class Config:
    quotes_api = os.getenv('quotes_api')
    horoscope_api = os.getenv('horoscope_api')
    token = os.getenv('token')
    path = Path(__file__).parents[0]

    logging.basicConfig(
        filename="app.log",
        filemode="a",
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%d-%m-%y %H:%M:%S",
    )
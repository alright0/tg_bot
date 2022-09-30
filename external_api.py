import requests
from config import Config

config = Config()


def get_quote() -> str:
    data_dict = {"method": "getQuote", "format": "json", "lang": "ru"}
    response = requests.post(config.quotes_api, data=data_dict)

    data = response.json()
    quote = data.get("quoteText")
    author = data.get("quoteAuthor")

    return str(quote) + (f"\nАвтор: {author}" if author else "")


def get_horoscope(horoscope_sign, horoscope_period) -> str:
    response = requests.get(f"{config.horoscope_api}/{horoscope_period}/{horoscope_sign}")
    data = response.json()

    source = data.get("source")
    text = data.get("text")

    return f"**{source}**\n{text}"

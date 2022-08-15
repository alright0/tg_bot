import telebot
import requests
import random
import logging
from constants import *
from config import Config
from markup import initial_markup, horoscope_markup, random_choice_markup


config = Config()
bot = telebot.TeleBot(Config.token)

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Чего тебе?", reply_markup=initial_markup())


@bot.message_handler(content_types=["text"])
def handle_text(message):

    # вход в меню гороскопов
    if message.text == HOROSCOPE_MENU_BUTTON:
        bot.send_message(
            message.chat.id,
            random.choice(NAVIGATION_MESSAGE),
            reply_markup=horoscope_markup(),
        )
    # вход в меню ответов на вопросы
    elif message.text == RANDOM_CHOICE_MENU_BUTTON:
        bot.send_message(
            message.chat.id,
            "Задумай свой вопрос и крутани шар. Ответы 'Да', 'Нет' и все, что между ними",
            reply_markup=random_choice_markup(),
        )
    # вход в главное меню(кнорка назад)
    elif message.text == GO_BACK_BUTTON:
        bot.send_message(
            message.chat.id,
            random.choice(NAVIGATION_MESSAGE),
            reply_markup=initial_markup(),
        )

    # крутануть шар
    elif message.text == RANDOM_CHOICE_BUTTON:
        bot.send_message(message.chat.id, random.choice(RANDOM_CHOICE_MESSAGE))
    # получить предсказание
    elif message.text in HOROSCOPE_BUTTON_LIST.keys():
        response = requests.get(config.horoscope_api + HOROSCOPE_BUTTON_LIST.get(message.text))
        data = response.json()

        source = data.get("source")
        text = data.get("text")

        bot.send_message(message.chat.id, f"{source}\n{text}")
    # получить цитату
    elif message.text in QUOTES_BUTTON_LIST:
        data_dict = {"method": "getQuote", "format": "json", "lang": "ru"}
        response = requests.post(config.quotes_api, data=data_dict)

        data = response.json()
        quote = data.get("quoteText")
        author = data.get("quoteAuthor")

        result = str(quote) + (f"\nАвтор: {author}" if author else "")

        bot.send_message(
            message.chat.id,
            result,
            reply_markup=initial_markup(),
        )
    logging.info(
        f"user: {message.from_user.first_name} {message.from_user.last_name}. message: {message.text}"
    )


bot.polling(none_stop=True, interval=0)

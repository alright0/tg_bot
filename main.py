import telebot
import requests
from telebot import types
import random
import logging
from constants import *
from config import Config

config = Config()
bot = telebot.TeleBot(Config.token)


def initial_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    get_quote_button = types.KeyboardButton(random.choice(QUOTES_BUTTON_LIST))
    enter_horoscope_button = types.KeyboardButton(HOROSCOPE_MENU_BUTTON)
    random_choice_button = types.KeyboardButton(RANDOM_CHOICE_MENU_BUTTON)

    markup.add(
        get_quote_button, enter_horoscope_button, random_choice_button, row_width=1
    )

    return markup


def horoscope_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    go_back_button = types.KeyboardButton(GO_BACK_BUTTON)
    horoscope_buttons = [types.KeyboardButton(b) for b in HOROSCOPE_BUTTON_LIST.keys()]

    markup.add(go_back_button)
    markup.add(*horoscope_buttons, row_width=3)

    return markup


def random_choice_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    go_back_button = types.KeyboardButton(GO_BACK_BUTTON)
    random_choice_button = types.KeyboardButton(RANDOM_CHOICE_BUTTON)

    markup.add(go_back_button, random_choice_button, row_width=1)

    return markup


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

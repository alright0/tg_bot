import telebot
import random
import logging
from constants import *
from config import Config
from markup import Markup
from external_api import get_quote_json, get_horoscope

config = Config()
menu = Markup()
bot = telebot.TeleBot(Config.token)


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Чего тебе?", reply_markup=menu.initial_markup())


@bot.message_handler(content_types=["text"])
def handle_text(message):
    markup = None

    # вход в меню гороскопов
    if message.text == HOROSCOPE_MENU_BUTTON:
        text = random.choice(NAVIGATION_MESSAGE_LIST)
        markup = menu.horoscope_markup()

    # вход в меню ответов на вопросы
    elif message.text == RANDOM_CHOICE_MENU_BUTTON:
        text = 'Задумай свой вопрос и крутани шар. Ответы: "Да", "Нет" и все, что между ними'
        markup = menu.random_choice_markup()

    # вход в главное меню(кнорка назад)
    elif message.text == INITIAL_MENU:
        text = random.choice(NAVIGATION_MESSAGE_LIST)
        markup = menu.initial_markup()

    # крутануть шар
    elif message.text == RANDOM_CHOICE_BUTTON:
        text = random.choice(RANDOM_CHOICE_MESSAGE_LIST)

    # получить гороскоп
    elif message.text in HOROSCOPE_BUTTON_LIST.keys():
        horoscope_sign = HOROSCOPE_BUTTON_LIST.get(message.text)
        text = get_horoscope(horoscope_sign)

    # получить цитату
    elif message.text in QUOTES_BUTTON_LIST:
        text = get_quote_json()
        markup = menu.initial_markup()

    # остальное
    else:
        text = "Жми на кнопки, а не рассказы мне пиши."

    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=markup,
    )

    logging.info(
        f"user: {message.from_user.first_name} {message.from_user.last_name}. message: {message.text}"
    )


bot.polling(none_stop=True, interval=0)

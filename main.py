from time import sleep

import telebot
import random
import logging

from telebot.apihelper import ApiTelegramException
from telebot.types import BotCommand

from constants import *
from config import Config, Database as db
from markup import Markup
from external_api import get_quote, get_horoscope
from functions import clean_html
import schedule
import threading

config = Config()
menu = Markup()
bot = telebot.TeleBot(Config.token)

bot.set_my_commands(config.commands)

db()

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Чего тебе?", reply_markup=menu.initial_markup())


@bot.message_handler(content_types=["text"])
def handle_text(message):
    markup = None
    # вход в меню гороскопов(выбор периода)
    if message.text == HOROSCOPE_MENU_BUTTON:
        text = random.choice(NAVIGATION_MESSAGE_LIST)
        markup = menu.horoscope_menu_markup()

    # вход в меню гороскопов(выбор знака)
    elif message.text in HOROSCOPE_PERIOD_LIST.keys():
        text = random.choice(NAVIGATION_MESSAGE_LIST)
        markup = menu.horoscope_signs_markup()
        config.state.update({"horoscope_period": HOROSCOPE_PERIOD_LIST.get(message.text)})

    # вход в меню ответов на вопросы
    elif message.text == RANDOM_CHOICE_MENU_BUTTON:
        text = '*Задумай свой вопрос и крутани шар*\nОтветы: "Да", "Нет" и все, что между ними'
        markup = menu.random_choice_markup()

    # подписаться на цитаты
    elif message.text == SUBSCRIBE_MENU:
        user = message.from_user
        text = 'Хочешь получать умные цитаты каждый день?\nСтетхем будет завидовать тебе!'

        if db.check_user_is_subscriber(user.id):
            markup = menu.manage_unsubscribe_markup()
        else:
            markup = menu.manage_subscribe_markup()

    # вход в главное меню(кнорка назад)
    elif message.text == INITIAL_MENU:
        text = random.choice(NAVIGATION_MESSAGE_LIST)
        markup = menu.initial_markup()

    # крутануть шар
    elif message.text == RANDOM_CHOICE_BUTTON:
        text = random.choice(RANDOM_CHOICE_MESSAGE_LIST)

    # получить цитату
    elif message.text in QUOTES_BUTTON_LIST:
        text = get_quote()
        markup = menu.initial_markup()

    # получить гороскоп
    elif message.text in HOROSCOPE_BUTTON_LIST.keys():
        horoscope_sign = HOROSCOPE_BUTTON_LIST.get(message.text)
        horoscope_period = config.state.get("horoscope_period", 'today')
        text = get_horoscope(horoscope_sign, horoscope_period)

    # подписаться на цитаты
    elif message.text == SUBSCRIBE_BUTTON:
        user = message.from_user
        markup = menu.manage_unsubscribe_markup()
        text = "Красава! Умная мысль посетит тебя утром!"

        if not db.check_user_is_subscriber(user.id):
            db.add_user(message)
        else:
            text = "У тебя уже есть подписка на цитаты! Побереги себя!"

    # отписаться от цитат
    elif message.text == UNSUBSCRIBE_BUTTON:
        user = message.from_user
        markup = menu.manage_subscribe_markup()
        text = "Ты больше не будешь получать цитаты, потому что ты не фелосаф"
        if db.check_user_is_subscriber(user.id):
            db.delete_user(user.id)
        else:
            text = "Сначала подпишись на цитаты, потом отписывайся, я не наоборот!!"


    # остальное
    else:
        text = "Жми на кнопки, а не рассказы мне пиши"

    bot.send_message(
        chat_id=message.chat.id,
        text=clean_html(text),
        reply_markup=markup,
        parse_mode="MARKDOWN"
    )

    user = message.from_user
    logging.info(
        f"user: {user.first_name} {user.last_name}. username: {user.username}. message: {message.text}"
    )


def send_quote():
    ids = set(db.get_all_subscribers())
    for id in ids:
        try:
            id = id[0]
            quote = get_quote()

            bot.send_message(id, quote)
            logging.info(f"quote sent to user: {id}")
        except ApiTelegramException as e:
            db.delete_user(id)


def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)


schedule.every().day.at("09:00").do(send_quote)
threading.Thread(target=schedule_checker).start()

bot.infinity_polling(interval=0, timeout=600)

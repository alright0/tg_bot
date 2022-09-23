import telebot
import random
import logging
from constants import *
from config import Config, Database as db
from markup import Markup
from external_api import get_quote_json, get_horoscope
import re
import sqlite3


config = Config()
menu = Markup()
bot = telebot.TeleBot(Config.token)

db()

state = {
    "horoscope_period": 'today'
}

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
        state.update({"horoscope_period": HOROSCOPE_PERIOD_LIST.get(message.text)})

    # вход в меню ответов на вопросы
    elif message.text == RANDOM_CHOICE_MENU_BUTTON:
        text = '*Задумай свой вопрос и крутани шар*\nОтветы: "Да", "Нет" и все, что между ними'
        markup = menu.random_choice_markup()

    # подписаться на цитаты
    elif message.text == SUBSCRIBE_MENU:
        text = 'Хочешь получать умные цитаты каждый день?\nСтетхем будет завидовать тебе!'
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
        text = get_quote_json()
        markup = menu.initial_markup()

    # получить гороскоп
    elif message.text in HOROSCOPE_BUTTON_LIST.keys():
        horoscope_sign = HOROSCOPE_BUTTON_LIST.get(message.text)
        horoscope_period = state.get("horoscope_period")
        text = get_horoscope(horoscope_sign, horoscope_period)

    # подписаться на цитаты
    elif message.text == SUBSCRIBE_BUTTON:
        user = message.from_user

        if not db.check_user_is_subscriber(user):
            db.add_user(user)
            text = "Красава! Получишь цитату в течение попозже!"
        else:
            text = "Ты уже подписан на цитаты! Побереги себя!"

    elif message.text == UNSUBSCRIBE_BUTTON:
        user = message.from_user

        if db.check_user_is_subscriber(user):
            text = "Ты больше не будешь получать цитаты, потому что ты не фелосаф"
            db.delete_user(user)
        else:
            text = "Ты даже не подписался на них! Сначала подпишись потом выебывайся!"



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


def clean_html(text):
    replace_closed_tags = re.compile('</.*?>')
    delete_all_tags = re.compile('<.*?>')

    text = re.sub (replace_closed_tags, '\n', text)
    return re.sub(delete_all_tags, '', text)


bot.polling(none_stop=True, interval=0)

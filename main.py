from time import sleep

import telebot
import random
import logging

from telebot import types
from telebot.apihelper import ApiTelegramException

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
def command_start(message):
    bot.send_message(message.chat.id, "Чего тебе?", reply_markup=menu.initial_markup())


@bot.message_handler(commands=["horoscope"])
def command_horoscope(message):
    markup = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(k, callback_data=v) for k, v in HOROSCOPE_PERIOD_LIST.items()]
    markup.add(*buttons)

    bot.send_message(
        chat_id=message.chat.id,
        text="Выбери период",
        reply_markup=markup,
        parse_mode="MARKDOWN",
    )


@bot.message_handler(commands=["subscribe"])
def command_subscribe(message):
    user = message.from_user

    markup = types.InlineKeyboardMarkup()
    thanks_button = types.InlineKeyboardButton('Не хочу', callback_data=THANKS)
    if db.check_user_is_subscriber(user.id):
        button = types.InlineKeyboardButton("Отписаться", callback_data=f"deluser")
        text = "У тебя уже есть подписка на цитаты. Не говори, что хочешь отписаться"
    else:
        button = types.InlineKeyboardButton("Подписаться", callback_data=f"adduser")
        text = "Хочешь получать умные цитаты каждый день?\nСтетхем будет завидовать тебе!"
    markup.add(button, thanks_button)

    bot.send_message(
        chat_id=message.chat.id,
        parse_mode="MARKDOWN",
        text=clean_html(text),
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "adduser")
def callback_subscribe(call):
    if call.message:
        user = call.message.chat
        if not db.check_user_is_subscriber(user.id):
            text = "Красава! Умная мысль посетит тебя утром!"
            db.add_user(call.message)
        else:
            text = "У тебя уже есть подписка 😙"

        bot.edit_message_text(
            chat_id=user.id,
            message_id=call.message.message_id,
            text=clean_html(text),
            reply_markup=None
        )


@bot.callback_query_handler(func=lambda call: call.data == "deluser")
def callback_unsubscribe(call):
    if call.message:
        if db.check_user_is_subscriber(call.message.chat.id):
            db.delete_user(call.message.chat.id)
            text = "Мудила, ну и вали отсюда"
        else:
            text = "У тебя еще нет подписки, а ты уже пытаешься отписаться, псина?"

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=clean_html(text),
            reply_markup=None
        )


@bot.callback_query_handler(func=lambda call: call.data in HOROSCOPE_PERIOD_LIST.values())
def callback_inline(call):
    if call.message:
        config.state.update({"horoscope_period": call.data})

        markup = types.InlineKeyboardMarkup()
        buttons = [types.InlineKeyboardButton(k, callback_data=v) for k, v in HOROSCOPE_BUTTON_LIST.items()]
        markup.add(*buttons)

        text = "Теперь выбери знак"

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=markup
        )


@bot.callback_query_handler(func=lambda call: call.data in HOROSCOPE_BUTTON_LIST.values())
def callback_get_sign(call):
    if call.message:
        horoscope_period = config.state.get("horoscope_period", 'today')
        horoscope_sign = call.data

        markup = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(THANKS, callback_data=THANKS)
        markup.add(button)

        text = get_horoscope(horoscope_sign, horoscope_period)

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=clean_html(text),
            reply_markup=markup
        )


@bot.callback_query_handler(func=lambda call: call.data == THANKS)
def callback_thanks(call):
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=call.message.text, reply_markup=None)

    text = f'{random.choice(WELCOME_LIST)} {random.choice(SMILE_LIST)}'

    bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text=text)


@bot.message_handler(content_types=["text"])
def handle_text(message):
    markup = None

    # вход в меню ответов на вопросы
    if message.text == RANDOM_CHOICE_MENU_BUTTON:
        text = '*Задумай свой вопрос и крутани шар*\nОтветы: "*Да*", "*Нет*" и все, что между ними'
        markup = menu.random_choice_markup()

    # вход в главное меню(кнопка назад)
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

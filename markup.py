from telebot import types
from constants import *
import random

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

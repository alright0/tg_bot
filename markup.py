from telebot import types
from constants import *
import random


class Button:
    @staticmethod
    def main_menu():
        return types.KeyboardButton(INITIAL_MENU)

    @staticmethod
    def horoscope_menu():
        return types.KeyboardButton(HOROSCOPE_MENU_BUTTON)

    @staticmethod
    def random_choice_menu():
        return types.KeyboardButton(RANDOM_CHOICE_MENU_BUTTON)

    @staticmethod
    def get_quote():
        return types.KeyboardButton(_dynamic_naming(QUOTES_BUTTON_LIST))

    @staticmethod
    def random_choice():
        return types.KeyboardButton(RANDOM_CHOICE_BUTTON)

    @staticmethod
    def horoscope_signs_buttons():
        return [types.KeyboardButton(b) for b in HOROSCOPE_BUTTON_LIST.keys()]


class Markup:
    def __init__(self):
        initial_markup = self.initial_markup()
        horoscope_markup = self.horoscope_markup()
        random_choice_markup = self.random_choice_markup()

    def initial_markup(self):
        buttons = [
            {
                "buttons": [
                    Button.get_quote(),
                    Button.horoscope_menu(),
                    Button.random_choice_menu(),
                ],
                "rows": 1,
            },
        ]

        return self._build_markup(buttons)

    def horoscope_markup(self):
        buttons = [
            {
                "buttons": Button.main_menu(),
                "rows": 1,
            },
            {
                "buttons": Button.horoscope_signs_buttons(),
                "rows": 4,
            },
        ]

        return self._build_markup(buttons)

    def random_choice_markup(self):
        buttons = [
            {
                "buttons": Button.main_menu(),
                "rows": 1,
            },
            {
                "buttons": Button.random_choice(),
                "rows": 1,
            },
        ]

        return self._build_markup(buttons)

    @staticmethod
    def _build_markup(buttons):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        for button in buttons:
            _buttons = button.get("buttons", Button.main_menu())
            buttons_list = _list_wrapper(_buttons)
            rows = button.get("rows", 1)

            markup.add(*buttons_list, row_width=rows)
        return markup


def _list_wrapper(obj):
    if isinstance(obj, (list, tuple)):
        return obj
    return [obj]


def _dynamic_naming(names) -> str:
    """Метод для создания кнопок с динамическими именами. Если нужно,
        чтобы текст кнопки менялся при каждом ее нажатии.
        :param names: список имен кнопки
        :return: имя кнопки
    """
    return random.choice(_list_wrapper(names))
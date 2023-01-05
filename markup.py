from telebot import types
from constants import *
import random


class Button:
    @staticmethod
    def main_menu():
        return types.KeyboardButton(INITIAL_MENU)

    @staticmethod
    def random_choice_menu():
        return types.KeyboardButton(RANDOM_CHOICE_MENU_BUTTON)

    @staticmethod
    def get_quote():
        return types.KeyboardButton(_dynamic_naming(QUOTES_BUTTON_LIST))

    @staticmethod
    def random_choice():
        return types.KeyboardButton(RANDOM_CHOICE_BUTTON)


class Markup:
    def __init__(self):
        initial_markup = self.initial_markup()
        random_choice_markup = self.random_choice_markup()

    def initial_markup(self):
        buttons = [
            self._create_button(
                [
                    Button.get_quote(),
                    Button.random_choice_menu(),
                ],
                rows=1
            )
        ]

        return self._build_markup(buttons)

    def random_choice_markup(self):
        buttons = [
            self._create_button(Button.main_menu(), rows=1),
            self._create_button(Button.random_choice(), rows=1)
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

    def _create_button(self, buttons, rows=1):
        return {
            "buttons": buttons,
            "rows": rows,
        }

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


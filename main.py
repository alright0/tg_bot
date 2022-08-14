import telebot
import requests
from telebot import types
import random
import logging
from pathlib import Path

path = Path(__file__).parents[0]

logging.basicConfig(
    filename="app.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%d-%m-%y %H:%M:%S",
)

QUOTES_API = "http://api.forismatic.com/api/1.0/"
HOROSCOPE_API = "https://horoscopes.rambler.ru/api/front/v1/horoscope/today/"

TOKEN = "5314229527:AAG5lKaYOu4Ubtr_VTJirKk6Tf7UExGL6EA"

QUOTES_BUTTON_LIST = [
    "ЖГИ!",
    "РВИ ДУШУ, БЛЕАТЬ!",
    "ЕЩЕ!",
    "МОАР!",
    "ДАВАЙ, СКА!",
    "ДА! ЕЩЕ!",
    "БОЖЕ, АФТАР, ПЛАКАЮ!",
    "ДЕВАЧКИ, ПЛАЧУ!",
]
RANDOM_CHOICE_MENU_BUTTON = "Заебал, ответь мои на вопросы!"
RANDOM_CHOICE_BUTTON = "Крутануть шар с предсказаниями"
HOROSCOPE_MENU_BUTTON = "Заебал, покажи мою судьбу!"
GO_BACK_BUTTON = "Надоело, давай назад!"
HOROSCOPE_BUTTON_LIST = {
    "Овен": "aries",
    "Телец": "taurus",
    "Близнецы": "gemini",
    "Рак": "cancer",
    "Лев": "leo",
    "Дева": "virgo",
    "Весы": "libra",
    "Скорпион": "scorpio",
    "Стрелец": "sagittarius",
    "Козерог": "capricorn",
    "Водолей": "aquarius",
    "Рыбы": "pisces",
}
RANDOM_CHOICE_MESSAGE = [
    "Да",
    "Нет",
    "Пока не понятно",
    "Скорее нет, чем да",
    "Скорее да, чем нет",
    "Это очень неопределенно",
    "Попробуй еще раз",
    "Скоро все прояснится",
    "Нужно больше времени",
    "Я не знаю ответа на этот вопрос",
    "Определенно да",
    "Определенно нет",
]
NAVIGATION_MESSAGE = [
    "Погнали!",
    "Погнали",
    "пагнали",
    "Да тебе не угодишь, е-мое, хватит гонять меня!",
    "Е-мое, хватит шастать туда-сюда!",
    "Погнали, расскажу тебе все!",
    "Бля, ну погнали...",
    "Бли, погнали",
    "Опять?",
    "Определись уже!",
]


bot = telebot.TeleBot(TOKEN)


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
        response = requests.get(HOROSCOPE_API + HOROSCOPE_BUTTON_LIST.get(message.text))
        data = response.json()

        source = data.get("source")
        text = data.get("text")

        bot.send_message(message.chat.id, f"{source}\n{text}")
    # получить цитату
    elif message.text in QUOTES_BUTTON_LIST:
        data_dict = {"method": "getQuote", "format": "json", "lang": "ru"}
        response = requests.post(QUOTES_API, data=data_dict)

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

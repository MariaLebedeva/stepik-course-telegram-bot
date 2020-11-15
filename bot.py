import telebot
from datetime import date, timedelta

token = '325273800:AAGrT1sh8FREiy2i_Xss865c9tJDP3rRLzg'

bot = telebot.TeleBot(token)

states = {}
calls = {}

WEATHER_DATA = {
    'ноябрь': {
        14: 2,
        15: 0,
        16: 1
    }
}

MONTHS = {
    1: "январь",
    2: "февраль",
    3: "март",
    4: "апрель",
    5: "май",
    6: "июнь",
    7: "июль",
    8: "август",
    9: "сентябрь",
    10: "октябрь",
    11: "ноябрь",
    12: "декабрь"
}

MAIN_STATE = 'main'
TASK_DATE_STATE = 'task_date'


@bot.message_handler(func=lambda message: True)
def dispatcher(message):
    user_id = message.from_user.id
    current_user_state = states.get(user_id, MAIN_STATE)

    if current_user_state == MAIN_STATE:
        main_handler(message)
    elif current_user_state == TASK_DATE_STATE:
        task_date_handler(message)
    else:
        bot.reply_to(message, "Я тебя не понял")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Это бот-планировщик. Он поможет сориентироваться в твоих задачах.")


def main_handler(message):
    user_id = message.from_user.id
    if "покажи задачи" in message.text.lower():
        bot.reply_to(message, "А какая дата? Введи в формате 'Месяц, число'.")
        states[user_id] = TASK_DATE_STATE
    elif "привет" in message.text.lower():
        bot.reply_to(message, say_hello(message.from_user.first_name, message.from_user.language_code))
    elif "вызовы" in message.text.lower():
        if user_id in calls:
            bot.send_message(user_id, str(calls[user_id]))
        else:
            bot.send_message(user_id, "0")
    else:
        bot.reply_to(message, "Я тебя не понял")


def task_date_handler(message):
    user_id = message.from_user.id
    if user_id not in calls:
        calls[user_id] = 0
    calls[user_id] += 1

    if "сегодня" in message.text.lower():
        today = date.today()
        month_name = MONTHS[today.month]
        current_weather = WEATHER_DATA[month_name][today.day]
        bot.send_message(message.from_user.id, "Количество задач {0}".format(current_weather))
        states[message.from_user.id] = MAIN_STATE
    elif "завтра" in message.text.lower():
        today = date.today() + timedelta(days=1)
        month_name = MONTHS[today.month]
        current_weather = WEATHER_DATA[month_name][today.day]
        bot.send_message(message.from_user.id, "Количество задач {0}".format(current_weather))
        states[message.from_user.id] = MAIN_STATE
    else:
        month, day = message.text.split(",")
        day = int(day.strip())
        month = month.lower()
        if month in WEATHER_DATA:
            if day in WEATHER_DATA[month]:
                current_weather = WEATHER_DATA[month][day]
                bot.send_message(message.from_user.id, "Количество задач {0}".format(current_weather))
        else:
            bot.send_message(message.from_user.id, "Нет данных в хранилище.")
        # bot.reply_to(message, "Я тебя не понял")


def say_hello(user_name, lang_code):
    if lang_code == 'en':
        return "Hello, " + user_name + "!"
    return "Привет, " + user_name + "!"



bot.polling()

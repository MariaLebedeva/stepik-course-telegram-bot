import telebot

token = '325273800:AAGrT1sh8FREiy2i_Xss865c9tJDP3rRLzg'

bot = telebot.TeleBot(token)

states = {}

MAIN_STATE = 'main'
TASK_DATE_STATE = 'task_date'


def say_hello(user_name, lang_code):
    if lang_code == 'en':
        return "Hello, " + user_name + "!"
    return "Привет, " + user_name + "!"


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Это бот-планировщик. Он поможет сориентироваться в твоих задачах.")


def main_handler(message):
    if message.text == "Покажи задачи":
        bot.reply_to(message, "Уточни дату")
        states[message.from_user.id] = TASK_DATE_STATE
    elif message.text == "Привет!":
        bot.reply_to(message, say_hello(message.from_user.first_name, message.from_user.language_code))
    else:
        bot.reply_to(message, "Я тебя не понял")


def task_date_handler(message):
    if message.text == "Сегодня":
        bot.send_message(message.from_user.id, "У тебе 2 задачи")
        states[message.from_user.id] = MAIN_STATE
    elif message.text == "Завтра":
        bot.send_message(message.from_user.id, "У тебя нет задач")
        states[message.from_user.id] = MAIN_STATE
    else:
        bot.reply_to(message, "Я тебя не понял")


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


bot.polling()

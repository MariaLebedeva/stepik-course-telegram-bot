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


@bot.message_handler(func=lambda message: True)
def dispatcher(message):
    if message.text == "Привет!":
        bot.reply_to(message, say_hello(message.from_user.first_name, message.from_user.language_code))
    elif message.text == "Покажи задачи":
        bot.reply_to(message, "Уточни дату")
    elif message.text == "Сегодня":
        bot.reply_to(message, "На сегодня 2 задачи")
    elif message.text == "Завтра":
        bot.reply_to(message, "Нет задач")
    else:
        bot.reply_to(message, "Я тебя не понял")


bot.polling()

import telebot

token = '325273800:AAGrT1sh8FREiy2i_Xss865c9tJDP3rRLzg'

bot = telebot.TeleBot(token)

score = {'victories': 0, 'defeats': 0}


def say_hello(user_name, lang_code):
    if lang_code == 'en':
        return "Hello, " + user_name + "!"
    return "Привет, " + user_name + "!"


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Это бот-тренажер ударений. Он поможет научиться правильной постановке ударений в сложных "
                          "словах.")


@bot.message_handler(func=lambda message: True)
def content(message):
    if message.text == "Привет!":
        bot.reply_to(message, say_hello(message.from_user.first_name, message.from_user.language_code))
    elif message.text == "Спроси меня слово":
        bot.reply_to(message, "Как правильно - Искра или искрА?")
    elif message.text == "Искра":
        bot.reply_to(message, "Правильно!")
        score['victories'] += 1
    elif message.text == "искрА":
        bot.reply_to(message, "Неправильно :(")
        score['defeats'] += 1
    elif message.text == "Покажи счет":
        bot.reply_to(message, str(score['victories']) + " : " + str(score['defeats']))
    else:
        bot.reply_to(message, "Я тебя не понял")


bot.polling()

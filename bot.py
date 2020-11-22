import random
from datetime import date, timedelta
import telebot
import requests


token = '325273800:AAGrT1sh8FREiy2i_Xss865c9tJDP3rRLzg'

weather_api_id = '744c9b39d3c73ea63d1289e2f8e9ce16'
weather_api_url = 'http://api.openweathermap.org/data/2.5/weather'

bot = telebot.TeleBot(token)

states = {}
params = {'units': 'metric', 'appid': weather_api_id }
data = None

MAIN_STATE = 'main'
CITY_STATE = 'city'
DETAILS_STATE = 'details'


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "This bot will show you current weather in any city")


@bot.message_handler(func=lambda message: True)
def dispatcher(message):
    user_id = message.from_user.id
    current_user_state = states.get(user_id, MAIN_STATE)

    if current_user_state == MAIN_STATE:
        main_handler(message)
    elif current_user_state == CITY_STATE:
        city_handler(message)
    elif current_user_state == DETAILS_STATE:
        details_handler(message)
    else:
        bot.reply_to(message, "I didn't understand you")


def main_handler(message):
    user_id = message.from_user.id
    if "show weather" in message.text.lower():
        bot.reply_to(message, "In which city?")
        states[user_id] = CITY_STATE
    elif "hello" in message.text.lower():
        bot.reply_to(message, "Hello, {}!".format(message.from_user.first_name))
    else:
        bot.reply_to(message, "I didn't understand you")


def city_handler(message):
    params["q"] = message.text
    bot.reply_to(message, "What details would you know: temperature, pressure, humidity or all?")
    states[message.from_user.id] = DETAILS_STATE


def details_handler(message):
    user_id = message.from_user.id
    data = requests.get(weather_api_url, params).json()
    if "temperature" in message.text.lower():
        bot.reply_to(message, "Current temperature in {} is {}".format(data["name"], data["main"]["temp"]))
        states[user_id] = MAIN_STATE
    elif "pressure" in message.text.lower():
        bot.reply_to(message, "Current pressure in {} is {}".format(data["name"], data["main"]["pressure"]))
        states[user_id] = MAIN_STATE
    elif "humidity" in message.text.lower():
        bot.reply_to(message, "Current humidity in {} is {}%".format(data["name"], data["main"]["humidity"]))
        states[user_id] = MAIN_STATE
    elif "all" in message.text.lower():
        bot.reply_to(message, "Current temperature in {} is {}, pressure is {}, humidity {}%".format(data["name"],
                                                                                                    data["main"][
                                                                                                        "temp"],
                                                                                                    data["main"][
                                                                                                        "pressure"],
                                                                                                    data["main"][
                                                                                                        "humidity"]))
        states[user_id] = MAIN_STATE
    else:
        bot.reply_to(message, "I didn't understand you")


bot.polling()

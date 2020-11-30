import telebot
import requests
import json
import os
import redis


token = '325273800:AAGrT1sh8FREiy2i_Xss865c9tJDP3rRLzg'
bot = telebot.TeleBot(token)

weather_api_id = '744c9b39d3c73ea63d1289e2f8e9ce16'
weather_api_url = 'http://api.openweathermap.org/data/2.5/weather'

params = {'units': 'metric', 'appid': weather_api_id }

MAIN_STATE = 'main'
CITY_STATE = 'city'
DETAILS_STATE = 'details'

redis_url = os.environ.get('REDIS_URL')

if redis_url is None:
    try:
        data = json.load(open("data.json", "r", encoding="utf-8"))
    except FileNotFoundError:
        data = {
            'states': {},
            MAIN_STATE: {

            },
            CITY_STATE: {

            },
            DETAILS_STATE: {
                # user_id: city_name
            }
        }
else:
    redis_db = redis.from_url(redis_url)
    raw_data = redis_db.get("data")
    if raw_data is None:
        data = {
            'states': {},
            MAIN_STATE: {

            },
            CITY_STATE: {

            },
            DETAILS_STATE: {
                # user_id: city_name
            }
        }
    else:
        data = json.loads(raw_data)


def change_data(user_id, key, value):
    data[key][user_id] = value
    if redis_url is None:
        json.dump(
            data,
            open("data.json", "w", encoding="utf=8"),
            indent=2,
            ensure_ascii=False
        )
    else:
        redis_db = redis.from_url(redis_url)
        redis_db.set("data", json.dumps(data))


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "This bot will show you current weather in any city")


@bot.message_handler(func=lambda message: True)
def dispatcher(message):
    user_id = str(message.from_user.id)
    current_user_state = data['states'].get(user_id, MAIN_STATE)

    if current_user_state == MAIN_STATE:
        main_handler(message)
    elif current_user_state == CITY_STATE:
        city_handler(message)
    elif current_user_state == DETAILS_STATE:
        details_handler(message)
    else:
        bot.reply_to(message, "I didn't understand you")


def main_handler(message):
    user_id = str(message.from_user.id)
    if "show weather" in message.text.lower():
        bot.reply_to(message, "In which city?")
        change_data(user_id, 'states', CITY_STATE)
    elif "hello" in message.text.lower():
        bot.reply_to(message, "Hello, {}!".format(message.from_user.first_name))
    else:
        bot.reply_to(message, "I didn't understand you")


def city_handler(message):
    user_id = str(message.from_user.id)
    try:
        params["q"] = message.text
        requests.get(weather_api_url, params).json()['name']
    except KeyError:
        bot.reply_to(message, "Incorrect city, try to input the city again")
        return
    bot.reply_to(message, "What details would you know: temperature, pressure, humidity or all?")
    change_data(user_id, "states", DETAILS_STATE)
    change_data(user_id, DETAILS_STATE, message.text)


def details_handler(message):
    user_id = str(message.from_user.id)
    params["q"] = data[DETAILS_STATE][user_id]
    weather_data = requests.get(weather_api_url, params).json()
    if "temperature" in message.text.lower():
        bot.reply_to(message, "Current temperature in {} is {}°C".format(weather_data["name"], weather_data["main"]["temp"]))
        change_data(user_id, 'states', MAIN_STATE)
    elif "pressure" in message.text.lower():
        bot.reply_to(message, "Current pressure in {} is {}hPa".format(weather_data["name"], weather_data["main"]["pressure"]))
        change_data(user_id, 'states', MAIN_STATE)
    elif "humidity" in message.text.lower():
        bot.reply_to(message, "Current humidity in {} is {}%".format(weather_data["name"], weather_data["main"]["humidity"]))
        change_data(user_id, 'states', MAIN_STATE)
    elif "all" in message.text.lower():
        bot.reply_to(message, "Current temperature in {} is {}°C, pressure is {}hPa, humidity {}%".format(weather_data["name"],
                                                                                                          weather_data["main"][
                                                                                                        "temp"],
                                                                                                          weather_data["main"][
                                                                                                        "pressure"],
                                                                                                          weather_data["main"][
                                                                                                        "humidity"]))
        change_data(user_id, 'states', MAIN_STATE)
    else:
        bot.reply_to(message, "I didn't understand you")


if __name__ == "__main__":
    bot.polling()
    print("The bot is shutdown")

import telebot
from telebot.types import ReplyKeyboardMarkup
import requests
import json
import os
import redis


token = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(token)

weather_api_id = os.environ.get('WEATHER_API_ID')
weather_api_url = 'http://api.openweathermap.org/data/2.5/weather'

params = {'units': 'metric', 'appid': weather_api_id}

MAIN_STATE = 'main'
CITY_STATE = 'city'
DETAILS_STATE = 'details'
START_DATA = {
    'states': {},
    MAIN_STATE: {

    },
    CITY_STATE: {

    },
    DETAILS_STATE: {
        # user_id: city_name
    },
    'popular_cities': {}
}


redis_url = os.environ.get('REDIS_URL')

if redis_url is None:
    try:
        data = json.load(open("data.json", "r", encoding="utf-8"))
    except FileNotFoundError:
        data = START_DATA
else:
    redis_db = redis.from_url(redis_url)
    raw_data = redis_db.get("data")
    if raw_data is None:
        data = START_DATA
    else:
        data = json.loads(raw_data)


def change_data(user_id, key, value):
    data[key][user_id] = value
    flush_on_disc()


def flush_on_disc():
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


def most_popular_cities(user_id):
    if data['popular_cities'].get(user_id) is None:
        return None
    city1 = city2 = ''
    counter1 = counter2 = 0
    for city in data['popular_cities'][user_id].keys():
        if data['popular_cities'][user_id][city] > counter1:
            city1 = city
            counter1 = data['popular_cities'][user_id][city]
        elif data['popular_cities'][user_id][city] > counter2:
            city2 = city
            counter2 = data['popular_cities'][user_id][city]
    if city1 == "" or city2 == "":
        return None
    return city1, city2


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Say hello", "Show weather")
    bot.send_message(message.chat.id, "This bot will show you current weather in any city", reply_markup=markup)


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
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        cities = most_popular_cities(user_id)
        if cities is None:
            markup.row("Moscow", "Saint Petersburg")
        else:
            markup.row(*cities)
        bot.send_message(message.chat.id, "In which city? Select the city form offered or input your city.", reply_markup=markup)
        change_data(user_id, 'states', CITY_STATE)
    elif "say hello" in message.text.lower():
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

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("temperature", "pressure", "humidity", "all")

    if data['popular_cities'][user_id].get(message.text) is None:
        data['popular_cities'][user_id][message.text] = 1
    else:
        data['popular_cities'][user_id][message.text] += 1

    bot.send_message(message.chat.id, "What details would you know: temperature, pressure, humidity or all?",
                     reply_markup=markup)
    change_data(user_id, "states", DETAILS_STATE)
    change_data(user_id, DETAILS_STATE, message.text)


def details_handler(message):
    user_id = str(message.from_user.id)
    params["q"] = data[DETAILS_STATE][user_id]
    weather_data = requests.get(weather_api_url, params).json()

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("Say hello", "Show weather")
    if "temperature" in message.text.lower():
        bot.send_message(message.chat.id,
                         "Current temperature in {} is {}°C".format(weather_data["name"], weather_data["main"]["temp"]),
                         reply_markup=markup)
        change_data(user_id, 'states', MAIN_STATE)
    elif "pressure" in message.text.lower():
        bot.send_message(message.chat.id, "Current pressure in {} is {}hPa".format(weather_data["name"],
                                                                                   weather_data["main"]["pressure"]),
                         reply_markup=markup)
        change_data(user_id, 'states', MAIN_STATE)
    elif "humidity" in message.text.lower():
        bot.send_message(message.chat.id,
                         "Current humidity in {} is {}%".format(weather_data["name"], weather_data["main"]["humidity"]),
                         reply_markup=markup)
        change_data(user_id, 'states', MAIN_STATE)
    elif "all" in message.text.lower():
        bot.send_message(message.chat.id, "Current temperature in {} is {}°C, pressure is {}hPa, humidity {}%".format(
            weather_data["name"],
            weather_data["main"][
                "temp"],
            weather_data["main"][
                "pressure"],
            weather_data["main"][
                "humidity"]), reply_markup=markup)
        change_data(user_id, 'states', MAIN_STATE)
    else:
        bot.reply_to(message, "I didn't understand you")


if __name__ == "__main__":
    bot.polling()
    print("The bot is shutdown")

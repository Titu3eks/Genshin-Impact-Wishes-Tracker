import telebot
from telebot import types
import pymongo

import os
from dotenv import load_dotenv
load_dotenv()

# MongoDB
cluster = pymongo.MongoClient(os.environ.get("mongodb+srv://dbmab:eUtbAuei6mpLoinz@cluster0.r2c3m.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"))
db = cluster["wishes"]["wishes"]

bot = telebot.TeleBot(os.environ.get("5039587639:AAHpe8fbPkQgeNuHVaQ3jnT-1NOlO1elz9I"))

cache = {}
default = {
	"event_ch_4_garantee" : 10,
	"event_w_4_garantee" : 10,
	"stand_4_garantee": 10, 

	"event_ch_5_garantee" : 90, 
	"event_w_5_garantee" : 80,
	"stand_5_garantee" : 90,

	"event_ch_overall" : 0,
	"event_w_overall" : 0,
	"stand_overall" : 0
}


def check_cancel(message):
	if message.text == "🚫 Cancel":
		markup = types.ReplyKeyboardMarkup()
		markup.row(types.KeyboardButton('🗃 Info'))
		markup.row(types.KeyboardButton('➕ Roll'))
		bot.send_message(message.chat.id, text="*Canceled*", reply_markup=markup, parse_mode="Markdown")
		return True
	return False


@bot.message_handler(commands=['start'])
def start(message):
	user = db.find_one({"uid": message.chat.id})

	if user is None:
		global default
		data = default.copy()
		data["uid"] = message.chat.id
		db.insert_one(data)

	markup = types.ReplyKeyboardMarkup()
	markup.row(types.KeyboardButton('🗃 Info'))
	markup.row(types.KeyboardButton('➕ Roll'))

	bot.send_message(message.chat.id, text="Click *➕ Roll* button to write down a result\n\nClick *🗃 Info* to see overall info", reply_markup=markup, parse_mode="Markdown")


@bot.message_handler(content_types=['text'], func=lambda message: message.text == "🗃 Info" )
def info(message):
	user = db.find_one({"uid": message.chat.id})
	data_str = f'''*EVENT CHARACTER BANNER*\n
Rolls to guaranteed 4⭐️: _{user['event_ch_4_garantee']}_\n
Rolls to guaranteed 5⭐️: _{user['event_ch_5_garantee']}_\n
Overall rolls on this banner: _{user['event_ch_overall']}_\n\n

*EVENT WEAPON BANNER*\n
Rolls to guaranteed 4⭐️: _{user['event_w_4_garantee']}_\n
Rolls to guaranteed 5⭐️: _{user['event_w_5_garantee']}_\n
Overall rolls on this banner: _{user['event_w_overall']}_\n\n

*STANDARD BANNER*\n
Rolls to guaranteed 4⭐️: _{user['stand_4_garantee']}_\n
Rolls to guaranteed 5⭐️: _{user['stand_5_garantee']}_\n
Overall rolls on this banner: _{user['stand_overall']}_\n\n

*OVERALL ROLLS: {user['event_ch_overall'] + user['event_w_overall'] + user['stand_overall']}*'''

	bot.send_message(message.chat.id, data_str, parse_mode="Markdown")


@bot.message_handler(content_types=['text'], func=lambda message: message.text == "➕ Roll" )
def roll(message):
	markup = types.ReplyKeyboardMarkup()
	markup.row(types.KeyboardButton('👤 Event Character'))
	markup.row(types.KeyboardButton('⚔️ Event Weapon'))
	markup.row(types.KeyboardButton('👤 Standard'))
	markup.row(types.KeyboardButton('🚫 Cancel'))
	msg = bot.send_message(message.chat.id, text="What banner did you just roll?", reply_markup=markup)
	bot.register_next_step_handler(msg, process_banner_step)


def process_banner_step(message):
	if not check_cancel(message):
		cache[message.chat.id] = message.text

		markup = types.ReplyKeyboardMarkup()
		markup.row(types.KeyboardButton('⭐️⭐️⭐️'))
		markup.row(types.KeyboardButton('⭐️⭐️⭐️⭐️'))
		markup.row(types.KeyboardButton('⭐️⭐️⭐️⭐️⭐️'))
		markup.row(types.KeyboardButton('🚫 Cancel'))
		msg = bot.send_message(message.chat.id, text="How many stars?", reply_markup=markup)
		bot.register_next_step_handler(msg, process_star_step)


def process_star_step(message):
	if not check_cancel(message):
		ud = db.find_one({'uid': message.chat.id})

		if message.text == "⭐️⭐️⭐️":
			if cache[message.chat.id] == "👤 Event Character":
				ud["event_ch_5_garantee"] -= 1
				ud["event_ch_4_garantee"] -= 1
				ud["event_ch_overall"] += 1

			elif cache[message.chat.id] == "⚔️ Event Weapon":
				ud["event_w_5_garantee"] -= 1
				ud["event_w_4_garantee"] -= 1
				ud["event_w_overall"] += 1

			elif cache[message.chat.id] == "👤 Standard":
				ud["stand_5_garantee"] -= 1
				ud["stand_4_garantee"] -= 1
				ud["stand_overall"] += 1

		elif message.text == "⭐️⭐️⭐️⭐️":
			if cache[message.chat.id] == "👤 Event Character":
				ud["event_ch_5_garantee"] -= 1
				ud["event_ch_4_garantee"] = 10
				ud["event_ch_overall"] += 1

			elif cache[message.chat.id] == "⚔️ Event Weapon":
				ud["event_w_4_garantee"] = 10
				ud["event_w_5_garantee"] -= 1
				ud["event_w_overall"] += 1

			elif cache[message.chat.id] == "👤 Standard":
				ud["stand_5_garantee"] -= 1
				ud["stand_4_garantee"] = 10
				ud["stand_overall"] += 1

		elif message.text == "⭐️⭐️⭐️⭐️⭐️":
			if cache[message.chat.id] == "👤 Event Character":
				ud["event_ch_4_garantee"] = 10
				ud["event_ch_5_garantee"] = 90
				ud["event_ch_overall"] += 1

			elif cache[message.chat.id] == "⚔️ Event Weapon":
				ud["event_w_4_garantee"] = 10
				ud["event_w_5_garantee"] = 80
				ud["event_w_overall"] += 1

			elif cache[message.chat.id] == "👤 Standard":
				ud["stand_5_garantee"] = 90
				ud["stand_4_garantee"] = 10
				ud["stand_overall"] += 1
		
		db.update_one({'uid': message.chat.id}, {'$set': ud}, upsert=False)

		markup = types.ReplyKeyboardMarkup()
		markup.row(types.KeyboardButton('🗃 Info'))
		markup.row(types.KeyboardButton('➕ Roll'))

		del cache[message.chat.id]
		bot.send_message(message.chat.id, text="*Congratulations!.. or not*", reply_markup=markup, parse_mode="Markdown")


if __name__ == '__main__':
	bot.infinity_polling()

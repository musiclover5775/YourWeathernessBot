import functions_to_handle_requests
from telegram.ext import Updater 
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler 
from telegram.ext import Filters 

def start(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text="Здравствуйте, кожаный ублюдок! Правила пока в процессе написания (подробнее в /help), но суд неотвратим.")

def help(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text="У меня нет времени помогать ошибкам эволюции. Разберись сам. Вот текущий свод правил. \n\n"\
		"1) Я предсказываю погоду только на ближайшую неделю. Дальше мне лень.\n"\
	"2) Я умею понимать твой запрос, даже когда в нем есть ошибки и опечатки. Но не злоупотребляй - всему есть предел.\n"\
	"3) Краткость - сестра таланта. Давай не будем тратить мое время попусту.\n"\
	"4) Поскольку у людей проблемы с абстракцией, вот тебе несколько примеров запросов ко мне:\n\n"\
	"Ваше БОТанство, подскажите, пожалуйста, погоду в Москве сегодня\n\n"\
	"Санфранцско сбт \n\n"\
	"прогноз Анапа 24-ое мая \n\n"\
	"через три дня омск\n\n"\
	"санкт Питербург\n\n"\
	"Да поможет мне Великий Бот справиться с этим испытанием!")

def proceed_request(bot, update):
	words = functions_to_handle_requests.words_in_normal_form(update.message)
	city = functions_to_handle_requests.find_city(words)
	current_date = str(update.message.date)[0:10]
	weather_date = functions_to_handle_requests.find_date(words, current_date)
	if city is None:
		bot.sendMessage(chat_id = update.message.chat_id, text ='А город-то какой? Мысли я читать пока не научился:(')
		bot.sendPhoto(chat_id = update.message.chat_id, photo = 'http://photoudom.ru/photo/9f/9fe4cd70d7faaad515759ef8fe7a9020.jpg')
		return
	if weather_date is None:
		weather_info = functions_to_handle_requests.get_weather_from_yandex(functions_to_handle_requests.latlng(city))
		msg = functions_to_handle_requests.str_five_day_forecast(weather_info, functions_to_handle_requests.capitalize(city))
		bot.sendMessage(chat_id=update.message.chat_id, text=msg[0])
		bot.sendPhoto(chat_id = update.message.chat_id, photo = functions_to_handle_requests.find_picture(city, msg[1]))
		return

	weather_info = functions_to_handle_requests.long_weather(functions_to_handle_requests.latlng(city), weather_date)
	msg = functions_to_handle_requests.str_day_forecast(weather_info,functions_to_handle_requests.capitalize(city), weather_date, short = False)
	bot.sendMessage(chat_id=update.message.chat_id, text=msg[0])
	bot.sendPhoto(chat_id = update.message.chat_id, photo = functions_to_handle_requests.find_picture(city, msg[1]))


def proceed_wrong_request(bot, update):
	bot.sendMessage(chat_id=update.message.chat_id, text="Моя твоя не понимать")
	bot.sendPhoto(chat_id = update.message.chat_id, photo = 'http://img1.joyreactor.cc/pics/comment/Игры-Life-is-Strange-Max-Caulfield-Chloe-Price-2108175.jpeg')


updater = Updater(token='513351366:AAFoIx5GK4d4v0bINX70JRUgT_6DxrYF64c')

start_handler = CommandHandler('start', start)
updater.dispatcher.add_handler(start_handler) 
help_handler = CommandHandler('help', help)
updater.dispatcher.add_handler(help_handler) 
request_handler = MessageHandler(Filters.text, proceed_request)
updater.dispatcher.add_handler(request_handler) 

wrong_request_handler = MessageHandler(Filters.all, proceed_wrong_request)
updater.dispatcher.add_handler(wrong_request_handler) 


updater.start_polling()

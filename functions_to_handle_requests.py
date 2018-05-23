import calendar
import datetime
import geocoder
import re
import requests
import pymorphy2

ya_weather_api_key = 'fb278b91-e9a0-4ec3-a8be-1c631e52f395'
google_geocoder_key = 'AIzaSyBKsepsxGEwETPARwZ1YvuNTyLoOfKO3vM'
url_orfography = 'https://speller.yandex.net/services/spellservice.json/checkText?text={word}'
bing_key = 'c958282f5bbb4f4ba855bc29dd29e664'

day_signs = {'сегодня' : 0, 'сейчас' : 0,  'завтра' : 1, 'послезавтра' : 2, 'послепослезавтра' : 3 }
weekdays_long = {'понедельник' : 0, 'вторник' : 2, 'среда' : 2, 'четверг' : 3, 'пятница' : 4, 'суббота' : 5, 'воскресение' : 6}
weekdays_mid = {'пнд' : 0, 'втр' : 2, 'срд' : 2, 'чтв' : 3, 'птн' : 4, 'сбт' : 5, 'вск' : 6}
weekdays_short = {'пн' : 0, 'вт' : 2, 'ср' : 2, 'чт' : 3, 'пт' : 4, 'сб' : 5, 'вс' : 6}

weekdays = dict()
weekdays.update(weekdays_short)
weekdays.update(weekdays_mid)
weekdays.update(weekdays_long)

months = {"01" : "января", "02" : "февраля", "03" : "марта", "04": "апреля", "05" : "мая", "06":"июня", "07":"июля", "08" :\
 "август", "09" : "сентября", "10" : "октября", "11" : "ноября", "12": "декабря"}

months_dict =  {"январь" : '01', "февраль" : '02', "март" : '03', "апрель" : '04', "май" : '05', "июнь" : '06', "июль" :\
 '07', "август" : '08',  "сентябрь" :'09', "октябрь" : '10', "ноябрь" : '11', "декабрь" : '12'}

prec_strength = ['', 'слабый', "", "сильный", "очень сильный"]

prec_type = ['','дождь', 'дождь со снегом', 'снег']

day_parts = ['утро', "день", "вечер", "ночь"]

cherez = {"через", "чрез", "спустя"}

chisl = {"ноль" : 0,'один' : 1, "два": 2, "три":3, "четыре":4, "пять":5}

not_cities = {'день','город', 'град', "лола", "и-чо"}


def capitalize_first_word(string):
	x = re.split(" ", string)
	x[0] = x[0].capitalize()
	return " ".join(x)

def translate(word, lan = 'en-ru'):
	url ='https://translate.yandex.net/api/v1.5/tr.json/translate?key=trnsl.1.1.2'\
	'0180516T214229Z.50a48fcd84bcd2ec.c7e27dfa1e2f8902ba805f8c299b673492c3993f&lang={lan}&text={txt}'
	r = requests.get(url.format(txt = word, lan = lan)).json()
	return(r['text'][0])

def capitalize(city):
	city = pymorphy2.MorphAnalyzer().parse(translate(city))[0].normal_form
	x = re.split("-", city)
	if len(x)!=2:
		return city.capitalize()
	x[0] = x[0].capitalize()
	x[1] = x[1].capitalize()
	return x[0] + '-' + x[1]

def correction_of_misspells(word):
	if re.match('[\d]+', word):
		return word
	url = 'https://speller.yandex.net/services/spellservice.json/checkText?text={txt}'
	r = requests.get(url.format(txt = word)).json()
	if len(r) > 0 and 's' in r[0].keys() and len(r[0]['s']) > 0:
		word = r[0]['s'][0]
	return word


def normal_form(word):
	return pymorphy2.MorphAnalyzer().parse(word)[0].normal_form


def find_in_words(word_dict, words):
	for word in words:
		if word  in word_dict:
			return word
	

def words_in_normal_form(message):
	txt = message['text']
	maybe_words = re.split('[\s.,:;!@#?$%]+', txt)
	words = []
	for maybe_word in maybe_words:
		if maybe_word in weekdays:
			words.append(maybe_word)
			continue
		corrected_word = correction_of_misspells(maybe_word)
		if corrected_word is not None and ((len(corrected_word) > 2 or corrected_word in weekdays_short) or re.match('[\d]+', corrected_word)):
			words.append(corrected_word)

	words_in_normal_form = [normal_form(word) for word in words]

	return words_in_normal_form


def latlng(city):
	return geocoder.google(city, key = google_geocoder_key).latlng

def get_weather_from_yandex(latlng):
	url = 'https://api.weather.yandex.ru/v1/forecast?lat={lat}&lon={lng}&lang=ru_RU&110n=true'.format(lat = latlng[0], lng = latlng[1])

	return requests.get(url, headers = {'X-Yandex-API-Key': ya_weather_api_key}).json()

def yandex_weather_translations():
	url = 'https://api.weather.yandex.ru/v1/translations'
	return requests.get(url, headers = {'X-Yandex-API-Key': ya_weather_api_key}).json()

#возвращает дату или None
def find_date(words, current_date):
	month = find_in_words(months_dict.keys(), words)
	for word in words:
		if re.match('[\d]+', word):
			word = re.match('[\d]+', word).group(0)
			if 32 > int(word) > 9:
				if int(current_date[8:10]) <= int(word):
					month = current_date[5:7]
				else:
					if current_date[5:7] != '12':
						month = str(int(current_date[5:7])+1)
						if len(month) == 1:
							month = '0' + month
					else:
						month = '01'

				return current_date[0:4] +'-' + month + '-' + word
			if month is not None:
				day = ''
				if int(word) > 31:
					continue
				if int(word) < 10:
					day = '0' + word
				return current_date[0:4] +'-' + months_dict[month] + '-' + day
			else:
				if int(word) < 7:
					return str(datetime.date(int(current_date[0:4]),int(current_date[5:7]), int(current_date[8:10])) + datetime.timedelta(days = int(word)+1))

		elif word in chisl.keys():
			addition = chisl[word]
			return str(datetime.date(int(current_date[0:4]),int(current_date[5:7]), int(current_date[8:10])) + datetime.timedelta(days = addition + 1))

		else:
			if word in weekdays.keys():
				dif = weekdays[word] - calendar.weekday(int(current_date[0:4]),int(current_date[5:7]), int(current_date[8:10]))
				if dif < 0:
					dif +=7
				return str(datetime.date(int(current_date[0:4]),int(current_date[5:7]), int(current_date[8:10])) + datetime.timedelta(days = dif))
			elif word in day_signs.keys():
				return str(datetime.date(int(current_date[0:4]),int(current_date[5:7]), int(current_date[8:10])) + datetime.timedelta(days = day_signs[word]))


def find_city(words):
	for word in words:
		if len(word) > 3 and pymorphy2.MorphAnalyzer().parse(word)[0].tag.POS in {'NOUN'}:
			geocode = geocoder.geonames(word, key='schooler')
			pop = geocode.population
			if (pop is not None) and pop > 10000 and (word not in not_cities):
				return geocode.address


def find_picture(word, cond):
	url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
	headers = {"Ocp-Apim-Subscription-Key" : bing_key}
	params  = {"q": word + ' ' + cond, "license": "public", "imageType": "photo"}
	response = requests.get(url, headers=headers, params=params)
	search_results = response.json()
	if search_results is not None and 'value' in search_results.keys() and len(search_results["value"])>2 and "thumbnailUrl" in search_results["value"][2].keys():
		thumbnail_url = search_results["value"][2]["thumbnailUrl"]
	else:
		if cond != '':
			return find_picture(word, '')
		else:
			return 'http://lemurano.com.ua/images/207910cf4897b00385d57eeb91be8ad1.jpg'
	return thumbnail_url

 #date in format YYYY-MM-DD, no more than 6 days from now
def short_weather(latlng, date, part_of_day = 'day_short'):
	full_info = get_weather_from_yandex(latlng)
	forecasts = full_info['forecasts']
	forecast = dict()
	for fc in forecasts:
		if fc['date'] == date:
			forecast = fc['parts'][part_of_day]
			break
	return forecast

#return dict with keys утро , день, вечер, ночь
def long_weather(latlng, date):
	full_info = get_weather_from_yandex(latlng)
	forecasts = full_info['forecasts']
	forecast = dict()
	for fc in forecasts:
		if fc['date'] == date:
			forecast['утро'] = fc['parts']['morning']
			forecast['день'] = fc['parts']['day']
			forecast['вечер'] = fc['parts']['evening']
			forecast['ночь'] = fc['parts']['night']
			break
	return forecast


def str_day_forecast(weather, city, date, short = True ):
	if len(weather.keys()) < 4:
			return ['У меня нет информации на этот счет', '']
	translate = yandex_weather_translations()
	if short:
		tmp = '{date}:\n'\
		'{cond}, скорость ветра {wind_speed} м/с;\n'\
		"Средняя температура: {t_avg}" + u"\u2103" + ", ощущается как {t_feels}" + u"\u2103"
		return [tmp.format(date = date[8:10]+ " " + months[date[5:7]], t_avg = weather['temp'], t_feels = weather['feels_like'],
			cond = capitalize_first_word(translate[weather['condition']]),  wind_speed = weather['wind_speed']), capitalize_first_word(weather['condition'])]
	else:
		ans = 'Сколько ресурсов впустую!\n\n'\
		'{city}, {date}\n\n'.format(city = city, date = date[8:10]+ " " + months[date[5:7]])
		for part in day_parts:
			tmp = '{day_part}:\n'\
			'{cond}, скорость ветра {wind_speed} м/с;\n'\
			"Средняя температура: {t_avg}" + u"\u2103" + ", ощущается как {t_feels}" + u"\u2103" +"\n\n"
			ans += tmp.format( day_part = part.capitalize(), city = city, date = date[8:10]+ " " + months[date[5:7]], t_avg = weather[part]['temp_avg'], t_feels = weather[part]['feels_like'],
				cond = capitalize_first_word(translate[weather[part]['condition']]),  wind_speed = weather[part]['wind_speed'])
		ans += 'Надеюсь, ты доволен собой!'
		return [ans, capitalize_first_word(weather['день']['condition'])]


def str_five_day_forecast(full_weather, city):
	weather = full_weather['forecasts']
	if len(weather) <4:
		return ['У меня нет информации на этот счет', '']
	ans = 'Сколько ресурсов впустую!\n\n'\
	'{city}, прогноз на ближайшие пять дней.\n\n'.format(city = city)

	for i in range(5):
		cur_forecast = weather[i]['parts']['day_short']
		date = weather[i]['date']
		fcst = str_day_forecast(cur_forecast, city, date)
		ans += fcst[0] + '\n\n'
		if i == 0:
			cond = fcst[1]

	ans += "Все-таки людишкам тяжело живется, сочувствую"
	return [ans, cond]

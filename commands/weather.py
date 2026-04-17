from dotenv import load_dotenv
from utils.models import model_sentence_transformers
from sentence_transformers import util
from datetime import datetime, timedelta
import locale
import pandas as pd
from num2words import num2words
import pymorphy3
from urls.config import URLS
from words2numsrus import NumberExtractor

load_dotenv()

model_transformers = model_sentence_transformers
morph = pymorphy3.MorphAnalyzer()

extractor = NumberExtractor()


def get_date_by_weekday(target_weekday):
    weekdays = {
        "понедельник": 1,
        "вторник": 2,
        "среда": 3,
        "четверг": 4,
        "пятница": 5,
        "суббота": 6,
        "воскресенье": 7
    }

    target_weekday = weekdays[target_weekday]

    today = datetime.now()
    current_weekday = today.isoweekday()
    days_diff = target_weekday - current_weekday

    if days_diff < 0:
        days_diff += 7

    target_date = today + timedelta(days=days_diff)
    months = ["янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]
    return f'{target_date.day} {months[target_date.month - 1]}'


def get_word_list(query, list_, model=None):
    global model_transformers

    embs = model_transformers.encode(list_, convert_to_tensor=True)
    res = []
    words = query.split()
    for w in words:
        query_em = model_transformers.encode(w, convert_to_tensor=True)
        s = util.cos_sim(query_em, embs)[0]

        for idx, i in enumerate(s):
            if i.item() >= 0.9:
                res.append({
                    'index': idx,
                    'k': i.item(),
                    'name': list_[idx]
                })
    res = sorted(res, key=lambda a: a['k'], reverse=True)
    return res


def speak_weather(city, temp, today, day):
    v = 'в '
    if day == 'сегодня':
        v = ''
    return (
        f'{v}{day} в {city.inflect({'datv'}).word} минимальная температура {num2words(today.iloc[0]['temp_min'], lang='ru')} {temp.make_agree_with_number(today.iloc[0]['temp_min']).word}. '
        f'Максимальная температура {num2words(today.iloc[0]['temp_max'], lang='ru')} {temp.make_agree_with_number(today.iloc[0]['temp_max']).word}. '
        f'{today.iloc[0]['description']}')


def get_weather(query, model=None):
    locale.setlocale(locale.LC_TIME, 'russian')
    data_weather = pd.read_csv(URLS['weather_csv'])

    days = ['сегодня', 'завтра', 'сейчас']
    res = get_word_list(query, days)
    f = None

    temp = morph.parse('градус')[0]
    city = morph.parse('москва')[0]

    if res:
        f = res[0]['name']
    now = datetime.now()

    if f == 'сегодня':
        day_of_month = now.day
        month_short = now.strftime("%b")
        key = f'{day_of_month} {month_short}'
        today = data_weather[data_weather['date'] == key]

        return speak_weather(city, temp, today, 'сегодня')

    elif f == 'завтра':
        next_day = now + timedelta(days=1)
        day_of_month = next_day.day
        month_short = next_day.strftime("%b")
        key = f'{day_of_month} {month_short}'
        today = data_weather[data_weather['date'] == key]
        print(data_weather['date'])
        print(key)
        return speak_weather(city, temp, today, 'завтра')

    # elif f == 'сейчас':

    else:
        days_of_week = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
        res = get_word_list(query, days_of_week, model)
        if res:
            key = get_date_by_weekday(res[0]['name'])
            today = data_weather[data_weather['date'] == key]
            day = res[0]['name']
            if res[0]['name'] == 'среда':
                day = 'среду'
            elif res[0]['name'] == 'пятница':
                day = 'пятницу'
            elif res[0]['name'] == 'суббота':
                day = 'субботу'
            return speak_weather(city, temp, today, day)
        else:
            result = extractor.replace_groups(query)
            months = {
                "январь": "янв",
                "февраль": "фев",
                "март": "мар",
                "апрель": "апр",
                "май": "май",
                "июнь": "июн",
                "июль": "июл",
                "август": "авг",
                "сентябрь": "сен",
                "октябрь": "окт",
                "ноябрь": "ноя",
                "декабрь": "дек"
            }
            month = get_word_list(query, list(months.keys()), model)
            if month:
                s_name = months[month[0]['name']]
                number = ''
                for i in result:
                    if i.isdigit():
                        number += i
                if number != '':
                    full_number = f'{number} {s_name}'
                    number_month = data_weather[data_weather['date'] == full_number]
                    print(number_month)

            # data_weather = pd.read_csv(URLS['weather_now'])
        return (
            f'сейчас в {city.inflect({'datv'}).word} {num2words(data_weather.iloc[0]['now_weather'], lang='ru')} {temp.make_agree_with_number(data_weather.iloc[0]['now_weather']).word}. '
            f'ощущается как {num2words(data_weather.iloc[0]['now_feel'], lang='ru')} {temp.make_agree_with_number(data_weather.iloc[0]['now_feel']).word}. '
            f'{data_weather.iloc[0]['now_desc']}')


get_weather('какая погода двадцать первого апреля')

from dotenv import load_dotenv
from models import model_sentence_transformers
from sentence_transformers import util
from datetime import datetime
import locale
import pandas as pd
from num2words import num2words

load_dotenv()

model_transformers = model_sentence_transformers


def get_word_list(query, list_, model=None):
    global model_transformers

    embs = model_transformers.encode(list_, convert_to_tensor=True)
    res = []
    words = query.split()
    for w in words:
        query_em = model_transformers.encode(w, convert_to_tensor=True)
        s = util.cos_sim(query_em, embs)[0]

        for idx, i in enumerate(s):
            if i.item() >= 0.8:
                res.append({
                    'index': idx,
                    'k': i.item(),
                    'name': list_[idx]
                })
    res = sorted(res, key=lambda a: a['k'], reverse=True)
    return res


def get_weather(query, model=None):
    data_weather = pd.read_csv('weather_data.csv')

    days_of_week = ['сегодня', 'завтра']
    res = get_word_list(query, days_of_week)
    f = None

    if res:
        f = res[0]['name']

    if f == 'сегодня':
        locale.setlocale(locale.LC_TIME, 'russian')
        now = datetime.now()
        day_of_month = now.day
        month_short = now.strftime("%b")
        key = f'{day_of_month} {month_short}'
        today = data_weather[data_weather['date'] == key]

        return (
            f'Сегодня в Москве минимальная температура {num2words(today.iloc[0]['temp_min'], lang='ru')} градусов. '
            f'Максимальная температура {num2words(today.iloc[0]['temp_max'], lang='ru')} градусов. '
            f'{today.iloc[0]['description']}')
    elif f == 'завтра':
        pass
    else:
        m = ["январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август", "сентябрь", "октябрь", "ноябрь",
             "декабрь"]

        print(get_word_list(query, m, model))


get_weather('какая сегодня погода')

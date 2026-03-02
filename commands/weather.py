import os
from pyowm import OWM
from dotenv import load_dotenv
from pyowm.utils import timestamps
from models import model_sentence_transformers
from sentence_transformers import util

load_dotenv()

model = model_sentence_transformers


def get_word_list(query, list_):
    global model

    embs = model.encode(list_, convert_to_tensor=True)
    res = []
    words = query.split()
    for w in words:
        query_em = model.encode(w, convert_to_tensor=True)
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


def get_weather(query):
    global model

    days_of_week = ['сегодня', 'завтра']
    res = get_word_list(query, days_of_week)
    f = None

    if res:
        f = res[0]['name']
        print(f)

    if f == 'сегодня':
        print(1)
        pass
    elif f == 'завтра':
        pass
    else:
        m = ["январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август", "сентябрь", "октябрь", "ноябрь",
             "декабрь"]

        print(get_word_list(query, m))


get_weather('какая сегодня погода')

import json
import locale
from datetime import datetime, timedelta

import pandas as pd
import pymorphy3
from num2words import num2words
from sentence_transformers import util
from words2numsrus import NumberExtractor

from utils.models import model_sentence_transformers
from urls.config import URLS

model_transformers = model_sentence_transformers
morph = pymorphy3.MorphAnalyzer()
extractor = NumberExtractor()

MONTHS_SHORT = {
    "янв": 1, "фев": 2, "мар": 3, "апр": 4, "май": 5, "июн": 6,
    "июл": 7, "авг": 8, "сен": 9, "окт": 10, "ноя": 11, "дек": 12,
}


# ---------- Безопасное склонение ----------

def _inflect(parsed_or_word, grammemes, default=None):
    if parsed_or_word is None:
        return default

    if isinstance(parsed_or_word, str):
        raw = parsed_or_word.strip()
        if not raw:
            return default or raw
        parsed = morph.parse(raw.lower())[0]
        result = parsed.inflect(grammemes)
        if result is None:
            return default or raw
        word = result.word
        return word[:1].upper() + word[1:] if raw[:1].isupper() else word

    result = parsed_or_word.inflect(grammemes)
    word = result.word if result is not None else (default or parsed_or_word.word)
    if parsed_or_word.word[:1].isupper():
        word = word[:1].upper() + word[1:]
    return word


def _parse_city(name):
    if not name:
        return morph.parse('город')[0]
    return morph.parse(name.strip())[0]


def _to_int(value):
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _load_csv(path):
    import os
    if not path or not os.path.exists(path) or os.path.getsize(path) == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


# ---------- Нормализация дат ----------

def _normalize_dates(df):
    if df.empty or 'date' not in df.columns:
        return df

    df = df.copy()
    months_per_row = []
    for raw in df['date'].astype(str):
        parts = raw.strip().split()
        if len(parts) == 2 and parts[1][:3].lower() in MONTHS_SHORT:
            months_per_row.append(MONTHS_SHORT[parts[1][:3].lower()])
        else:
            months_per_row.append(None)

    current_month = None
    filled = []
    for m in months_per_row:
        if m is not None:
            current_month = m
        filled.append(current_month)

    year = datetime.now().year
    dates = []
    for raw, month in zip(df['date'].astype(str), filled):
        try:
            day = int(raw.strip().split()[0])
        except (ValueError, IndexError):
            dates.append(pd.NaT)
            continue
        if month is None:
            dates.append(pd.NaT)
            continue
        try:
            dates.append(datetime(year, month, day))
        except ValueError:
            dates.append(pd.NaT)

    df['_date'] = dates
    return df


# ---------- Работа с днями недели ----------

def get_date_by_weekday(target_weekday):
    weekdays = {"понедельник": 1, "вторник": 2, "среда": 3, "четверг": 4,
                "пятница": 5, "суббота": 6, "воскресенье": 7}
    target = weekdays[target_weekday]
    today = datetime.now()
    diff = target - today.isoweekday()
    if diff < 0:
        diff += 7
    return (today + timedelta(days=diff)).date()


# ---------- Поиск по эмбеддингам ----------

def get_word_list(query, list_, model=None):
    global model_transformers
    embs = model_transformers.encode(list_, convert_to_tensor=True)
    res = []
    for w in query.split():
        query_em = model_transformers.encode(w, convert_to_tensor=True)
        s = util.cos_sim(query_em, embs)[0]
        for idx, i in enumerate(s):
            if i.item() >= 0.9:
                res.append({'index': idx, 'k': i.item(), 'name': list_[idx]})
    return sorted(res, key=lambda a: a['k'], reverse=True)


# ---------- Согласование градусов ----------

def _agree(temp, n):
    n = abs(n)
    if n % 10 == 1 and n % 100 != 11:
        return _inflect(temp, {'sing', 'nomn'})
    if 2 <= n % 10 <= 4 and not (12 <= n % 100 <= 14):
        return _inflect(temp, {'sing', 'gent'})
    return _inflect(temp, {'plur', 'gent'})


# ---------- Формирование фразы ----------

def speak_weather(city, temp, today, day):
    city_datv = _inflect(city, {'datv'}, default='городе')

    if today is None or today.empty:
        return f'Нет данных о погоде на {day} в {city_datv}.'

    row = today.iloc[0]
    t_min = _to_int(row.get('temp_min'))
    t_max = _to_int(row.get('temp_max'))
    description = row.get('description', '') or ''

    if t_min is None or t_max is None:
        return f'Нет корректных данных о температуре на {day} в {city_datv}.'

    v = 'в ' if day in ['сегодня', 'завтра'] else ''

    return (
        f'{v}{day} в {city_datv} минимальная температура '
        f'{num2words(t_min, lang="ru")} {_agree(temp, t_min)}. '
        f'Максимальная температура '
        f'{num2words(t_max, lang="ru")} {_agree(temp, t_max)}. '
        f'{description}.'
    )


# ---------- Основная функция ----------

def get_weather(query, model=None):
    try:
        locale.setlocale(locale.LC_TIME, 'russian')
    except locale.Error:
        pass

    data_weather = _normalize_dates(_load_csv(URLS['weather_csv']))

    days = ['сегодня', 'завтра', 'сейчас']
    res = get_word_list(query, days)
    f = res[0]['name'] if res else None

    try:
        with open(URLS['current_city'], 'r', encoding='utf-8') as file:
            city_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return 'Не удалось определить город.'

    temp = morph.parse('градус')[0]
    city = _parse_city(city_data.get('name', ''))

    now = datetime.now()

    if f == 'сегодня':
        if data_weather.empty:
            return 'Нет данных о погоде.'
        today = data_weather[data_weather['_date'].dt.date == now.date()]
        return speak_weather(city, temp, today, 'сегодня')

    elif f == 'завтра':
        if data_weather.empty:
            return 'Нет данных о погоде.'
        tomorrow = (now + timedelta(days=1)).date()
        today = data_weather[data_weather['_date'].dt.date == tomorrow]
        return speak_weather(city, temp, today, 'завтра')

    elif f == 'сейчас':
        data_now = _load_csv(URLS['weather_now'])
        if data_now.empty:
            return 'Нет данных о текущей погоде.'

        row = data_now.iloc[0]
        now_t = _to_int(row.get('now_weather'))
        now_f = _to_int(row.get('now_feel'))
        now_desc = row.get('now_desc', '') or ''

        city_datv = _inflect(city, {'datv'}, default='городе')

        if now_t is None or now_f is None:
            return f'Сейчас в {city_datv} {now_desc}.'

        return (
            f'Сейчас в {city_datv} {num2words(now_t, lang="ru")} {_agree(temp, now_t)}. '
            f'Ощущается как {num2words(now_f, lang="ru")} {_agree(temp, now_f)}. '
            f'{now_desc}.'
        )

    else:
        days_of_week = ["понедельник", "вторник", "среда", "четверг",
                        "пятница", "суббота", "воскресенье"]
        res = get_word_list(query, days_of_week, model)
        if res:
            if data_weather.empty:
                return 'Нет данных о погоде.'
            target_date = get_date_by_weekday(res[0]['name'])
            today = data_weather[data_weather['_date'].dt.date == target_date]
            day = _inflect(morph.parse(res[0]['name'])[0], {'accs'})
            return speak_weather(city, temp, today, day)

        # --- Поиск по месяцу и числу ---
        result = extractor.replace_groups(query)
        months = {
            "январь": "янв", "февраль": "фев", "март": "мар",
            "апрель": "апр", "май": "май", "июнь": "июн",
            "июль": "июл", "август": "авг", "сентябрь": "сен",
            "октябрь": "окт", "ноябрь": "ноя", "декабрь": "дек",
        }
        month = get_word_list(query, list(months.keys()), model)
        if month:
            if data_weather.empty:
                return 'Нет данных о погоде.'

            s_name = months[month[0]['name']]
            number = ''.join(i for i in result if i.isdigit())
            if number != '':
                month_num = MONTHS_SHORT[s_name[:3]]
                try:
                    target_date = datetime(now.year, month_num, int(number)).date()
                except ValueError:
                    return f'Нет такой даты: {number} {month[0]["name"]}.'
                weather = data_weather[data_weather['_date'].dt.date == target_date]
                if weather.empty:
                    return f'Нет данных о погоде на {number} {month[0]["name"]}.'
                city_datv = _inflect(city, {'datv'}, default='городе')
                t_min = _to_int(weather.iloc[0].get('temp_min'))
                t_max = _to_int(weather.iloc[0].get('temp_max'))
                desc = weather.iloc[0].get('description', '') or ''
                if t_min is None or t_max is None:
                    return f'Нет корректных данных о температуре на {number} {month[0]["name"]}.'
                return (
                    f'В эту дату в {city_datv} минимальная температура '
                    f'{num2words(t_min, lang="ru")} {_agree(temp, t_min)}. '
                    f'Максимальная температура '
                    f'{num2words(t_max, lang="ru")} {_agree(temp, t_max)}. '
                    f'{desc}.'
                )

    return 'Не понял, на какой день нужен прогноз погоды.'
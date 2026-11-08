import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
from user_data.change_city import get_weather_link
import os
from urls.config import URLS


def _parse_month_items(soup):
    """Парсит месячный прогноз из div.widget-month .widget-body."""
    widget = soup.find('div', class_='widget-month')
    if not widget:
        return []

    body = widget.find('div', class_='widget-body')
    if not body:
        return []

    items = body.find_all(['div', 'a'], class_='row-item-month-date')
    result = []

    for item in items:
        date_el = item.find('div', class_='date')
        if not date_el:
            continue
        date_text = date_el.get_text(strip=True)  # "26 окт" или "27"

        temp_el = item.find('div', class_='temp')
        maxt = 'N/A'
        mint = 'N/A'

        if temp_el:
            max_el = temp_el.find('div', class_='maxt')
            if max_el:
                tv = max_el.find('temperature-value')
                if tv and tv.get('value') is not None:
                    maxt = tv['value']

            min_el = temp_el.find('div', class_='mint')
            if min_el:
                tv = min_el.find('temperature-value')
                if tv and tv.get('value') is not None:
                    mint = tv['value']

        description = item.get('data-tooltip', '')

        result.append({
            'date': date_text,
            'temp_max': maxt,
            'temp_min': mint,
            'description': description,
        })

    return result


def parser_weather():
    if not os.path.exists(URLS['current_city']):
        get_weather_link()

    with open(URLS['current_city'], 'r', encoding='utf-8') as f:
        link = json.load(f)['link']

    url = f'{link}/month/'
    now_url = f'{link}/now/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html',
    }

    # ---- Месячный прогноз ----
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        text = response.text
        with open(URLS['weather_txt'], 'w', encoding='utf-8') as f:
            f.write(text)
    except Exception:
        with open(URLS['weather_txt'], 'r', encoding='utf-8') as f:
            text = f.read()

    soup = BeautifulSoup(text, 'html.parser')
    weather_data = _parse_month_items(soup)

    if weather_data:
        df = pd.DataFrame(weather_data)
        df.to_csv(URLS['weather_csv'], index=False, encoding='utf-8')
    else:
        # не перезаписываем CSV пустым файлом
        print('Месячный прогноз не найден — CSV не обновлён')

    # ---- Погода сейчас ----
    try:
        response_now = requests.get(now_url, headers=headers, timeout=10)
        response_now.raise_for_status()
        text_now = response_now.text
    except Exception:
        with open(URLS['weather_txt'], 'r', encoding='utf-8') as f:
            text_now = f.read()

    soup_now = BeautifulSoup(text_now, 'html.parser')

    now_weather_el = soup_now.find('div', class_='now-weather')
    now_feel_el = soup_now.find('div', class_='now-feel')
    now_desc_el = soup_now.find('div', class_='now-desc')
    now_localdate_el = soup_now.find('div', class_='now-localdate')

    now_weather = now_weather_el.find('temperature-value').get('value', '') if now_weather_el else ''
    now_feel = now_feel_el.find('temperature-value').get('value', '') if now_feel_el else ''
    now_desc = now_desc_el.get_text(strip=True) if now_desc_el else ''
    now_localdate = now_localdate_el.get_text(strip=True) if now_localdate_el else ''

    now_hum = ''
    for item in soup_now.find_all('div', class_='now-info-item'):
        title_el = item.find('div', class_='item-title')
        if title_el and title_el.get_text(strip=True) == 'Влажность':
            value_el = item.find('div', class_='item-information')
            if value_el:
                inner = value_el.find('div', class_='item-value')
                now_hum = inner.get_text(strip=True) if inner else value_el.get_text(strip=True)
            break

    df_now = pd.DataFrame([{
        'datetime': now_localdate,
        'now_weather': now_weather,
        'now_feel': now_feel,
        'now_desc': now_desc,
        'now_hum': now_hum,
    }])
    df_now.to_csv(URLS['weather_now'], index=False, encoding='utf-8')


if __name__ == '__main__':
    parser_weather()
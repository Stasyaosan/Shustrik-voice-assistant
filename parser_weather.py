import json

import requests
from bs4 import BeautifulSoup
import pandas as pd
from user_data.change_city import get_weather_link
import os


def parser_weather():
    if not os.path.exists('user_data/current_city.json'):
        get_weather_link()

    with open('user_data/current_city.json', 'r', encoding='utf-8') as f:
        link = json.load(f)['link']

    url = f'{link}/month/'
    now_url = f'{link}/now/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        text = response.text
        with open('data_weather.txt', 'w', encoding='utf-8') as f:
            f.write(text)
    except:
        with open('data_weather.txt', 'r', encoding='utf-8') as f:
            text = f.read()

    try:
        response_now = requests.get(now_url, headers=headers, timeout=10)
        response_now.raise_for_status()
        text_now = response_now.text
        with open('data_weather.txt', 'w', encoding='utf-8') as f:
            f.write(text)
    except:
        with open('data_weather.txt', 'r', encoding='utf-8') as f:
            text_now = f.read()

    soup = BeautifulSoup(text, 'html.parser')
    weather_items = soup.find_all(['div', 'a'], 'row-item-month-date')
    if not weather_items:
        print('Элементы не найдены')
    else:
        q = ''
        weather_data = []
        for i in weather_items:
            date_elem = i.find('div', class_='date')
            date = date_elem.text.strip()
            temp_elem = i.find('div', class_='temp')

            if not date.isdigit():
                q = ''
                for char in date:
                    if not char.isdigit() and not char == ' ':
                        q += char

            description = i.get('data-tooltip', '')

            if temp_elem:

                max_elem = temp_elem.find('div', class_='maxt')
                if max_elem:
                    temp_elem_temp_maxt = max_elem.find('temperature-value')
                    if temp_elem_temp_maxt:
                        maxt = temp_elem_temp_maxt.get('value')
                mix_elem = temp_elem.find('div', class_='mint')
                if mix_elem:
                    temp_elem_temp_mint = mix_elem.find('temperature-value')
                    if temp_elem_temp_mint:
                        mint = temp_elem_temp_mint.get('value')
            else:
                maxt = 'N/A'
                mint = 'N/A'

            if q != '':
                date = date.replace(q, '').strip()
                weather_data.append({
                    'date': f'{date} {q}',
                    'temp_max': maxt,
                    'temp_min': mint,
                    'description': description
                })
        df = pd.DataFrame(weather_data)
        df.to_csv('weather_data.csv')

    soup_now = BeautifulSoup(text_now, 'html.parser')
    now_weather = soup_now.find('div', class_='now-weather').find('temperature-value').get('value', '')
    now_feel = soup_now.find('div', class_='now-feel').find('temperature-value').get('value', '')
    now_desc = soup_now.find('div', class_='now-desc').text.strip()
    now_localdate = soup_now.find('div', class_='now-localdate').text

    now_ps = soup_now.find_all('div', class_='now-info-item')
    now_hum = ''
    for i in now_ps:
        title = i.find('div', class_='item-title').text.strip()
        if title == 'Влажность':
            info = i.find('div', class_='item-information').find('div', class_='item-value').text
            now_hum = info
            break

    weather_data_now = [{
        'datetime': now_localdate.strip(),
        'now_weather': now_weather.strip(),
        'now_feel': now_feel.strip(),
        'now_desc': now_desc.strip(),
        'now_hum': now_hum.strip()
    }]

    df = pd.DataFrame(weather_data_now)
    df.to_csv('weather_data_now.csv')


parser_weather()

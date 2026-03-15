import requests
from bs4 import BeautifulSoup
import pandas as pd


def parser_weather():
    url = 'https://www.gismeteo.ru/weather-moscow-4368/month/'
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
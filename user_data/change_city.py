import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd


def get_weather_link(city=''):
    driver = webdriver.Chrome()
    driver.get('https://www.gismeteo.ru/')

    input_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'js-input'))
    )
    input_element.send_keys(city)
    time.sleep(1)

    wait = WebDriverWait(driver, 10)
    dropdown_list = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, 'group-cities'))
    )
    city_items = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.group-city a.city-link'))
    )

    if city_items:
        link = city_items[0].get_attribute('href')
        with open('user_data/current_city.json', 'w', encoding='utf-8') as f:
            json.dump({'name': city, 'link': link}, f, indent=4)
        return True

    driver.quit()
    return False


def change_city(words):
    df = pd.read_json('user_data/russia-cities.json')

    words = words.split()
    word = ''
    for i in words:
        j = False
        for idx, row in df.iterrows():
            row_ = row['namecase'].values()
            if i in row_:
                word = row['name']
                j = True
                break
        if j:
            break
    get_weather_link(word)
    return word

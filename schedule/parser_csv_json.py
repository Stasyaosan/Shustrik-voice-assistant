import json
import pandas as pd
from datetime import datetime

df = pd.read_csv('9а.csv')


def get_schedule(day_of_week):
    pn = df[df['день'] == f'1.{day_of_week}']
    pn = pn[['время', 'предмет', 'кабинеты', 'учитель', 'учитель на замену']]
    current_time_hour = datetime.now().hour
    current_time_minutes = datetime.now().minute

    pn['часы'] = pn['время'].str.split(':').str[0].astype(int)
    pn['минуты'] = pn['время'].str.split(':').str[1].astype(int)

    pn = pn[pn['часы'] >= current_time_hour]
    pn = pn.reset_index(drop=True)
    res = {}
    index = 0
    for key, value in pn.to_dict().items():

        for i, j in value.items():
            if i in res:
                res[i].append(j)
            else:
                res[i] = [j]
    print(res)


get_schedule('пн')

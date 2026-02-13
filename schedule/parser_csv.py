import pandas as pd
from datetime import datetime

df = pd.read_csv('schedule/9а.csv')

d = {
    'пн': 1,
    'вт': 2,
    'ср': 3,
    'чт': 4,
    'пт': 5
}


def get_schedule(day_of_week, m=False):
    pn = df[df['день'] == f'{d[day_of_week]}.{day_of_week}']
    pn = pn[['время', 'предмет', 'кабинеты', 'учитель', 'учитель на замену']]
    current_time_hour = datetime.now().hour
    current_time_minutes = datetime.now().minute

    pn['часы'] = pn['время'].str.split(':').str[0].astype(int)
    pn['минуты'] = pn['время'].str.split(':').str[1].astype(int)

    if m:
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
    return res

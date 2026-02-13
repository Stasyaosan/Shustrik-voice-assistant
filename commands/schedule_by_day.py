from datetime import datetime
from num2words import num2words

from schedule.parser_csv import get_schedule


def schedule_speak(speak, d, count=0, m=False):
    now = datetime.now()
    day_today = now.weekday() + count
    schedule = None
    if day_today <= 4:
        day_ = list(d.items())[day_today]
        schedule = day_
    if schedule:
        schedule = get_schedule(schedule[1], m)
        for index_n, data_schedule in schedule.items():
            time = data_schedule[0].split(':')
            speak(f'Расписание на время {num2words(time[0], lang='ru')} {num2words(time[1], lang='ru')}')
            speak(f'Предмет: {data_schedule[1]}')


def schedule_by_day(command, speak):
    d = {
        'понедельник': 'пн',
        'вторник': 'вт',
        'среда': 'ср',
        'четверг': 'чт',
        'пятница': 'пт',
    }
    day = None
    for day_of_week, sr_day_of_week in d.items():
        if day_of_week.lower() in command.lower():
            day = sr_day_of_week
    if day:
        schedule = get_schedule(day)
        for index_n, data_schedule in schedule.items():
            time = data_schedule[0].split(':')
            speak(f'Расписание на время {num2words(time[0], lang='ru')} {num2words(time[1], lang='ru')}')
            speak(f'Предмет: {data_schedule[1]}')
        if schedule:
            pass
        else:
            pass
    else:
        if 'сегодня' in command:
            schedule_speak(speak, d)
        elif 'сейчас' in command:
            schedule_speak(speak, d, m=True)
        elif 'завтра' in command:
            schedule_speak(speak, d, 1)

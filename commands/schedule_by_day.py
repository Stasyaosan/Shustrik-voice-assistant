from datetime import datetime
from num2words import num2words
from parser_csv import get_schedule
from models import model_sentence_transformers
from sentence_transformers import util


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


def schedule_subject(query, speak):
    d = {
        'понедельник': 'пн',
        'вторник': 'вт',
        'среда': 'ср',
        'четверг': 'чт',
        'пятница': 'пт',
    }
    model = model_sentence_transformers
    query_em = model.encode(query, convert_to_tensor=True)

    day_of_week = ['Понедельник', 'Вторник', 'Среда', "Четверг", "Пятница"]
    program_embs = model.encode(day_of_week, convert_to_tensor=True)

    s = util.cos_sim(query_em, program_embs)[0]

    res = []
    for idx, i in enumerate(s):
        if i.item() >= 0.5:
            res.append({
                'index': idx,
                'k': i.item(),
                'name': day_of_week[idx]
            })
    if res:
        res = sorted(res, key=lambda m: m['k'])[-1]['name']
        day_of_week_ = d[res.lower()]
        day_of_week_full = res.lower()
        schedule = get_schedule(day_of_week_)
        subjects = []
        for i, data in schedule.items():
            subjects.append(data[1])
        program_embs = model.encode(subjects, convert_to_tensor=True)
        s = util.cos_sim(query_em, program_embs)[0]
        res = []
        for idx, i in enumerate(s):
            if i.item() >= 0.5:
                res.append({
                    'index': idx,
                    'k': i.item(),
                    'name': subjects[idx]
                })
        if res:
            res = sorted(res, key=lambda m: m['k'])[-1]['name']
            subject = res
            subject_current = []
            for i, data in schedule.items():
                if data[1] == subject:
                    subject_current.append(data)
            print(subject_current)
            for i in subject_current:
                time = i[0].split(':')
                speak(f'Расписание в {i[1]} на время {num2words(time[0], lang='ru')} {num2words(time[1], lang='ru')}')
                speak(f'Преподаватель: {i[2]}')
        else:
            schedule_by_day(day_of_week_full, speak)

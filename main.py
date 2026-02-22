import json
import time
from datetime import datetime
from siler_audio import Silero
from num2words import num2words
from Query_recognition import Query
from pyowm import OWM
from dotenv import load_dotenv
import os
from open_program import ProgramSearcher
from wikipedia_api import Wiki
from commands.schedule_by_day import *
from Threads import SpeakThread
from vosk_recognition import vosk_rec

audio_silero = Silero()
qr = Query()

load_dotenv()


class Voice:
    def __init__(self):
        self.is_listening = False
        self.ps = ProgramSearcher()
        self.wiki = Wiki()
        self.q = SpeakThread()
        self.q.start()
        with open('config.json', 'r', encoding='utf-8') as f:
            self.intents_keys = json.load(f)['intents'].keys()

        # self.calibrate_microphone()

    def speak(self, text):
        print(f"[speak] {text}")
        self.q.add(audio_silero.silero_tts_basic, text)

    def stop(self):
        print("[stop] Остановка...")
        self.is_listening = False

    # def calibrate_microphone(self):
    #     print("Калибровка микрофона...")
    #     try:
    #         with self.microphone as source:
    #             self.recognizer.adjust_for_ambient_noise(source, duration=2)
    #         print("Калибровка завершена!")
    #         return True
    #     except Exception as e:
    #         print(f"Ошибка калибровки микрофона: {e}")
    #         return False

    def listen(self):
        try:
            text = vosk_rec()
            return text.lower()

        except Exception as e:
            print(f"Ошибка слушания: {e}")
            return ""

    def delete_commands(self, command, indent):
        command_worlds = command.split(" ")
        for i in range(len(command_worlds)):
            if qr.get_intent(command_worlds[i]) == indent:
                command = command.replace(command_worlds[i], '')
        command = command.strip()
        return command

    def process_command(self, command):
        if not command:
            return

        index = command.find('барсик')
        if index != -1:
            command = command[index:]

        if not command.startswith('барсик'):
            return

        print(f"Команда: {command}")

        command = command.replace('барсик', '').strip()

        args = command
        for intent in self.intents_keys:
            args = self.delete_commands(command, intent)

        if qr.get_intent(command):
            self.q.clear()

        if qr.get_intent(command) == 'greeting':
            self.speak("Привет! Рад вас слышать!")

        elif qr.get_intent(command) == 'time':
            h = datetime.now().strftime("%H")
            m = datetime.now().strftime("%M")
            a_h = num2words(h, lang='ru')
            a_m = num2words(m, lang='ru')
            self.speak(f"Сейчас {a_h} {a_m}")

        elif qr.get_intent(command) == 'schedule_by_day':
            schedule_subject(command, self.speak)

        elif qr.get_intent(command) == 'weather':
            own = OWM(os.getenv('API_KEY_WEATHER'))
            mgr = own.weather_manager()
            obs = mgr.weather_at_place('Москва,RU')
            weather = obs.weather
            res = f'Температура: {num2words(round(weather.temperature('celsius')['temp']), lang='ru')} градусов. Влажность: {num2words(round(weather.humidity), lang='ru')}%'
            self.speak(f"Сейчас {res}")

        elif qr.get_intent(command) == 'farewell':
            self.speak("До свидания! Я заснул.")
            self.is_listening = False

        elif qr.get_intent(command) == 'open_program':
            self.speak(self.ps.search_s(args))

        elif qr.get_intent(command) == 'wikipedia_search':
            self.speak(self.wiki.search(args)['content'])

        else:
            self.speak("Пока не понимаю эту команду.")

    def listening_loop(self):
        print("Цикл прослушивания запущен")
        # self.speak("Ассистент запущен. Говорите команды")

        while True:
            if self.is_listening:
                command = self.listen()
                if command and command.strip():
                    self.process_command(command)
                time.sleep(0.5)
            else:
                command = self.listen()
                index = command.find('барсик')
                if index != -1:
                    command = command[index:]
                    if command.lower() == 'барсик проснись':
                        self.is_listening = True
                        self.speak('Я проснулся')

    def start_listening(self):
        if self.is_listening:
            print("Уже слушаем...")
            return

        self.is_listening = True
        self.listening_loop()
        print("Прослушивание запущено")


if __name__ == "__main__":
    v = Voice()

    try:
        v.start_listening()
        print("Ассистент активен. Нажмите Ctrl+C для остановки.")

        while v.is_listening:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nОстановка пользователем")
    finally:
        v.stop()
        print("Ассистент завершил работу")

import json
import time
from datetime import datetime
import pymorphy3
from num2words import num2words
from dotenv import load_dotenv

from parsers.parser_weather import parser_weather
from user_data.change_city import change_city

from utils.Threads import SpeakThread
from utils.vosk_recognition import vosk_rec
from utils.models import model_sentence_transformers
from utils.siler_audio import Silero
from utils.Query_recognition import Query

from commands.open_program import ProgramSearcher
from commands.wikipedia_api import Wiki
from commands.schedule_by_day import schedule_subject
from commands.weather import get_weather
from colorama import init, Fore, Back, Style

init()

try:
    audio_silero = Silero()
    qr = Query()

    load_dotenv()
except:
    pass


class Voice:
    def __init__(self):
        self.model_transformers = model_sentence_transformers
        self.is_listening = False
        self.ps = ProgramSearcher()
        self.wiki = Wiki()
        self.q = SpeakThread()
        self.q.start()
        self.morph = pymorphy3.MorphAnalyzer()
        with open('config.json', 'r', encoding='utf-8') as f:
            self.intents_keys = json.load(f)['intents'].keys()

        # self.calibrate_microphone()

    def speak(self, text):
        print(Fore.GREEN + Style.DIM + f"[speak] {text}" + Style.RESET_ALL)
        self.q.add(audio_silero.silero_tts_basic, text)

    def stop(self):
        print("[stop] Остановка...")
        self.is_listening = False

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

        print(Fore.YELLOW + Style.DIM + f"Команда: {command}" + Style.RESET_ALL)

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
            parser_weather()
            self.speak(get_weather(command, self.model_transformers))

        elif qr.get_intent(command) == 'farewell':
            self.speak("До свидания! Я заснул.")
            self.is_listening = False

        elif qr.get_intent(command) == 'open_program':
            print(args)
            self.speak(self.ps.search_s(args))

        elif qr.get_intent(command) == 'wikipedia_search':
            self.speak(self.wiki.search(args)['content'])

        elif qr.get_intent(command) == 'change_city':
            city = change_city(command)
            print(command)
            print(city)
            self.speak(f'Город изменён на {city}')

        else:
            self.speak("Пока не понимаю эту команду.")

    def listening_loop(self):
        print("Цикл прослушивания запущен")
        # self.speak("Ассистент запущен.")

        while True:
            try:
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
            except Exception as e:
                print(print(Fore.RED + str(e) + Style.RESET_ALL))
                continue

    def start_listening(self):
        if self.is_listening:
            print("Уже слушаем...")
            return

        self.is_listening = True
        self.listening_loop()
        print("Прослушивание запущено")


if __name__ == "__main__":

    v = Voice()
    v.start_listening()
    print("Ассистент активен. Нажмите Ctrl+C для остановки.")

    while v.is_listening:
        time.sleep(1)

    v.stop()
    print("Ассистент завершил работу")

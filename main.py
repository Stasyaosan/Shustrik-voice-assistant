import time

import speech_recognition as sr
import threading
import pyttsx3


class Voice:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        self.engine = pyttsx3.init()
        self.is_listening = False

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        with self.microphone as s:
            audio = self.recognizer.listen(s, timeout=5, phrase_time_limit=10)
        try:
            text = self.recognizer.recognize_google(audio, language='ru-RU')
        except:
            text = ''
        return text.lower()

    def process_command(self, command):

        if not command:
            return

        if 'привет' in command:
            self.speak('Привет! Сем могу помочь')
        elif 'пока' in command:
            self.speak('До свидания')
            self.is_listening = False
        elif 'время' in command:
            print('Времяяя')
            from datetime import datetime
            now = datetime.now().strftime('%H:%M')
            self.speak(f'Сейчас: {now}')
        else:
            self.speak('Я пока не умею обрабатывать эту команду')

    def listening_loop(self):
        print(111)
        while self.is_listening:
            command = self.listen()
            print(command)
            self.process_command(command)
            time.sleep(0.1)

    def start_listening(self):
        self.is_listening = True
        self.speak('Ассистент запущен. Слушаю команды')

        if self.is_listening:
            self.listening_thread = threading.Thread(target=self.listening_loop)
            self.listening_thread.daemon = True
            self.listening_thread.start()


v = Voice()
v.start_listening()

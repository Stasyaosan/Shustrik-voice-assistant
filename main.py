import time
import speech_recognition as sr
import threading
import multiprocessing
from datetime import datetime
from siler_audio import Silero
from num2words import num2words

audio_silero = Silero()


def tts_process_main(q: multiprocessing.Queue):
    while True:
        text = q.get()
        if text is None:
            break

        try:
            audio_silero.silero_tts_basic(text)
            # speaker.Speak(text)

        except Exception as e:
            print(f"[TTS-process] Ошибка синтеза: {e}")


class Voice:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False

        self.tts_queue = multiprocessing.Queue()
        self.tts_process = multiprocessing.Process(target=tts_process_main, args=(self.tts_queue,))
        self.tts_process.start()

        self.listening_thread = None

        self.calibrate_microphone()

    def speak(self, text):
        print(f"[speak] {text}")
        self.tts_queue.put(text)

    def stop(self):
        print("[stop] Остановка...")
        self.is_listening = False
        self.tts_queue.put(None)
        if self.tts_process.is_alive():
            self.tts_process.join(timeout=3)
        print("[stop] TTS остановлен")

    def calibrate_microphone(self):
        print("Калибровка микрофона...")
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            print("Калибровка завершена!")
            return True
        except Exception as e:
            print(f"Ошибка калибровки микрофона: {e}")
            return False

    def listen(self):
        try:
            with self.microphone as source:
                print("Слушаю...")
                # Увеличиваем timeout и phrase_time_limit для лучшего распознавания
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=8)

            print("Распознаю речь...")
            text = self.recognizer.recognize_google(audio, language='ru-RU')
            print(f"Распознано: {text}")
            return text.lower()

        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            print("Речь не распознана")
            return ""
        except Exception as e:
            print(f"Ошибка слушания: {e}")
            return ""

    def process_command(self, command):
        if not command:
            return

        print(f"Команда: {command}")

        command_lower = command.lower()

        if "привет" in command_lower:
            self.speak("Привет! Рад вас слышать!")
        elif "время" in command_lower:

            h = datetime.now().strftime("%H")
            m = datetime.now().strftime("%M")
            a_h = num2words(h, lang='ru')
            a_m = num2words(m, lang='ru')
            self.speak(f"Сейчас {a_h} {a_m}")
        elif "как дела" in command_lower:
            self.speak("Всё отлично! Готов!")
        elif "пока" in command_lower or "стоп" in command_lower or "остановись" in command_lower:
            self.speak("До свидания! Выключаюсь.")
            self.is_listening = False
        else:
            self.speak("Пока не понимаю эту команду. Попробуйте сказать 'привет', 'время' или 'пока'")

    def listening_loop(self):
        print("Цикл прослушивания запущен")
        self.speak("Ассистент запущен. Говорите команды")

        while self.is_listening:
            command = self.listen()
            if command and command.strip():
                self.process_command(command)
            time.sleep(0.5)

    def start_listening(self):
        if self.is_listening:
            print("Уже слушаем...")
            return

        self.is_listening = True
        self.listening_thread = threading.Thread(target=self.listening_loop)
        self.listening_thread.daemon = True
        self.listening_thread.start()
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

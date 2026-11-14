import pyaudio
import json
from urls.config import URLS
import os



def _vosk_rec():
    vosk_model_path = URLS['vosk_model']
    from vosk import Model, KaldiRecognizer

    model = Model(str(vosk_model_path))

    recognizer = KaldiRecognizer(model, 16000)

    # Настройка микрофона
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=8000)

    stream.start_stream()

    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)

            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                return result.get("text")

    except KeyboardInterrupt:
        print("\nОстановлено")
        raise SystemExit

def _online_rec(language: str = "ru-RU"):
    import speech_recognition as sr

    r = sr.Recognizer()
    r.pause_threshold = 1.3
    with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = r.listen(source, timeout=5.0, phrase_time_limit=20.0)
            except sr.WaitTimeoutError:
                return None

    try:
        h = r.recognize_google(audio, language=language)
        return h
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"[online] Google API error: {e}")
        return None

def vosk_rec():
    if os.getenv('ONLINE_MODELS') == 'true':
        return _online_rec()
    return _vosk_rec()

import torch
import sounddevice as sd


class Silero:
    def __init__(self):
        self.device = torch.device('cpu')
        self.model, example_text = torch.hub.load(
            repo_or_dir='snakers4/silero-models',
            model='silero_tts',
            language='ru',
            speaker='v3_1_ru'
        )

    def silero_tts_basic(self, text, speaker='aidar'):
        self.model.to(self.device)

        # Генерация речи
        self.sample_rate = 48000
        audio = self.model.apply_tts(
            text=text,
            speaker=speaker,
            sample_rate=self.sample_rate,
            put_accent=True,
            put_yo=True
        )

        sd.play(audio, self.sample_rate)
        sd.wait()

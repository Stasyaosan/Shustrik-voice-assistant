import torch
import sounddevice as sd
from urls.config import URLS
from dotenv import load_dotenv
from os import getenv

load_dotenv()


class Silero:
    def __init__(self):
        self.device = torch.device('cpu')
        language = 'ru'
        model_id = 'v3_1_ru'
        if getenv('ONLINE_MODELS') == 'true':
            self.model, example_text = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                                 model='silero_tts',
                                                 language=language,
                                                 speaker=model_id)
        else:
            model_path = URLS['silero_model']
            self.model = torch.package.PackageImporter(model_path).load_pickle("tts_models", "model")

    def silero_tts_basic(self, text, speaker='aidar'):
        self.model.to(self.device)

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

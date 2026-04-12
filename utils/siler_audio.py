import torch
import sounddevice as sd
from urls.config import URLS


class Silero:
    def __init__(self):
        self.device = torch.device('cpu')
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

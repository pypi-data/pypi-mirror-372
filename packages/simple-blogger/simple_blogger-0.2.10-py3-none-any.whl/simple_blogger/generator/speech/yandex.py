from speechkit import configure_credentials, creds
from speechkit import model_repository
from simple_blogger.generator.speech import SpeechGenerator, File
import os
from io import BytesIO

configure_credentials(
    yandex_credentials=creds.YandexCredentials(
        api_key=os.environ.get('YC_API_KEY')
    )
)

class YandexSpeechGenerator(SpeechGenerator):
    def __init__(self, voice='masha', role='good', speed= 1.2):
        self.voice=voice
        self.role=role
        self.speed=speed

    def generate(self, text_to_speak):
        model = model_repository.synthesis_model()
        model.voice = self.voice
        model.role = self.role
        model.speed = self.speed
        model.unsafe_mode = True   
        result = model.synthesize(text_to_speak, raw_format=False)
        stream=BytesIO()
        result.export(stream, format=self.ext())
        return File(self.ext(), stream)
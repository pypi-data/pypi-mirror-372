from simple_blogger.generator import File, IGeneratorBase
from pydub import AudioSegment
from abc import abstractmethod
from io import BytesIO

class ISpeechGeneratorBase(IGeneratorBase):    
    @abstractmethod
    def generate(self, text_to_speak)->File:
        """Generation method"""

class SpeechGenerator(ISpeechGeneratorBase):
    def __init__(self):
        pass

    def generate(self, _):       
        stream = BytesIO()
        AudioSegment.empty().export(stream)
        return File(self.ext(), stream)
    
    def ext(self):
        return 'mp3'
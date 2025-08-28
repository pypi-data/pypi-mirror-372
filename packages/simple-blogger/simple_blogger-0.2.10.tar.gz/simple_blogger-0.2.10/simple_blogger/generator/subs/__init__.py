from simple_blogger.generator import File, IGeneratorBase
from abc import abstractmethod
from io import StringIO
import srt
from datetime import timedelta

class ISubsGeneratorBase(IGeneratorBase):    
    @abstractmethod
    def generate(self, text_to_sub)->File:
        """Generation method"""

class SubsGenerator(ISubsGeneratorBase):
    def __init__(self, duration_constructor=lambda:10):
        self.duration_constructor = duration_constructor
        pass

    def generate(self, text_to_sub):  
        subs = []
        delta = 3
        speed = len(text_to_sub) / (duration - delta + 1 if (duration:=self.duration_constructor()) > delta else 1)
        text = ' '
        tik = 0
        index = 0
        for word in text_to_sub.split():
            if len(text) + len(word) > speed * delta:
                subs.append(srt.Subtitle(index=index,start=timedelta(seconds=tik), end=timedelta(seconds=tik+delta),content=text))
                text = word
                tik += delta
                index += 1
            else:
                text += f" {word}"
        if text != '':
            subs.append(srt.Subtitle(index=index,start=timedelta(seconds=tik), end=timedelta(seconds=duration)-timedelta(milliseconds=100) ,content=text))
        stream = StringIO(srt.compose(subtitles=subs, reindex=False))
        return File(self.ext(), stream)
    
    def ext(self):
        return 'srt'
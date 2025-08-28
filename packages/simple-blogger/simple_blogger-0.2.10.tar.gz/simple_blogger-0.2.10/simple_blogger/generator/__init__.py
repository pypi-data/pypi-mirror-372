from dataclasses import dataclass
from abc import ABC, abstractmethod
from io import IOBase
from PIL import Image
from io import BytesIO, StringIO

@dataclass
class File:
    ext: str
    file: IOBase

    def get_file(self):
        self.file.seek(0)
        return self.file
    
    ext2ct = {
        'jpg': 'image/jpeg',
        'png': 'image/png',
        'txt': 'text/plain',
        'mp4': 'video/mp4'
    }

    def get_content_type(self)->str:
        if self.ext in File.ext2ct:
            return File.ext2ct[self.ext]
        return 'application/octet-stream'
    
class IGeneratorBase(ABC):    
    @abstractmethod
    def generate(self, prompt)->File:
        """Generation method"""

    @abstractmethod
    def ext()->str:
        """Content file extension"""
    
class TextGenerator(IGeneratorBase):
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt

    def generate(self, prompt, **_):
        return File(self.ext(), StringIO(prompt))
    
    def ext(self):
        return 'txt'

class ImageGenerator(IGeneratorBase):
    def __init__(self):
        pass

    def generate(self, *_, **__):
        stream = BytesIO()
        Image.new(mode='RGBA', size=(320, 240), color=1).save(stream, format=self.ext())
        return File(self.ext(), stream)
    
    def ext(self):
        return 'png'
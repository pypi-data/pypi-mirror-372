from simple_blogger.builder.content import IContentBuilder
from moviepy.audio.io.AudioFileClip import AudioFileClip 
import tempfile, uuid, os

class DurationBuilder():
    def __init__(self, content_builder:IContentBuilder):
        self.content_builder=content_builder
    
    def build(self)->float:
        audio_filename = f"{tempfile.gettempdir()}/{str(uuid.uuid4())}.{self.content_builder.ext()}"
        open(audio_filename, 'wb').write(self.content_builder.build().get_file().read())
        audio = AudioFileClip(audio_filename)
        return audio.duration
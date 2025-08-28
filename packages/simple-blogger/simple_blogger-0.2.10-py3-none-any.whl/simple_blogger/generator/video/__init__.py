from simple_blogger.generator import IGeneratorBase, File, ImageGenerator
import tempfile, uuid
from moviepy import ImageClip

class VideoGenerator(IGeneratorBase):
    def __init__(self):
        pass

    def generate(self, _=None):       
        image = ImageGenerator().generate()
        clip = ImageClip(image.get_file(), duration=3)
        temp_file = f"{tempfile.gettempdir()}/{str(uuid.uuid4())}.{self.ext()}"
        clip.write_videofile(temp_file, fps=self.fps())
        return File(self.ext(), open(temp_file,'rb'))
    
    def fps(self):
        return 24
    
    def ext(self):
        return 'mp4'
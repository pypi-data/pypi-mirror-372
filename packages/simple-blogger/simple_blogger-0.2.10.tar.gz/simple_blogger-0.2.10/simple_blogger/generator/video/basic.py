from simple_blogger.generator import File
from simple_blogger.generator.video import VideoGenerator
from simple_blogger.generator import ImageGenerator
from moviepy import ImageSequenceClip
import tempfile, uuid, io

class ImageSequenceGenerator(VideoGenerator):
    def __init__(self, image_generator:ImageGenerator, duration_constructor=lambda:10, image_count=5):
        self.image_generator=image_generator
        self.duration_constructor=duration_constructor
        self.image_count=image_count

    def _savefile(self, file:File)->str:
        temp_file_name = f"{tempfile.gettempdir()}/{str(uuid.uuid4())}.{file.ext}"
        open(temp_file_name, 'wb').write(file.get_file().read())
        return temp_file_name

    def generate(self, prompt=None):
        images = [self.image_generator.generate(prompt) for _ in range(self.image_count)]
        duration = self.duration_constructor()
        image_duration = duration / self.image_count
        clip = ImageSequenceClip(
            sequence=[self._savefile(image) for image in images],
            durations=[image_duration]*self.image_count)
        temp_file_name = f"{tempfile.gettempdir()}/{str(uuid.uuid4())}.{self.ext()}"
        clip.write_videofile(temp_file_name, fps=self.fps())
        return File(self.ext(), io.BytesIO(open(temp_file_name,'rb').read()))
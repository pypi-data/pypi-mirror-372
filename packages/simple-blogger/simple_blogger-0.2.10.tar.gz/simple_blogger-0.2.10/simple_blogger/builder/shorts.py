from moviepy.audio.io.AudioFileClip import AudioFileClip 
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy import CompositeVideoClip
import tempfile, uuid, os
from io import BytesIO
from simple_blogger.generator import File
from simple_blogger.builder.content import IContentBuilder
import simple_blogger.resources

class ShortsBuilder(IContentBuilder):
    def __init__(self, 
                 audio_builder:IContentBuilder,
                 subs_builder:IContentBuilder,
                 video_builder:IContentBuilder,
                 font=None
                 ):
        self.audio_builder=audio_builder
        self.subs_builder=subs_builder
        self.video_builder=video_builder
        self.font=font or os.path.join(*simple_blogger.resources.__path__, 'Mulish', 'static', 'Mulish-Bold.ttf')

    def ext(self):
        return self.video_builder.ext()

    def build(self):
        audio_filename = f"{tempfile.gettempdir()}/{str(uuid.uuid4())}.{self.audio_builder.ext()}"
        open(audio_filename, 'wb').write(self.audio_builder.build().get_file().read())
        audio = AudioFileClip(audio_filename)
        
        subs_filename = f"{tempfile.gettempdir()}/{str(uuid.uuid4())}.{self.subs_builder.ext()}"
        open(subs_filename, 'wt', encoding='UTF-8').write(self.subs_builder.build().get_file().read())
        subs = SubtitlesClip(subtitles=subs_filename, font=self.font, encoding='UTF-8')
        
        video_filename = f"{tempfile.gettempdir()}/{str(uuid.uuid4())}.{self.video_builder.ext()}"
        open(video_filename, 'wb').write(self.video_builder.build().get_file().read())
        video = VideoFileClip(video_filename)
        
        media_filename = f"{tempfile.gettempdir()}/{str(uuid.uuid4())}.{self.video_builder.ext()}"
        media = CompositeVideoClip([video, subs.with_position(("center", 0.9), relative=True)]).with_audio(audio)
        media.write_videofile(media_filename)

        return File(self.video_builder.ext(), BytesIO(open(media_filename, 'rb').read()))
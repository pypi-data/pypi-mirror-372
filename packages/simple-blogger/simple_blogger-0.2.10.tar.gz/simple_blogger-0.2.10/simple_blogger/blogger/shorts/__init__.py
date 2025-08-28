from simple_blogger.builder import PostBuilder
from simple_blogger.blogger.basic import CommonBlogger
from simple_blogger.generator.video.basic import ImageSequenceGenerator
from simple_blogger.builder.shorts import ShortsBuilder
from simple_blogger.generator.subs import SubsGenerator
from simple_blogger.generator.speech.yandex import YandexSpeechGenerator
from simple_blogger.builder.task import TaskExtractor
from simple_blogger.cache.file_system import FileCache
from simple_blogger.builder.prompt import TaskPromptBuilder, ContentBuilderPromptBuilder
from simple_blogger.builder.content import CachedContentBuilder, ContentBuilder
from simple_blogger.builder.tools import DurationBuilder
from simple_blogger.preprocessor.text import MarkdownCleaner, SerialProcessor, EmojiCleaner
import tempfile, uuid

class ShortsBlogger(CommonBlogger):
    def __init__(self, posters, image_count=5, index=None):
        self.image_count=image_count
        super().__init__(posters=posters, index=index)
        
    def _speech_generator(self):
        return YandexSpeechGenerator()
    
    def __path_constructor(self):
        return '.'

    def _builder(self):
        tasks = self._load_tasks()
        task_extractor = TaskExtractor(tasks=tasks, check=self._check_task)
        root_folder = tempfile.gettempdir()
        file_suffix = str(uuid.uuid4())
        message_builder = CachedContentBuilder(
                            task_builder=task_extractor,
                            path_constructor=self.__path_constructor,
                            builder=ContentBuilder(
                                generator=self._message_generator(), 
                                prompt_builder=TaskPromptBuilder(
                                        task_builder=task_extractor,
                                        prompt_constructor=self._message_prompt_constructor
                                    )
                            ),
                            force_rebuild=False,
                            cache=FileCache(root_folder, is_binary=False),
                            filename=f"text_{file_suffix}"
                        )
        audio_builder=CachedContentBuilder(
                            task_builder=task_extractor,
                            path_constructor=self.__path_constructor,
                            builder=ContentBuilder(
                                generator=self._speech_generator(), 
                                prompt_builder=ContentBuilderPromptBuilder(content_builder=message_builder),
                                prompt_processor=SerialProcessor([MarkdownCleaner(), EmojiCleaner()])
                            ),
                            force_rebuild=False,
                            filename=f"audio_{file_suffix}",
                            cache=FileCache(root_folder)
                        )
        duration_builder=DurationBuilder(audio_builder)
        subs_builder=CachedContentBuilder(
                        task_builder=task_extractor,
                        path_constructor=self.__path_constructor,
                        builder=ContentBuilder(
                            generator=SubsGenerator(duration_constructor=duration_builder.build), 
                            prompt_builder=ContentBuilderPromptBuilder(content_builder=message_builder),
                            prompt_processor=SerialProcessor([MarkdownCleaner(), EmojiCleaner()])
                        ),
                        force_rebuild=False,
                        filename=f"subs_{file_suffix}",
                        cache=FileCache(root_folder, is_binary=False)                            
                    )        
        image_prompt_builder=ContentBuilderPromptBuilder(
                                content_builder=CachedContentBuilder(
                                    task_builder=task_extractor,
                                    path_constructor=self.__path_constructor,
                                    builder=ContentBuilder(
                                        generator=self._image_prompt_generator(), 
                                        prompt_builder=TaskPromptBuilder(
                                            task_builder=task_extractor,
                                            prompt_constructor=self._image_prompt_prompt_constructor
                                        )),
                                    force_rebuild=False,
                                    filename=f"image_prompt_{file_suffix}",
                                    cache=FileCache(root_folder, is_binary=False)
                                )
                            )
        video_builder = CachedContentBuilder(
                            task_builder=task_extractor,
                            path_constructor=False,
                            builder=ContentBuilder(
                                generator=ImageSequenceGenerator(self._image_generator(), duration_builder.build, self.image_count),
                                prompt_builder=image_prompt_builder,
                            ),
                            force_rebuild=False,
                            cache=FileCache(root_folder),
                            filename=f"video_{file_suffix}"
                        )
        media_builder = CachedContentBuilder(
                            task_builder=task_extractor,
                            path_constructor=self.__path_constructor,
                            builder=ShortsBuilder(audio_builder, subs_builder, video_builder),
                            force_rebuild=False,
                            cache=FileCache(root_folder),
                            filename=f"media_{file_suffix}"
                        )

        builder = PostBuilder(
            message_builder=message_builder,
            media_builder=media_builder
        )
        return builder
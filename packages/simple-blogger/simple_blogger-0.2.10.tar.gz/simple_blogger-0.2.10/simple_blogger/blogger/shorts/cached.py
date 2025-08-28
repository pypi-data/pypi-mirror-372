from simple_blogger.builder import PostBuilder
from simple_blogger.blogger import CachedBlogger
from simple_blogger.blogger.shorts import ShortsBlogger
from simple_blogger.generator.video.basic import ImageSequenceGenerator
from simple_blogger.builder.shorts import ShortsBuilder
from simple_blogger.generator.subs import SubsGenerator
from simple_blogger.builder.task import TaskExtractor
from simple_blogger.cache.file_system import FileCache
from simple_blogger.builder.prompt import TaskPromptBuilder, ContentBuilderPromptBuilder
from simple_blogger.builder.content import CachedContentBuilder, ContentBuilder
from simple_blogger.builder.tools import DurationBuilder
from simple_blogger.preprocessor.text import MarkdownCleaner, SerialProcessor, EmojiCleaner
import json

class CachedShortsBlogger(ShortsBlogger, CachedBlogger):
    def __init__(self, posters, image_count=5, force_rebuild=False, index=None):
        ShortsBlogger.__init__(self, posters, image_count, index)
        CachedBlogger.__init__(self, force_rebuild)
        
    def _builder(self):
        tasks = json.load(open(self._tasks_file_path(), "rt", encoding="UTF-8"))
        task_extractor = TaskExtractor(tasks=tasks, check=self._check_task)
        message_builder = CachedContentBuilder(
                            task_builder=task_extractor,
                            path_constructor=self._path_constructor,
                            builder=ContentBuilder(
                                generator=self._message_generator(), 
                                prompt_builder=TaskPromptBuilder(
                                        task_builder=task_extractor,
                                        prompt_constructor=self._message_prompt_constructor
                                    )
                            ),
                            force_rebuild=self.force_rebuild,
                            cache=FileCache(root_folder=self._data_folder(), is_binary=False),
                            filename="text"
                        )
        audio_builder=CachedContentBuilder(
                            task_builder=task_extractor,
                            path_constructor=self._path_constructor,
                            builder=ContentBuilder(
                                generator=self._speech_generator(), 
                                prompt_builder=ContentBuilderPromptBuilder(content_builder=message_builder),
                                prompt_processor=SerialProcessor([MarkdownCleaner(), EmojiCleaner()])
                            ),
                            force_rebuild=self.force_rebuild,
                            filename="audio",
                            cache=FileCache(root_folder=self._data_folder())
                        )
        duration_builder=DurationBuilder(audio_builder)
        subs_builder=CachedContentBuilder(
                        task_builder=task_extractor,
                        path_constructor=self._path_constructor,
                        builder=ContentBuilder(
                            generator=SubsGenerator(duration_constructor=duration_builder.build), 
                            prompt_builder=ContentBuilderPromptBuilder(content_builder=message_builder),
                            prompt_processor=SerialProcessor([MarkdownCleaner(), EmojiCleaner()])
                        ),
                        force_rebuild=self.force_rebuild,
                        filename="subs",
                        cache=FileCache(root_folder=self._data_folder(), is_binary=False)                            
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
                                    force_rebuild=self.force_rebuild,
                                    filename="image_prompt",
                                    cache=FileCache(root_folder=self._data_folder(), is_binary=False)
                                )
                            )
        video_builder = CachedContentBuilder(
                            task_builder=task_extractor,
                            path_constructor=self._path_constructor,
                            builder=ContentBuilder(
                                generator=ImageSequenceGenerator(self._image_generator(), duration_builder.build, self.image_count),
                                prompt_builder=image_prompt_builder,
                            ),
                            force_rebuild=self.force_rebuild,
                            cache=FileCache(root_folder=self._data_folder()),
                            filename="video"
                        )
        media_builder = CachedContentBuilder(
                            task_builder=task_extractor,
                            path_constructor=self._path_constructor,
                            builder=ShortsBuilder(audio_builder, subs_builder, video_builder),
                            force_rebuild=self.force_rebuild,
                            cache=FileCache(root_folder=self._data_folder()),
                            filename="media"
                        )

        builder = PostBuilder(
            message_builder=message_builder,
            media_builder=media_builder
        )
        return builder
from simple_blogger.builder import PostBuilder
from simple_blogger.blogger import CachedBlogger
from simple_blogger.blogger.basic import SimpleBlogger, CommonBlogger
from simple_blogger.builder.task import TaskExtractor
from simple_blogger.cache.file_system import FileCache
from simple_blogger.builder.prompt import TaskPromptBuilder, ContentBuilderPromptBuilder
from simple_blogger.builder.content import CachedContentBuilder, ContentBuilder
import json, os

class CachedSimpleBlogger(SimpleBlogger, CachedBlogger):
    def __init__(self, posters, force_rebuild=False, index=None):
        CachedBlogger.__init__(self, force_rebuild=force_rebuild)
        SimpleBlogger.__init__(self, posters=posters, index=index)

    def _builder(self):
        tasks = json.load(open(self._tasks_file_path(), "rt", encoding="UTF-8")) if os.path.exists(self._tasks_file_path()) else []
        task_extractor = TaskExtractor(tasks=tasks, check=self._check_task)
        message_builder=CachedContentBuilder(
            task_builder=task_extractor,
            path_constructor=self._path_constructor,
            force_rebuild=self.force_rebuild,
            builder=ContentBuilder(
                generator=self._message_generator(), 
                prompt_builder=TaskPromptBuilder(
                        task_builder=task_extractor,
                        prompt_constructor=self._message_prompt_constructor
                    )
                ),
            cache=FileCache(root_folder=self._data_folder(), is_binary=False),
            filename=f"text"
        )
        media_builder=CachedContentBuilder(
            task_builder=task_extractor,
            path_constructor=self._path_constructor,
            force_rebuild=self.force_rebuild,
            builder=ContentBuilder(
                generator=self._image_generator(),
                prompt_builder=TaskPromptBuilder(
                        task_builder=task_extractor,
                        prompt_constructor=self._image_prompt_constructor
                    )
                ),
            cache=FileCache(root_folder=self._data_folder()),
            filename=f"image"
        )
        builder = PostBuilder(
            message_builder=message_builder,
            media_builder=media_builder
        )
        return builder
    
class CachedCommonBlogger(CommonBlogger, CachedBlogger):
    def __init__(self, posters, force_rebuild=False, index=None):
        CachedBlogger.__init__(self, force_rebuild=force_rebuild)
        CommonBlogger.__init__(self, posters=posters, index=index)
        
    def _builder(self):
        tasks = json.load(open(self._tasks_file_path(), "rt", encoding="UTF-8")) if os.path.exists(self._tasks_file_path()) else []
        task_extractor = TaskExtractor(tasks=tasks, check=self._check_task)
        message_builder=CachedContentBuilder(
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
        content_builder=CachedContentBuilder(
            task_builder=task_extractor,
            path_constructor=self._path_constructor,
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
        media_builder=CachedContentBuilder(
            task_builder=task_extractor,
            path_constructor=self._path_constructor,
            builder=ContentBuilder(
                generator=self._image_generator(),
                prompt_builder=ContentBuilderPromptBuilder(
                    content_builder=content_builder
                )
            ),
            force_rebuild=self.force_rebuild,
            cache=FileCache(root_folder=self._data_folder()),
            filename="image"
        )
        builder = PostBuilder(
            message_builder=message_builder,
            media_builder=media_builder
        )
        return builder
    
    

    
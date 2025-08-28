from simple_blogger.builder import PostBuilder
from simple_blogger.blogger import ProjectBlogger
from simple_blogger.generator.yandex import YandexTextGenerator
from simple_blogger.builder.prompt import TaskPromptBuilder, ContentBuilderPromptBuilder
from simple_blogger.builder.content import ContentBuilder
    
class SimpleBlogger(ProjectBlogger):
    def _image_prompt_constructor(self, task):
        return f"Нарисуй рисунок, вдохновленный темой {task['topic']} из области '{task['category']}'"
    
    def _builder(self):
        tasks = self._load_tasks()
        task_extractor = self._task_extractor(tasks)
        message_builder=ContentBuilder(
            generator=self._message_generator(), 
            prompt_builder=TaskPromptBuilder(
                task_builder=task_extractor,
                prompt_constructor=self._message_prompt_constructor
            )
        )
        media_builder=ContentBuilder(
            generator=self._image_generator(),
            prompt_builder=TaskPromptBuilder(
                task_builder=task_extractor,
                prompt_constructor=self._image_prompt_constructor
            )
        )
        builder = PostBuilder(
            message_builder=message_builder,
            media_builder=media_builder
        )
        return builder
    
    def print_current_task(self):
        task = super().print_current_task()
        print(f"image: {self._image_prompt_constructor(task)}")
        return task 
    
class CommonBlogger(ProjectBlogger):        
    def _image_prompt_prompt_constructor(self, task):
        return f"Напиши промпт для генерации изображения на тему '{task['topic']}' из области '{task['category']}'"
    
    def _image_prompt_generator(self):
        return YandexTextGenerator(system_prompt=self._system_prompt())
    
    def print_current_task(self):
        task = super().print_current_task()
        print(f"image_prompt: {self._image_prompt_prompt_constructor(task)}")
        return task
    
    def _builder(self):
        tasks = self._load_tasks()
        task_extractor = self._task_extractor(tasks)
        message_builder=ContentBuilder(
            generator=self._message_generator(), 
            prompt_builder=TaskPromptBuilder(
                task_builder=task_extractor,
                prompt_constructor=self._message_prompt_constructor
            )
        )
        image_prompt_builder=ContentBuilder(
            generator=self._image_prompt_generator(), 
            prompt_builder=TaskPromptBuilder(
                task_builder=task_extractor,
                prompt_constructor=self._image_prompt_prompt_constructor
            )
        )
        media_builder=ContentBuilder(
            generator=self._image_generator(),
            prompt_builder=ContentBuilderPromptBuilder(
                content_builder=image_prompt_builder
            )
        )
        builder = PostBuilder(
            message_builder=message_builder,
            media_builder=media_builder
        )
        return builder
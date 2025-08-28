from simple_blogger.builder import PostBuilder
from simple_blogger.builder.content import CachedContentBuilder, ContentBuilder
from simple_blogger.builder.prompt import ContentBuilderPromptBuilder, TaskPromptBuilder
from simple_blogger.cache import Cache
from simple_blogger.poster import IPoster
from simple_blogger.generator.yandex import YandexTextGenerator, YandexImageGenerator
from simple_blogger.builder.task import IdentityTaskBuilder, TaskExtractor
from abc import abstractmethod
from datetime import date, timedelta
import json, os, random

from simple_blogger.preprocessor.text import EmojiCleaner, MarkdownCleaner, SerialProcessor

class SimplestBlogger():
    def __init__(self, builder:PostBuilder, posters:list[IPoster]):
        self.builder = builder
        self.posters = posters

    def post(self, **__):
        post = self.builder.build()
        for poster in self.posters:
            poster.post(post=post)
    
    def _system_prompt(self):
        return 'Ты - известный блоггер с 1000000 подписчиков'

    def _message_generator(self):
        return YandexTextGenerator(system_prompt=self._system_prompt())
    
    def _image_generator(self):
        return YandexImageGenerator()
    
class Journalist(SimplestBlogger):
    def _prompt_constructor(self, *_, **__):
        return "Выбери рандомную тему из рандомной области. Напиши эссе на эту тему. Используй смайлики и не более 150 слов."

    def __init__(self, posters):
        task_builder = IdentityTaskBuilder('.')
        message_builder=CachedContentBuilder(
            task_builder=task_builder,
            path_constructor=lambda _:'.',
            builder=ContentBuilder(
                generator=self._message_generator(),
                prompt_builder=TaskPromptBuilder(
                        task_builder=task_builder,
                        prompt_constructor=self._prompt_constructor
                    )
            ),
            cache=Cache(),
            filename=f"text"
        )
        image_builder=ContentBuilder(
            generator=self._image_generator(), 
            prompt_builder=ContentBuilderPromptBuilder(
                content_builder=message_builder
            ),
            prompt_processor=SerialProcessor([MarkdownCleaner(), EmojiCleaner()])
        )
        builder = PostBuilder(
            message_builder=message_builder,
            media_builder=image_builder
        )
        super().__init__(builder, posters)  
    
class ProjectBlogger(SimplestBlogger):
    def __init__(self, posters, index=None):
        self.index = index
        super().__init__(self._builder(), posters)

    def _message_prompt_constructor(self, task):
        return f"Напиши пост на тему {task['topic']} из области '{task['category']}', используй не более 100 слов, используй смайлики"
    
    def root_folder(self):
        return './files'
    
    def ideas_folder(self):
        return os.path.join(self.root_folder(), 'ideas')
    
    def projects_folder(self):
        return os.path.join(self.root_folder(), 'projects')
    
    def _tasks_file_path(self):
        return f"{self.root_folder()}/projects/in_progress{(self.index or '')}.json"
    
    def _load_tasks(self):
        return json.load(open(self._tasks_file_path(), "rt", encoding="UTF-8"))
    
    def _check_task(self, task, days_before=0, **_):
        check_date = date.today() + timedelta(days=days_before)
        return task['date'] == check_date.strftime('%Y-%m-%d')
    
    def _task_extractor(self, tasks):
        return TaskExtractor(tasks=tasks, check=self._check_task)           
    
    def print_current_task(self):
        tasks = self._load_tasks()
        task_extractor = self._task_extractor(tasks)
        task = task_extractor.build()
        print(f"system: {self._system_prompt()}")
        print(f"message: {self._message_prompt_constructor(task)}")
        return task
    
    @abstractmethod
    def _builder(self):
        """Build Post Builder"""

    def init_project(self, create_idea_example=False):
        os.makedirs(self.root_folder(), exist_ok=True)
        os.makedirs(self.ideas_folder(), exist_ok=True)
        os.makedirs(self.projects_folder(), exist_ok=True)
        if create_idea_example:
            ideas_example_file = os.path.join(self.ideas_folder(), 'idea.json')
            if not os.path.exists(ideas_example_file):
                json.dump({ 'topic': 'topic', 'category': 'category' }, open(ideas_example_file, 'wt', encoding='UTF-8'))

    def _load_project_tasks(self, multiple_projects=False):
        project_tasks=[]
        tasks=[]
        for root, _, files in os.walk(self.ideas_folder(), ):
            for i, file in enumerate(files):
                input_file = f"{root}/{file}"
                data = json.load(open(input_file, "rt", encoding="UTF-8"))
                for idea in data:
                    task = idea
                    task['index'] = i
                    tasks.append(task)
                if multiple_projects:
                    project_tasks.append(tasks)
                    tasks=[]
        if not multiple_projects:
            project_tasks.append(tasks)
        return project_tasks
    
    def _save_tasks(self, project_tasks):
        for i, tasks in enumerate(project_tasks):
            tasks_file=os.path.join(self.projects_folder(), f"in_progress{'' if i==0 else i}.json")
            json.dump(tasks, open(tasks_file, 'wt', encoding='UTF-8'), indent=4, ensure_ascii=False)

    def _shuffle(self, project_tasks):
        year = date.today().year
        for tasks in project_tasks:
            random.seed(year)
            random.shuffle(tasks)

class CachedBlogger(ProjectBlogger):
    def __init__(self, force_rebuild=False):
        self.force_rebuild = force_rebuild
    
    def _path_constructor(self, task):
        return os.path.join(task['category'], task['topic'])
    
    def _data_folder(self):
        return os.path.join(self.root_folder(), "data")
    
    def print_current_task(self):
        task = super().print_current_task()
        print(f"path: {self._path_constructor(task)}")
        return task
    
    def init_project(self, create_idea_example=False):
        super().init_project(create_idea_example)
        os.makedirs(self._data_folder(), exist_ok=True)


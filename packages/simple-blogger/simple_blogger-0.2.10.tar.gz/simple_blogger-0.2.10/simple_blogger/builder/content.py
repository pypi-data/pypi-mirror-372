from __future__ import annotations 
import simple_blogger.builder.prompt, os
from simple_blogger.generator import File
from simple_blogger.cache.file_system import FileCache
from simple_blogger.builder.task import ITaskBuilder
from simple_blogger.preprocessor.text import ITextProcessor, IdentityProcessor
from abc import ABC, abstractmethod

class IContentBuilder(ABC):    
    @abstractmethod
    def build(self)->File:
        """Content builder method"""

    @abstractmethod
    def ext(self)->str:
        """Content extension"""

class ContentBuilder(IContentBuilder):
    def __init__(self, generator, prompt_builder:simple_blogger.builder.prompt.IPromptBuilder, prompt_processor:ITextProcessor=None):
        self.generator = generator
        self.prompt_builder = prompt_builder
        self.prompt_processor=prompt_processor or IdentityProcessor()

    def build(self):
        prompt = self.prompt_processor.process(self.prompt_builder.build())
        return prompt and self.generator.generate(prompt)
    
    def ext(self):
        return self.generator.ext()

class CachedContentBuilder(IContentBuilder):
    def __init__(self, task_builder:ITaskBuilder, path_constructor, builder:IContentBuilder, force_rebuild=False, cache=None, filename='topic'):
        self.task_builder = task_builder
        self.path_constructor = path_constructor
        self.builder = builder
        self.force_rebuild = force_rebuild
        self.cache = cache or FileCache(is_binary = builder.ext() != 'txt')
        self.filename = filename

    def __build(self, task):
        uri = os.path.join(self.path_constructor(task), f"{self.filename}.{self.builder.ext()}")
        if self.force_rebuild or (cached := self.cache.load(uri=uri)) is None:
            new = self.builder.build()
            if new is not None:
                self.cache.save(uri=uri, io_base=new.file)
            return new
        return File(self.builder.ext(), cached) 

    def build(self, **__):
        task = self.task_builder.build()
        return task and self.__build(task)
    
    def ext(self):
        return self.builder.ext()
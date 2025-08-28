from abc import ABC, abstractmethod
from markdown import Markdown
import emoji

class ITextProcessor(ABC):
    @abstractmethod
    def process(self, message:str)->str:
        """ Message preprocess method """

class IdentityProcessor(ITextProcessor):        
    def process(self, message:str)->str:
        return message
    
class MarkdownCleaner():
    def __init__(self):
        self.md = Markdown(output_format="plain")
        self.md.stripTopLevelTags = False

    def process(self, message:str)->str:
        return self.md.convert(message)
    
class EmojiCleaner(ITextProcessor):        
    def process(self, message:str)->str:
        return emoji.replace_emoji(message)
    
class SerialProcessor(ITextProcessor):
    def __init__(self, processors:list[ITextProcessor]):
        self.processors = processors

    def process(self, message:str)->str:
        for processor in self.processors:
            message = processor.process(message=message)
        return message
    
class TagAdder(ITextProcessor):
    def __init__(self, tags:list[str]):
        self.tags = tags

    def process(self, message:str)->str:
        text_lower = message.lower()
        delimiter = '\n\n'
        for tag in self.tags:
            if not tag.lower() in text_lower:
                message += f"{delimiter}{tag}"
                delimiter = ' '
        return message
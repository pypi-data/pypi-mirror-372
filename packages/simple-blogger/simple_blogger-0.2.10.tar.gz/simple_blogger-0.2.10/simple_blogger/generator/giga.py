from simple_blogger.generator import File, ImageGenerator, TextGenerator
from gigachat import GigaChat
from io import StringIO, BytesIO
from bs4 import BeautifulSoup
import os, base64

class GigaChatTextGenerator(TextGenerator):
    def __init__(self, system_prompt, api_key_name ='GIGACHAT_CREDENTIALS', model_name='GigaChat-2', creativity=0.5):
        super().__init__(system_prompt=system_prompt)
        self.api_key = os.environ.get(api_key_name)
        self.model_name=model_name
        self.creativity=creativity*2

    def generate(self, prompt, **_):
        giga = GigaChat(
            credentials=self.api_key,
            verify_ssl_certs=False,
        )
        text = giga.chat({
                                "model": f"{self.model_name}",
                                "messages": [
                                    { "role": "system", "content": f"{self.system_prompt}" },
                                    { "role": "user", "content": f"{prompt}" },
                                ],
                                "temperature": self.creativity
                            }).choices[0].message.content
        return File('txt', StringIO(text))
    
class GigaChatImageGenerator(ImageGenerator):
    def __init__(self, api_key_name ='GIGACHAT_CREDENTIALS', model_name='GigaChat-2', system_prompt=None, style_prompt=None):
        super().__init__()
        self.api_key = os.environ.get(api_key_name)
        self.model_name=model_name
        self.system_prompt=system_prompt
        self.style_prompt=style_prompt

    def generate(self, prompt, **_):
        giga = GigaChat(
            credentials=self.api_key,
            verify_ssl_certs=False,
        )
        prompt = f"{prompt}{'\n' + self.style_prompt if self.style_prompt else ''}"
        response = giga.chat({
                                "model": f"{self.model_name}",
                                "messages": [
                                    { "role": "system", "content": f"{self.system_prompt}" },
                                    { "role": "user", "content": f"{prompt}" },
                                ],
                                "function_call": "auto"
                            }).choices[0].message.content
        
        file_id = BeautifulSoup(response, "html.parser").find('img').get("src")
        image = giga.get_image(file_id)

        return File(self.ext(), BytesIO(base64.b64decode(image.content)))
    
    def ext(self):
        return 'jpeg'
from simple_blogger.generator import File, TextGenerator
from openai import OpenAI
from io import StringIO
import os

class DeepSeekTextGenerator(TextGenerator):
    def __init__(self, system_prompt, api_key_name ='DEEPSEEK_API_KEY', model_name='deepseek-chat', creativity=0.5):
        super().__init__(system_prompt=system_prompt)
        self.base_url='https://api.deepseek.com'
        self.api_key = os.environ.get(api_key_name)
        self.model_name=model_name
        self.creativity=creativity*2

    def generate(self, prompt, **_):
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        text = client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        { "role": "system", "content": self.system_prompt },
                        { "role": "user", "content": prompt },
                    ],
                    temperature=self.creativity
                ).choices[0].message.content
        return File('txt', StringIO(text))
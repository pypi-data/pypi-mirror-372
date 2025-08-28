from simple_blogger.generator import File, TextGenerator, ImageGenerator
from io import StringIO, BytesIO
from yandex_cloud_ml_sdk import YCloudML
import os

class YandexTextGenerator(TextGenerator):
    def __init__(self, system_prompt, folder_id=None, model_name='yandexgpt', model_version='latest', creativity=0.5):
        super().__init__(system_prompt=system_prompt)
        self.folder_id=folder_id or os.environ.get('YC_FOLDER_ID')
        self.model_name=model_name
        self.model_version=model_version
        self.creativity=creativity

    def generate(self, prompt, **_):
        sdk = YCloudML(folder_id=self.folder_id)
        model = sdk.models.completions(model_name=self.model_name, model_version=self.model_version)
        model.configure(temperature=self.creativity)
        text = model.run([
                        { "role": "system", "text": self.system_prompt },
                        { "role": "user", "text": prompt },
                    ]
                ).alternatives[0].text
        return File(self.ext(), StringIO(text))
    
class YandexImageGenerator(ImageGenerator):
    def __init__(self, folder_id=None, model_name='yandex-art', model_version='latest', system_prompt=None, style_prompt=None):
        super().__init__()
        self.folder_id=folder_id or os.environ.get('YC_FOLDER_ID')
        self.model_name=model_name
        self.model_version=model_version
        self.system_prompt=system_prompt
        self.style_prompt=style_prompt

    def generate(self, prompt, **_):
        sdk = YCloudML(folder_id=self.folder_id)
        model = sdk.models.image_generation(self.model_name)
        prompt = f"{self.system_prompt + '\n' if self.system_prompt else ''}{prompt}{'\n' + self.style_prompt if self.style_prompt else ''}"
        operation = model.run_deferred(prompt)
        result = operation.wait()
        return File(self.ext(), BytesIO(result.image_bytes))
    
    def ext(self):
        return 'jpeg'
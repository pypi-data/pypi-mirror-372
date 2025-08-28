from setuptools import setup, find_packages

setup(
  name='simple_blogger',
  version='0.2.10',
  author='Aleksey Sergeyev',
  author_email='aleksey.sergeyev@yandex.com',
  description='A simple blogger library',
  long_description=open('README.md', 'rt').read(),
  long_description_content_type='text/markdown',
  url='https://github.com/athenova/simple_blogger',
  packages=find_packages(),
  install_requires=['pillow>=10.4.0', 
                    'openai>=1.76.0', 
                    'pyTelegramBotAPI>=4.26.0', 
                    'requests>=2.32.3', 
                    'yandex-cloud-ml-sdk>=0.4.1', 
                    "emoji>=2.14.1",
                    'markdown>=3.7', 
                    "vk>=3.0",
                    "gigachat>=0.1.42",
                    "beautifulsoup4>=4.13.4",
                    # 'boto3==1.35.99', 
                    # "yandex-speechkit>=1.5.0",
                    # "moviepy>=2.1.2"
                    ],
  classifiers=[
    'Programming Language :: Python :: 3.10',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='python blog ai',
  project_urls={
    'Documentation': 'https://github.com/athenova/simple_blogger'
  },
  python_requires='>=3.10.6'
)
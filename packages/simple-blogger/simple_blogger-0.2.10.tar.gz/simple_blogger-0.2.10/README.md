# **Python Simple Blogger library (simple_blogger)** #

This is simple library to make simple blog project with Python. 
The library is distributed under the MIT license and can be downloaded and used by anyone.

----------

## How to install ##

To install, you can use the command:

    pip3 install simple_blogger

Or download the repository from [GitHub](https://github.com/athenova/simple_blogger)

----------

## Simplest Blogger ##

Use simplest blogger to generate and post simple messages

### Wisher example ###

Uses Deepseek engine to generate a wish text and sends it to Telegram channel. 
Adds tag `#haveaniceday` to all posts. 

```python
blogger = SimplestBlogger(
    builder = PostBuilder(
            message_builder=ContentBuilder(
                generator=DeepSeekTextGenerator(system_prompt='You are the most optimistic human in the world'),
                prompt_builder=IdentityPromptBuilder(f"Wish a nice day to the World, use emojies")
            )
        ),
    posters = [
            TelegramPoster(processor=TagAdder(['#haveaniceday']))
        ]
)
blogger.post()
```

### A slightly more complicated horoscope example ###

Sends pisces hororoscope for tomorrow to Telegram Channel and VK group.

```python
class HoroscopeBlogger(SimplestBlogger):
    def __init__(self, sign):
        tomorrow = datetime.today() + timedelta(days=1)
        builder = PostBuilder(
            message_builder=ContentBuilder(
                generator=DeepSeekTextGenerator(system_prompt='You are a professional astrologist'),
                prompt_builder=IdentityPromptBuilder(f"Make a a horoscope on {tomorrow.strftime('%Y-%m-%d')} for '{sign}', use emojies, use less than 300 words")
            )
        )
        processor = TagAdder(['#horoscope', '#astrology', f"#{sign}"])
        posters = [
            TelegramPoster(processor=processor),
            VkPoster(processor=processor)
        ]
        super().__init__(builder, posters)

pisces_blogger = HoroscopeBlogger(sign='pisces')
pisces_blogger.post()
```

### Environment variables ###

Library uses `dall-e-3` model to generate images and `deepseek-chat` to generate texts by default and sends publications to telegram channels.
It needs following environment variables:
- BLOGGER_BOT_TOKEN
- OPENAI_API_KEY
- DEEPSEEK_API_KEY

Yandex generators needs following environment variables:
- YC_API_KEY
- YC_FOLDER_ID


## From the developer ##

> There are(or will be) more examples of using this library in sibling repos on [GitHub](https://github.com/athenova/simple_blogger)
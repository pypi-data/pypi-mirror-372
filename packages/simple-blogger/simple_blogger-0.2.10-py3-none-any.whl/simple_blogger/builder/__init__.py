from simple_blogger.poster import Post

class PostBuilder():
    def __init__(self, message_builder=None, media_builder=None):
        self.message_builder = message_builder
        self.media_builder = media_builder

    def build(self):
        return Post(
            self.message_builder and self.message_builder.build(),
            self.media_builder and self.media_builder.build()
        )
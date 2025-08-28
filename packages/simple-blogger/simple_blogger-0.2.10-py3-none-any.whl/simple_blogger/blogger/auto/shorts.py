from simple_blogger.blogger.shorts import ShortsBlogger
from simple_blogger.blogger.shorts.cached import CachedShortsBlogger
from simple_blogger.blogger.auto import AutoBlogger

class AutoCommonShortsBlogger(ShortsBlogger, AutoBlogger):
    def __init__(self, posters, first_post_date=None, image_count=5, index=None):
        ShortsBlogger.__init__(self, posters, image_count, index)
        AutoBlogger.__init__(self,first_post_date)

class CachedAutoCommonShortsBlogger(CachedShortsBlogger, AutoBlogger):
    def __init__(self, posters, first_post_date=None, image_count=5, force_rebuild=False, index=None):
        CachedShortsBlogger.__init__(self, posters, image_count, force_rebuild, index)
        AutoBlogger.__init__(self,first_post_date)
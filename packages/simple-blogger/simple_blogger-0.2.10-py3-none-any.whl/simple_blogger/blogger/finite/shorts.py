from simple_blogger.blogger.shorts import ShortsBlogger
from simple_blogger.blogger.shorts.cached import CachedShortsBlogger
from simple_blogger.blogger.finite import FiniteBlogger

class FiniteCommonShortsBlogger(ShortsBlogger, FiniteBlogger):
    def __init__(self, posters, image_count=5, index=None):
        ShortsBlogger.__init__(self, posters, image_count, index)

class CacheFiniteShortBlogger(CachedShortsBlogger, FiniteBlogger):
    def __init__(self, posters, image_count=5, force_rebuild=False, index=None):
        CachedShortsBlogger.__init__(self, posters, image_count, force_rebuild, index)
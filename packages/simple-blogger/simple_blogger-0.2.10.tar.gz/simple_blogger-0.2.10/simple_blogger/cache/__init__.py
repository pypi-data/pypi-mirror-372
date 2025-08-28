class Cache():
    def __init__(self):
        self.cache = None

    def load(self, **_):
        return self.cache
        
    def save(self, io_base, **_):
        self.cache = io_base
import os

class FileCache():
    def __init__(self, root_folder='.', is_binary=True):
        self.root_folder = root_folder
        self.is_binary = is_binary

    def load(self, uri):
        path = f"{self.root_folder}/{uri}"
        if os.path.exists(path = path):
            return open(file = path, 
                        mode = 'rb' if self.is_binary else 'rt',
                        encoding = None if self.is_binary else 'UTF-8') 
        else: 
            return None
        
    def save(self, uri, io_base):
        path = f"{self.root_folder}/{uri}"
        folder = os.path.dirname(path)
        os.makedirs(folder, exist_ok=True)
        open(file = path, 
             mode = 'wb' if self.is_binary else 'wt',
             encoding = None if self.is_binary else 'UTF-8').write(io_base.getvalue())
import pdb
import os
import json


class File():
    def __init__(self, parent, name, extension):
        self.parent = parent
        self.name = name
        self.extension = extension
        self.target = self.__get_path()

    def __repr__(self):
        return f'{os.path.join(self.parent, self.ne)}'

    def __get_path(self):
        with open('file_extensions.json') as data:
            exts = json.load(data)
            for e in exts:
                if self.extension in exts[e]:
                    return os.path.join(e, self.extension)

    @property
    def destination(self):
        return os.path.join(self.parent, self.target, self.ne)

    @property
    def ne(self):
        return f'{self.name}.{self.extension}'


class Directory():
    def __init__(self, path):
        self.path = path
        self.files = [self.__get_file_info(f) for f in os.listdir(
            path) if not os.path.isdir(os.path.join(path, f))]

    def __move_file(self, f: File):
        original = f.__repr__()
        i = 0
        while os.path.isfile(f.destination):
            i += 1
            f.name = '_'.join([str(i), f.name])
        os.rename(original, f.destination)

    def organize(self):
        for f in self.files:
            ndir = os.path.join(self.path, f.target)
            if not os.path.exists(ndir):
                os.makedirs(ndir)
            self.__move_file(f)

    def __get_file_info(self, fn: str) -> File:
        i = fn.split('.')
        fn = '.'.join(i[:-1])
        return File(self.path, fn, i[-1])


Directory(os.path.join(os.path.expanduser("~"), "test")).organize()

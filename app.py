import pdb
import os
from os import path as osp
import json


class File():
    def __init__(self, parent, name, extension):
        self.parent = parent
        self.name = name
        self.extension = extension
        self.target = self.__get_path()

    def __repr__(self):
        return f'{osp.join(self.parent, self.ne)}'

    def __get_path(self):
        with open(osp.join(osp.abspath(osp.dirname(__file__)),
                           'file_extensions.json')) as data:
            exts = json.load(data)
            for e in exts:
                if self.extension in exts[e]:
                    return osp.join(e, self.extension)

    @property
    def destination(self):
        return osp.join(self.parent, self.target, self.ne)

    @property
    def ne(self):
        return f'{self.name}.{self.extension}'


class Directory():
    def __init__(self, path):
        self.path = path
        self.files = [self.__get_file_info(f) for f in os.listdir(
            path) if not osp.isdir(osp.join(path, f))]

    def __move_file(self, f: File):
        original = f.__repr__()
        i = 0
        while osp.isfile(f.destination):
            i += 1
            f.name = '_'.join([str(i), f.name])
        os.rename(original, f.destination)

    def organize(self):
        for f in self.files:
            ndir = osp.join(self.path, f.target)
            if not osp.exists(ndir):
                os.makedirs(ndir)
            self.__move_file(f)

    def __get_file_info(self, fn: str) -> File:
        i = fn.split('.')
        fn = '.'.join(i[:-1])
        return File(self.path, fn, i[-1])


Directory(osp.join(osp.expanduser("~"), "Downloads")).organize()

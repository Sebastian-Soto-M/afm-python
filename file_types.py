import os
import json
from os.path import join, expanduser


class FileType():
    def __init__(self, extension):
        self.target_folder = 'Downloads'
        self.extension = extension
        self.path = join(expanduser('~'), self.target_folder)
        super().__init__()

    def create_path(self, parent_folder):
        return join(self.path, parent_folder, self.extension)


class Image(FileType):
    def __init__(self, extension):
        super().__init__(extension)

    def get_path(self):
        return super().create_path('img')


class Uncategorized(FileType):
    def __init__(self, extension):
        super().__init__(extension)

    def get_path(self):
        return super().create_path('uncategorized')


class Audio(FileType):
    def __init__(self, extension):
        super().__init__(extension)

    def get_path(self):
        return super().create_path('audio')


class Compressed(FileType):
    def __init__(self, extension):
        super().__init__(extension)

    def get_path(self):
        return super().create_path('compressed')


class Data(FileType):
    def __init__(self, extension):
        super().__init__(extension)

    def get_path(self):
        return super().create_path('data')


class Disk(FileType):
    def __init__(self, extension):
        super().__init__(extension)

    def get_path(self):
        return super().create_path('disk')


class Executable(FileType):
    def __init__(self, extension):
        super().__init__(extension)

    def get_path(self):
        return super().create_path('executable')


class Font(FileType):
    def __init__(self, extension):
        super().__init__(extension)

    def get_path(self):
        return super().create_path('font')


class Presentation(FileType):
    def __init__(self, extension):
        super().__init__(extension)

    def get_path(self):
        return super().create_path('presentation')


class System (FileType):
    def __init__(self, extension):
        super().__init__(extension)

    def get_path(self):
        return super().create_path('system')


class Video(FileType):
    def __init__(self, extension):
        super().__init__(extension)

    def get_path(self):
        return super().create_path('video')


class Internet(FileType):
    def __init__(self, extension):
        super().__init__(extension)

    def get_path(self):
        return super().create_path('internet')


class Text(FileType):
    def __init__(self, extension):
        super().__init__(extension)

    def get_path(self):
        return super().create_path('text_files')


class Git(FileType):
    def __init__(self, extension):
        super().__init__(extension)

    def get_path(self):
        return super().create_path('git')


class FileTypeFactory(object):
    def factory(extension):
        pfolder = os.path.dirname(os.path.abspath(__file__))
        with open(join(pfolder, 'file_extensions.json')) as json_file:
            file_extensions = json.load(json_file)
        if extension in file_extensions['image']:
            return Image(extension)
        if extension in file_extensions['audio']:
            return Audio(extension)
        if extension in file_extensions['compressed']:
            return Compressed(extension)
        if extension in file_extensions['data']:
            return Data(extension)
        if extension in file_extensions['disc']:
            return Disk(extension)
        if extension in file_extensions['executable']:
            return Executable(extension)
        if extension in file_extensions['font']:
            return Font(extension)
        if extension in file_extensions['presentation']:
            return Presentation(extension)
        if extension in file_extensions['system']:
            return System(extension)
        if extension in file_extensions['internet']:
            return Internet(extension)
        if extension in file_extensions['text']:
            return Text(extension)
        if extension in file_extensions['audio']:
            return Audio(extension)
        if extension in file_extensions['git']:
            return Git(extension)
        else:
            return Uncategorized(extension)

from __future__ import annotations

# from pydantic.dataclasses import dataclass
from dataclasses import dataclass
from datetime import datetime
from os import listdir, rename
from os.path import isfile, join
from pathlib import Path
from typing import Optional, Tuple

from pydantic import BaseModel


class AFMConfiguration(BaseModel):
    include: dict[str, list[str]]
    exclude: list[str]


@dataclass
class FileModel:
    path: str
    full_name: str
    name: Optional[str] = None
    extension: Optional[str] = None
    is_dotfile: bool = False

    def __post_init__(self):
        if self.name is None and self.extension is None:
            detail = self.full_name.split('.')
            if len(detail) > 1:
                self.extension = detail[-1]
                self.is_dotfile = self.full_name[0] == '.'
                self.name = self.extension if self.is_dotfile else '.'.join(
                    detail[:-1])
            else:
                self.extension = self.full_name
                self.name = self.full_name

    def __str__(self):
        return f'{join(self.path, self.full_name)}'


@dataclass
class HistoryRow:
    original_path: str
    current_path: str
    date: datetime

    def __str__(self):
        op = join('~', *self.original_path.split('/')[3:])
        cp = join('~', *self.current_path.split('/')[3:])
        return '\n'.join([
            f'\nMoved {self.date.ctime()}',
            f'Original path:\t{op}',
            f'Current path:\t{cp}'
        ])


class FileToMove(BaseModel):
    origin: FileModel
    target: str

    def __find_valid_target(self) -> Result:
        # if the file exists in the target destination
        target = FileModel(path=self.target, full_name=self.origin.full_name)
        info = [self.origin.name, 0]
        while renamed := isfile(str(target)):
            info[1] += 1
            target.name = f'{info[0]}-{info[1]}'
            target.full_name = f'{target.name}.{target.extension}'
        return self.Result(
            paths=(str(self.origin), str(target)), renamed=not renamed)

    @property
    def paths(self) -> Tuple[str, str]:
        return self.__find_valid_target().paths

    def move(self):
        rename(*self.paths)

    def __str__(self):
        result = self.__find_valid_target()
        original_path, target_path = result.paths
        msg = f'{original_path} -> {target_path}'
        return f'{msg} | Avoided name conflict' if result.renamed else msg

    @dataclass
    class Result:
        paths: Tuple[str, str]
        renamed: bool


class Directory:
    def __init__(self, config: AFMConfiguration, path: str, verbose: bool):
        self.__config = config
        self.__path = path
        self.__verbose = verbose

    @property
    def path(self):
        return self.__path

    @property
    def files(self) -> list[FileModel]:
        return self.__get_file_models(self.__path)

    def __get_file_models(self, dir_path: str) -> list[FileModel]:
        return [
            FileModel(path=dir_path, full_name=f)
            for f in listdir(dir_path)
            if not Path(
                join(dir_path, f)).is_dir()
        ]

    def copy_with_path(self, path: str) -> Directory:
        return Directory(
            config=self.__config, path=path,
            verbose=self.__verbose
        )

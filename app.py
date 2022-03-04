# type: ignore
from __future__ import annotations

from datetime import datetime
import argparse
import json
from os import listdir, rename
from os.path import isfile, join
from pathlib import Path
from typing import Optional, Tuple

from pydantic import BaseModel
from dataclasses import dataclass
# from pydantic.dataclasses import dataclass
import sqlite3

DB_PATH = join(Path.cwd(), 'changes.db')
TBL_NAME = 'change_history'


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


class FileManager:
    def __init__(self, path: str, verbose: bool):
        self.config = self.__read_config()
        self.directory = Directory(self.config, path, verbose)
        self.files_to_move: list[FileToMove] = []

    def __read_config(self) -> AFMConfiguration:
        config_path = Path(join(Path(__file__).parent, 'config.json'))
        with config_path.open('r') as cf:
            config = json.load(cf)
            return AFMConfiguration(**config)

    def organize(self):
        for original in self.directory.files:
            if original.extension in self.config.exclude:
                print(f'ignored: {str(original)}')
            else:
                for e in self.config.include:
                    if original.extension in self.config.include[e]:
                        res = join(e, original.extension)
                        break
                    else:
                        res = join('uncategorized', original.extension)
                self.files_to_move.append(
                    FileToMove(
                        origin=original,
                        target=join(
                            original.path,
                            res
                        )
                    )
                )

    def persist_changes(self):
        for ftm in self.files_to_move:
            ftm.move()
        self.write_changes()

    def read_last_changes(self):
        with sqlite3.connect(DB_PATH,
                             detect_types=sqlite3.PARSE_DECLTYPES |
                             sqlite3.PARSE_COLNAMES) as con:
            c = con.cursor()
            c.execute(f'select date,origin_path,target_path from {TBL_NAME}')
            for row in c.fetchall():
                hr = self.HistoryRow(
                    date=row[0],
                    original_path=row[1],
                    current_path=row[2])
                print(hr)

    def write_changes(self):
        changes = self.files_to_move
        with sqlite3.connect(DB_PATH) as con:
            c = con.cursor()
            c.execute('''
                create table if not exists {} (
                    id integer primary key,
                    origin_path text not null,
                    target_path text not null,
                    date timestamp
                );
            '''.format(TBL_NAME))
            c.executemany(
                '''
                    insert into {}(origin_path, target_path, date)
                    values(?,?,?)
                '''.format(TBL_NAME),
                [
                    [*ftm.paths, datetime.now()] for ftm in changes
                ])
            con.commit()

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


def menu():
    parser = argparse.ArgumentParser(description='Automatic File Manager')
    parser.add_argument(
        'path', metavar='PATH', type=str,
        help='The path of the folder you want to sort'
    )
    parser.add_argument(
        "-a", "--absolute", help="Use absolute path", action="store_true")
    parser.add_argument(
        "-v", "--verbose", help="provide a descriptive output", action="store_true")
    return parser.parse_args()


def main():
    args = menu()
    pth = args.path
    if args.absolute is None:
        pth = join(os.getcwd(), pth)
    fm = FileManager(pth, args.verbose)
    fm.organize()
    fm.persist_changes()
    # fm.read_last_changes()


if __name__ == '__main__':
    main()

from __future__ import annotations

import argparse
import json
import os
# from pydantic.dataclasses import dataclass
import sqlite3
from datetime import datetime
from os.path import join
from pathlib import Path

from models import AFMConfiguration, Directory, FileToMove, HistoryRow

DB_PATH = join(Path.cwd(), 'changes.db')
TBL_NAME = 'change_history'


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
                hr = HistoryRow(
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

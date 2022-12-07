import argparse
import os.path
from dataclasses import dataclass
from dataclasses import field
from typing import ClassVar

import pytest

from support import timing

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

# NOTE: paste test text here
INPUT_S = '''\
$ cd /
$ ls
dir a
14848514 b.txt
8504156 c.dat
dir d
$ cd a
$ ls
dir e
29116 f
2557 g
62596 h.lst
$ cd e
$ ls
584 i
$ cd ..
$ cd ..
$ cd d
$ ls
4060174 j
8033020 d.log
5626152 d.ext
7214296 k
'''
EXPECTED = 24933642


@dataclass()
class File:
    name: str
    size: int


@dataclass
class Directory:
    index: ClassVar[dict] = dict()
    name: str
    path: str = field(init=False)
    parent: 'Directory' = None
    sub_dirs: dict[str, 'Directory'] = field(default_factory=dict)
    files: dict[str, File] = field(default_factory=dict)

    def __post_init__(self):
        self.path = self.parent.path + self.name + '/' if self.parent else '/'
        self.index[self.path] = self

    @property
    def size(self):
        my_files_size = sum(f.size for f in self.files.values())
        my_dirs_size = sum(d.size for d in self.sub_dirs.values())
        return my_files_size + my_dirs_size

    def __repr__(self):
        return self.path


def compute(s: str) -> int:
    # start at root
    current = root = Directory('root')

    lines = s.splitlines()
    for line in lines:
        match line.split():
            case '$', 'ls':
                continue
            case '$', 'cd', '/':
                current = root
            case '$', 'cd', '..':
                current = current.parent
            case '$', 'cd', dir_name:
                current = current.sub_dirs[dir_name]
            case 'dir', dir_name:
                # new directory, add to path index
                new_dir = Directory(dir_name, parent=current)
                # and add it to current dirs
                current.sub_dirs[dir_name] = new_dir
            case file_size, file_name:
                current.files[file_name] = File(file_name, int(file_size))
            case _:
                raise AssertionError('uncaught case')

    available = 70_000_000
    needed = 30_000_000
    taken = root.size
    unused = available - taken

    sorted_dirs = sorted((d for d in Directory.index.values()), key=lambda x: x.size)
    for d in sorted_dirs:
        size = d.size
        if unused + size > needed:
            return size


@pytest.mark.solved
@pytest.mark.parametrize(
    ('input_s', 'expected'),
    (
            (INPUT_S, EXPECTED),
    ),
)
def test(input_s: str, expected: int) -> None:
    assert compute(input_s) == expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('data_file', nargs='?', default=INPUT_TXT)
    args = parser.parse_args()

    with open(args.data_file) as f, timing():
        print(compute(f.read()))

    return 0


if __name__ == '__main__':
    raise SystemExit(main())

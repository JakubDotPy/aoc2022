from __future__ import annotations

import contextlib
import enum
import os
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Generator

HERE = os.path.dirname(os.path.abspath(__file__))


@contextlib.contextmanager
def timing(name: str = '') -> Generator[None, None, None]:
    before = time.time()
    try:
        yield
    finally:
        after = time.time()
        t = (after - before) * 1000
        unit = 'ms'
        if t < 100:
            t *= 1000
            unit = 'μs'
        if name:
            name = f' ({name})'
        print(f'> {int(t)} {unit}{name}', file=sys.stderr, flush=True)


def _get_cookie_headers() -> dict[str, str]:
    with open(os.path.join(HERE, '../.env')) as f:
        contents = f.read().strip()
    return {'Cookie': contents}


def get_input(year: int, day: int) -> str:
    url = f'https://adventofcode.com/{year}/day/{day}/input'
    req = urllib.request.Request(url, headers=_get_cookie_headers())
    return urllib.request.urlopen(req).read().decode()


def get_year_day() -> tuple[int, int]:
    cwd = os.getcwd()
    day_s = os.path.basename(cwd)
    year_s = os.path.basename(os.path.dirname(cwd))

    if not day_s.startswith('day') or not year_s.startswith('aoc'):
        raise AssertionError(f'unexpected working dir: {cwd}')

    return int(year_s[len('aoc'):]), int(day_s[len('day'):])


def download_input() -> int:
    year, day = get_year_day()

    for i in range(5):
        try:
            s = get_input(year, day)
        except urllib.error.URLError as e:
            print(f'zzz: not ready yet: {e}')
            time.sleep(1)
        else:
            break
    else:
        raise SystemExit('timed out after attempting many times')

    with open('input.txt', 'w') as f:
        f.write(s)

    lines = s.splitlines()
    if len(lines) > 10:
        for line in lines[:10]:
            print(line)
        print('...')
    else:
        print(lines[0][:80])
        print('...')

    return 0


def new_day() -> None:
    print(' Creating new advent day '.center(50, '-'))

    temp_dir = Path('day00').absolute()

    # find number of last day
    last_day = sorted(
        folder.name
        for folder in Path().iterdir()
        if folder.is_dir() and folder.name.startswith('day')
    )[-1]

    print(f'Last day is {last_day}.')

    # prepare the paths
    last_day_num = int(re.findall(r'\d+', last_day)[0])
    new_day_num = last_day_num + 1
    new_day_folder_name = f'day{new_day_num:02}'
    new_path = Path(new_day_folder_name).absolute()

    # copy folder
    print(f"Creating folder '{new_day_folder_name}'.")
    shutil.copytree(temp_dir, new_path)

    # replace template mark with commented solved
    old = r'@pytest.mark.template'
    new = r'# @pytest.mark.solved'
    pattern = re.compile(old)
    with open(new_path / 'part1.py', 'r+') as f:
        contents = f.read()
        contents = pattern.sub(new, contents)
        f.seek(0)
        f.write(contents)

    # edit run configurations
    print('Editing run configuration.')
    for file in Path('.run').iterdir():
        print(f' - editing {file}')
        with open(file, 'r') as f:
            contents = f.read()
            new_contents = re.sub(
                fr'{last_day}', fr'{new_day_folder_name}', contents
            )
        with open(file, 'w') as f:
            f.write(new_contents)

    print(' Finished '.center(50, '-'))


# --- helper functions and classes

def adjacent_4(x: int, y: int) -> Generator[tuple[int, int], None, None]:
    yield x, y - 1
    yield x + 1, y
    yield x, y + 1
    yield x - 1, y


def adjacent_8(x: int, y: int) -> Generator[tuple[int, int], None, None]:
    for y_d in (-1, 0, 1):
        for x_d in (-1, 0, 1):
            if y_d == x_d == 0:
                continue
            yield x + x_d, y + y_d


def parse_coords_int(s: str) -> dict[tuple[int, int], int]:
    coords = {}
    for y, line in enumerate(s.splitlines()):
        for x, c in enumerate(line):
            coords[(x, y)] = int(c)
    return coords


def parse_coords_hash(s: str) -> set[tuple[int, int]]:
    coords = set()
    for y, line in enumerate(s.splitlines()):
        for x, c in enumerate(line):
            if c == '#':
                coords.add((x, y))
    return coords


def parse_numbers_split(s: str) -> list[int]:
    return [int(x) for x in s.split()]


def parse_numbers_comma(s: str) -> list[int]:
    return [int(x) for x in s.strip().split(',')]


def format_coords_hash(coords: set[tuple[int, int]]) -> str:
    min_x = min(x for x, _ in coords)
    max_x = max(x for x, _ in coords)
    min_y = min(y for _, y in coords)
    max_y = max(y for _, y in coords)
    return '\n'.join(
        ''.join(
            '#' if (x, y) in coords else ' '
            for x in range(min_x, max_x + 1)
        )
        for y in range(min_y, max_y + 1)
    )


def print_coords_hash(coords: set[tuple[int, int]]) -> None:
    print(format_coords_hash(coords))


class Direction4(enum.Enum):
    UP = (0, -1)
    RIGHT = (1, 0)
    DOWN = (0, 1)
    LEFT = (-1, 0)

    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y

    @property
    def _vals(self) -> tuple[Direction4, ...]:
        return tuple(type(self).__members__.values())

    @property
    def cw(self) -> Direction4:
        vals = self._vals
        return vals[(vals.index(self) + 1) % len(vals)]

    @property
    def ccw(self) -> Direction4:
        vals = self._vals
        return vals[(vals.index(self) - 1) % len(vals)]

    @property
    def opposite(self) -> Direction4:
        vals = self._vals
        return vals[(vals.index(self) + 2) % len(vals)]

    def apply(self, x: int, y: int, *, n: int = 1) -> tuple[int, int]:
        return self.x * n + x, self.y * n + y

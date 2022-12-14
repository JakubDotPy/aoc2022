import argparse
import itertools
import os.path
import re
from itertools import pairwise

import pytest

from support import Direction4
from support import timing

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

# NOTE: paste test text here
INPUT_S = '''\
498,4 -> 498,6 -> 496,6
503,4 -> 502,4 -> 502,9 -> 494,9
'''
EXPECTED = 93

BLOCKED = set()


def by_pairs(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return zip(a, a)


def parse_walls(s):
    global BLOCKED
    lines = s.splitlines()
    for line in lines:
        coords = by_pairs(map(int, re.findall(r'\d+', line)))
        for (a_x, a_y), (o_x, o_y) in pairwise(coords):
            if a_x == o_x:
                range_start, range_stop = min(a_y, o_y), max(a_y, o_y)
                BLOCKED.update(set((a_x, yy) for yy in range(range_start, range_stop + 1)))
            else:
                range_start, range_stop = min(a_x, o_x), max(a_x, o_x)
                BLOCKED.update(set((xx, a_y) for xx in range(range_start, range_stop + 1)))


def left(pos):
    pos = Direction4.DOWN.apply(*pos)
    return Direction4.LEFT.apply(*pos)


def right(pos):
    pos = Direction4.DOWN.apply(*pos)
    return Direction4.RIGHT.apply(*pos)


def blocked(pos):
    return pos in BLOCKED


def compute(s: str) -> int:
    parse_walls(s)
    abbys_level = max(y for _, y in BLOCKED)
    s += f'0,{abbys_level + 2} -> 1000,{abbys_level + 2}'
    parse_walls(s)

    dispenser_pos = (500, 0)
    num_sand = 1

    for num_sand in itertools.count():
        pos = dispenser_pos
        while True:

            if pos in BLOCKED:
                # now blocked is directly under the dispenser
                return num_sand
            elif pos[1] == abbys_level + 1:
                # effectively draws a line, checks the bottom border
                BLOCKED.add(pos)
                break

            if Direction4.DOWN.apply(*pos) not in BLOCKED:
                pos = Direction4.DOWN.apply(*pos)
            elif left(pos) not in BLOCKED:
                pos = left(pos)
            elif right(pos) not in BLOCKED:
                pos = right(pos)
            else:
                BLOCKED.add(pos)
                break


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

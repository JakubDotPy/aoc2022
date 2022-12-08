import argparse
import operator
import os.path
from functools import reduce

import pytest

from support import Direction4
from support import parse_coords_int
from support import timing

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

# NOTE: paste test text here
INPUT_S = '''\
30373
25512
65332
33549
35390
'''
EXPECTED = 8


def take_while_lower(lim, iterable):
    for c in iterable:
        yield c
        if c >= lim:
            return  # we've reached limit, stop the iterator


def get_in_direction(grid, coords, dir):
    while True:
        try:
            coords = dir.apply(*coords)
            yield grid[coords]
        except KeyError:
            # out of bounds
            return


def compute(s: str) -> int:
    grid = parse_coords_int(s)
    best_visible = 0
    for pos, tree_height in grid.items():
        visible = reduce(
            operator.mul,
            (
                sum(1 for _ in take_while_lower(tree_height, get_in_direction(grid, pos, direction)))
                for direction in Direction4
            )
        )
        if visible > best_visible:
            best_visible = visible
    return best_visible


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

import argparse
import os.path
from itertools import repeat

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
EXPECTED = 21


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
    visible = 0
    for pos, tree_height in grid.items():
        heights_in_dir = map(
            get_in_direction, repeat(grid), repeat(pos), Direction4
        )
        visible += any((
            all(h < tree_height for h in dir_heights)
            for dir_heights in heights_in_dir
        ))
    return visible


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

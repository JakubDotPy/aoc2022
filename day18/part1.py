import argparse
import os.path
from collections import deque

import pytest

from support import timing

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

# NOTE: paste test text here
INPUT_S_1 = '''\
1,1,1
2,1,1
'''
EXPECTED_1 = 10
INPUT_S_2 = '''\
2,2,2
1,2,2
3,2,2
2,1,2
2,3,2
2,2,1
2,2,3
2,2,4
2,2,6
1,2,5
3,2,5
2,1,5
2,3,5
'''
EXPECTED_2 = 64


def in_bounds(cube, bounds):
    return all(
        bound[0] <= coord <= bound[1]
        for coord, bound in zip(cube, bounds)
    )


def compute(s: str) -> int:
    cubes = set()
    faces = 0
    for line in s.splitlines():
        x, y, z = map(int, line.split(','))
        candidates = (
        (x + 1, y, z),
        (x - 1, y, z),
        (x, y + 1, z),
        (x, y - 1, z),
        (x, y, z + 1),
        (x, y, z - 1),
        )
        faces += 6  # assume free standing
        for c in candidates:
            if c in cubes:
                # if adjacent, remove two faces
                faces -= 2
            cubes.add((x, y, z))

    return faces


# @pytest.mark.solved
@pytest.mark.parametrize(
    ('input_s', 'expected'),
    (
            (INPUT_S_1, EXPECTED_1),
            (INPUT_S_2, EXPECTED_2),
    ),
)
def test(input_s: str, expected: int) -> None:
    print()  # newline in test output, helps readability
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

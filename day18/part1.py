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
    cubes = set(
        tuple(map(int, line.split(',')))
        for line in s.splitlines()
    )

    # consider the envelope around the cubes to be one larger
    min_max = lambda x: (min(x) - 1, max(x) + 1)
    # (min_x, max_x), (min_y, max_y), (min_z, max_z)
    bounds = tuple(map(min_max, zip(*cubes)))

    start = tuple(coord[0] for coord in bounds)
    total_sides = 0

    # BFS
    seen = set()
    queue = deque((start,))
    while queue:
        # Pop the first current from the queue
        current = queue.popleft()

        if current in seen:
            continue

        # Mark the current as seen
        seen.add(current)

        # Get all the neighbors of the current
        x, y, z = current
        candidates = (
            (x + 1, y, z),
            (x - 1, y, z),
            (x, y + 1, z),
            (x, y - 1, z),
            (x, y, z + 1),
            (x, y, z - 1),
        )
        for candidate in candidates:
            if candidate in seen:
                continue
            if candidate in cubes:
                total_sides += 1
                continue
            if not in_bounds(candidate, bounds):
                continue

            queue.append(candidate)

    return total_sides


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

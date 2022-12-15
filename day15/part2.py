import argparse
import os.path
import re
from dataclasses import dataclass
from itertools import product
from typing import ClassVar

import pytest

from support import timing

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

# NOTE: paste test text here
INPUT_S = '''\
Sensor at x=2, y=18: closest beacon is at x=-2, y=15
Sensor at x=9, y=16: closest beacon is at x=10, y=16
Sensor at x=13, y=2: closest beacon is at x=15, y=3
Sensor at x=12, y=14: closest beacon is at x=10, y=16
Sensor at x=10, y=20: closest beacon is at x=10, y=16
Sensor at x=14, y=17: closest beacon is at x=10, y=16
Sensor at x=8, y=7: closest beacon is at x=2, y=10
Sensor at x=2, y=0: closest beacon is at x=2, y=10
Sensor at x=0, y=11: closest beacon is at x=2, y=10
Sensor at x=20, y=14: closest beacon is at x=25, y=17
Sensor at x=17, y=20: closest beacon is at x=21, y=22
Sensor at x=16, y=7: closest beacon is at x=15, y=3
Sensor at x=14, y=3: closest beacon is at x=15, y=3
Sensor at x=20, y=1: closest beacon is at x=15, y=3
'''
EXPECTED = 56000011

Point = tuple[int, int]


def line_intersection(line1, line2):
    """Stack overflow copypasta"""
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) // div
    y = det(d, ydiff) // div
    return x, y


@dataclass
class Sensor:
    pos: Point
    beacon: Point
    r_slopes: ClassVar[set[tuple[Point, Point]]] = set()  # index of all \\
    l_slopes: ClassVar[set[tuple[Point, Point]]] = set()  # index of all //

    def __post_init__(self):
        self._calculate_lines()

    def __str__(self):
        return f'Sensor({self.pos!r}, {self.beacon!r})'

    @property
    def dist_to_beacon(self):
        return manh_dist(self.pos, self.beacon)

    def _calculate_lines(self):
        # unpack for convenience
        (px, py), dist = self.pos, self.dist_to_beacon

        # NOTE: we must add + 1 so we get the outer lines!!
        dist += 1
        # top ^, bottom v
        top, bottom = (px, py - dist), (px, py + dist)
        # left right points < >
        left, right = (px - dist, py), (px + dist, py)

        # add the lines to sets
        self.l_slopes.add((left, top))  # top /
        self.l_slopes.add((bottom, right))  # bottom /
        self.r_slopes.add((top, right))  # top \
        self.r_slopes.add((left, bottom))  # bottom \


def manh_dist(a: Point, b: Point):
    (ax, ay), (bx, by) = a, b
    return abs(ax - bx) + abs(ay - by)


def parse(s):
    sensors = list()
    grid = dict()
    for line in s.strip().splitlines():
        s_x, s_y, b_x, b_y = map(int, re.findall(r'-?\d+', line))
        sensors.append(Sensor(pos=(s_x, s_y), beacon=(b_x, b_y)))
        grid[(s_x, s_y)] = 'S'
        grid[(b_x, b_y)] = 'B'
    return sensors, grid


def print_grid(grid: dict[tuple[int, int]]):
    min_x = min(x for x, _ in grid)
    max_x = max(x for x, _ in grid)
    min_y = min(y for _, y in grid)
    max_y = max(y for _, y in grid)
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if y == 10:
                print('-', end='')
            else:
                print(grid.get((x, y), '.'), end='')
        print()


def compute(s: str) -> int:
    sensors, grid = parse(s)
    x_lim = y_lim = 4_000_000

    # bruteforce on the intersections
    for left, right in product(Sensor.l_slopes, Sensor.r_slopes):
        inters = x, y = line_intersection(left, right)
        if not ((0 < x < x_lim) and (0 < y < y_lim)):
            continue

        if all(manh_dist(inters, s.pos) > s.dist_to_beacon for s in sensors):
            return x * 4_000_000 + y

    return 0


# @pytest.mark.solved
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

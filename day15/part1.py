import argparse
import os.path
import re
from dataclasses import dataclass
from functools import cached_property

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
EXPECTED = 26


def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y


@dataclass(frozen=True)
class Sensor:
    pos: tuple[int, int]
    beacon: tuple[int, int]

    def __str__(self):
        return f'Sensor({self.pos!r}, {self.beacon!r})'

    @cached_property
    def dist_to_beacon(self):
        (x, y), (bx, by) = self.pos, self.beacon
        return abs(x - bx) + abs(y - by)

    def x_on_level(self, level):
        # unpack for convenience
        (px, py), dist = self.pos, self.dist_to_beacon

        # top or bottom pointy point ^ v
        pointy = (px, py - dist) if level < py else (px, py + dist)
        # left right points < >
        left, right = (px - dist, py), (px + dist, py)

        # construct the left and right slope line / \ .. or \ / based on pointy
        left_line, right_line = (left, pointy), (pointy, right)
        # horizontal line we want
        level_line = (px - dist, level), (px + dist, level)

        # calculate intersections
        lx, ly = map(int, line_intersection(left_line, level_line))
        rx, ry = map(int, line_intersection(right_line, level_line))

        # return only left and right x coords, we know the y is level
        return lx, rx


def parse(s):
    sensors = set()
    grid = dict()
    for line in s.strip().splitlines():
        s_x, s_y, b_x, b_y = map(int, re.findall(r'-?\d+', line))
        sensors.add(Sensor(pos=(s_x, s_y), beacon=(b_x, b_y)))
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
    level = 2_000_000
    impossible = set()
    for sensor in sensors:
        if not ((sensor.pos[1] - sensor.dist_to_beacon) <= level <= (sensor.pos[1] + sensor.dist_to_beacon)):
            continue  # there will be no intersect in the diamond
        left_intersect, right_intersect = sensor.x_on_level(level)
        impossible.update(range(left_intersect, right_intersect))
    return len(impossible)


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

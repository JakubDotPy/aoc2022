import argparse
import itertools
import os.path
import textwrap
from copy import deepcopy
from dataclasses import dataclass
from typing import ClassVar

import pytest

from support import Direction4
from support import timing

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

# NOTE: paste test text here
INPUT_S = '''\
>>><<><>><<<>><>>><<<>>><<<><<<>><>><<>>
'''
EXPECTED = 3068

Coord = tuple[int, int]


@dataclass
class Rock:
    SHAPES_STR: ClassVar[str] = textwrap.dedent("""\
        ####
        
        .#.
        ###
        .#.
        
        ..#
        ..#
        ###
        
        #
        #
        #
        #
        
        ##
        ##
        """)
    name: str
    shape: set[Coord]

    @classmethod
    def from_str(cls, name, s):
        """Load the rock coords from string.

        Must load the coords "bottom up".
        """
        coords = set()
        for y, line in enumerate(reversed(s.splitlines())):
            for x, c in enumerate(line):
                if c == '#':
                    coords.add((x, y))
        return cls(name, coords)

    def move(self, _dir: Direction4, n=1):
        self.shape = {_dir.apply(*coord, n=n) for coord in self}

    def fall(self):
        """Direction is reversed due to the up-down flip."""
        self.shape = {Direction4.UP.apply(*coord) for coord in self}

    def __iter__(self):
        yield from self.shape

    def __str__(self):
        return f'Rock({self.name})'

    __repr__ = __str__


class Chamber:
    jet_to_dir = {
        '<': Direction4.LEFT,
        '>': Direction4.RIGHT,
    }

    def __init__(self, jets: str, rocks: list[Rock]):
        self.jets = itertools.cycle(jets)
        self.rocks = itertools.cycle(rocks)
        self.occupied: set[Coord] = set()
        self.rock = None

    @property
    def max_height(self):
        if not self.occupied:
            return 0
        return max(c[1] for c in self.occupied)

    def collision(self, rock: Rock):
        in_wall = any(c[0] in [0, 8] for c in rock)
        on_the_floor = any(c[1] == 0 for c in rock)
        in_occupied = any(c in self.occupied for c in rock)
        return any((in_wall, on_the_floor, in_occupied))

    def spawn_rock(self, rock):
        rock = deepcopy(rock)
        rock.move(Direction4.DOWN, n=self.max_height + 1 + 3)
        rock.move(Direction4.RIGHT, n=3)
        self.rock = rock

    def process_rock(self):
        """Repeat following.

        - spawn rock
        - move
        - fall
        """
        rock = next(self.rocks)
        self.spawn_rock(rock)

        while True:
            _dir = self.jet_to_dir[next(self.jets)]

            # move the rock
            self.rock.move(_dir)
            if self.collision(self.rock):
                # if collision, revert
                self.rock.move(_dir.opposite)

            # fall the rock
            self.rock.fall()
            if self.collision(self.rock):
                # collision during the fall, freeze and continue
                self.rock.move(Direction4.DOWN)
                self.occupied |= self.rock.shape
                break

    def _coord_to_char(self, c):
        if c in self.occupied:
            return '#'
        if self.rock and c in self.rock:
            return '@'
        return '.'

    def __str__(self):
        print_height = self.max_height + 8
        rows = []
        for y in range(print_height, 0, -1):
            row = str(y) + ' |' + ''.join(self._coord_to_char((x, y)) for x in range(1, 8)) + '|'
            rows.append(row)
        rows.append('0 +-------+')
        return '\n'.join(rows)


def compute(s: str) -> int:
    jets: str = s.strip()
    shapes: list[str] = Rock.SHAPES_STR.split('\n\n')
    names: str = '-+jio'
    rocks = [Rock.from_str(n, s) for n, s in zip(names, shapes)]
    chamber = Chamber(jets, rocks)

    for _ in range(2022):
        chamber.process_rock()
        # print(chamber)

    return chamber.max_height


@pytest.mark.solved
@pytest.mark.parametrize(
    ('input_s', 'expected'),
    (
            (INPUT_S, EXPECTED),
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

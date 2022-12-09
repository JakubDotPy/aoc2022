import argparse
import os.path
from itertools import pairwise

import pytest

from support import Direction4
from support import timing

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

# NOTE: paste test text here
INPUT_S = '''\
R 4
U 4
L 3
D 1
R 4
D 1
L 5
R 2
'''
EXPECTED = 13


class Knot:
    def __init__(self, pos=(0, 0), name=''):
        self.name = name
        self.pos = pos
        self.seen = [pos, ]

    @property
    def _x(self):
        return self.pos[0]

    @property
    def _y(self):
        return self.pos[1]

    def should_move_to(self, other):
        return other - self > 1

    def move_to(self, other):
        if other._x > self._x:
            self.pos = Direction4.RIGHT.apply(*self.pos)
        elif other._x < self._x:
            self.pos = Direction4.LEFT.apply(*self.pos)
        if other._y > self._y:
            self.pos = Direction4.UP.apply(*self.pos)
        elif other._y < self._y:
            self.pos = Direction4.DOWN.apply(*self.pos)
        self.seen.append(self.pos)

    def __sub__(self, other):
        return max((abs(self.pos[0] - other.pos[0]), abs(self.pos[1] - other.pos[1])))

    def __repr__(self):
        return f'{self.name} {self.pos}'


class Rope:

    def __init__(self, start=(0, 0), length=1):
        self.knots = [Knot(start, i) for i in range(length)]
        self.head = self.knots[0]
        self.tail = self.knots[-1]
        self.head.name, self.tail.name = 'H', 'T'

    def move_head(self, dir: Direction4, amount: int):
        for _ in range(amount):
            self.head.pos = dir.apply(*self.head.pos)
            # backpropagation of the movement
            for this, prev in pairwise(self.knots):
                if prev.should_move_to(this):
                    prev.move_to(this)


def parse_moves(s):
    moves = []
    for line in s.splitlines():
        letter, amt = line.split()
        moves.append(
            (next(dir for dir in Direction4 if dir.name.startswith(letter)), int(amt))
        )
    return moves


def compute(s: str) -> int:
    moves = parse_moves(s)
    r = Rope(length=10)
    for dir, amt in moves:
        r.move_head(dir, amt)
    return len(set(r.tail.seen))


@pytest.mark.solved
@pytest.mark.parametrize(
    ('input_s', 'expected'),
    (
            ('''\
R 4
U 4
L 3
D 1
R 4
D 1
L 5
R 2
''', 1),
            ('''\
R 5
U 8
L 8
D 3
R 17
D 10
L 25
U 20
''', 36),
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

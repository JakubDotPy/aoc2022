import argparse
import os.path

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


class Rope:
    symbol = {
        'head': 'H',
        'tail': 'T',
    }

    def __init__(self, start=(0, 0), length=1):
        self.start = start
        self.head = start
        self.tail = start
        self.length = length
        self.head_index = self.tail_index = 0
        self.head_seen = [start, ]
        self.tail_seen = [start, ]

    def move(self, dir: Direction4, amount: int):
        # move head
        for _ in range(amount):
            self.head = dir.apply(*self.head)
            self.head_seen.append(self.head)
            self.head_index += 1
            if self._h_t_dist > self.length:
                self.tail = self.head_seen[self.head_index - 1]
                self.tail_seen.append(self.tail)

    @property
    def _h_t_dist(self):
        return max((abs(self.head[0] - self.tail[0]), abs(self.head[1] - self.tail[1])))


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
    r = Rope()
    for dir, amt in moves:
        r.move(dir, amt)
    return len(set(r.tail_seen))


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

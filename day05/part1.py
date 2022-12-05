import argparse
import os.path
import re
from collections import deque

import pytest

from support import timing

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

# NOTE: paste test text here
INPUT_S = '''\
    [D]    
[N] [C]    
[Z] [M] [P]
 1   2   3 

move 1 from 2 to 1
move 3 from 1 to 3
move 2 from 2 to 1
move 1 from 1 to 2
'''
EXPECTED = 'CMZ'


def compute(s: str) -> int:
    crates, instructions = s.split('\n\n')
    crates = crates.splitlines()
    deques = {i: deque() for i in range(1, len(crates[-1].split()) + 1)}
    for line in crates[:-1]:
        for i, letter in enumerate(line[1::4], start=1):
            if letter != ' ':
                deques[i].appendleft(letter)

    for line in instructions.splitlines():
        amount, _from, _to = map(int, re.findall(r'\d+', line))
        for _ in range(amount):
            deques[_to].append(deques[_from].pop())

    return ''.join(d.pop() for d in deques.values())


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

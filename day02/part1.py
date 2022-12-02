import argparse
import os.path

import pytest

from support import timing

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

# NOTE: paste test text here
INPUT_S = '''\
A Y
B X
C Z
'''
EXPECTED = 15

"""
A rock      X
B paper     Y
C scissors  Z
"""


def compute(s: str) -> int:
    move_points = {
        'X': 1,
        'Y': 2,
        'Z': 3,
    }
    counter_to_win = {
        'A': 'Y',
        'B': 'Z',
        'C': 'X',
    }
    counter_to_draw = {
        'A': 'X',
        'B': 'Y',
        'C': 'Z',
    }

    my_score = 0

    # parse lines
    lines = s.splitlines()
    for line in lines:
        him, me = line.split()
        my_score += move_points[me]
        if counter_to_draw[him] == me:
            my_score += 3
        if counter_to_win[him] == me:
            my_score += 6

    return my_score


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

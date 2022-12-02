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
EXPECTED = 12

"""
him | move    | me
-----------------
 A  |rock     | X
 B  |paper    | Y
 C  |scissors | Z
"""


def compute(s: str) -> int:
    move_points = {
        'X': 1,
        'Y': 2,
        'Z': 3,
    }

    """
    New strategy:
    x - loose
    y - draw
    z - win
    """

    counter_to_win = {
        'A': 'Y',
        'B': 'Z',
        'C': 'X',
    }
    counter_to_loose = {
        'A': 'Z',
        'B': 'X',
        'C': 'Y',
    }
    counter_to_draw = {
        'A': 'X',
        'B': 'Y',
        'C': 'Z',
    }
    strategy_to_move = {
        'X': counter_to_loose,
        'Y': counter_to_draw,
        'Z': counter_to_win,
    }
    strategy_points = {
        'X': 0,
        'Y': 3,
        'Z': 6,
    }

    my_score = 0

    # parse lines
    lines = s.splitlines()
    for line in lines:
        him, ordered_strategy = line.split()
        # choose move by strategy
        strategy = strategy_to_move[ordered_strategy]
        my_move = strategy[him]
        # points
        my_score += move_points[my_move]
        my_score += strategy_points[ordered_strategy]

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

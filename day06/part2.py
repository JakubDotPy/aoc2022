import argparse
import collections
import os.path
from itertools import islice

import pytest

from support import timing

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

# NOTE: paste test text here
INPUT_S = '''\

'''
EXPECTED = 1


def sliding_window(iterable, n):
    # sliding_window('ABCDEFG', 4) --> ABCD BCDE CDEF DEFG
    it = iter(iterable)
    window = collections.deque(islice(it, n), maxlen=n)
    if len(window) == n:
        yield tuple(window)
    for x in it:
        window.append(x)
        yield tuple(window)


def compute(s: str) -> int:
    lines = s.splitlines()
    for line in lines:
        for i, window in enumerate(sliding_window(line, 14)):
            if len(set(window)) == 14:
                return i + 14


@pytest.mark.solved
@pytest.mark.parametrize(
    ('input_s', 'expected'),
    (
            ('mjqjpqmgbljsphdztnvjfqwrcgsmlb', 19),
            ('bvwbjplbgvbhsrlpgdmjqwftvncz', 23),
            ('nppdvjthqldpwncqszvftbrmjlhg', 23),
            ('nznrnfrfntjfmvfwmzdfjlvtqnbhcprsg', 29),
            ('zcfzfwzzqfrljwzlrfnpqdbhtmscgvjw', 26),
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

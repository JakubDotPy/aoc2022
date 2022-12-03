import argparse
import os.path
from string import ascii_lowercase
from string import ascii_uppercase

import pytest

from support import grouper
from support import timing

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

# NOTE: paste test text here
INPUT_S = '''\
vJrwpWtwJgWrhcsFMMfFFhFp
jqHRNqRjqzjGDLGLrsFMfFZSrLrFZsSL
PmmdzqPrVvPwwTWBwg
wMqvLMZHhHMvwLHjbvcjnnSBnvTQFn
ttgJtRGJQctTZtZT
CrZsJsPPZsGzwwsLwLmpwMDw
'''
EXPECTED = 70

priority_mapping = (
        dict(zip(ascii_lowercase, range(1, 27)))
        | dict(zip(ascii_uppercase, range(27, 53)))
)


def compute(s: str) -> int:
    lines = s.splitlines()
    priorities = []
    for tripple in grouper(lines, 3):
        first, second, third = tripple
        same = set(first) & set(second) & set(third)
        priorities.append(same.pop())

    return sum(priority_mapping[char] for char in priorities)


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

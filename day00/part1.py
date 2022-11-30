import argparse
import os.path

import pytest

from support import timing

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

# NOTE: paste test text here
INPUT_S = '''\

'''
EXPECTED = 1


def compute(s: str) -> int:
    # parse numbers
    nums = [int(n) for n in s.splitlines()]
    for n in nums:
        ...

    # parse lines
    lines = s.splitlines()
    for line in lines:
        ...

    # TODO: implement solution here!
    return 0


@pytest.mark.template
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

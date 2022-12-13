import argparse
import functools
import os.path
from itertools import zip_longest

import pytest

from support import timing

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

# NOTE: paste test text here
INPUT_S = '''\
[1,1,3,1,1]
[1,1,5,1,1]

[[1],[2,3,4]]
[[1],4]

[9]
[[8,7,6]]

[[4,4],4,4]
[[4,4],4,4,4]

[7,7,7,7]
[7,7,7]

[]
[3]

[[[]]]
[[]]

[1,[2,[3,[4,[5,6,7]]]],8,9]
[1,[2,[3,[4,[5,6,0]]]],8,9]
'''
EXPECTED = 140


def normalize(l, r):
    if isinstance(l, int) and not isinstance(r, int):
        return [l], r
    elif not isinstance(l, int) and isinstance(r, int):
        return l, [r]
    else:
        return l, r


def compare(left, right):
    left, right = normalize(left, right)
    match left, right:
        case int(), int():
            return left - right if left != right else 0
        case list(), list():
            for l, r in zip_longest(left, right):
                if l is None:
                    return -1
                if r is None:
                    return 1
                compared = compare(l, r)
                if compared != 0:
                    return compared
            else:
                return 0
        case _:
            raise AssertionError(f'uncaught {left, right}')


def compute(s: str) -> int:
    s = s.replace('\n\n', '\n')
    dividers = [[[2]], [[6]]]
    packets = [eval(line) for line in s.strip().splitlines()]
    packets.extend(dividers)
    packets.sort(key=functools.cmp_to_key(compare))
    return (packets.index(dividers[0]) + 1) * (packets.index(dividers[1]) + 1)


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

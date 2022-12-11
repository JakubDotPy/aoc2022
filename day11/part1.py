import argparse
import os.path
from collections import deque

import pytest

from support import timing

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

# NOTE: paste test text here
INPUT_S = '''\
Monkey 0:
  Starting items: 79, 98
  Operation: new = old * 19
  Test: divisible by 23
    If true: throw to monkey 2
    If false: throw to monkey 3

Monkey 1:
  Starting items: 54, 65, 75, 74
  Operation: new = old + 6
  Test: divisible by 19
    If true: throw to monkey 2
    If false: throw to monkey 0

Monkey 2:
  Starting items: 79, 60, 97
  Operation: new = old * old
  Test: divisible by 13
    If true: throw to monkey 1
    If false: throw to monkey 3

Monkey 3:
  Starting items: 74
  Operation: new = old + 3
  Test: divisible by 17
    If true: throw to monkey 0
    If false: throw to monkey 1
'''
EXPECTED = 10605


class Monkey:
    other_monkeys: dict[int, 'Monkey'] = dict()

    def __init__(self, name, items, operation, test_operation, true_monkey, false_monkey):
        self.name = name
        self.items = deque(items)
        self.operation = operation
        self.test_operation = test_operation
        self.processed_items = 0
        self.true_monkey = true_monkey
        self.false_monkey = false_monkey
        self._register()

    def _register(self):
        self.other_monkeys[self.name] = self

    def _getitem(self):
        return self.items.popleft()

    def _receive_item(self, item):
        self.items.append(item)

    def preprocess(self, worry_level):
        return worry_level // 3

    def test_the_level(self, item):
        item = self.operation(item)
        item = self.preprocess(item)
        monkey_to_go = self.true_monkey if self.test_operation(item) else self.false_monkey
        self.other_monkeys[monkey_to_go]._receive_item(item)

    def process_items(self):
        while self.items:
            item = self._getitem()
            self.processed_items += 1
            self.test_the_level(item)

    def __str__(self):
        return f'{self.__class__.__name__}({self.name}, {self.items})'

    __repr__ = __str__


def compute(s: str) -> int:
    monkeys = [
        Monkey(
            name=0,
            items=[57, 58],
            operation=lambda x: x * 19,
            test_operation=lambda x: x % 7 == 0,
            true_monkey=2,
            false_monkey=3,
        ),
        Monkey(
            name=1,
            items=[66, 52, 59, 79, 94, 73],
            operation=lambda x: x + 1,
            test_operation=lambda x: x % 19 == 0,
            true_monkey=4,
            false_monkey=6,
        ),
        Monkey(
            name=2,
            items=[80],
            operation=lambda x: x + 6,
            test_operation=lambda x: x % 5 == 0,
            true_monkey=7,
            false_monkey=5,
        ),
        Monkey(
            name=3,
            items=[82, 81, 68, 66, 71, 83, 75, 97],
            operation=lambda x: x + 5,
            test_operation=lambda x: x % 11 == 0,
            true_monkey=5,
            false_monkey=2,
        ),
        Monkey(
            name=4,
            items=[55, 52, 67, 70, 69, 94, 90],
            operation=lambda x: x * x,
            test_operation=lambda x: x % 17 == 0,
            true_monkey=0,
            false_monkey=3,
        ),
        Monkey(
            name=5,
            items=[69, 85, 89, 91],
            operation=lambda x: x + 7,
            test_operation=lambda x: x % 13 == 0,
            true_monkey=1,
            false_monkey=7,
        ),
        Monkey(
            name=6,
            items=[75, 53, 73, 52, 75],
            operation=lambda x: x * 7,
            test_operation=lambda x: x % 2 == 0,
            true_monkey=0,
            false_monkey=4,
        ),
        Monkey(
            name=7,
            items=[94, 60, 79],
            operation=lambda x: x + 2,
            test_operation=lambda x: x % 3 == 0,
            true_monkey=1,
            false_monkey=6,
        ),
    ]

    for _ in range(20):
        for monkey in monkeys:
            monkey.process_items()

    monkey_business_levels = sorted(m.processed_items for m in monkeys)
    return monkey_business_levels[-1] * monkey_business_levels[-2]


# @pytest.mark.solved
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

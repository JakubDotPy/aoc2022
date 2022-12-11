import argparse
import functools
import os.path
import re
from collections import deque
from dataclasses import dataclass
from dataclasses import field
from typing import ClassVar

import matplotlib.pyplot as plt
import networkx as nx
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


@dataclass
class Monkey:
    index: ClassVar[dict[int, 'Monkey']] = dict()
    name: int
    operation: callable
    mod: int
    true_monkey: int
    false_monkey: int
    processed_items: int = 0
    items: deque = field(default_factory=deque)

    def __post_init__(self):
        self._register()

    def _register(self):
        Monkey.index[self.name] = self

    def preprocess(self, worry_level):
        return worry_level // 3

    def test_the_level(self, item):
        item = self.operation(item)
        item = self.preprocess(item)
        monkey_to_go = self.true_monkey if item % self.mod == 0 else self.false_monkey
        Monkey.index[monkey_to_go].items.append(item)

    def process_items(self):
        while self.items:
            self.processed_items += 1
            self.test_the_level(self.items.popleft())

    def __str__(self):
        return f'{self.__class__.__name__}({self.name}, {self.items})'

    __repr__ = __str__


def show_graph(monkeys):
    G = nx.DiGraph()
    G.add_edges_from(
        [(m.name, m.true_monkey) for m in monkeys]
        + [(m.name, m.false_monkey) for m in monkeys]
    )
    nx.draw(G, with_labels=True, font_weight='bold')
    plt.show()


def eval_op(op, amt, x):
    return eval(f'{x}{op}{amt}')


def square_op(x):
    return x * x


def parse_monkeys(s):
    monkeys = []
    for monkey_str in s.split('\n\n'):
        monkey_str = re.sub(r'[,:]', '', monkey_str)
        for line in monkey_str.splitlines():
            match line.strip().split():
                case 'Monkey', name:
                    name = int(name[0])
                case 'Starting', 'items', *items:
                    items = deque(map(int, items))
                case 'Operation', *_, 'old':
                    operation = square_op
                case 'Operation', *_, op, amt:
                    operation = functools.partial(eval_op, op, amt)
                case 'Test', *_, mod:
                    mod = int(mod)
                case 'If', 'true', *_, true_monkey:
                    true_monkey = int(true_monkey)
                case 'If', 'false', *_, false_monkey:
                    false_monkey = int(false_monkey)
                case _:
                    raise AssertionError(f'uncaught case {line}')
        monkeys.append(Monkey(
            name=name,
            items=items,
            operation=operation,
            mod=mod,
            true_monkey=true_monkey,
            false_monkey=false_monkey,
        ))
    return monkeys


def compute(s: str) -> int:
    monkeys = parse_monkeys(s)

    for _ in range(20):
        for monkey in monkeys:
            monkey.process_items()

    monkey_business_levels = sorted(m.processed_items for m in monkeys)
    return monkey_business_levels[-1] * monkey_business_levels[-2]


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

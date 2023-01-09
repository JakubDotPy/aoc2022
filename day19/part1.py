import argparse
import collections
import os.path
import re
from dataclasses import dataclass
from dataclasses import field

import pytest

import support
from support import timing

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

# NOTE: paste test text here
INPUT_S = '''\
Blueprint 1: Each ore robot costs 4 ore. Each clay robot costs 2 ore. Each obsidian robot costs 3 ore and 14 clay. Each geode robot costs 2 ore and 7 obsidian.
Blueprint 2: Each ore robot costs 2 ore. Each clay robot costs 3 ore. Each obsidian robot costs 3 ore and 8 clay. Each geode robot costs 3 ore and 12 obsidian.
'''
EXPECTED = 33

ROBOT_RE = re.compile(r'(\w+)(?= robot).*?(\d+) (\w+)(?: and (\d+) (\w+))?')


@dataclass
class Robot:
    produces: str
    cost: dict[str, int]

    def mine(self):
        return self.produces

    def can_be_created(self, available_ores: dict[str, int]) -> bool:
        return all(
            (costs_ore in available_ores and available_ores[costs_ore] >= costs_value)
            for costs_ore, costs_value in
            self.cost.items()
        )


@dataclass
class Factory:
    robot_blueprints: list[Robot]
    active_robots: list[Robot] = field(init=False)
    available_ores: collections.Counter = field(default_factory=collections.Counter, init=False)
    wall_clock: int = field(default=1, init=False)

    def __post_init__(self):
        self.active_robots = [self.robot_blueprints[0]]  # we always start with the base robot

    def mine(self):
        for robot in self.active_robots:
            self.available_ores[robot.produces] += 1

    def create_robots(self) -> list[Robot]:
        created = []
        for robot in reversed(self.robot_blueprints):
            if robot.can_be_created(self.available_ores):
                created.append(robot)
                for ore, cost in robot.cost.items():
                    self.available_ores[ore] -= cost
        return created


def line_to_robots(line: str) -> list[Robot]:
    matches = ROBOT_RE.findall(line)
    robots = []
    for robot_type, *costs in matches:
        costs_dict = {
            ore: int(amt)
            for amt, ore in support.grouper(costs, 2)
            if ore
        }
        robots.append(Robot(robot_type, costs_dict))
    return robots


def compute_one(line) -> int:
    factory = Factory(robot_blueprints=line_to_robots(line))

    while factory.wall_clock < 24:
        fresh_robots = factory.create_robots()
        factory.mine()
        factory.active_robots.extend(fresh_robots)
        factory.wall_clock += 1

    return factory.available_ores['geodes']


def compute(s: str) -> int:
    quality_levels = {
        blp_n: compute_one(line)
        for blp_n, line in enumerate(s.splitlines(), start=1)
    }

    return sum(k * v for k, v in quality_levels.items())


# @pytest.mark.solved
@pytest.mark.parametrize(
    ('input_s', 'expected'),
    (
            (INPUT_S, EXPECTED),
    ),
)
def test(input_s: str, expected: int) -> None:
    print()  # newline in test output, helps readability
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

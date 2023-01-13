import argparse
import collections
import os.path
import re
from copy import deepcopy
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

    def can_be_created(self, available_ores: dict[str, int]) -> bool:
        return all(
            (costs_ore in available_ores and available_ores[costs_ore] >= costs_value)
            for costs_ore, costs_value in
            self.cost.items()
        )


@dataclass
class State:
    robots: list[Robot]
    ores: collections.Counter = field(default_factory=collections.Counter)


@dataclass
class StateFactory:
    robot_blueprints: list[Robot]

    def _initial_state(self):
        return State(
            robots=[self.robot_blueprints[0]],  # we start with the first robot
            ores=collections.Counter()
        )

    def _mine(self, state: State) -> State:
        new_state = deepcopy(state)
        for robot in new_state.robots:
            new_state.ores[robot.produces] += 1
        return new_state

    def _create_robots(self, state: State) -> list[State]:
        new_states = []
        for robot in self.robot_blueprints:
            if robot.can_be_created(state.ores):
                new_state = deepcopy(state)
                new_state.robots.append(robot)
                for ore, cost in robot.cost.items():
                    new_state.ores[ore] -= cost
                new_states.append(new_state)
        return new_states

    def crate_new_states(self, state: State) -> list[State]:
        return [self._mine(state)] + self._create_robots(state)


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
    factory = StateFactory(robot_blueprints=line_to_robots(line))

    first_state = factory._initial_state()
    second_states = factory.crate_new_states(first_state)

    return 0


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

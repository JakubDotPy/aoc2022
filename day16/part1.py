import argparse
import functools
import os.path
import re

import networkx as nx
import pytest

from support import timing

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

# NOTE: paste test text here
INPUT_S = '''\
Valve AA has flow rate=0; tunnels lead to valves DD, II, BB
Valve BB has flow rate=13; tunnels lead to valves CC, AA
Valve CC has flow rate=2; tunnels lead to valves DD, BB
Valve DD has flow rate=20; tunnels lead to valves CC, AA, EE
Valve EE has flow rate=3; tunnels lead to valves FF, DD
Valve FF has flow rate=0; tunnels lead to valves EE, GG
Valve GG has flow rate=0; tunnels lead to valves FF, HH
Valve HH has flow rate=22; tunnel leads to valve GG
Valve II has flow rate=0; tunnels lead to valves AA, JJ
Valve JJ has flow rate=21; tunnel leads to valve II
'''
EXPECTED = 1651


def make_graph(s):
    G = nx.DiGraph()
    flow_rates = {}
    for line in s.strip().splitlines():
        this, *others = re.findall(r'[A-Z]{2}', line)
        this_flow_rate = int(re.findall(r'\d+', line)[0])
        flow_rates[this] = this_flow_rate
        for o in others:
            G.add_edge(this, o)
    for node, data in G.nodes(data=True):
        data['flow_rate'] = flow_rates[node]

    return G


def released_value(G, valve_solution):
    return sum(G.nodes[valve]['flow_rate'] * time for valve, time in valve_solution.items())


def get_valve_times(distances, valves: set, time_remaining, current_node='AA', valve_to_time=None):
    if valve_to_time is None:
        valve_to_time = {}

    for chosen_valve in valves:
        new_time = time_remaining - distances[current_node][chosen_valve] - 1
        if new_time < 2:
            continue  # we don't have time to open, continue with next option
        new_valve_to_time = valve_to_time | {chosen_valve: new_time}
        # recursively choose others
        yield from get_valve_times(distances, valves - {chosen_valve}, new_time, chosen_valve, new_valve_to_time)
    yield valve_to_time  # the return solution


def compute(s: str) -> int:
    G = make_graph(s)

    nonzero_valves = set(node for node, rate in G.nodes(data='flow_rate') if rate)
    all_distances = nx.floyd_warshall(G)

    # find all bruteforce solutions
    get_released = functools.partial(released_value, G)  # pre-apply the graph
    scores = map(get_released, get_valve_times(all_distances, nonzero_valves, current_node='AA', time_remaining=30))

    return max(scores)


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

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
        data['state'] = False

    return G


def now_released(G):
    return sum(
        data['flow_rate'] * int(data['state'])
        for node, data in G.nodes(data=True)
    )


def closed_valves(G):
    return set(
        node
        for node, data in G.nodes(data=True)
        if not data['state']
    )


def open_valve(G, valve_name):
    G.nodes[valve_name]['state'] = True


def compute(s: str) -> int:
    G = make_graph(s)
    G.closed_valves = functools.partial(closed_valves, G)  # attach new function
    G.now_released = functools.partial(now_released, G)  # attach new function
    G.open_valve = functools.partial(open_valve, G)
    # show_graph(G)

    total_released = 0
    for _ in range(30):  # minutes
        total_released += G.now_released()
        G.open_valve('JJ')

    return total_released


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

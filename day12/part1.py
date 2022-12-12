import argparse
import os.path

import networkx as nx
import pytest

from support import adjacent_4
from support import timing

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

# NOTE: paste test text here
INPUT_S = '''\
Sabqponm
abcryxxl
accszExk
acctuvwj
abdefghi
'''
EXPECTED = 31

Coord = tuple[int, int]
Graph_dict = dict[Coord, int]


def parse_map(s: str) -> tuple[Coord, Coord, Graph_dict]:
    start = None
    end = None
    graph_dict = {}
    for y, line in enumerate(s.splitlines()):
        for x, c in enumerate(line):
            if c == 'S':
                val = 'a'
                start = (x, y)
            elif c == 'E':
                val = 'z'
                end = (x, y)
            else:
                val = c
            graph_dict[(x, y)] = ord(val)
    return start, end, graph_dict


def prepare_graph(graph_dict: Graph_dict) -> nx.Graph:
    G = nx.DiGraph()

    for coord, height in graph_dict.items():
        for adj in adjacent_4(*coord):
            if adj_height := graph_dict.get(adj, 0):
                if adj_height in range(0, height + 2):
                    G.add_edge(coord, adj, cost=adj_height - height)
    return G


def compute(s: str) -> int:
    start, end, graph_dict = parse_map(s)
    G = prepare_graph(graph_dict)
    shortest_path = nx.shortest_path(G, start, end)
    return len(shortest_path) - 1


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

import argparse
import os.path
from dataclasses import dataclass

import pytest

from support import timing

INPUT_TXT = os.path.join(os.path.dirname(__file__), 'input.txt')

# NOTE: paste test text here
INPUT_S = '''\
1
2
-3
3
-2
0
4
'''
EXPECTED = 1623178306


@dataclass
class Node:
    data: int
    next: 'Node' = None
    prev: 'Node' = None

    def __str__(self):
        return str(self.data)


def create_circular_linked_list(numbers):
    # create the first node
    head = Node(data=numbers[0])
    current_node = head

    # create the rest of the nodes and link them together
    for number in numbers[1:]:
        new_node = Node(data=number, prev=current_node)
        current_node.next = new_node
        current_node = new_node

        if number == 0:
            NODE_ZERO = new_node  # NOTE: keep track of the NODE_ZERO

    # link the last node to the first node to create the circular linked list
    current_node.next = head
    head.prev = current_node
    return head, NODE_ZERO


def yield_circular_linked_list(node):
    current_node = node
    yield current_node
    current_node = current_node.next
    while current_node != node:
        yield current_node
        current_node = current_node.next


def print_circular_linked_list(node):
    print('-' * 50)
    print(', '.join(str(n) for n in yield_circular_linked_list(node)))


def find_nth_node(node, n):
    current_node = node
    for i in range(n):
        current_node = current_node.next
    return current_node


def remove_and_insert_nth(node, n):
    # remove the node from the list
    node.prev.next = node.next
    node.next.prev = node.prev
    # insert the node n places forward
    current_node = node
    for i in range(n + 1):
        current_node = current_node.next
    node.prev = current_node.prev
    node.next = current_node
    current_node.prev.next = node
    current_node.prev = node


def get_shift(n, l):
    return n % (l - 1) if n else 0


def compute(s: str) -> int:
    # load into dictionary
    nums = [int(n) * 811589153 for n in s.splitlines()]
    num_len = len(nums)
    head, node_zero = create_circular_linked_list(nums)
    orig_nodes = list(yield_circular_linked_list(head))

    for _ in range(10):
        for node in orig_nodes:
            # print(f'{node!s}')
            shift = get_shift(node.data, num_len)
            remove_and_insert_nth(node, shift)
            # print_circular_linked_list(node_zero)

    return sum((
        find_nth_node(node_zero, 1000 % num_len).data,
        find_nth_node(node_zero, 2000 % num_len).data,
        find_nth_node(node_zero, 3000 % num_len).data,
    ))


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

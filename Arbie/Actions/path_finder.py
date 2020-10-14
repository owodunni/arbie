"""Path finder contains Actions for finding paths between nodes."""

from typing import List

from Arbie.Actions import Action
from Arbie.Variables.graph import TradingGraph, FilteredTradingGraph
from Arbie.Variables.pool import Pool

import networkx as nx


def get_cycles(graph, start_node):
    output_cycles = set()


    def smallest_node(nodes):
        values = list(map(lambda x: hash(x), nodes))
        smallest = min(values)
        i = values.index(smallest)
        return cycle[i]

    def get_hashable_cycle(nodes):
        """cycle as a tuple in a deterministic order."""
        m = smallest_node(nodes)
        mi = cycle.index(m)
        mi_plus_1 = mi + 1 if mi < len(nodes) - 1 else 0
        if hash(nodes[mi-1]) > hash(nodes[mi_plus_1]):
            result = nodes[mi:] + nodes[:mi]
        else:
            result = list(reversed(nodes[:mi_plus_1])) + list(reversed(nodes[mi_plus_1:]))
        return tuple(result)

    all_cycles = list(nx.simple_cycles(graph))
    for cycle in all_cycles:
        if start_node in cycle:
            output_cycles.add(get_hashable_cycle(cycle))

    return [list(i) for i in output_cycles]


class PathFinder(Action):
    """Find all trades from a trading graph."""

    def on_next(self, pools: List[Pool]):
        token = self.store['UoA']
        graph = FilteredTradingGraph(TradingGraph(pools))
        return get_cycles(graph.graph, token)

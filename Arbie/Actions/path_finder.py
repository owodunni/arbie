"""Path finder contains Actions for finding paths between nodes."""

from typing import List

from Arbie import Token, Tokens
from Arbie.Actions import Action
from Arbie.Actions.arbitrage import Trade, TradeOpportunity
from Arbie.Variables.graph import TradingGraph, FilteredTradingGraph
from Arbie.Variables.pool import Pool

import networkx as nx


class Node(object):
    """A edge in a cycle."""

    def __init__(self, token: Token, pool: Pool=None):
        self.token = token
        self.pool = pool

    def __eq__(self, other):
        return self.token == other.token

class Cycle(object):
    """A cycle of nodes with the ratio of the cycle."""

    def __init__(self, nodes: List[Node], ratio):
        self.nodes = nodes
        self.ratio = ratio


class CycleFinder(object):
    """Algorithm for finding cycles and the ratio of the cycle.

Recursive Depth first search is done over all nodes. When reaching the start
node a cycle has been found. While searching also remembers the weights for
taking a cycle. This is useful for sorting the cycles after trade value."""

    def __init__(self, graph: nx.DiGraph, start_node: Token):
        self.graph = graph
        self.start_node = Node(start_node)

    def find_all_cycles(self):
        cycles = []
        self._visit_neighbours(cycles, [self.start_node], self.start_node, 1)
        return cycles

    def _visit_neighbours(self, found_cycles: List[Cycle], visited: List[Node], current_node: Node, ratio_to_current_node):
        for u, next_token, data in self.graph.edges(current_node.token, True):
            ratio_to_next_node = ratio_to_current_node * data['weight']
            next_node = Node(next_token, data['object'])
            self._visit_node(found_cycles, visited, next_node, ratio_to_next_node)

    def _visit_node(self, found_cycles: List[Cycle], visited: Tokens, current_node: Node, ratio_to_current_node):
        if current_node == self.start_node:
            # We have come back to start. Append cycle to result
            found_cycles.append(Cycle(visited + [current_node], ratio_to_current_node))
            return

        if current_node in visited:
            # We have found a cycle back to the current node. Stop
            return

        self._visit_neighbours(found_cycles, visited + [current_node], current_node, ratio_to_current_node)


def create_trade(cycle: Cycle) -> TradeOpportunity:
    trades = []
    start_node = cycle.nodes[0].token
    for node in cycle.nodes[1:]:
        trades.append(Trade(node.pool, start_node, node.token))
        start_node = node.token
    return trades


class PathFinder(Action):
    """Find all trades from a trading graph.

Also find the ratio of taking that trade"""

    def on_next(self, pools: List[Pool]) -> List[TradeOpportunity]:
        token = self.store['UoA']
        graph = FilteredTradingGraph(TradingGraph(pools))
        finder = CycleFinder(graph.graph, token)
        return sorted(finder.find_all_cycles(), key=lambda x: x.ratio)

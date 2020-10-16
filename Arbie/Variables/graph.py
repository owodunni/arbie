"""Graph contains different trading graphs.

To create efficient Arbitrage algorithms we need graphs
suited for modelling relationships between Automated Market Makers.
"""
from typing import List

import networkx as nx

from Arbie.token import Token
from Arbie.Variables.pool import Pool


class Graph(object):
    """Base class for wrapping networkx graph."""

    def __len__(self):
        return len(self.graph)

    def __getitem__(self, key):
        return self.graph[key]

    def get_edges(self):
        return self.graph.edges

    def get_nodes(self):
        return self.graph.nodes

    def _add_edge(self, start_node: Token, end_node: Token, weight, pool):
        if start_node is end_node:
            return

        self.graph.add_edge(start_node, end_node, weight=weight, object=pool)


class TradingGraph(Graph):
    """A trading graph.

    Represents each possible trading path between all tokens.
    """

    def __init__(self, pools: List[Pool]):
        self.graph = nx.MultiDiGraph()
        self._create_graph(pools)

    def _create_graph(self, pools: List[Pool]):
        """Create graph from a set of Pools."""
        for pool in pools:
            self._add_nodes(pool.tokens)

        for pool in pools:  # noqa: WPS440,WPS441
            self._add_edges(pool)  # noqa: WPS441

    def _add_nodes(self, tokens: List[Token]):
        self.graph.add_nodes_from(tokens)

    def _add_edges(self, pool: Pool):

        for start_node in pool.tokens:
            for end_node in pool.tokens:
                weight = pool.spot_price(start_node, end_node)
                self._add_edge(start_node, end_node, weight, pool)


class FilteredTradingGraph(Graph):
    """A Filtered Trading Graph.

    Represents the best trades between each token pair.
    The best trade is the one that has the highest ratio.
    """

    weight_key = 'weight'
    pool_key = 'object'

    def __init__(self, graph: TradingGraph):
        self.graph = nx.DiGraph()
        self._filter_graph(graph)

    def _filter_graph(self, graph: TradingGraph):
        self.graph.add_nodes_from(graph.get_nodes())

        for (start_node, end_node, data) in graph.get_edges().data():

            edge_data = self.graph.get_edge_data(start_node, end_node)

            if edge_data is not None:
                if edge_data[self.weight_key] < data[self.weight_key]:
                    # The most valuable path is already added
                    continue

            self._add_edge(
                start_node,
                end_node,
                data[self.weight_key],
                data[self.pool_key])

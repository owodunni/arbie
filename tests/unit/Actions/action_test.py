"""Unittest for the action structure."""

import pytest

from Arbie import Token
from Arbie.Actions.action import Store
from Arbie.Actions.amm import Amm
from Arbie.Actions.path_finder import GraphMaker, PathFinder, TradingGraph

eth = Token('eth')  # 300
dai = Token('dai')  # 1
btc = Token('btc')  # 10000
yam = Token('yam')  # 0.1

small = 10
medium = 100
large = 1000


pools = [
    Amm(
        [eth, dai, yam],
        [small / 300.0, small / 1.0, small / 0.1],
        [1 / 3.0, 1 / 3.0, 1 / 3.0], 0.004),
    Amm(
        [eth, btc],
        [large / 300.0, large / 10000],
        [5 / 6, 1 / 6], 0.01),
    Amm(
        [eth, dai, btc],
        [medium / 300.0, medium / 1.0, medium / 10000],
        [1 / 2.0, 1 / 4.0, 1 / 4.0], 0.004),
    Amm(
        [dai, yam],
        [small / 1.0, small / 0.1],
        [1 / 2.0, 1 / 2.0], 0.001),
]


class TestPathFinder(object):

    @pytest.fixture
    def store(self) -> Store:
        return Store()

    @pytest.fixture
    def graph(self, store: Store) -> TradingGraph:
        graph_maker = GraphMaker(store)
        return graph_maker.on_next(pools)

    def test_create_graph(self, graph: TradingGraph):
        assert len(graph.nodes) == 4

        eth_node = graph.nodes[eth]
        assert len(eth_node.paths) == 3

        yam_node = graph.nodes[yam]
        assert len(yam_node.paths) == 2

    def test_find_neighbours(self, graph: TradingGraph):
        neighbours = graph.get_neighbours(graph.nodes[eth])

        assert len(neighbours) == 3

    def test_find_trades(self, graph: TradingGraph, store: Store):
        path_finder = PathFinder(store)
        trades = path_finder.on_next(graph)

        assert len(trades) == 4  # Bogus test for now

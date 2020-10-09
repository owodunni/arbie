"""Unittest for the action structure."""

import pytest

from Arbie.Actions.action import Store
from Arbie.Actions.path_finder import GraphMaker, PathFinder

from Arbie.Actions.amm import Amm
from Arbie import Token

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
        [small/300.0, small/1.0, small/0.1],
        [1/3.0, 1/3.0, 1/3.0], 0.004),
    Amm(
        [eth, btc],
        [large/300.0, large/10000],
        [5/6, 1/6], 0.01),
    Amm(
        [eth, dai, btc],
        [medium/300.0,  medium/1.0, medium/10000],
        [1/2.0, 1/4.0, 1/4.0], 0.004),
    Amm(
        [dai, yam],
        [small/1.0, small/0.1],
        [1/2.0, 1/2.0], 0.001)]

class TestPathFinder(object):


    def test_create_graph(self):
        store = Store()
        graph_maker = GraphMaker(store)
        graph = graph_maker.on_next(pools)
        assert len(graph.nodes) == 4

        eth_node = graph.nodes[eth]
        assert len(eth_node.paths) == 3

        yam_node = graph.nodes[yam]
        assert len(yam_node.paths) == 2

    def test_find_neighbours(self):

        store = Store()
        graph_maker = GraphMaker(store)
        graph = graph_maker.on_next(pools)

        neighbours = graph.get_neighbours(graph.nodes[eth])

        assert len(neighbours) == 3

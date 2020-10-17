"""Unittest for the action structure."""
from Arbie.Variables.graph import FilteredTradingGraph, TradingGraph


def test_create(pools):
    graph = TradingGraph(pools)
    assert len(graph) == 4
    assert len(graph.get_edges()) == 16


def test_create_filter(pools):
    f_graph = FilteredTradingGraph(TradingGraph(pools), 0)
    assert len(f_graph) == 4
    assert len(f_graph.get_edges()) == 10

"""Path finder contains Actions for finding paths between nodes."""

from typing import List

from Arbie.Actions import Action
from Arbie.Variables.graph import TradingGraph, FilteredTradingGraph
from Arbie.Variables.pool import Pool


class PathFinder(Action):
    """Find all trades from a trading graph."""

    def on_next(self, pools: List[Pool]):
        graph = FilteredTradingGraph(TradingGraph(pools))


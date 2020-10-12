"""Path finder contains Actions for finding paths between nodes."""

from Arbie.Actions import Action
from Arbie.Variables.graph import TradingGraph


class PathFinder(Action):
    """Find all trades from a trading graph."""

    def on_next(self, graph: TradingGraph):
        raise NotImplementedError('Not implemented.')

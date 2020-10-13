"""Path finder contains Actions for finding paths between nodes."""

from typing import List

from Arbie.Actions import Action
from Arbie.Variables.graph import TradingGraph, FilteredTradingGraph
from Arbie.Variables.pool import Pool

import networkx as nx



def find_all_cycles(G, source, cycle_length_limit=None):
    """forked from networkx dfs_edges function. Assumes nodes are integers, or at least
    types which work with min() and > ."""
    nodes = [source]
    # extra variables for cycle detection:
    cycle_stack = []
    output_cycles = set()

    def smallest_node(cycle):
        values = list(map(lambda x: hash(x), cycle))
        smallest = min(values)
        i = values.index(smallest)
        return cycle[i]

    def get_hashable_cycle(cycle):
        """cycle as a tuple in a deterministic order."""
        m = smallest_node(cycle)
        mi = cycle.index(m)
        mi_plus_1 = mi + 1 if mi < len(cycle) - 1 else 0
        if hash(cycle[mi-1]) > hash(cycle[mi_plus_1]):
            result = cycle[mi:] + cycle[:mi]
        else:
            result = list(reversed(cycle[:mi_plus_1])) + list(reversed(cycle[mi_plus_1:]))
        return tuple(result)
    
    for start in nodes:
        if start in cycle_stack:
            continue
        cycle_stack.append(start)
        
        stack = [(start,iter(G[start]))]
        while stack:
            parent,children = stack[-1]
            try:
                child = next(children)
                
                if child not in cycle_stack:
                    cycle_stack.append(child)
                    stack.append((child,iter(G[child])))
                else:
                    i = cycle_stack.index(child)
                    if i < len(cycle_stack) - 1:
                        output_cycles.add(get_hashable_cycle(cycle_stack[i:]))
                
            except StopIteration:
                stack.pop()
                cycle_stack.pop()
    
    return [list(i) for i in output_cycles]


class PathFinder(Action):
    """Find all trades from a trading graph."""

    def on_next(self, pools: List[Pool]):

        token = self.store['UoA']
        graph = FilteredTradingGraph(TradingGraph(pools))
        return list(find_all_cycles(graph.graph, source=token))

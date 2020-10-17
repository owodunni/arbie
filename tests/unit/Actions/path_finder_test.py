"""Unittest for path finding algorithms."""

import pytest

from Arbie.Actions import Store
from Arbie.Actions.arbitrage import find_arbitrage
from Arbie.Actions.path_finder import PathFinder, create_trade


@pytest.fixture
def path_finder(eth):
    store = Store()
    store.add('UoA', eth)
    return PathFinder(store)


class TestpathFinder(object):

    def test_on_next(self, path_finder, pools):
        cycles = path_finder.on_next(pools)
        assert len(cycles) == 9

    def test_profit_of_paths(self, path_finder, pools):
        cycles = path_finder.on_next(pools)
        trade = create_trade(cycles[0])
        balance = find_arbitrage(trade)
        assert balance.value == pytest.approx(4.05461516215215)

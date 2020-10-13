"""Unittest for path finding algorithms."""

import pytest

from Arbie.Actions import Store
from Arbie.Actions.path_finder import PathFinder


@pytest.fixture
def path_finder(eth):
    store = Store()
    store.add('UoA', eth)
    return PathFinder(store)

class TestpathFinder(object):

    def test_on_next(self, path_finder, pools):
        cycles = path_finder.on_next(pools)
        assert len(cycles) == 6

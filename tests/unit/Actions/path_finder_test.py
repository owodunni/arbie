"""Unittests of PathFinder."""
import pytest
import yaml

from Arbie.Actions import Store
from Arbie.arbie import App


@pytest.fixture
def config_file():
    return """
    actions:
        PathFinder:
            input:
                unit_of_account: eth
                min_liquidity: 4
            output:
                cycles: found_cycles
        Arbitrage:
    """


@pytest.fixture
def store(pools, eth) -> Store:
    store = Store()
    store.add("pools", pools)
    store.add("eth", eth)
    return store


class TestPathFinder(object):
    def test_run(self, store, config_file):
        config = yaml.safe_load(config_file)
        app = App(config, store)
        assert len(app.action_tree.actions) == 2
        app.run()
        assert len(store["found_cycles"]) == 5
        trades = app.store["filtered_trades"]
        assert trades[0].profit == pytest.approx(1.47700668)

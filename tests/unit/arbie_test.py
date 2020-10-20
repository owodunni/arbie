"""Unittest of app."""

import pytest
import yaml

from Arbie.Actions import Store
from Arbie.Actions.arbitrage import find_arbitrage
from Arbie.Actions.path_finder import create_trade
from Arbie.arbie import App


@pytest.fixture
def store(pools, eth) -> Store:
    store = Store()
    store.add('pools', pools)
    store.add('eth', eth)
    return store


@pytest.fixture
def app(store, config_file):
    config = yaml.safe_load(config_file)
    app = App(config, store)
    assert len(app.action_tree.actions) == 1
    app.run()
    assert len(store['found_cycles']) == 5
    return app


def test_profit_of_paths(app: App):
    cycles = app.store['found_cycles']
    trade = create_trade(cycles[0])
    balance = find_arbitrage(trade)
    assert balance.value == pytest.approx(3.35866448326422)

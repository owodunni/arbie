"""Unittests of PathFinder."""
import asyncio
from unittest.mock import MagicMock

import pytest
import yaml

from Arbie import SettingsParser
from Arbie.Actions import Store
from Arbie.app import App


@pytest.fixture
def config_file():
    return """
    action_tree:
        actions:
            PathFinder:
                input:
                    weth: eth
                    min_liquidity: 4
                output:
                    cycles: found_cycles
            Arbitrage:
    """


@pytest.fixture
def store(pools, eth) -> Store:
    store = Store()
    store.add("pools", pools)
    future = asyncio.Future()
    future.set_result(eth)
    weth_mock = MagicMock()
    weth_mock.create_token.return_value = future
    store.add("eth", weth_mock)
    return store


class TestPathFinder(object):
    @pytest.mark.asyncio
    async def test_run(self, store, config_file, mocker):
        mocker.patch.object(SettingsParser, "setup_store", return_value=store)

        config = yaml.safe_load(config_file)
        app = App(config)
        assert len(app.action_tree.actions) == 2
        await app.run()
        assert len(store["found_cycles"]) == 5
        trades = app.store["filtered_trades"]
        assert trades[0].profit == pytest.approx(1.354642)

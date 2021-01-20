"""Systemtests of app."""

import asyncio

import pytest
import yaml
from pytest_mock.plugin import MockerFixture

from Arbie.app import App
from Arbie.Contracts import GenericToken
from Arbie.Services import Coingecko
from Arbie.Variables import BigNumber


class Result(object):
    pool_finder_pools = "PoolFinder.1.pools"
    pool_finder_tokens = "PoolFinder.1.tokens"
    whitelist_addresses = "Whitelist.1.addresses"
    pool_updater_pools = "PoolUpdater.1.pools"
    arbitrage_filtered_trades = "Arbitrage.1.filtered_trades"
    trader_profit = "Trader.1.profit"


pytestmark = pytest.mark.asyncio


async def wait_and_stop(tree, key):
    while True:
        if key in tree.store.state:
            tree.stop()
            return
        await asyncio.sleep(0.1)


async def wait_and_run(app):
    await asyncio.sleep(0.2)
    await app.run()


def replace_base_conf(config, base_config):
    split_conf = config.split("action_tree:")
    return f"""
{base_config}

action_tree:
{split_conf[1]}
            """


def setup_config(path, base_config):
    with open(f"Brig/{path}", "r") as f:
        return replace_base_conf(f.read(), base_config)


class TestApp(object):
    @pytest.fixture
    def base_config(
        self,
        web3_server,
        redis_server,
        weth,
        pool_factory,
        pair_factory,
        router,
        deploy_address,
    ):
        return f"""
store:
    address: {redis_server}
web3:
    address: {web3_server}
variables:
    weth:
        type: Weth
        address: '{weth.get_address()}'
    uniswap_factory:
        type: UniswapFactory
        address: '{pair_factory.get_address()}'
    balancer_factory:
        type: BalancerFactory
        address: '{pool_factory.get_address()}'
    router:
        type: UniswapV2Router
        address: '{router.get_address()}'
        """  # noqa: WPS221

    @pytest.fixture
    def base_config_with_account(self, base_config):
        split_conf = base_config.split("variables:")
        return f"""
{split_conf[0]}
account:
    path: Brig/Trader/test_account.json
variables:
{split_conf[1]}
"""

    @pytest.fixture
    def pool_finder_config(self, base_config):
        conf = setup_config("PoolFinder/pool_finder.yml", base_config)
        split_conf = conf.split("input:")
        return f"""
{split_conf[0]}
      input:
        balancer_start: 0
{split_conf[1]}
"""

    @pytest.fixture
    def path_finder_config(self, base_config):
        return setup_config("PathFinder/path_finder.yml", base_config)

    @pytest.fixture
    def pool_updater_config(self, base_config):
        return setup_config("PoolUpdater/pool_updater.yml", base_config)

    @pytest.fixture
    def trader_config(self, base_config_with_account):
        return setup_config("Trader/trader.yml", base_config_with_account)

    @pytest.fixture
    def pool_finder(self, pool_finder_config, mocker: MockerFixture, whitelist):
        mocker.patch.object(Coingecko, "coins", return_value=whitelist)

        config = yaml.safe_load(pool_finder_config)
        app = App(config)
        assert len(app.action_tree.actions) == 2
        yield app
        app.store.delete(Result.pool_finder_pools)
        app.store.delete(Result.pool_finder_tokens)
        app.store.delete(Result.whitelist_addresses)

    @pytest.fixture
    def pool_updater(self, pool_updater_config):
        config = yaml.safe_load(pool_updater_config)
        app = App(config)
        yield app
        app.store.delete(Result.pool_updater_pools)

    @pytest.fixture
    def path_finder(self, path_finder_config):
        config = yaml.safe_load(path_finder_config)
        app = App(config)
        yield app
        app.store.delete(Result.arbitrage_filtered_trades)

    @pytest.fixture
    def trader(self, trader_config, weth: GenericToken, dummy_account):
        weth.transfer(dummy_account.address, BigNumber(4))
        config = yaml.safe_load(trader_config)
        app = App(config)
        yield app
        app.store.delete(Result.trader_profit)

    @pytest.mark.slow
    async def test_full_pipeline(self, pool_finder, pool_updater, path_finder, trader):
        await asyncio.gather(
            wait_and_run(pool_finder),
            pool_updater.run(),
            wait_and_stop(pool_updater, Result.pool_updater_pools),
            path_finder.run(),
            wait_and_stop(path_finder, Result.arbitrage_filtered_trades),
            trader.run(),
            wait_and_stop(trader, Result.trader_profit),
        )

        assert len(pool_finder.store.get(Result.pool_finder_pools)) == 4
        assert len(pool_finder.store.get(Result.pool_finder_tokens)) == 3
        assert len(pool_finder.store.get(Result.whitelist_addresses)) == 4
        assert len(pool_updater.store.get(Result.pool_updater_pools)) == 4
        assert len(path_finder.store.get(Result.arbitrage_filtered_trades)) == 1
        assert trader.store.get(Result.trader_profit) > 3.278

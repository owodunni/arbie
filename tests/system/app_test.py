"""Systemtests of app."""

import asyncio

import pytest
import yaml

from Arbie.app import App


class Result(object):
    pools = "arbie.1.pools"
    trades = "filtered_trades"
    profit = "profit"


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


class TestApp(object):
    @pytest.fixture
    def base_config(
        self,
        web3_server,
        redis_server,
        weth,
        pool_factory,
        pair_factory,
        arbie,
        deploy_address,
    ):
        return f"""
        store:
            address: {redis_server}
        web3:
            address: {web3_server}

        variables:
            weth:
                type: Token
                address: '{weth.get_address()}'
            uniswap_factory:
                type: UniswapFactory
                address: '{pair_factory.get_address()}'
            balancer_factory:
                type: BalancerFactory
                address: '{pool_factory.get_address()}'
            arbie:
                type: Arbie
                address: '{arbie.get_address()}'
            trader_address:
                type: str
                value: '{deploy_address}'

        """  # noqa: WPS221

    @pytest.fixture
    def pool_config(self, base_config):
        return (
            base_config
            + f"""
        action_tree:
            actions:
                PoolFinder:
                    input:
                        balancer_start: 0
                    output:
                        pools: {Result.pools}
        """
        )

    @pytest.fixture
    def trade_config(self, base_config):
        return (
            base_config
            + f"""
        action_tree:
            event:
                {Result.pools}
            actions:
                PathFinder:
                    input:
                        pools:  {Result.pools}
                        weth: weth
                    output:
                        trades: trades
                Arbitrage:
                    input:
                        trades: trades
                    output:
        """
        )

    @pytest.fixture
    def app(self, pool_config):
        config = yaml.safe_load(pool_config)
        app = App(config)
        assert len(app.action_tree.actions) == 1
        yield app
        app.store.delete(Result.pools)

    @pytest.mark.slow
    async def test_run(self, app):
        await app.run()
        assert len(app.store.get(Result.pools)) == 7
        tokens = app.store.get("all_tokens")
        assert len(tokens) == 3

    @pytest.mark.slow
    async def test_full_pipeline(self, app, trade_config):
        trade_finder = App(yaml.safe_load(trade_config))
        await asyncio.gather(
            wait_and_run(app),
            trade_finder.run(),
            wait_and_stop(trade_finder, Result.trades),
        )
        assert len(trade_finder.store.get(Result.trades)) == 4

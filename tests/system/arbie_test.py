"""Systemtests of app."""

import asyncio

import pytest
import yaml

from Arbie.arbie import App
from Arbie.Contracts import BalancerFactory, ContractFactory, UniswapFactory
from Arbie.Contracts.tokens import GenericToken
from Arbie.Variables import BigNumber

small = 10e4
medium = 10e6
large = 10e8


class Result(object):
    pools = "arbie.1.pools"
    trades = "filtered_trades"


@pytest.fixture
async def pool_factory(
    dai: GenericToken,
    weth: GenericToken,
    yam: GenericToken,
    wbtc: GenericToken,
    bad,
    w3,
    deploy_address,
) -> BalancerFactory:
    factory = ContractFactory(w3, BalancerFactory).deploy_contract(deploy_address)

    f1 = factory.setup_pool(
        [weth, dai, yam],
        [5, 5, 5],
        [
            BigNumber(small / 303.0),
            BigNumber(small / 0.9),
            BigNumber(small / 0.1),
        ],
    )
    f2 = factory.setup_pool(
        [bad, dai],
        [5, 5],
        [
            BigNumber(100),
            BigNumber(small / 0.9),
        ],
        approve_owner=False,
    )
    factory.new_pool()

    f3 = factory.setup_pool(
        [weth, wbtc],
        [5, 1],
        [
            BigNumber(5 * large / 301.0),
            BigNumber(large / 10000),
        ],  # noqa: WPS221
    )
    f4 = factory.setup_pool(
        [weth, dai, wbtc],
        [2, 1, 1],
        [
            BigNumber(2 * medium / 301.0),
            BigNumber(medium / 1.1),
            BigNumber(large / 10020),
        ],
    )

    await asyncio.gather(f1, f2, f3, f4)

    return factory


@pytest.fixture
async def pair_factory(
    dai: GenericToken,
    weth: GenericToken,
    yam: GenericToken,
    wbtc: GenericToken,
    bad,
    w3,
    deploy_address,
) -> UniswapFactory:
    factory = ContractFactory(w3, UniswapFactory).deploy_contract(
        deploy_address, deploy_address
    )

    factory.setup_pair(
        [dai, yam],
        [
            BigNumber(small / 1.1),
            BigNumber(small / 0.1),
        ],  # noqa: WPS221
    )
    factory.setup_pair(
        [weth, dai],
        [BigNumber(large / 300), BigNumber(large)],
    )
    factory.setup_pair(
        [weth, wbtc],
        [
            BigNumber(large / 300),
            BigNumber(large / 10000),
        ],
    )
    factory.create_pair(weth, bad)
    factory.create_pair(weth, yam)
    return factory


pytestmark = pytest.mark.asyncio


async def wait_and_stop(tree, key):
    while True:
        if key in tree.store.state:
            tree.stop()
            return
        else:
            await asyncio.sleep(0.1)


async def wait_and_run(app):
    await asyncio.sleep(0.2)
    await app.run()


class TestApp(object):
    @pytest.fixture
    def base_config(self, web3_server, redis_server, weth, pool_factory, pair_factory):
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
        """

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
        assert len(app.store.state.keys()) == 4
        yield app
        app.store.delete(Result.pools)

    @pytest.mark.slow
    async def test_run(self, app):
        await app.run()
        assert len(app.store.state.keys()) == 5
        assert len(app.store.get(Result.pools)) == 6
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
        assert len(trade_finder.store.get(Result.trades)) == 3

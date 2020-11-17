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


def to_big_number(token: GenericToken, amount) -> BigNumber:
    return BigNumber(amount, token.decimals())


class Result(object):
    pools = "arbie.1.pools"


@pytest.fixture
def pool_factory(
    dai: GenericToken,
    weth: GenericToken,
    yam: GenericToken,
    wbtc: GenericToken,
    bad,
    w3,
    deploy_address,
) -> BalancerFactory:
    factory = ContractFactory(w3, BalancerFactory).deploy_contract(deploy_address)

    factory.setup_pool(
        [weth, dai, yam],
        [5, 5, 5],
        [
            to_big_number(weth, small / 303.0),
            to_big_number(dai, small / 0.9),
            to_big_number(yam, small / 0.1),
        ],
    )
    factory.setup_pool(
        [bad, dai],
        [5, 5, 5],
        [
            BigNumber(100),
            to_big_number(dai, small / 0.9),
        ],
        approve_owner=False,
    )
    factory.new_pool()

    factory.setup_pool(
        [weth, wbtc],
        [5, 1],
        [
            to_big_number(weth, 5 * large / 301.0),
            to_big_number(wbtc, large / 10000),
        ],  # noqa: WPS221
    )
    factory.setup_pool(
        [weth, dai, wbtc],
        [2, 1, 1],
        [
            to_big_number(weth, 2 * medium / 301.0),
            to_big_number(dai, medium / 1.1),
            to_big_number(wbtc, large / 10020),
        ],
    )

    return factory


@pytest.fixture
def pair_factory(
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
            to_big_number(dai, small / 1.1),
            to_big_number(yam, small / 0.1),
        ],  # noqa: WPS221
    )
    factory.setup_pair(
        [weth, dai], [to_big_number(weth, large / 300), to_big_number(dai, large)]
    )
    factory.setup_pair(
        [weth, wbtc],
        [to_big_number(weth, large / 300), to_big_number(wbtc, large / 10000)],
    )
    factory.create_pair(weth, bad)
    factory.create_pair(weth, yam)
    return factory


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
                redis: {Result.pools}
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

    async def wait_until_result(self, app, result):
        while True:
            try:
                app.store.get(result)
            except Exception:
                await asyncio.sleep(0.1)
                continue
            app.stop()
            return

    @pytest.fixture()
    def app(self, pool_config):
        config = yaml.safe_load(pool_config)
        app = App(config)
        assert len(app.action_tree.actions) == 1
        assert len(app.store.state.keys()) == 4
        yield app
        app.store.delete(Result.pools)

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_run(self, app):
        await app.run()
        assert len(app.store.state.keys()) == 5
        assert len(app.store.get(Result.pools)) == 6
        tokens = app.store.get("all_tokens")
        assert len(tokens) == 3

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_full_pipeline(self, pool_config, trade_config):
        # pool_finder = App(yaml.safe_load(pool_config))
        # trade_finder = App(yaml.safe_load(trade_config))
        # await asyncio.gather(
        #    pool_finder.run(),
        #    trade_finder.run(),
        #    self.wait_until_result(trade_finder, "filtered_trades"),
        # )
        raise AssertionError()
        # assert len(trade_finder.store.get("filtered_trades")) == 3

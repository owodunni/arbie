"""Systemtests of app."""

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
        deploy_address, deploy_address.value
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


@pytest.fixture
def base_config(web3_server, redis_server, weth, pool_factory, pair_factory):
    return f"""

    web3_address: {web3_server}
    redis_address: {redis_server}
    weth_address: '{weth.get_address()}'
    uniswap_address: '{pair_factory.get_address()}'
    balancer_address: '{pool_factory.get_address()}'
    """


@pytest.fixture
def config_file(base_config):
    return (
        base_config
        + """
    actions:
        PoolFinder:
            input:
                balancer_start: 0
    """
    )


@pytest.fixture
def full_config(base_config):
    return (
        base_config
        + """
    actions:
        PoolFinder:
            input:
                balancer_start: 0
            output:
                pools: arbie.version.pools
                tokens: tokens
        PathFinder:
            input:
                pools: arbie.version.pools
                unit_of_account: weth
            output:
                trades: trades
        Arbitrage:
            input:
                trades: trades
            output:

    """
    )


class TestApp(object):
    @pytest.fixture()
    def app(self, config_file):
        config = yaml.safe_load(config_file)
        app = App(config)
        assert len(app.action_tree.actions) == 1
        assert len(app.store.state.keys()) == 3
        return app

    @pytest.mark.slow
    def test_run(self, app):
        app.run()
        assert len(app.store.state.keys()) == 5
        assert len(app.store.get("all_pools")) == 6
        tokens = app.store.get("all_tokens")
        assert len(tokens) == 3

    @pytest.mark.slow
    def test_full_pipeline(self, full_config):
        config = yaml.safe_load(full_config)
        app = App(config)
        app.run()

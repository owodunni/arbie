"""Unittest of app."""

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
        [weth, wbtc],
        [5, 1],
        [to_big_number(weth, large / 301.0), to_big_number(wbtc, large / 10000)],
    )
    factory.setup_pool(
        [weth, dai, wbtc],
        [2, 1, 1],
        [
            to_big_number(weth, medium / 301.0),
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
    return factory


@pytest.fixture
def config_file(web3_server, weth, pool_factory, pair_factory):
    return f"""

    web3_address: {web3_server}
    weth_address: '{weth.get_address()}'
    uniswap_address: '{pair_factory.get_address()}'
    balancer_address: '{pool_factory.get_address()}'

    actions:
        PoolFinder:
    """


class TestApp(object):
    @pytest.fixture()
    def app(self, config_file):
        config = yaml.safe_load(config_file)
        app = App(config)
        assert len(app.action_tree.actions) == 1
        assert len(app.store.state.keys()) == 3
        return app

    def test_run(self, app):
        app.run()
        assert len(app.store.state.keys()) == 5
        assert len(app.store.get('all_pools')) == 6
        assert len(app.store.get('all_tokens')) == 3

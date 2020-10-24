"""Unittest of app."""

import pytest
import yaml

from Arbie.arbie import App
from Arbie.Contracts import BalancerFactory, ContractFactory, UniswapFactory


@pytest.fixture
def uni_factory(deploy_address, w3) -> UniswapFactory:
    return ContractFactory(w3, UniswapFactory).deploy_contract(
        deploy_address, deploy_address.value
    )


@pytest.fixture
def bal_factory(deploy_address, w3) -> BalancerFactory:
    return ContractFactory(w3, BalancerFactory).deploy_contract(
        deploy_address, deploy_address.value
    )


@pytest.fixture
def config_file(web3_server):
    return f"""

    web3_address: {web3_server}

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
def app(store, config_file):
    config = yaml.safe_load(config_file)
    app = App(config, store)
    assert len(app.action_tree.actions) == 2

"""Help module for web3 tests."""

import pytest
from web3 import Web3

from Arbie.Contracts.contract import ContractFactory
from Arbie.Contracts.tokens import BadERC20Token, GenericToken
from Arbie.Variables import Address, BigNumber


@pytest.fixture
def web3_server(request):
    return request.config.getoption("--web3_server")


@pytest.fixture
def redis_server(request):
    return request.config.getoption("--redis_server")


@pytest.fixture
def w3(web3_server):
    return Web3(Web3.HTTPProvider(web3_server))


@pytest.fixture
def deploy_address(w3) -> Address:
    deploy_address = w3.eth.accounts[0]
    return Address(deploy_address)


@pytest.fixture
def dummy_address(w3) -> Address:
    address = w3.eth.accounts[1]
    return Address(address)


@pytest.fixture
def token_factory(w3) -> ContractFactory:
    return ContractFactory(w3, GenericToken)


large_number = BigNumber(10e14)


@pytest.fixture
def dai(deploy_address, token_factory) -> GenericToken:
    token = token_factory.deploy_contract(
        deploy_address, "Dai", "DAI", large_number.value
    )
    token.approve_owner()
    return token


@pytest.fixture
def weth(deploy_address, token_factory) -> GenericToken:
    token = token_factory.deploy_contract(
        deploy_address, "Weth", "WETH", large_number.value
    )
    token.approve_owner()
    return token


@pytest.fixture
def yam(deploy_address, token_factory) -> GenericToken:
    token = token_factory.deploy_contract(
        deploy_address, "yam", "YAM", large_number.value
    )
    token.approve_owner()
    return token


@pytest.fixture
def wbtc(deploy_address, token_factory) -> GenericToken:
    token = token_factory.deploy_contract(
        deploy_address, "Wbtc", "WBTC", large_number.value
    )
    token.approve_owner()
    return token


@pytest.fixture
def bad(deploy_address, w3) -> BadERC20Token:
    return ContractFactory(w3, BadERC20Token).deploy_contract(
        deploy_address, large_number.value
    )

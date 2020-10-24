"""Help module for web3 tests."""
from typing import List

import pytest
from web3 import Web3

from Arbie.Contracts.contract import ContractFactory
from Arbie.Contracts.tokens import GenericToken
from Arbie.Variables import Address


@pytest.fixture
def web3_server(request):
    return request.config.getoption("--web3_server")


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


@pytest.fixture
def dai(deploy_address, token_factory) -> GenericToken:
    token = token_factory.deploy_contract(deploy_address, 10000, "Dai", 18, "DAI")
    token.approve_owner()
    return token


@pytest.fixture
def weth(deploy_address, token_factory) -> GenericToken:
    token = token_factory.deploy_contract(deploy_address, 10000, "Weth", 18, "WETH")
    token.approve_owner()
    return token


@pytest.fixture
def yam(deploy_address, token_factory) -> GenericToken:
    token = token_factory.deploy_contract(deploy_address, 1000000, "yam", 10, "YAM")
    token.approve_owner()
    return token


@pytest.fixture
def wbtc(deploy_address, token_factory) -> GenericToken:
    token = token_factory.deploy_contract(deploy_address, 10000, "Wbtc", 18, "WBTC")
    token.approve_owner()
    return token


@pytest.fixture
def tokens(dai, weth, yam, wbtc) -> List[GenericToken]:
    return [dai, weth, yam, wbtc]

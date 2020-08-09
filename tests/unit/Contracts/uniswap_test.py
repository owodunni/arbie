"""Test uniswap contracts."""

import pytest
from eth_tester import PyEVMBackend
from web3 import EthereumTesterProvider, Web3

from Arbie.Contracts import Address
from Arbie.Contracts.contract import ContractFactory
from Arbie.Contracts.tokens import GenericToken
from Arbie.Contracts.uniswap import Factory


@pytest.fixture
def tester_provider():
    return EthereumTesterProvider(PyEVMBackend())


@pytest.fixture
def eth_tester(tester_provider):
    return tester_provider.ethereum_tester


@pytest.fixture
def w3(tester_provider):
    return Web3(tester_provider)


@pytest.fixture
def deploy_address(eth_tester) -> Address:
    deploy_address = eth_tester.get_accounts()[0]
    return Address(deploy_address)


@pytest.fixture
def factory(deploy_address, w3) -> Factory:
    return ContractFactory(w3, Factory, Factory.name).deploy_contract(deploy_address, deploy_address.value)


@pytest.fixture
def token_factory(w3) -> ContractFactory:
    return ContractFactory(w3, GenericToken, GenericToken.name)


@pytest.fixture
def dai(deploy_address, token_factory) -> GenericToken:
    return token_factory.deploy_contract(deploy_address, 100, 'Dai', 18, 'DAI')  # noqa: WPS432


@pytest.fixture
def weth(deploy_address, token_factory) -> GenericToken:
    return token_factory.deploy_contract(deploy_address, 100, 'Weth', 18, 'WETH')  # noqa: WPS432


def test_get_all_pairs_length(factory):
    assert factory.all_pairs_length() == 0


def test_create_pair(factory, dai, weth):
    factory.create_pair(dai, weth)
    assert factory.all_pairs_length() == 1


def test_get_all_pairs(factory, dai, weth):
    factory.create_pair(dai, weth)
    assert len(factory.all_pairs()) == 1

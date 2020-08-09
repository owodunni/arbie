"""Test uniswap contracts."""

import pytest

from Arbie.Contracts import Address, Network
from Arbie.Contracts.uniswap import Factory, Pair
from Arbie.Contracts.contract import read_abi, read_bytecode, Id
from Arbie.Contracts.tokens import GenericToken

from web3 import (
    EthereumTesterProvider,
    Web3,
)

from eth_tester import PyEVMBackend


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
    return Factory.create(w3, deploy_address)

@pytest.fixture
def dai(deploy_address, w3) -> GenericToken:
    return GenericToken.create(w3, deploy_address, 100, 'Dai', 18, 'DAI')

@pytest.fixture
def weth(deploy_address, w3) -> GenericToken:
    return GenericToken.create(w3, deploy_address, 100, 'Weth', 18, 'WETH')

def test_get_all_pairs_length(factory):
    assert factory.all_pairs_length() == 0

def test_create_pair(factory, dai, weth):
    factory.create_pair(dai, weth)
    assert factory.all_pairs_length() == 1

#def test_get_all_pairs(factory, dai, weth):
#    factory.create_pair(dai, weth)
#    assert len(factory.all_pairs()) == 1

#class TestFactory:

    #def test_init(self):
    #    fac = Factory(w3, network=Network.mainnet)
    #    assert fac.address =='0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f'

    #def test_get_all_pairs_length(self):
    #    fac = Factory(w3, Network.mainnet)
    #    self.assertGreater(fac.all_pairs_length(),4000)

    #def test_get_all_pairs(self):
    #    fac = Factory(w3, Network.mainnet)
    #    pairs = fac.all_pairs()
    #    self.assertGreater(len(pairs),4000)

#class TestPair:

    #def test_init(self):
    #    pair = Pair(w3, Address('0xAfa9046cf24F39d0fc39046a03Ad2a2A888EC6B0'))

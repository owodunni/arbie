"""Test uniswap contracts."""

import pytest

from Arbie.Contracts import Address, Network
from Arbie.Contracts.uniswap import Factory, Pair
from Arbie.Contracts.contract import read_abi, read_bytecode, Id

from web3 import (
    EthereumTesterProvider,
    Web3,
)


@pytest.fixture
def tester_provider():
    return EthereumTesterProvider()


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

def test_get_all_pairs_length(deploy_address, w3):
    fac = Factory.create(w3, deploy_address)
    assert fac.all_pairs_length() == 0
    #fac.create_pair()
    #assert fac.all_pairs_length() == 1

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

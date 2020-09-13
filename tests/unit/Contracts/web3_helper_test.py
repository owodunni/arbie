"""Help module for web3 tests."""
import pytest
from web3 import Web3

from Arbie.Contracts.contract import Address


@pytest.fixture
def w3():
    return Web3(Web3.HTTPProvider('http://ganache:7545'))


@pytest.fixture
def deploy_address(w3) -> Address:
    deploy_address = w3.eth.accounts[0]
    return Address(deploy_address)

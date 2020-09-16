"""Help module for web3 tests."""
import pytest
from web3 import Web3

from Arbie.Contracts.contract import Address


@pytest.fixture
def web3_server(request):
    return request.config.getoption('--web3_server')


@pytest.fixture
def w3(web3_server):
    return Web3(Web3.HTTPProvider(web3_server))


@pytest.fixture
def deploy_address(w3) -> Address:
    deploy_address = w3.eth.accounts[0]
    return Address(deploy_address)

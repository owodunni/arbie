"""Help module for web3 tests."""
import pytest
from web3 import Web3

from Arbie.Contracts.contract import Address


def pytest_addoption(parser):
    parser.addoption('--web3_server', action='store', default='http://127.0.0.1:7545')


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

@pytest.fixture
def dummy_address(w3) -> Address:
    address = w3.eth.accounts[1]
    return Address(address)
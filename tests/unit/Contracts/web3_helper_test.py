"""Help module for web3 tests."""
import pytest
from eth_tester import PyEVMBackend
from web3 import EthereumTesterProvider, Web3

from Arbie.Contracts import Address


@pytest.fixture
def tester_provider():
    genesis_overrides = {'gas_limit': 4881400}
    custom_genesis_params = PyEVMBackend._generate_genesis_params(overrides=genesis_overrides)  # noqa: WPS437
    pyevm_backend = PyEVMBackend(genesis_parameters=custom_genesis_params)

    return EthereumTesterProvider(pyevm_backend)


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

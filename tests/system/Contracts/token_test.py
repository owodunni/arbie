"""Test uniswap contracts."""
import pytest

from Arbie.Variables import BigNumber
from Arbie.Contracts import ContractFactory
from Arbie.Contracts.tokens import GenericToken


@pytest.fixture
def token_factory(w3) -> ContractFactory:
    return ContractFactory(w3, GenericToken)


@pytest.fixture
def dai(deploy_address, token_factory) -> GenericToken:
    return token_factory.deploy_contract(
        deploy_address, 100, 'Dai', 18, 'DAI')


def test_equals(dai, token_factory):
    dai2 = token_factory.load_contract(owner_address=dai.owner_address, address=dai.get_address())
    assert dai == dai2


def test_approve(dai: GenericToken, deploy_address):
    assert dai.approve(deploy_address, BigNumber(10))


def test_transfer(dai: GenericToken, deploy_address, dummy_address):
    dai.approve(deploy_address, BigNumber(10))
    dai.transfer(dummy_address, BigNumber(10))
    assert dai.balance_of(dummy_address).to_number() == 10


def test_name(dai: GenericToken):
    assert dai.get_name() == 'BNB'

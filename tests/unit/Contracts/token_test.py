"""Test uniswap contracts."""
import pytest

from Arbie import BigNumber
from Arbie.Contracts import ContractFactory
from Arbie.Contracts.tokens import GenericToken


@pytest.fixture
def token_factory(w3) -> ContractFactory:
    return ContractFactory(w3, GenericToken)


@pytest.fixture
def dai(deploy_address, token_factory) -> GenericToken:  # noqa: WPS442
    return token_factory.deploy_contract(
        deploy_address, 100, 'Dai', 18, 'DAI')  # noqa: WPS432


def test_approve(dai: GenericToken, deploy_address):  # noqa:WPS442
    assert dai.approve(deploy_address, BigNumber(10))


def test_transfer(dai: GenericToken, deploy_address, dummy_address):  # noqa:WPS442
    dai.approve(deploy_address, BigNumber(10))
    dai.transfer(dummy_address, BigNumber(10))
    assert dai.balance_of(dummy_address).to_numer() == 10

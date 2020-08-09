"""Test uniswap contracts."""
import pytest

from Arbie.Contracts.contract import ContractFactory
from Arbie.Contracts.tokens import GenericToken
from Arbie.Contracts.uniswap import Factory

from .web3_helper_test import *  # noqa: F403, WPS300, WPS347, F401


@pytest.fixture
def factory(deploy_address, w3) -> Factory:
    return ContractFactory(w3, Factory).deploy_contract(deploy_address, deploy_address.value)


@pytest.fixture
def token_factory(w3) -> ContractFactory:
    return ContractFactory(w3, GenericToken)


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

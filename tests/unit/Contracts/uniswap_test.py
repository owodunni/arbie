"""Test uniswap contracts."""
import pytest

from Arbie.Contracts import ContractFactory
from Arbie.Contracts.tokens import GenericToken
from Arbie.Contracts.uniswap import Factory, Pair


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


@pytest.fixture
def factory_with_pair(factory, dai, weth) -> Factory:
    assert factory.create_pair(dai, weth)
    return factory


def test_get_all_pairs_length(factory):
    assert factory.all_pairs_length() == 0


def test_create_pair(factory_with_pair):
    assert factory_with_pair.all_pairs_length() == 1


def test_get_all_pairs(factory_with_pair):
    assert len(factory_with_pair.all_pairs()) == 1


@pytest.fixture
def pair(factory_with_pair) -> Pair:
    pairs = factory_with_pair.all_pairs()
    return pairs[0]


def test_get_k(pair):
    assert pair.get_k_last() == 0


def test_get_weights(pair):
    assert pair.get_reserves() == [0, 0, 0]

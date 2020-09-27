"""Test uniswap contracts."""
import pytest

from Arbie import BigNumber
from Arbie.Contracts import ContractFactory
from Arbie.Contracts.tokens import GenericToken
from Arbie.Contracts.uniswap import Factory, Pair

bg10 = BigNumber(10)
bg5 = BigNumber(5)


@pytest.fixture
def factory(deploy_address, w3) -> Factory:
    return ContractFactory(w3, Factory).deploy_contract(deploy_address, deploy_address.value)


@pytest.fixture
def token_factory(w3) -> ContractFactory:
    return ContractFactory(w3, GenericToken)


@pytest.fixture
def dai(deploy_address, token_factory) -> GenericToken:
    token = token_factory.deploy_contract(deploy_address, 10000, 'Dai', 18, 'DAI')  # noqa: WPS432
    token.approve_owner()
    return token


@pytest.fixture
def weth(deploy_address, token_factory) -> GenericToken:
    token = token_factory.deploy_contract(deploy_address, 10000, 'Weth', 18, 'WETH')  # noqa: WPS432
    token.approve_owner()
    return token


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
    assert pair.get_reserves() == [0, 0]


def test_mint(
        pair: Pair,
        dai: GenericToken,
        weth: GenericToken,
        deploy_address):

    assert dai.transfer(pair.get_address(), bg10)
    assert weth.transfer(pair.get_address(), bg10)
    assert pair.mint(deploy_address)
    assert pair.get_reserves() == [bg10, bg10]
    assert pair.get_k_last() == 0


def test_create_amm(
        pair: Pair,
        dai: GenericToken,
        weth: GenericToken,
        deploy_address):

    assert dai.transfer(pair.get_address(), bg5)
    assert weth.transfer(pair.get_address(), bg10)
    assert pair.mint(deploy_address)
    amm = pair.create_amm()
    assert amm.spot_price(weth.create_token(), dai.create_token()) == 2

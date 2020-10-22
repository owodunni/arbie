"""Test uniswap contracts."""
import pytest

from Arbie.Contracts import ContractFactory
from Arbie.Contracts.tokens import GenericToken
from Arbie.Contracts.uniswap import Factory, Pair
from Arbie.Variables import BigNumber

bg10 = BigNumber(10)
bg5 = BigNumber(5)


@pytest.fixture
def factory(deploy_address, w3) -> Factory:
    return ContractFactory(w3, Factory).deploy_contract(
        deploy_address, deploy_address.value
    )


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


def test_get_weights(pair):
    assert pair.get_balances() == [0, 0]


def test_mint(pair: Pair, dai: GenericToken, weth: GenericToken, deploy_address):

    assert dai.transfer(pair.get_address(), bg10)
    assert weth.transfer(pair.get_address(), bg10)
    assert pair.mint(deploy_address)
    assert pair.get_balances() == [bg10, bg10]


def test_create_pool(pair: Pair, dai: GenericToken, weth: GenericToken, deploy_address):

    dai.transfer(pair.get_address(), bg5)
    weth.transfer(pair.get_address(), bg10)
    pair.mint(deploy_address)
    pool = pair.create_pool()

    assert pool.spot_price(weth.create_token(), dai.create_token()) == 2
    balances = pool.get_balances(weth.create_token(), dai.create_token())
    assert balances[0] == 10
    assert balances[1] == 5

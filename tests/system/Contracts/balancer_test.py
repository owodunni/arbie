"""Test balancer contracts."""
import pytest

from Arbie.Contracts import ContractFactory
from Arbie.Contracts.balancer import Pool, PoolFactory
from Arbie.Contracts.tokens import GenericToken
from Arbie.Variables import Address, BigNumber

bg10 = BigNumber(10)
bg5 = BigNumber(5)


@pytest.fixture
def pool_factory(deploy_address, w3) -> PoolFactory:
    return ContractFactory(w3, PoolFactory).deploy_contract(deploy_address)


@pytest.fixture
def pool(pool_factory) -> Pool:
    pool_factory.new_bpool()
    return pool_factory.all_pools()[0]


def test_create_new_pool(pool_factory):
    pool_factory.new_bpool()
    assert len(pool_factory.all_pools()) == 1


def test_get_number_of_tokens(pool_factory):
    pool_factory.new_bpool()
    pools = pool_factory.all_pools()
    assert pools[0].get_number_of_tokens() == 0


def test_bind_weight(pool):
    with pytest.raises(ValueError):
        amount = BigNumber(5)
        weight = 0.2
        pool.bind(Address(), amount, weight)


@pytest.fixture
def pool_with_tokens(
        pool: Pool,
        dai: GenericToken,
        weth: GenericToken) -> Pool:
    weight = 5

    dai.approve_owner()
    dai.approve(pool.get_address(), bg5)

    weth.approve_owner()
    weth.approve(pool.get_address(), bg10)

    pool.bind(dai.get_address(), bg5, weight)
    pool.bind(weth.get_address(), bg10, weight)

    pool.finalize()
    return pool


def test_bind_token_to_pool(pool_with_tokens: Pool):
    tokens = pool_with_tokens.get_tokens()
    assert len(tokens) == 2
    assert pool_with_tokens.get_balances() == [bg5, bg10]
    assert pool_with_tokens.get_weights() == [0.5, 0.5]


def test_create_pool(
        pool_with_tokens: Pool,
        dai: GenericToken,
        weth: GenericToken):
    pool = pool_with_tokens.create_pool()
    assert pool.spot_price(weth.create_token(), dai.create_token()) == 2
    assert pool.balances[0].value == 5
    assert pool.balances[1].value == 10

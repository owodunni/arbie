"""Test balancer contracts."""
import pytest

from Arbie.Contracts import ContractFactory
from Arbie.Contracts.balancer import BalancerFactory, BalancerPool
from Arbie.Contracts.tokens import GenericToken
from Arbie.Variables import Address, BigNumber

bg10 = BigNumber(10)
bg5 = BigNumber(5)


@pytest.fixture
def pool_factory(deploy_address, w3) -> BalancerFactory:
    return ContractFactory(w3, BalancerFactory).deploy_contract(deploy_address)


def test_create_new_pool(pool_factory):
    pool_factory.new_pool()
    assert len(pool_factory.all_pools()) == 1


def test_get_number_of_tokens(pool_factory):
    pool_factory.new_pool()
    pool_factory.new_pool()
    pools = pool_factory.all_pools()
    assert len(pools) == 2
    assert pools[0].get_number_of_tokens() == 0


def test_bind_weight(pool_factory):
    pool = pool_factory.new_pool()
    with pytest.raises(ValueError):
        amount = BigNumber(5)
        weight = 0.2
        pool.bind(Address(), amount, weight)


@pytest.fixture
def pool_with_tokens(
    pool_factory: BalancerFactory, dai: GenericToken, weth: GenericToken
) -> BalancerPool:
    weight = 5
    return pool_factory.setup_pool([dai, weth], [weight, weight], [bg5, bg10])


def test_bind_token_to_pool(pool_with_tokens: BalancerPool):
    tokens = pool_with_tokens.get_tokens()
    assert len(tokens) == 2
    assert pool_with_tokens.get_balances() == [bg5, bg10]
    assert pool_with_tokens.get_weights() == [0.5, 0.5]


def test_create_pool(
    pool_with_tokens: BalancerPool, dai: GenericToken, weth: GenericToken
):
    pool = pool_with_tokens.create_pool()
    assert pool.spot_price(weth.create_token(), dai.create_token()) == 2
    assert pool.balances[0].value == 5
    assert pool.balances[1].value == 10

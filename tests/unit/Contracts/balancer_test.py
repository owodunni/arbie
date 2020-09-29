"""Test balancer contracts."""
import pytest

from Arbie import BigNumber
from Arbie.Contracts import Address, ContractFactory
from Arbie.Contracts.balancer import Pool, PoolFactory
from Arbie.Contracts.tokens import GenericToken


@pytest.fixture
def pool_factory(deploy_address, w3) -> PoolFactory:
    return ContractFactory(w3, PoolFactory).deploy_contract(deploy_address)


@pytest.fixture
def pool(pool_factory) -> Pool:  # noqa: WPS442
    pool_factory.new_bpool()
    return pool_factory.all_pools()[0]


def test_create_new_pool(pool_factory):  # noqa: WPS442
    pool_factory.new_bpool()
    assert len(pool_factory.all_pools()) == 1


def test_get_number_of_tokens(pool_factory):  # noqa: WPS442
    pool_factory.new_bpool()
    pools = pool_factory.all_pools()
    assert pools[0].get_number_of_tokens() == 0


def test_bind_weight(pool):  # noqa: WPS442
    with pytest.raises(ValueError):
        amount = BigNumber(5)
        weight = 0.2
        pool.bind(Address(''), amount, weight)


def test_bind_token_to_pool(
        pool: Pool,  # noqa: WPS442
        dai: GenericToken,
        weth: GenericToken):
    amount = BigNumber(5)
    weight = 5

    dai.approve_owner()
    dai.approve(pool.get_address(), amount)

    weth.approve_owner()
    weth.approve(pool.get_address(), amount)

    pool.bind(dai.get_address(), amount, weight)
    pool.bind(weth.get_address(), amount, weight)

    pool.finalize()
    tokens = pool.get_tokens()
    assert len(tokens) == 2
    assert tokens[0].get_address() == dai.get_address()

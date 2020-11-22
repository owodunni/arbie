"""Test balancer contracts."""
import pytest

from Arbie import IERC20TokenError
from Arbie.Contracts import ContractFactory
from Arbie.Contracts.balancer import BalancerFactory, BalancerPool
from Arbie.Contracts.tokens import BadERC20Token, GenericToken
from Arbie.Variables import BigNumber, PoolType

bg10 = BigNumber(10)
bg5 = BigNumber(5)


@pytest.fixture
def pool_factory(deploy_address, w3) -> BalancerFactory:
    return ContractFactory(w3, BalancerFactory).deploy_contract(deploy_address)


@pytest.mark.asyncio
async def test_create_new_pool(pool_factory):
    pool_factory.new_pool()
    assert len(await pool_factory.all_pools()) == 1


@pytest.mark.asyncio
async def test_get_number_of_tokens(pool_factory):
    pool_factory.new_pool()
    pool_factory.new_pool()
    pools = await pool_factory.all_pools()
    assert len(pools) == 2
    assert pools[0].get_number_of_tokens() == 0


def test_bind_weight(pool_factory):
    pool = pool_factory.new_pool()
    with pytest.raises(ValueError):
        amount = BigNumber(5)
        weight = 0.2
        pool.bind("", amount, weight)


@pytest.fixture
async def pool_with_tokens(
    pool_factory: BalancerFactory, dai: GenericToken, weth: GenericToken
) -> BalancerPool:
    weight = 5
    return await pool_factory.setup_pool([dai, weth], [weight, weight], [bg5, bg10])


@pytest.fixture
async def factory_with_bad_token(
    pool_factory: BalancerFactory, dai: GenericToken, bad: BadERC20Token
):
    weight = 5
    await pool_factory.setup_pool(
        [bad, dai], [weight, weight], [bg5, bg10], approve_owner=False
    )
    return pool_factory


@pytest.mark.asyncio
async def test_bind_token_to_pool(pool_with_tokens: BalancerPool):
    tokens = await pool_with_tokens.get_tokens()
    assert len(tokens) == 2
    balances = await pool_with_tokens.get_balances()
    assert balances == [bg5, bg10]
    assert await pool_with_tokens.get_weights() == [0.5, 0.5]


@pytest.mark.asyncio
async def test_create_pool(
    pool_with_tokens: BalancerPool, dai: GenericToken, weth: GenericToken
):
    pool = await pool_with_tokens.create_pool()
    weth_token = await weth.create_token()
    dai_token = await dai.create_token()
    assert pool.pool_type == PoolType.balancer
    assert pool.spot_price(weth_token, dai_token) == 2
    assert pool.balances[0].value == 5
    assert pool.balances[1].value == 10


@pytest.mark.asyncio
async def test_create_bad_pool(factory_with_bad_token: BalancerFactory):
    pools = await factory_with_bad_token.all_pools()
    with pytest.raises(IERC20TokenError):
        await pools[0].create_pool()

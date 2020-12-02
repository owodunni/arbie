"""Test uniswap contracts."""
import asyncio

import pytest

from Arbie import IERC20TokenError
from Arbie.Contracts.tokens import BadERC20Token, GenericToken
from Arbie.Contracts.uniswap import UniswapFactory, UniswapPair
from Arbie.Variables import BigNumber, PoolType

bg10 = BigNumber(10)
bg5 = BigNumber(5)

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def factory_with_pair(factory, dai, weth) -> UniswapFactory:
    await factory.create_pair(dai, weth)
    return factory


async def test_get_all_pairs_length(factory):
    assert await factory.all_pairs_length() == 0


async def test_create_pair(factory_with_pair):
    assert await factory_with_pair.all_pairs_length() == 1


async def test_get_all_pairs(factory_with_pair):
    assert len(await factory_with_pair.all_pairs()) == 1


@pytest.fixture
async def pair(factory_with_pair) -> UniswapPair:
    pairs = await factory_with_pair.all_pairs()
    return pairs[0]


async def test_get_weights(pair):
    assert await pair.get_balances() == [0, 0]


async def test_mint(
    pair: UniswapPair, dai: GenericToken, weth: GenericToken, deploy_address
):
    assert dai.transfer(pair.get_address(), bg10)
    assert weth.transfer(pair.get_address(), bg10)
    assert pair.mint(deploy_address)
    assert await pair.get_balances() == [bg10, bg10]


async def test_create_pool(
    pair: UniswapPair, dai: GenericToken, weth: GenericToken, deploy_address
):
    dai.transfer(pair.get_address(), bg5)
    weth.transfer(pair.get_address(), bg10)
    pair.mint(deploy_address)
    pool = await pair.create_pool()
    tokens = await asyncio.gather(weth.create_token(), dai.create_token())

    assert pool.pool_type == PoolType.uniswap
    assert pool.spot_price(tokens[0], tokens[1]) == 2
    balances = pool.get_balances(tokens[0], tokens[1])
    assert balances[0] == 10
    assert balances[1] == 5


async def test_create_bad_pool(
    factory: UniswapFactory, bad: BadERC20Token, dai: GenericToken
):
    pair = await factory.create_pair(bad, dai)
    with pytest.raises(IERC20TokenError):
        await pair.create_pool()

"""Help module for web3 tests."""
import asyncio

import pytest
from web3 import Web3

from Arbie.async_helpers import async_map
from Arbie.Contracts import (
    Arbie,
    BalancerFactory,
    ContractFactory,
    UniswapFactory,
    UniswapV2Router,
)
from Arbie.Contracts.tokens import BadERC20Token, GenericToken
from Arbie.Variables import BigNumber, Trade


@pytest.fixture
def web3_server(request):
    return request.config.getoption("--web3_server")


@pytest.fixture
def redis_server(request):
    return request.config.getoption("--redis_server")


@pytest.fixture
def w3(web3_server):
    return Web3(Web3.HTTPProvider(web3_server))


@pytest.fixture
def deploy_address(w3) -> str:
    return w3.eth.accounts[0]


@pytest.fixture
def dummy_address(w3) -> str:
    return w3.eth.accounts[1]


@pytest.fixture
def token_factory(w3) -> ContractFactory:
    return ContractFactory(w3, GenericToken)


large_number = BigNumber(10e14)


@pytest.fixture
async def dai(deploy_address, token_factory) -> GenericToken:
    token = token_factory.deploy_contract(
        deploy_address, "Dai", "DAI", large_number.value
    )
    await token.approve_owner()
    return token


@pytest.fixture
async def weth(deploy_address, token_factory) -> GenericToken:
    token = token_factory.deploy_contract(
        deploy_address, "Weth", "WETH", large_number.value
    )
    await token.approve_owner()
    return token


@pytest.fixture
async def yam(deploy_address, token_factory) -> GenericToken:
    token = token_factory.deploy_contract(
        deploy_address, "yam", "YAM", large_number.value
    )
    await token.approve_owner()
    return token


@pytest.fixture
async def wbtc(deploy_address, token_factory) -> GenericToken:
    token = token_factory.deploy_contract(
        deploy_address, "Wbtc", "WBTC", large_number.value
    )
    await token.approve_owner()
    return token


@pytest.fixture
def bad(deploy_address, w3) -> BadERC20Token:
    return ContractFactory(w3, BadERC20Token).deploy_contract(
        deploy_address, large_number.value
    )


small = 10e4
medium = 10e6
large = 10e8


@pytest.fixture
async def pool_factory(
    dai: GenericToken,
    weth: GenericToken,
    yam: GenericToken,
    wbtc: GenericToken,
    bad,
    w3,
    deploy_address,
) -> BalancerFactory:
    factory = ContractFactory(w3, BalancerFactory).deploy_contract(deploy_address)

    f1 = factory.setup_pool(
        [weth, dai, yam],
        [5, 5, 5],
        [
            BigNumber(small / 303.0),
            BigNumber(small / 0.9),
            BigNumber(small / 0.1),
        ],
    )
    f2 = factory.setup_pool(
        [bad, dai],
        [5, 5],
        [
            BigNumber(100),
            BigNumber(small / 0.9),
        ],
        approve_owner=False,
    )
    factory.new_pool()

    f3 = factory.setup_pool(
        [weth, wbtc],
        [5, 1],
        [
            BigNumber(5 * large / 301.0),
            BigNumber(large / 10000),
        ],  # noqa: WPS221
    )
    f4 = factory.setup_pool(
        [weth, dai, wbtc],
        [2, 1, 1],
        [
            BigNumber(2 * medium / 301.0),
            BigNumber(medium / 1.1),
            BigNumber(large / 10020),
        ],
    )

    await asyncio.gather(f1, f2, f3, f4)

    return factory


@pytest.fixture
def factory(deploy_address, w3) -> UniswapFactory:
    return ContractFactory(w3, UniswapFactory).deploy_contract(
        deploy_address, deploy_address
    )


@pytest.fixture
async def pair_factory(  # noqa: WPS210, WPS217
    factory,
    dai: GenericToken,
    weth: GenericToken,
    yam: GenericToken,
    wbtc: GenericToken,
    bad,
    w3,
    deploy_address,
) -> UniswapFactory:

    await factory.setup_pair(
        [wbtc, dai],
        [
            BigNumber(large / 10000.0),
            BigNumber(large),
        ],
    )
    await factory.setup_pair(
        [dai, yam],
        [
            BigNumber(small / 1.1),
            BigNumber(small / 0.1),
        ],  # noqa: WPS221
    )
    await factory.setup_pair(
        [weth, dai],
        [BigNumber(large / 300), BigNumber(large)],
    )
    await factory.setup_pair(
        [wbtc, weth],
        [
            BigNumber(large / 10000),
            BigNumber(large / 300),
        ],
    )
    await factory.create_pair(weth, bad)
    await factory.create_pair(weth, yam)
    return factory


@pytest.fixture
def uniswap_router(w3, deploy_address, weth, factory):
    return ContractFactory(w3, UniswapV2Router).deploy_contract(
        deploy_address, factory.get_address(), weth.get_address()
    )


@pytest.fixture
def arbie(w3, deploy_address, uniswap_router):
    return ContractFactory(w3, Arbie).deploy_contract(
        deploy_address, uniswap_router.get_address()
    )


async def create_pool(pool):
    return await pool.create_pool()


async def create_token(token):
    return await token.create_token()


@pytest.fixture
async def pairs(factory, weth, dai, wbtc):
    p0 = await factory.setup_pair(
        [weth, dai],
        [
            BigNumber(large / 300.0),
            BigNumber(large),
        ],
    )

    p1 = await factory.setup_pair(
        [wbtc, dai],
        [
            BigNumber(large / 10000.0),
            BigNumber(large),
        ],
    )

    p2 = await factory.setup_pair(
        [wbtc, weth],
        [
            BigNumber(large / 10000.0),
            BigNumber(large / 285.0),
        ],
    )
    return await async_map(create_pool, [p0, p1, p2])


@pytest.fixture
async def path(weth, dai, wbtc):
    raw_path = [weth, dai, wbtc, weth]
    return await async_map(create_token, raw_path)


@pytest.fixture
def trade(pairs, path):
    return Trade(pairs, path)

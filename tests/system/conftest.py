"""Help module for web3 tests."""
import asyncio
import json

import pytest
from eth_account import Account
from web3 import Web3

from Arbie.async_helpers import async_map
from Arbie.Contracts import (
    BalancerFactory,
    ContractFactory,
    UniswapFactory,
    UniswapV2Router,
    Weth,
)
from Arbie.Contracts.tokens import BadERC20Token, GenericToken, MaliciousToken
from Arbie.settings_parser import setup_gas_strategy
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
def w3_with_gas_strategy(web3_server):
    w3 = Web3(Web3.HTTPProvider(web3_server))
    setup_gas_strategy(w3, 60)
    return w3


@pytest.fixture
def deploy_address(w3) -> str:
    return w3.eth.accounts[0]


@pytest.fixture
def dummy_address(w3) -> str:
    return w3.eth.accounts[1]


@pytest.fixture
def empty_account(w3) -> Account:
    with open("Brig/Trader/test_account.json", "r") as config_file:
        config = json.load(config_file)
        return Account.from_key(config["key"])


@pytest.fixture()
def dummy_account(w3, empty_account) -> Account:
    balance = w3.eth.getBalance(empty_account.address)
    required = 11 - BigNumber.from_value(balance).to_number()
    required = max(0, required)

    tx_recip = w3.eth.sendTransaction(
        {
            "from": w3.eth.accounts[2],
            "to": empty_account.address,
            "value": BigNumber(required).value,
        }
    )
    w3.eth.waitForTransactionReceipt(tx_recip)
    return empty_account


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
async def paused_token(w3, deploy_address) -> GenericToken:
    token = ContractFactory(w3, MaliciousToken).deploy_contract(
        deploy_address, "paused", "PAU", large_number.value
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


@pytest.fixture
def real_weth(w3, deploy_address):
    return ContractFactory(w3, Weth).deploy_contract(deploy_address)


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
    paused_token: GenericToken,
    bad,
    w3,
    deploy_address,
) -> UniswapFactory:
    await factory.setup_pair(
        [wbtc, dai],
        [
            BigNumber(medium / 20000.0),
            BigNumber(medium),
        ],
    )
    await factory.setup_pair(
        [dai, yam],
        [
            BigNumber(medium / 1.1),
            BigNumber(medium / 0.1),
        ],  # noqa: WPS221
    )
    await factory.setup_pair(
        [weth, dai],
        [BigNumber(medium / 310), BigNumber(medium)],
    )
    await factory.setup_pair(
        [wbtc, weth],
        [
            BigNumber(medium / 10000),
            BigNumber(medium / 285),
        ],
    )

    await factory.setup_pair(
        [paused_token, weth],
        [
            BigNumber(medium / 10000),
            BigNumber(medium / 285),
        ],
    )

    paused_token.pause()

    await factory.create_pair(weth, bad)
    await factory.create_pair(weth, yam)
    return factory


@pytest.fixture
def whitelist(  # noqa: WPS210, WPS217
    dai: GenericToken, weth: GenericToken, yam: GenericToken, wbtc: GenericToken
):
    return [
        dai.get_address().lower(),
        weth.get_address().lower(),
        yam.get_address().lower(),
        wbtc.get_address().lower(),
    ]


@pytest.fixture
def router(w3_with_gas_strategy, deploy_address, weth, factory):
    return ContractFactory(w3_with_gas_strategy, UniswapV2Router).deploy_contract(
        deploy_address, factory.get_address(), weth.get_address()
    )


async def create_pool(pool):
    return await pool.create_pool()


async def create_token(token):
    return await token.create_token()


@pytest.fixture
async def all_pairs(factory, weth, dai, wbtc, paused_token):
    """all_pairs set up a very specific arbitrage opportunity.

    We want a opportunity that requires less then 2 WETH and provides significant profit as
    to be able to separate profit from gas costs. If the numbers do not make sense it is because
    they are crafted to produce a high arbitrage opportunity  and high slippage.
    """
    p0 = await factory.setup_pair(
        [weth, dai],
        [
            BigNumber(small / 500 / 300.0),
            BigNumber(small / 500),
        ],
    )

    p1 = await factory.setup_pair(
        [wbtc, dai],
        [
            BigNumber(large / 10000.0),
            BigNumber(large / 10),
        ],
    )

    p2 = await factory.setup_pair(
        [wbtc, weth],
        [
            BigNumber(large / 10000.0),
            BigNumber(large / 300.0 + 31000),
        ],
    )

    p3 = await factory.setup_pair(
        [paused_token, weth],
        [
            BigNumber(large / 10000.0),
            BigNumber(large / 285.0),
        ],
    )

    paused_token.pause()

    return await async_map(create_pool, [p0, p1, p2, p3])


@pytest.fixture
def good_pairs(all_pairs):
    return all_pairs[:-1]


@pytest.fixture
def bad_pairs(all_pairs):
    return all_pairs[-1:] + all_pairs[-1:]


@pytest.fixture
async def good_path(weth, dai, wbtc):
    raw_path = [weth, dai, wbtc, weth]
    return await async_map(create_token, raw_path)


@pytest.fixture
async def bad_path(weth, paused_token):
    raw_path = [weth, paused_token, weth]
    return await async_map(create_token, raw_path)


@pytest.fixture
def trade(good_pairs, good_path):
    trade = Trade(good_pairs, good_path)
    trade.amount_in = 1
    return trade


@pytest.fixture
def bad_trade(bad_pairs, bad_path):
    trade = Trade(bad_pairs, bad_path)
    trade.amount_in = 1
    return trade

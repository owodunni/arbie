"""Pool finder is responsible for finding all pools."""
import asyncio
import logging
from math import isclose
from typing import List, Tuple

from prometheus_async.aio import time

from Arbie import IERC20TokenError, PoolValueError
from Arbie.Actions.action import Action
from Arbie.async_helpers import async_map
from Arbie.Contracts import BalancerFactory, GenericToken, UniswapFactory, UniswapPair
from Arbie.Contracts.pool_contract import PoolContract
from Arbie.prometheus import get_prometheus
from Arbie.Variables import Pools, Token, Tokens

logger = logging.getLogger()

CREATE_TOKEN_TIME = get_prometheus().summary(
    "pool_finder_create_and_check_token", "Time for creating and checking a token"
)


def check_and_get_price(balances) -> Tuple[bool, float]:
    for balance in balances:
        if isclose(balance.value, 0, abs_tol=1e-3):  # noqa: WPS432
            return True, 0
    return False, balances[0] / balances[1]


class TokenFinder(object):
    def __init__(self, weth):
        self.weth = weth
        self.tokens = []
        self.pairs = []

    async def create_token_if_weth_pair(self, pair: UniswapPair, price):
        tokens = await pair.get_tokens()
        t0 = tokens[0]
        t1 = tokens[1]
        if self.weth.address == t0.get_address():
            return await t1.create_token(price)
        if self.weth.address == t1.get_address():
            return await t0.create_token(1 / price)

    @time(CREATE_TOKEN_TIME)
    async def create_and_check_token(self, pair):
        balances = None
        try:
            balances = await pair.get_balances()
        except IERC20TokenError:
            return None

        is_zero, price = check_and_get_price(balances)
        if is_zero:
            return None

        token = await self.create_token_if_weth_pair(pair, price)
        if token:
            self.tokens.append(token)
            self.pairs.append(pair)
        logger.info(f"Finished creating token from {pair.get_address()}")

    async def create_tokens(self, uniswap_pairs: List[UniswapPair]) -> List[Token]:
        self.tokens = []
        self.pairs = []
        await async_map(self.create_and_check_token, uniswap_pairs)
        self.tokens.append(self.weth)
        return self.tokens, self.pairs


async def create_and_filter_pools(
    pool_contracts: List[PoolContract], tokens: List[Tokens]
) -> Pools:
    pools = []
    for contract in pool_contracts:
        logger.info(
            f"Filtering contract {pool_contracts.index(contract)} of {len(pool_contracts)}"
        )
        try:
            pool = await contract.create_pool()
        except IERC20TokenError as e:
            logger.warning(f"Failed to create pool, bad token. {e}")
            continue
        except PoolValueError as e:
            logger.warning(f"Failed to create pool, bad pool. {e}")
            continue
        for token in pool.tokens:
            try:
                index = tokens.index(token)
            # Token not found in pool
            except ValueError:
                continue
            if token in tokens:
                token.price = tokens[index].price
        pools.append(pool)
    return pools


class PoolFinder(Action):
    """PoolFinder is responsible for finding pools.

    [Settings]
    input:
        web3: web3
        weth: weth
        uniswap_factory: uniswap_factory
        fork_address: fork_address
    output:
        pools: all_pools
        tokens: all_tokens
    """

    async def on_next(self, data):
        weth = await data.weth().create_token(1)

        tokens, pools, weth_pairs = await self._get_pairs_and_tokens(data.uniswap_factory(), weth)

        tokens, pools = await self.filter_malicious_tokens(tokens, pools, weth, data.web3(), data.fork_address())

        await self._get_pools_and_tokens(pools, tokens)

        data.pools(pools)
        data.tokens(tokens)

    async def _get_pools_and_tokens(self, pair_contracts, tokens):
        pools = await create_and_filter_pools(pair_contracts, tokens),
        return tokens, pools

    async def _get_pairs_and_tokens(self, factory: UniswapFactory, weth):
        pairs = await factory.all_pairs()
        logging.getLogger().info("Found all uniswap pairs, filtering tokens.")
        tokens, weth_pairs = await TokenFinder(weth).create_tokens(pairs)
        return tokens, pairs, weth_pairs

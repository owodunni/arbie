"""Pool finder is responsible for finding all pools."""
import asyncio
import logging
from math import isclose
from typing import List, Tuple

from Arbie import IERC20TokenError, PoolValueError
from Arbie.Actions.action import Action
from Arbie.async_helpers import async_map
from Arbie.Contracts import BalancerFactory, GenericToken, UniswapFactory, UniswapPair
from Arbie.Contracts.pool_contract import PoolContract
from Arbie.Variables import Pools, Token, Tokens

logger = logging.getLogger()


def check_and_get_price(balances) -> Tuple[bool, float]:
    for balance in balances:
        if isclose(balance.value, 0, abs_tol=1e-3):  # noqa: WPS432
            return True, 0
    return False, balances[0] / balances[1]


class TokenFinder(object):
    def __init__(self, uoa):
        self.uoa = uoa

    async def create_token(self, pair: UniswapPair, price):
        tokens = await pair.get_tokens()
        t0 = tokens[0]
        t1 = tokens[1]
        if self.uoa.address == t0.get_address():
            return await t1.create_token(price)
        elif self.uoa.address == t1.get_address():
            return await t0.create_token(1 / price)
        return None

    async def create_and_check_token(self, pair):
        logger.info(f"Creating tokens from {pair.get_address()}")
        balances = None
        try:
            balances = await pair.get_balances()
        except IERC20TokenError:
            return None

        is_zero, price = check_and_get_price(balances)
        if is_zero:
            return None

        return await self.create_token(pair, price)

    async def create_tokens(self, uniswap_pairs: List[UniswapPair]) -> List[Token]:
        tokens = await async_map(self.create_and_check_token, uniswap_pairs)
        tokens.append(self.uoa)
        token_set = set(tokens)
        token_set.discard(None)
        return list(token_set)


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
        weth: weth
        uniswap_factory: uniswap_factory
        balancer_factory: balancer_factory
        balancer_start: 9562480
    output:
        pools: all_pools
        tokens: all_tokens
    """

    async def on_next(self, data):
        weth = data.weth()

        uni_coro = self._get_pairs_and_tokens(data.uniswap_factory(), weth)
        bal_coro = data.balancer_factory().all_pools(data.balancer_start(), 100)

        pools, tokens = await self._get_pools_and_tokens(
            *await self._get_results(uni_coro, bal_coro),
        )

        data.pools(pools)
        data.tokens(tokens)

    async def _get_pools_and_tokens(self, pool_contracts, pair_contracts, tokens):
        result = await asyncio.gather(
            create_and_filter_pools(pair_contracts, tokens),
            create_and_filter_pools(pool_contracts, tokens),
        )
        return result[0] + result[1], tokens

    async def _get_results(
        self, uni_coro, bal_coro
    ) -> Tuple[List[BalancerFactory], List[UniswapFactory], List[GenericToken]]:
        results = await asyncio.gather(uni_coro, bal_coro)
        pools = results[1]
        pairs = results[0][0]
        tokens = results[0][1]
        return pools, pairs, tokens

    async def _get_pairs_and_tokens(self, factory: UniswapFactory, weth):
        pairs = await factory.all_pairs()
        logging.getLogger().info("Found all uniswap pairs, filtering tokens.")
        tokens = await TokenFinder(weth).create_tokens(pairs)
        return pairs, tokens

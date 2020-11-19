"""Pool finder is responsible for finding all pools."""
import asyncio
import logging
from math import isclose
from typing import List, Tuple

from asyncstdlib.builtins import list as alist
from asyncstdlib.builtins import map as amap

from Arbie import IERC20TokenError, PoolValueError
from Arbie.Actions.action import Action
from Arbie.Contracts import UniswapPair
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

    async def create_token(self, pair, price):
        t0 = pair.get_token0()
        t1 = pair.get_token1()
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
        tokens = await alist(amap(self.create_and_check_token, uniswap_pairs))
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

        uniswap_pairs = data.uniswap_factory().all_pairs()
        balancer_pools = data.balancer_factory().all_pools(data.balancer_start(), 100)
        tokens = await TokenFinder(weth).create_tokens(uniswap_pairs)

        pool_results = await asyncio.gather(
            create_and_filter_pools(uniswap_pairs, tokens),
            create_and_filter_pools(balancer_pools, tokens),
        )

        data.pools(pool_results[0] + pool_results[1])
        data.tokens(tokens)

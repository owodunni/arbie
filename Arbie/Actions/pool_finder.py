"""Pool finder is responsible for finding all pools."""
import logging
from math import isclose
from typing import List, Tuple

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


def create_token(pair, price, uoa):
    t0 = pair.get_token0()
    t1 = pair.get_token1()
    if uoa.address == t0.get_address():
        return t1.create_token(price)
    elif uoa.address == t1.get_address():
        return t0.create_token(1 / price)
    return None


def create_and_check_token(pair, uoa):
    logger.info(f"Creating tokens from {pair.get_address()}")
    balances = None
    try:
        balances = pair.get_balances()
    except IERC20TokenError:
        return None

    is_zero, price = check_and_get_price(balances)
    if is_zero:
        return None

    return create_token(pair, price, uoa)


def create_tokens(uniswap_pairs: List[UniswapPair], uoa: Token) -> List[Token]:
    tokens = list(map(lambda p: create_and_check_token(p, uoa), uniswap_pairs))
    tokens.append(uoa)
    token_set = set(tokens)
    token_set.discard(None)
    return list(token_set)


def create_and_filter_pools(
    pool_contracts: List[PoolContract], tokens: List[Tokens]
) -> Pools:
    pools = []
    for contract in pool_contracts:
        logger.info(
            f"Filtering contract {pool_contracts.index(contract)} of {len(pool_contracts)}"
        )
        try:
            pool = contract.create_pool()
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

    def on_next(self, data):
        weth = data.weth()

        uniswap_pairs = data.uniswap_factory().all_pairs()
        balancer_pools = data.balancer_factory().all_pools(data.balancer_start(), 100)
        tokens = create_tokens(uniswap_pairs, weth)

        pools = create_and_filter_pools(
            uniswap_pairs, tokens
        ) + create_and_filter_pools(balancer_pools, tokens)

        data.pools(pools)
        data.tokens(tokens)

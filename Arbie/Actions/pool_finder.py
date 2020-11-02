"""Pool finder is responsible for finding all pools."""
import logging
from typing import List

from Arbie import IERC20TokenError
from Arbie.Actions.action import Action
from Arbie.Contracts import UniswapPair
from Arbie.Contracts.pool_contract import PoolContract
from Arbie.Variables import Pools, Token, Tokens

logger = logging.getLogger()


def create_tokens_and_pairs(
    uniswap_pairs: List[UniswapPair], uoa: Token
) -> List[Token]:
    token_set = set()
    token_set.add(uoa)
    for pair in uniswap_pairs:
        logger.info(
            f"Creating token {uniswap_pairs.index(pair)} of {len(uniswap_pairs)}"
        )
        t0 = pair.get_token0()
        t1 = pair.get_token1()
        balances = None
        try:
            balances = pair.get_balances()
        except IERC20TokenError:
            continue
        if balances[0] == 0 or balances[1] == 0:
            continue
        if uoa.address == t0.get_address():
            token_set.add(t1.create_token(balances[0] / balances[1]))
        elif uoa.address == t1.get_address():
            token_set.add(t0.create_token(balances[1] / balances[0]))

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
        except IERC20TokenError:
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
        tokens = create_tokens_and_pairs(uniswap_pairs, weth)

        pools = create_and_filter_pools(
            uniswap_pairs, tokens
        ) + create_and_filter_pools(balancer_pools, tokens)

        data.pools(pools)
        data.tokens(tokens)

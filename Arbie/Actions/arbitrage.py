"""arbitrage can be used to find to arbitrage opertunity between two Amms."""

from typing import List

from Arbie.Actions.amm import Amm, Token

Pools = List[Amm]


def run_action(pools: Pools, token_in: Token, token_out: Token) -> float:
    if len(pools) != 2:
        raise ValueError('Can only found arbitrage opertunity between two pools')

    if not token_in_pools(pools, token_in, token_out):
        raise ValueError('Tokens does not exist in pools')

    if not opertunity(pools, token_in, token_out):
        raise ValueError('No arbitrage opertunity found in pools')

    return 0


def token_in_pools(pools: Pools, token_in: Token, token_out: Token) -> bool:
    for pool in pools:
        if token_in not in pool.tokens or token_out not in pool.tokens:
            return False
    return True


def opertunity(pools: Pools, token_in: Token, token_out: Token) -> bool:
    prices = []
    for pool in pools:
        prices.append(pool.spot_price(token_in, token_out))

    # If there is an opertunity then the price of the first pool
    # should be smaller then the price of the second pool
    return prices[0] < prices[1]

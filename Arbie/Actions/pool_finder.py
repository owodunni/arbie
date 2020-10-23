"""Pool finder is responsible for finding all pools."""
from typing import List

from Arbie.Contracts import Pair
from Arbie.Variables import Token


class TokenFinder(object):
    def __init__(self, pairs: List[Pair]):
        self.pairs = pairs

    def get_tokens(self):
        return None


class PoolFinder(object):
    """PoolFinder is responsible for finding pools.

    [Settings]
    inputs:
        uni_factory: uni_factory
        bal_factory: bal_factory
    outputs:
        pools: all_pools
        tokens: all_tokens
        unit_of_account: eth
    """

    def on_next(self, data):
        uniswap_factory = data.uni_factory()
        balancer_factory = data.bal_factory()

        pairs = uniswap_factory.all_pairs()
        data.tokens(TokenFinder(pairs).get_tokens())

        pairs = pairs + balancer_factory.all_pools()

        pools = []

        for pool in pairs:
            pools.append(pool.create_pool())
        data.pools(pools)
        data.unit_of_account(
            Token(
                "eth",
                1,
            )
        )

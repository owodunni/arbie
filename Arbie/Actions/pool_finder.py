"""Pool finder is responsible for finding all pools."""
from typing import List

from Arbie.Actions.action import Action
from Arbie.Contracts import UniswapPair
from Arbie.Variables import Token


class TokenFinder(object):
    def __init__(self, pairs: List[UniswapPair]):
        self.pairs = pairs

    def get_tokens(self):
        return None


class PoolFinder(Action):
    """PoolFinder is responsible for finding pools.

    [Settings]
    input:
        uniswap_factory: uniswap_factory
        balanacer_factory: balancer_factory
    output:
        pools: all_pools
        tokens: all_tokens
        unit_of_account: weth
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
                "weth",
                1,
            )
        )

"""Pool updater updates pools and tokens."""

from Arbie.Actions import Action
from Arbie.Variables import Pools


def update_tokens(tokens):
    raise NotImplementedError()


def get_pools_and_tokens(pools: Pools):
    raise NotImplementedError()


class PoolUpdater(Action):
    """Pool Updater updates pools and tokens.

    [Settings]
    input:
        w3: web3
        pools: all_pools
        tokens: all_tokens
    output:
        new_pools: all_pools
        new_tokens: all_pools
    """

    async def on_next(self, data):
        pools, tokens = get_pools_and_tokens(data.pools())
        data.new_tokens(tokens)
        data.new_pools(pools)

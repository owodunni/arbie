"""Pool updater updates pools and tokens."""
from Arbie.Actions import Action
from Arbie.async_helpers import async_map, run_async
from Arbie.Contracts import BalancerPool, ContractFactory, UniswapPair
from Arbie.Variables import PoolType


class PoolUpdater(Action):
    """Pool Updater updates pools and tokens.

    [Settings]
    input:
        web3: web3
        pools: all_pools
    output:
        new_pools: all_pools
    """

    def __init__(self, config=None):
        self.pair_factory = None
        self.pool_factory = None
        super().__init__(config)

    async def on_next(self, data):
        web3 = data.web3()

        self.pair_factory = ContractFactory(web3, UniswapPair)
        self.pool_factory = ContractFactory(web3, BalancerPool)

        pools = await self._update_pools(data.pools())
        data.new_pools(pools)

    def _get_contract(self, address, pool_type):
        if pool_type == PoolType.uniswap:
            return self.pair_factory.load_contract(address=address)
        elif pool_type == PoolType.balancer:
            return self.pool_factory.load_contract(address=address)
        raise ValueError("Cannot update pool with unknown type")

    async def _update_pool(self, pool):
        pool_contract = await run_async(
            self._get_contract, pool.address, pool.pool_type
        )
        balances = await pool_contract.get_balances()
        balances_numb = [balance.to_number() for balance in balances]
        pool.update_balances(balances_numb)
        return pool

    async def _update_pools(self, pools):
        return await async_map(self._update_pool, pools)

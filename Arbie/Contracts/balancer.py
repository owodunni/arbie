"""Utility functions for interacting with balancer."""

from typing import List

from Arbie.Contracts import Address, Contract, ContractFactory


class Pool(Contract):

    name = 'pool'
    protocol = 'balancer'
    abi = 'bpool'

    def get_number_of_tokens(self):
        return self.contract.functions.getNumTokens().call()


class PoolFactory(Contract):
    name = 'pool_factory'
    protocol = 'balancer'
    abi = 'pool_factory'

    def new_bpool(self) -> bool:
        transaction = self.contract.functions.newBPool()
        return self._transact_status(transaction)

    def all_pools(self) -> List[Pool]:
        event_filter = self.contract.events.LOG_NEW_POOL.createFilter(fromBlock=0)
        return self._create_pools(event_filter.get_all_entries())

    def _create_pools(self, new_pool_event):
        pools = []
        factory = ContractFactory(self.w3, Pool)

        for event in new_pool_event:
            pool = factory.load_contract(self.owner_address, address=Address(event.args.pool))
            pools.append(pool)
        return pools

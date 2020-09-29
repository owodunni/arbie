"""Utility functions for interacting with balancer."""

from typing import List

from Arbie import BigNumber
from Arbie.Contracts import Address, Contract, ContractFactory
from Arbie.Contracts.tokens import GenericToken


class Pool(Contract):

    name = 'pool'
    protocol = 'balancer'
    abi = 'bpool'

    def get_number_of_tokens(self):
        return self.contract.functions.getNumTokens().call()

    def get_tokens(self) -> List[GenericToken]:
        token_addresses = self.contract.functions.getCurrentTokens().call()
        cf = ContractFactory(self.w3, GenericToken)
        return list(map(
            (lambda a: cf.load_contract(
                owner_address=self.owner_address, address=Address(a))),
            token_addresses))

    def bind(self, address: Address, balance: BigNumber, denorm_weight: int) -> bool:
        if denorm_weight < 1:
            raise ValueError('Weight should be larger than 1')
        eth_safe_weight = BigNumber(denorm_weight)
        transaction = self.contract.functions.bind(
            address.value,
            balance.value,
            eth_safe_weight.value)
        return self._transact_status(transaction)

    def finalize(self) -> bool:
        return self._transact_status(
            self.contract.functions.finalize())


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

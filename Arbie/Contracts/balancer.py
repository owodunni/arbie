"""Utility functions for interacting with balancer."""

from Arbie.Contracts import Contract


class PoolFactory(Contract):
    name = 'pool_factory'
    protocol = 'balancer'

    def new_bpool(self):
        transaction = self.contract.functions.newBPool()

        tx_hash = transaction.transact({
            'from': self.w3.eth.accounts[0],
        })
        self.w3.eth.waitForTransactionReceipt(tx_hash, 180)  # noqa: WPS432

    def all_pools(self):
        event_filter = self.contract.events.LOG_NEW_POOL.createFilter(fromBlock=0)
        return event_filter.get_all_entries()

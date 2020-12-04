"""Utility functions for interacting with Arbie.sol."""

from Arbie.Contracts.contract import Contract
from Arbie.Variables import BigNumber, Pools, Trade


def address_and_pool_type(pools: Pools):
    address = []
    pool_type = []

    for pool in pools:
        address.append(pool.address)
        pool_type.append(pool.pool_type.value)
    return address, pool_type


class Arbie(Contract):
    name = "Arbie"
    protocol = "arbie"

    def check_out_given_in(self, trade: Trade):
        addresses, types = address_and_pool_type(trade.pools)
        path_address = list(map(lambda t: t.address, trade.path))
        amount_out = self.contract.functions.checkOutGivenIn(
            BigNumber(trade.amount_in).value, addresses, types, path_address
        ).call()
        return BigNumber.from_value(amount_out).to_number()

    def swap(self, trade, from_address=None):
        addresses, types = address_and_pool_type(trade.pools)
        path = list(map(lambda t: t.address, trade.path))
        transaction = self.contract.functions.swap(
            BigNumber(trade.amount_in).value, addresses, types, path
        )

        return self._transact_status(transaction, from_address)

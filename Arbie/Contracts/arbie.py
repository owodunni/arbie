"""Utility functions for interacting with Arbie.sol."""

from Arbie.Contracts.contract import Contract
from Arbie.Contracts.tokens import GenericToken
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

    def approve(self, weth: GenericToken):
        if weth.allowance(self.get_address()) < BigNumber(10e6):  # noqa: WPS432
            return weth.approve(self.get_address(), BigNumber(10e8))  # noqa: WPS432
        return True

    def check_out_given_in(self, trade: Trade):
        addresses, types = address_and_pool_type(trade.pools)
        path_address = list(map(lambda t: t.address, trade.path))
        amount_out = self.contract.functions.checkOutGivenIn(
            BigNumber(trade.amount_in).value, addresses, types, path_address
        ).call()
        return BigNumber.from_value(amount_out).to_number()

    def estimate_swap_const(self, trade):
        price = self.w3.eth.generateGasPrice()
        if not price:
            price = 69 * 10e9  # noqa: WPS432
        gas = self._estimate_gas_swap(trade)
        return BigNumber.from_value(price * gas).to_number()

    def swap(self, trade):
        gas = self._estimate_gas_swap(trade)
        transaction = self._swap_transaction(trade)
        return self._transact_status(transaction, gas=gas)

    def _swap_transaction(self, trade):
        addresses, types = address_and_pool_type(trade.pools)
        path = list(map(lambda t: t.address, trade.path))
        return self.contract.functions.swap(
            BigNumber(trade.amount_in).value, addresses, types, path
        )

    def _estimate_gas_swap(self, trade):
        transaction = self._swap_transaction(trade)
        return self._estimate_gas(transaction)

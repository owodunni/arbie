"""Utility functions for interacting with Tokens."""

from Arbie.Contracts import Address, Contract


class GenericToken(Contract):
    name = 'bnb'
    protocol = 'tokens'
    abi = 'bnb'

    def approve(self, spender: Address, value: int) -> bool:
        transaction = self.contract.function.approve(spender.value, value)

        self.transact(transaction)

        # TODO: Get result from tx_recipt
        return False

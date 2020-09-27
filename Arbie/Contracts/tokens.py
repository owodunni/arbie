"""Utility functions for interacting with Tokens."""

from Arbie.Contracts import Address, Contract


class GenericToken(Contract):
    name = 'bnb'
    protocol = 'tokens'
    abi = 'bnb'

    def balance_of(self, owner: Address) -> int:
        return self.contract.functions.balanceOf(owner.value).call()

    def transfer(self, to: Address, value: int) -> bool:
        transaction = self.contract.functions.transfer(to.value, value)
        return self._transact_status(transaction)

    def approve(self, spender: Address, value: int) -> bool:
        transaction = self.contract.functions.approve(spender.value, value)
        return self._transact_status(transaction)

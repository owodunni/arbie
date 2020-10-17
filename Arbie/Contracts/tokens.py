"""Utility functions for interacting with Tokens."""

from Arbie import BigNumber
from Arbie.Actions.arbitrage import Token
from Arbie.Contracts import Address, Contract


class GenericToken(Contract):
    name = 'bnb'
    protocol = 'tokens'
    abi = 'bnb'

    def __str__(self):
        return f'GenericToken, name: {self.get_name()}, address: {self.get_address().value}'

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.get_address() == other.get_address()

    def decimals(self) -> int:
        return self.contract.functions.decimals().call()

    def balance_of(self, owner: Address) -> BigNumber:
        value = self.contract.functions.balanceOf(
            owner.value).call()
        return BigNumber.from_value(value, self.decimals())

    def transfer(self, to: Address, bg_number: BigNumber) -> bool:
        transaction = self.contract.functions.transfer(
            to.value, bg_number.value)
        return self._transact_status(transaction)

    def approve(
            self,
            spender: Address,
            bg_number: BigNumber) -> bool:
        transaction = self.contract.functions.approve(
            spender.value, bg_number.value)
        return self._transact_status(transaction)

    def approve_owner(self):
        return self.approve(
            self.owner_address, self.balance_of(self.owner_address))

    def get_name(self):
        return self.contract.functions.name().call()

    def create_token(self):
        return Token(self.get_name(), address=self.get_address().value)

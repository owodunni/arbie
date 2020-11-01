"""Utility functions for interacting with Tokens."""

from Arbie.Contracts.contract import Contract
from Arbie.Variables import Address, BigNumber, Token


class IERC20Token(Contract):
    name = "ierc20"
    protocol = "tokens"
    abi = "ierc20"

    def __eq__(self, other):
        return self.get_address() == other.get_address()

    def decimals(self) -> int:
        return self.contract.functions.decimals().call()

    def balance_of(self, owner: Address) -> BigNumber:
        value = self.contract.functions.balanceOf(owner.value).call()
        return BigNumber.from_value(value, self.decimals())

    def transfer(self, to: Address, bg_number: BigNumber) -> bool:
        transaction = self.contract.functions.transfer(to.value, bg_number.value)
        return self._transact_status(transaction)

    def approve(self, spender: Address, bg_number: BigNumber) -> bool:
        transaction = self.contract.functions.approve(spender.value, bg_number.value)
        return self._transact_status(transaction)

    def approve_owner(self):
        return self.approve(self.owner_address, self.balance_of(self.owner_address))

    def create_token(self, price=0):
        return Token("", price, self.get_address())


class BadERC20Token(IERC20Token):
    name = "baderc20"
    protocol = "tokens"
    abi = "baderc20"


class GenericToken(IERC20Token):
    name = "erc20"
    protocol = "tokens"
    abi = "erc20"

    def __str__(self):
        return f"GenericToken, name: {self.get_name()}, address: {self.get_address().value}"

    def __repr__(self):
        return self.__str__()

    def get_name(self):
        return self.contract.functions.name().call()

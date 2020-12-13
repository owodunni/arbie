"""Utility functions for interacting with Tokens."""

import asyncio
import logging

from Arbie.Contracts.contract import Contract
from Arbie.Variables import BigNumber, Token

token_protocol = "tokens"  # noqa: S105


class IERC20Token(Contract):
    name = "IERC20"
    protocol = token_protocol

    def __eq__(self, other):
        return self.get_address() == other.get_address()

    async def decimals(self) -> int:
        return await self._call_async(self.contract.functions.decimals())

    async def balance_of(self, owner: str) -> BigNumber:
        result = await asyncio.gather(
            self._call_async(self.contract.functions.balanceOf(owner)), self.decimals()
        )
        return BigNumber.from_value(result[0], result[1])

    def transfer(self, to: str, bg_number: BigNumber) -> bool:
        transaction = self.contract.functions.transfer(to, bg_number.value)
        return self._transact_status(transaction)

    def allowance(self, to: str):
        return self.contract.functions.allowance(self._get_account(), to).call()

    def approve(self, spender: str, bg_number: BigNumber) -> bool:
        transaction = self.contract.functions.approve(spender, bg_number.value)
        return self._transact_status(transaction)

    async def approve_owner(self):
        bg = await self.balance_of(self.owner_address)
        return self.approve(self.owner_address, bg)

    def create_token(self, price=0):
        return Token("", self.get_address(), price)


class BadERC20Token(IERC20Token):
    name = "BadERC20"
    protocol = token_protocol


class GenericToken(IERC20Token):
    name = "ERC20"
    protocol = token_protocol

    def __str__(self):
        return (
            f"GenericToken, name: {self._name().call()} address: {self.get_address()}"
        )

    def __repr__(self):
        return self.__str__()

    async def get_name(self) -> str:
        return await self._call_async(self._name())

    async def create_token(self, price=0):
        try:
            name = await self.get_name()
        except Exception:
            name = ""
            logging.getLogger().warning(
                f"Token: {self.get_address()} dosn't have a name."
            )
        return Token(name, self.get_address(), price)

    def _name(self):
        return self.contract.functions.name()


class Weth(GenericToken):
    name = "Weth"
    protocol = token_protocol

    def deposit(self, amount):
        transaction = self.contract.functions.deposit()
        return self._transact_status(transaction, BigNumber(amount).value)

    def withdraw(self, amount):
        transaction = self.contract.functions.withdraw(BigNumber(amount).value)
        return self._transact_status(transaction)

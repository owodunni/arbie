"""Utility functions for interacting with Uniswap."""

from typing import List

from Arbie import BigNumber
from Arbie.Actions.amm import Amm
from Arbie.Contracts.contract import Address, Contract, ContractFactory
from Arbie.Contracts.tokens import GenericToken

fee = 0.003
weight = 0.5


class Pair(Contract):

    name = 'pair'
    protocol = 'uniswap'
    abi = 'pair'

    def mint(self, address: Address) -> bool:
        transaction = self.contract.functions.mint(address.value)
        return self._transact_status(transaction)

    def get_price0(self) -> BigNumber:
        function = self.contract.functions.price0CumulativeLast()
        return self._get_price(function, self.get_token0().decimals())

    def get_price1(self) -> BigNumber:
        function = self.contract.functions.price1CumulativeLast()
        return self._get_price(function, self.get_token1().decimals())

    def get_k_last(self) -> int:
        return self.contract.functions.kLast().call()

    def get_token0(self) -> GenericToken:
        return self._get_token(self.contract.functions.token0())

    def get_token1(self) -> GenericToken:
        return self._get_token(self.contract.functions.token1())

    def get_tokens(self) -> List[GenericToken]:
        return [self.get_token0(), self.get_token1()]

    def get_reserves(self) -> List[BigNumber]:
        reserves = self.contract.functions.getReserves().call()

        bg_reservers = []
        for reserve, token in zip(reserves, self.get_tokens()):
            exp = token.decimals()
            bg_reservers.append(BigNumber.from_value(reserve, exp))

        return bg_reservers

    def create_amm(self) -> Amm:
        tokens = list(map((lambda t: t.create_token()), self.get_tokens()))
        balances = list(map((lambda bg: bg.to_number()), self.get_reserves()))

        return Amm(tokens, balances, [weight, weight], fee)

    def _get_price(self, function, exp) -> BigNumber:
        price = function.call()
        return BigNumber.from_value(price, exp)

    def _get_token(self, function) -> GenericToken:
        cf = ContractFactory(self.w3, GenericToken)
        token_address = function.call()
        return cf.load_contract(
            self.owner_address, address=Address(token_address))


class Factory(Contract):

    name = 'factory_v2'
    protocol = 'uniswap'
    abi = 'factory_v2'

    def all_pairs_length(self) -> int:
        return self.contract.functions.allPairsLength().call()

    def all_pairs(self) -> List[Pair]:
        cf = ContractFactory(self.w3, Pair)
        pairs = []
        for i in range(0, self.all_pairs_length()):
            address = self.contract.functions.allPairs(i).call()
            pairs.append(cf.load_contract(self.owner_address, address=Address(address)))
        return pairs

    def create_pair(self, token_a: GenericToken, token_b: GenericToken) -> bool:
        transaction = self.contract.functions.createPair(
            token_a.get_address().value,
            token_b.get_address().value)
        return self._transact_status(transaction)

"""Utility functions for interacting with Uniswap."""

from typing import List, Tuple

from Arbie.Contracts.contract import Address, Contract, ContractFactory
from Arbie.Contracts.tokens import GenericToken


class Pair(Contract):

    name = 'pair'
    protocol = 'uniswap'
    abi = 'pair'

    def get_k_last(self) -> int:
        return self.contract.functions.kLast().call()

    def get_reserves(self) -> Tuple[int, int, int]:
        return self.contract.functions.getReserves().call()


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
            pairs.append(cf.load_contract(address=Address(address)))
        return pairs

    def create_pair(self, token_a: GenericToken, token_b: GenericToken):
        transaction = self.contract.functions.createPair(
            token_a.contract.address,
            token_b.contract.address)

        self._transact(transaction)

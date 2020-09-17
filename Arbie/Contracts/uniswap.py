"""Utility functions for interacting with Uniswap."""

from typing import List

from Arbie.Contracts.contract import Address, Contract, ContractFactory
from Arbie.Contracts.tokens import GenericToken


class Pair(Contract):

    name = 'pair'
    protocol = 'uniswap'
    abi = 'pair'


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
            token_a.address.value,
            token_b.address.value)

        tx_hash = transaction.transact({
            'from': self.w3.eth.accounts[0],
        })
        self.w3.eth.waitForTransactionReceipt(tx_hash, 180)  # noqa: WPS432

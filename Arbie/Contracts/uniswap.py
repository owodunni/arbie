"""Utility functions for interacting with Uniswap."""

from typing import List

from Arbie.Contracts.contract import Address, Contract, Id, Network, deploy_contract
from Arbie.Contracts.tokens import GenericToken


class Pair(Contract):
    id = Id('uniswap', 'pair')
    def __init__(self, w3, address: Address):
        super().__init__(w3=w3, id=Pair.id, address = address)


class Factory(Contract):
    id = Id('uniswap', 'factory_v2')
    def __init__(self, w3, **kwargs):
        super().__init__(w3=w3, id=Factory.id, **kwargs)

    @classmethod
    def create(cls, w3, deploy_address: Address):
        contract_address = deploy_contract(w3, Factory.id, deploy_address, deploy_address.value)
        return cls(w3, address=contract_address)

    def all_pairs_length(self) -> int:
        return self.contract.functions.allPairsLength().call()

    def all_pairs(self) -> List[Pair]:
        pairs = []
        for i in range(0, self.all_pairs_length()):
            address = self.contract.functions.allPairs(i).call()
            pairs.append(Pair(self.w3, Address(address)))
        return pairs

    def create_pair(self, token_a: GenericToken, token_b: GenericToken):
        tx_hash = self.contract.functions.createPair(token_a.address.value, token_b.address.value).transact({
        'from': self.w3.eth.accounts[0],
        })
        self.w3.eth.waitForTransactionReceipt(tx_hash, 180)

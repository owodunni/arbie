"""Utility functions for interacting with Uniswap."""

from web3 import Web3

from typing import List

from Arbie.Contracts.contract import Address, Contract, Network


class Pair(Contract):

    def __init__(self, w3: Web3, address: Address):
        abi = self._read_resource('uniswap', 'pair_abi.json')
        self.contract = w3.eth.contract(address=address.value, abi=abi)


class Factory(Contract):

    def __init__(self, w3: Web3, network=Network.mainnet):
        abi = self._read_resource('uniswap', 'factory_v2_abi.json')
        self.w3 = w3
        self.address = self._get_address('uniswap', 'factory_v2', network)
        self.contract = w3.eth.contract(address=self.address.value, abi=abi)
    
    def all_pairs_length(self) -> int:
        return self.contract.functions.allPairsLength().call()

    def all_pairs(self) -> List[Pair]:
        pairs = []
        for i in range(0, self.all_pairs_length()-1):
            address = self.contract.functions.allPairs(i).call()
            pairs.append(Pair(self.w3, Address(address)))
        return pairs

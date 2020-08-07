"""Utility functions for interacting with Uniswap."""

from web3 import Web3

from Arbie.Contracts.contract import Address, Contract, Network


class Factory(Contract):

    def __init__(self, w3: Web3, network=Network.mainnet):
        abi = self._read_resource('uniswap', 'factory_v2_abi.json')
        self.address = self._get_address('uniswap', 'factory_v2', network)
        self.contract = w3.eth.contract(address=self.address.value, abi=abi)


class Pair(Contract):

    def __init__(self, w3: Web3, address: Address):
        abi = self._read_resource('uniswap', 'pair_abi.json')
        self.contract = w3.eth.contract(address=address.value, abi=abi)

"""Utility functions for interacting with Tokens."""

from typing import List

from Arbie.Contracts.contract import Address, Contract, Id, Network, deploy_contract


class GenericToken(Contract):
    id = Id('tokens', 'bnb')
    def __init__(self, w3, address: Address):
        super().__init__(w3=w3, id=Id('tokens', 'bnb'), address = address)

    @classmethod
    def create(cls, w3, deploy_address: Address, *args):
        contract_address = deploy_contract(w3, GenericToken.id, deploy_address, *args)
        return cls(w3, address=contract_address)
    
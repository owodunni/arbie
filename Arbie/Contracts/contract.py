"""Utility functions for interacting with smart contracts."""

import json
from enum import Enum

from pkg_resources import resource_string


class Address(object):

    def __init__(self, address: str):
        self.value = address


class Network(Enum):
    mainnet = 0
    kovan = 1
    ropsten = 2


class Contract(object):
    """Base class for contracts."""

    def __init__(self, w3, address: Address, contract):
        self.w3 = w3
        self.address = address
        self.contract = contract


class ContractFactory(object):

    def __init__(self, w3, factory_class):
        self.w3 = w3
        self.factory_class = factory_class

    def load_contract(self, **kwargs) -> Contract:
        """Load contract require address or network to be passed in kwargs."""
        address = self._read_address(**kwargs)
        contract = self._load_contract(address)
        return self.factory_class(self.w3, address, contract)

    def deploy_contract(self, deploy_address: Address, *args) -> Contract:
        contract_address = self._deploy_contract(deploy_address, *args)
        contract = self._load_contract(contract_address)
        return self.factory_class(self.w3, contract_address, contract)

    def _deploy_contract(self, deploy_address: Address, *args) -> Address:
        contract = self.w3.eth.contract(abi=self._read_abi(), bytecode=self._read_bytecode())

        # issue a transaction to deploy the contract.
        tx_hash = contract.constructor(*args).transact({
            'from': deploy_address.value,
            'gas': 48814000,
        })
        # wait for the transaction to be mined
        tx_receipt = self.w3.eth.waitForTransactionReceipt(tx_hash, 180)  # noqa: WPS432
        # instantiate and return an instance of our contract.
        return Address(tx_receipt.contractAddress)

    def _read_resource(self, path: str, filename: str) -> str:
        if path is None:
            path = ''
        else:
            path = '.{0}'.format(path)

        file_path = 'Arbie.resources.contracts{0}'.format(path)
        return resource_string(file_path, filename).decode('utf-8')

    def _get_address(self, network: Network):
        json_data = self._read_resource(None, 'contract_addresses.json')

        return Address(
            json.loads(json_data)[self.factory_class.protocol][self.factory_class.name][network.name])  # noqa: WPS221

    def _read_abi(self):
        return self._read_resource(self.factory_class.protocol, '{0}_abi.json'.format(self.factory_class.name))

    def _read_bytecode(self):
        key = 'bytecode'
        filename = '{0}_{1}.json'.format(self.factory_class.name, key)
        json_data = self._read_resource(self.factory_class.protocol, filename)
        return json.loads(json_data)[key]

    def _read_address(self, **kwargs):
        if 'address' in kwargs:
            return kwargs.get('address')
        if 'network' in kwargs:
            return self._get_address(kwargs.get('network'))

        raise NameError('kwargs does not contain network or address')

    def _load_contract(self, address: Address):
        return self.w3.eth.contract(address=address.value, abi=self._read_abi())

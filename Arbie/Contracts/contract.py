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


def transact(w3, address: Address, transaction):
    """Transact a transcation and return transaction receipt."""
    tx_hash = transaction.transact({
        'from': address.value,
        'gas': 48814000,
    })
    # wait for the transaction to be mined
    return w3.eth.waitForTransactionReceipt(tx_hash, 180)  # noqa: WPS432


class Contract(object):
    """Base class for contracts."""

    def __init__(self, w3, address: Address, contract):
        self.w3 = w3
        self.address = address
        self.contract = contract

    def _transact(self, transaction):
        return transact(self.w3, self.address, transaction)

    def _transact_status(self, transaction) -> bool:
        return bool(self._transact(transaction).status)


class ContractFactory(object):

    def __init__(self, w3, factory_class: Contract):
        self.w3 = w3

        if factory_class.name is None or factory_class.abi is None or factory_class.protocol is None:
            raise ValueError(f'{factory_class} dosent contain default parameters')
        self.factory_class = factory_class

    def load_contract(self, **kwargs) -> Contract:
        """Load contract require address or network to be passed in kwargs."""
        address = self._read_address(**kwargs)
        contract = self._load_contract(address)
        return self.factory_class(self.w3, address, contract)

    def deploy_contract(self, deploy_address: Address, *args) -> Contract:
        contract_address = self._deploy_contract(deploy_address, *args)
        contract = self._load_contract(contract_address)
        return self.factory_class(self.w3, deploy_address, contract)

    def _deploy_contract(self, deploy_address: Address, *args) -> Address:
        """Deploy contract and pass on args to contract abi constructor."""
        contract = self.w3.eth.contract(abi=self._read_abi(), bytecode=self._read_bytecode())

        transaction = contract.constructor(*args)
        tx_receipt = transact(self.w3, deploy_address, transaction)

        return Address(tx_receipt.contractAddress)

    def _read_resource(self, path: str, filename: str) -> str:
        if path is None:
            path = ''
        else:
            path = '.{0}'.format(path)

        file_path = 'Arbie.resources.contracts{0}'.format(path)
        return resource_string(file_path, filename).decode('utf-8')

    def _get_address(self, network: Network):
        json_data = json.loads(self._read_resource(
            None, 'contract_addresses.json'))

        address = json_data[self.factory_class.protocol][
            self.factory_class.abi][network.name]

        return Address(address)

    def _read_abi(self):
        return self._read_resource(self.factory_class.protocol, '{0}_abi.json'.format(self.factory_class.abi))

    def _read_bytecode(self):
        key = 'bytecode'
        filename = '{0}_{1}.json'.format(self.factory_class.abi, key)
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

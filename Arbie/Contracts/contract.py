"""Utility functions for interacting with smart contracts."""

import json
from enum import Enum

from pkg_resources import resource_string


class Address(object):

    def __init__(self, address: str):
        self.value = address

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        if isinstance(other, Address):
            return self.value == other.value
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

class Id(object):
    """Contract Id."""
    def __init__(self, protocol: str, name: str):
        self.protocol = protocol
        self.name = name


class Network(Enum):
    mainnet = 0
    kovan = 1
    ropsten = 2

def _read_resource(path: str, filename: str) -> str:
    if path is None:
        path = ''
    else:
        path = '.{0}'.format(path)

    file_path = 'Arbie.resources.contracts{0}'.format(path)
    return resource_string(file_path, filename).decode('utf-8')

def _get_address(id: Id, network: Network):
    json_data = _read_resource(None, 'contract_addresses.json')
    contract_address = json.loads(json_data)

    return Address(contract_address[id.protocol][id.name][network.name])

def read_abi(id: Id):
    return _read_resource(id.protocol, '{0}_abi.json'.format(id.name))

def read_bytecode(id: Id):
    key = 'bytecode'
    json_data = _read_resource(id.protocol, '{0}_{1}.json'.format(id.name, key))
    return json.loads(json_data)[key]

def read_address(id: Id, **kwargs):
    if 'address' in kwargs:
        return kwargs['address']
    elif 'network' in kwargs:
            return _get_address(id, kwargs['network'])
    else:
        raise NameError('kwargs does not contain network or address')

def load_contract(w3, id: Id, address: Address):
    abi = read_abi(id)
    return w3.eth.contract(address=address.value, abi=abi)

def deploy_contract(w3, id: Id, deploy_address: Address, *args) -> Address:
    contract = w3.eth.contract(abi=read_abi(id), bytecode=read_bytecode(id))

    # issue a transaction to deploy the contract.
    tx_hash = contract.constructor(*args).transact({
        'from': deploy_address.value,
    })
    # wait for the transaction to be mined
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)
    # instantiate and return an instance of our contract.
    return Address(tx_receipt.contractAddress)

class Contract(object):
    """Base class for contracts."""

    def __init__(self, w3, id: Id, **kwargs):
        self.w3 = w3
        self.id = id
        self.address = read_address(id, **kwargs)
        self.contract = load_contract(w3=w3, id=id, address=self.address)

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


class Network(Enum):
    mainnet = 0
    kovan = 1
    ropsten = 2


class Contract(object):
    """Base clas for contracts."""

    def _read_resource(self, path: str, filename: str) -> str:
        if path is None:
            path = ''
        else:
            path = '.{0}'.format(path)

        file_path = 'Arbie.resources.contracts{0}'.format(path)
        return resource_string(file_path, filename).decode('utf-8')

    def _get_address(self, protocol, contract, network: Network):
        json_data = self._read_resource(None, 'contract_addresses.json')
        contract_address = json.loads(json_data)

        return Address(contract_address[protocol][contract][network.name])

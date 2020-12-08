"""Utility functions for interacting with smart contracts."""

import json
from enum import Enum
from typing import Tuple

from pkg_resources import resource_string

from Arbie.async_helpers import run_async
from Arbie.Variables import BigNumber


class Network(Enum):
    mainnet = 0
    kovan = 1
    ropsten = 2


def transact(w3, address: str, transaction, value=0, gas_price=30):
    """Transact a transaction and return transaction receipt."""
    tx_hash = transaction.transact(
        {
            "from": address,
            "gas": 48814000,
            "value": value,
            "gas_price": BigNumber(gas_price).value,
        }
    )
    # wait for the transaction to be mined
    return w3.eth.waitForTransactionReceipt(tx_hash, 180)  # noqa: WPS432


class Contract(object):
    """Base class for contracts."""

    def __init__(self, w3, owner_address: str, contract):
        self.w3 = w3
        self.owner_address = owner_address
        self.contract = contract

    def get_address(self) -> str:
        return self.contract.address

    def _transact(self, transaction, from_address=None, value=0, gas_cost=30):
        if from_address is None:
            from_address = self.owner_address
        return transact(self.w3, from_address, transaction, value, gas_cost)

    def _transact_status(
        self, transaction, from_address=None, value=0, gas_cost=30
    ) -> bool:
        return self._transact(transaction, from_address, value, gas_cost).status

    def _transact_status_and_contract(self, transaction) -> Tuple[bool, str]:
        tx_receipt = self._transact(transaction)
        return tx_receipt.status, tx_receipt.logs[1].address

    async def _call_async(self, function):
        return await run_async(function.call)


class ContractFactory(object):
    def __init__(self, w3, factory_class: Contract):
        self.w3 = w3

        if factory_class.name is None or factory_class.protocol is None:
            raise ValueError(f"{factory_class} dose not contain default parameters")
        self.factory_class = factory_class

    def load_contract(self, owner_address: str = None, **kwargs) -> Contract:
        """Load contract require address or network to be passed in kwargs."""
        address = self._read_address(**kwargs)
        contract = self._load_contract(address)
        return self.factory_class(self.w3, owner_address, contract)

    def deploy_contract(self, owner_address: str, *args) -> Contract:
        contract_address = self._deploy_contract(owner_address, *args)
        contract = self._load_contract(contract_address)
        return self.factory_class(self.w3, owner_address, contract)

    def _deploy_contract(self, deploy_address: str, *args) -> str:
        """Deploy contract and pass on args to contract abi constructor."""
        contract = self.w3.eth.contract(
            abi=self._read_abi(), bytecode=self._read_bytecode()
        )

        transaction = contract.constructor(*args)
        tx_receipt = transact(self.w3, deploy_address, transaction)

        return tx_receipt.contractAddress

    def _read_resource(self, path: str, filename: str) -> str:
        if path is None:
            path = ""
        else:
            path = ".{0}".format(path)

        file_path = "Arbie.resources.contracts{0}".format(path)
        return resource_string(file_path, filename).decode("utf-8")

    def _get_address(self, network: Network):
        json_data = json.loads(self._read_resource(None, "contract_addresses.json"))

        return json_data[self.factory_class.protocol][self.factory_class.abi][
            network.name
        ]

    def _read_abi(self):
        return self._read_json("abi")

    def _read_bytecode(self):
        return self._read_json("bytecode")

    def _read_json(self, key):
        filename = f"{self.factory_class.name}.json"
        json_data = self._read_resource(self.factory_class.protocol, filename)
        return json.loads(json_data)[key]

    def _read_address(self, **kwargs):
        if "address" in kwargs:
            return kwargs.get("address")
        if "network" in kwargs:
            return self._get_address(kwargs.get("network"))

        raise NameError("kwargs does not contain network or address")

    def _load_contract(self, address: str):
        return self.w3.eth.contract(address=address, abi=self._read_abi())

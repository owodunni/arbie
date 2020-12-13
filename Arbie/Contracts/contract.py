"""Utility functions for interacting with smart contracts."""

import json
from enum import Enum
from typing import Tuple

from eth_account import Account
from pkg_resources import resource_string

from Arbie.async_helpers import run_async


class Network(Enum):
    mainnet = 0
    kovan = 1
    ropsten = 2


def _get_tx_params(w3, address, value=None, gas=None):
    """Get generic transaction parameters."""
    params = {
        "from": address,
        "nonce": w3.eth.getTransactionCount(address),
    }
    if value:
        params["value"] = value
    if gas:
        params["gas"] = gas
    return params


def _wait_for_tx(w3, tx_hash):
    return w3.eth.waitForTransactionReceipt(tx_hash, 120)  # noqa: WPS432


def transact(w3, address: str, transaction, value=None):
    """Transact a transaction and return transaction receipt."""
    tx_params = _get_tx_params(w3, address, value, 48814000)  # noqa: WPS432
    tx_hash = transaction.transact(tx_params)
    return _wait_for_tx(w3, tx_hash)


def signed_transaction(w3, user_account: Account, transaction, value, gas):
    tx_params = _get_tx_params(w3, user_account.address, value, gas)

    signed_txn = Account.sign_transaction(
        transaction.buildTransaction(tx_params), private_key=user_account.key
    )
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    return _wait_for_tx(w3, tx_hash)


class Contract(object):
    """Base class for contracts."""

    def __init__(
        self, w3, contract, owner_address: str = None, user_account: Account = None
    ):
        self.w3 = w3
        self.owner_address = owner_address
        self.contract = contract
        self.user_account = user_account

    def get_address(self) -> str:
        return self.contract.address

    def set_owner_address(self, address):
        if self.user_account is None:
            self.owner_address = address
        else:
            raise PermissionError(
                "A user account is set, update that instead of owner address."
            )

    def set_account(self, account):
        self.user_account = account
        self.owner_address = None

    def _transact(self, transaction, value=None, gas=None):
        if self.user_account is None:
            return transact(self.w3, self.owner_address, transaction, value)
        return signed_transaction(self.w3, self.user_account, transaction, value, gas)

    def _transact_status(self, transaction, value=None, gas=None) -> bool:
        return self._transact(transaction, value, gas).status

    def _transact_status_and_contract(self, transaction) -> Tuple[bool, str]:
        tx_receipt = self._transact(transaction)
        return tx_receipt.status, tx_receipt.logs[1].address

    def _get_account(self):
        if self.user_account is None:
            return self.owner_address
        return self.user_account.address

    def _estimate_gas(self, transaction):
        tx_params = _get_tx_params(self.w3, self._get_account())
        built_transaction = transaction.buildTransaction(tx_params)
        # When estimateing gas te key gas can not be in the transaction
        built_transaction.pop("gas", None)
        return self.w3.eth.estimateGas(built_transaction)

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
        user_account = self._read_account(**kwargs)
        return self.factory_class(
            self.w3,
            owner_address=owner_address,
            user_account=user_account,
            contract=contract,
        )

    def deploy_contract(self, owner_address: str, *args) -> Contract:
        contract_address = self._deploy_contract(owner_address, *args)
        contract = self._load_contract(contract_address)
        return self.factory_class(
            self.w3, owner_address=owner_address, contract=contract
        )

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

        return json_data[self.factory_class.protocol][self.factory_class.name][
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

    def _read_account(self, **kwargs):
        if "account" in kwargs:
            return kwargs.get("account")

    def _load_contract(self, address: str):
        return self.w3.eth.contract(address=address, abi=self._read_abi())

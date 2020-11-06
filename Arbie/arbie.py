"""Main application."""

import logging
import pickle  # noqa: S403

from web3 import Web3

from Arbie.Actions import ActionTree, Store
from Arbie.Contracts import (
    BalancerFactory,
    ContractFactory,
    IERC20Token,
    UniswapFactory,
)
from Arbie.Contracts.contract import to_network  # noqa: WPS347
from Arbie.Variables import Address


class App(object):
    """App is used for configuring and running Arbie."""

    uni_key = "uniswap_factory"
    bal_key = "balancer_factory"

    def __init__(self, config, **kwargs):
        self.config = config
        if "store" in kwargs:
            self.store = kwargs.get("store")
        elif "load_path" in kwargs:
            self._load(kwargs.get("load_path"))
        else:
            self.store = Store()
        actions = self._get_config("actions")
        if actions is not None:
            self.action_tree = ActionTree.create(actions, self.store)
        else:
            self.action_tree = None
        self._set_up()

    def run(self):
        if self.action_tree is None:
            logging.getLogger().warning("No actions given in configuration")
            return
        self.action_tree.run()

    def save(self, save_path):
        self.store.state.pop(self.uni_key, None)
        self.store.state.pop(self.bal_key, None)
        with open(save_path, "wb") as save_file:
            pickle.dump(self.store, save_file)

    def _load(self, load_path):
        with open(load_path, "rb") as load_file:
            self.store = pickle.load(load_file)  # noqa: S301

    def _set_up(self):
        address = self._get_config("web3_address")
        if address is None:
            logging.getLogger().warning("No Web3 confiurations found.")
            return

        self._set_up_web3(address)
        self._set_up_weth()

    def _set_up_web3(self, address):
        self.w3 = Web3(Web3.HTTPProvider(address))
        if not self.w3.isConnected():
            raise ConnectionError("Web3 is not connected")

        logging.getLogger().info(f"Connected to Node {address}")
        logging.getLogger().info(f"Current block is {self.w3.eth.blockNumber}")

        self._set_up_contracts()

    def _set_up_contracts(self):
        uni_factory = ContractFactory(self.w3, UniswapFactory)
        bal_factory = ContractFactory(self.w3, BalancerFactory)
        network = self._get_config("network")
        if network is not None:
            self.store.add(
                self.uni_key,
                uni_factory.load_contract(network=to_network(network)),
            )
            self.store.add(
                self.bal_key,
                bal_factory.load_contract(network=to_network(network)),
            )
        else:
            uni_address = Address(self.config["uniswap_address"])
            bal_address = Address(self.config["balancer_address"])
            self.store.add(self.uni_key, uni_factory.load_contract(address=uni_address))
            self.store.add(self.bal_key, bal_factory.load_contract(address=bal_address))

    def _set_up_weth(self):
        weth_factory = ContractFactory(self.w3, IERC20Token)

        weth_address = Address(self.config["weth_address"])
        self.store.add(
            "weth", weth_factory.load_contract(address=weth_address).create_token(1)
        )

    def _get_config(self, key):
        return self.config[key] if key in self.config else None

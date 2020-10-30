"""Main application."""

import logging

from web3 import Web3

from Arbie.Actions import ActionTree, Store
from Arbie.Contracts import BalancerFactory, ContractFactory, GenericToken, UniswapFactory
from Arbie.Variables import Address

default_store = Store()


class App(object):
    """App is used for configuring and running Arbie."""

    def __init__(self, config, store: Store = default_store):
        self.config = config
        self.store = store
        self.action_tree = ActionTree.create(self.config["actions"], self.store)
        self._set_up()

    def run(self):
        self.action_tree.run()

    def _set_up(self):
        address = self._get_config("web3_address")
        if address is None:
            logging.getLogger().warning("No Web3 confiurations found.")
            return

        self._set_up_web3(address)

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
        weth_factory = ContractFactory(self.w3, GenericToken)
        network = self._get_config("Network")
        if network is not None:
            self.store.add(
                "uniswap_factory", uni_factory.load_contract(network=network)
            )
            self.store.add(
                "balancer_factory", bal_factory.load_contract(network=network)
            )
        else:
            uni_address = Address(self.config["uniswap_address"])
            bal_address = Address(self.config["balancer_address"])
            weth_address = Address(self.config["weth_address"])
            self.store.add(
                "uniswap_factory", uni_factory.load_contract(address=uni_address)
            )
            self.store.add(
                "balancer_factory", bal_factory.load_contract(address=bal_address)
            )
            self.store.add(
                "weth", weth_factory.load_contract(address=weth_address).create_token(1)
            )

    def _get_config(self, key):
        return self.config[key] if key in self.config else None

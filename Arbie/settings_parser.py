"""settings parser can be used for parsing input yaml."""

import logging

from web3 import Web3

from Arbie.Actions import ActionTree, RedisState, Store
from Arbie.Contracts import (
    BalancerFactory,
    ContractFactory,
    IERC20Token,
    UniswapFactory,
)
from Arbie.Contracts.contract import Network


def to_network(string: str) -> Network:
    if string.lower() == "mainnet":
        return Network.mainnet
    if string.lower() == "kovan":
        return Network.kovan
    return Network.ropsten


class Keys(object):
    actions = "actions"
    address = "address"
    network = "network"
    store = "store"
    type_key = "type"
    variables = "variables"
    value = "value"
    version = "version"
    web3 = "web3"
    action_tree = "action_tree"
    event = "event"
    redis = "redis"


class VariableParser(object):
    """VariableParser parses settings config and adds variable to store."""

    def __init__(self, config, w3_config):
        self.config = config
        self.w3 = self.set_up_web3(w3_config)

    def add_variables(self, store):
        for name, variable_config in self.config.items():
            store.add(name, self._create_variable(variable_config))
        store.add(Keys.web3, self.w3)

    def set_up_web3(self, config):
        address = config[Keys.address]
        w3 = Web3(Web3.HTTPProvider(address))

        if not w3.isConnected():
            raise ConnectionError("Web3 is not connected")

        logging.getLogger().info(f"Connected to Node {address}")
        logging.getLogger().info(f"Current block is {w3.eth.blockNumber}")
        return w3

    def set_up_uniswap(self, config):
        return self._set_up_contracts(config, UniswapFactory)

    def set_up_balancer(self, config):
        return self._set_up_contracts(config, BalancerFactory)

    def set_up_token(self, config):
        return self._set_up_contracts(config, IERC20Token).create_token(1)

    def _create_variable(self, variable_config):  # noqa: WPS321
        variable_type = variable_config[Keys.type_key]
        if variable_type == "UniswapFactory":
            return self.set_up_uniswap(variable_config)
        if variable_type == "BalancerFactory":
            return self.set_up_balancer(variable_config)
        if variable_type == "Token":
            return self.set_up_token(variable_config)
        if variable_type == "float":
            return float(variable_config[Keys.value])
        if variable_type == "int":
            return int(variable_config[Keys.value])
        if variable_type == "str":
            return str(variable_config[Keys.value])
        raise TypeError(f"No rule for creating variable if type {variable_type}")

    def _set_up_contracts(self, config, contract):
        factory = ContractFactory(self.w3, contract)
        if Keys.network in config:
            return factory.load_contract(network=to_network(config[Keys.network]))
        return factory.load_contract(address=config[Keys.address])


class SettingsParser(object):
    """Settings Parser is used to configure Arbie."""

    def __init__(self, config):
        self.config = config

    def setup_store(self):
        store = self.store()
        if Keys.variables in self.config:
            self._add_variables(store)
        return store

    def store(self):
        if Keys.store in self.config:
            store_config = self.config[Keys.store]
            redis_state = RedisState(store_config[Keys.address])
            return Store(redis_state)
        return Store()

    def action_tree(self, store):
        if Keys.action_tree in self.config:
            return self._setup_action_tree(store, self.config[Keys.action_tree])

    def _setup_action_tree(self, store, config):
        tree = ActionTree.create(config[Keys.actions], store)
        if Keys.event in config:
            tree.register_event(config[Keys.event])
        return tree

    def _add_variables(self, store):
        variable_parser = VariableParser(
            self.config[Keys.variables], self.config[Keys.web3]
        )
        variable_parser.add_variables(store)

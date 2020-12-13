"""settings parser can be used for parsing input yaml."""

import json
import logging

from eth_account import Account
from requests import Session
from requests.adapters import HTTPAdapter
from web3 import Web3, middleware
from web3.gas_strategies.time_based import fast_gas_price_strategy

from Arbie.Actions import ActionTree, RedisState, Store
from Arbie.Contracts import (
    BalancerFactory,
    ContractFactory,
    UniswapFactory,
    UniswapV2Router,
    Weth,
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
    account = "account"
    key = "key"
    path = "path"


def setup_gas_strategy(w3):
    w3.eth.setGasPriceStrategy(fast_gas_price_strategy)

    w3.middleware_onion.add(middleware.time_based_cache_middleware)
    w3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
    w3.middleware_onion.add(middleware.simple_cache_middleware)


class VariableParser(object):
    """VariableParser parses settings config and adds variable to store."""

    def __init__(self, config, w3_config, account_config):
        self.config = config
        self.w3 = self.set_up_web3(w3_config)
        if account_config is None:
            self.account = None
        else:
            self.account = self._set_up_account(account_config)

    def add_variables(self, store):
        for name, variable_config in self.config.items():
            store.add(name, self._create_variable(variable_config))
        store.add(Keys.web3, self.w3)
        if self.account:
            store.add(Keys.account, self.account)

    def set_up_web3(self, config):
        address = config[Keys.address]

        adapter = HTTPAdapter(
            pool_connections=20, pool_maxsize=20, max_retries=10  # noqa: WPS432
        )  # noqa: WPS432
        session = Session()
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        w3 = Web3(Web3.HTTPProvider(address, session=session))
        setup_gas_strategy(w3)
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
        return self._set_up_contracts(config, Weth)

    def set_up_router(self, config):
        return self._set_up_contracts(config, UniswapV2Router)

    def _create_variable(self, variable_config):  # noqa: WPS321
        variable_type = variable_config[Keys.type_key]
        if variable_type == "UniswapFactory":
            return self.set_up_uniswap(variable_config)
        if variable_type == "BalancerFactory":
            return self.set_up_balancer(variable_config)
        if variable_type == "Weth":
            return self.set_up_token(variable_config)
        if variable_type == "UniswapV2Router":
            return self.set_up_router(variable_config)
        if variable_type == "float":
            return float(variable_config[Keys.value])
        if variable_type == "int":
            return int(variable_config[Keys.value])
        if variable_type == "str":
            return str(variable_config[Keys.value])
        raise TypeError(f"No rule for creating variable if type {variable_type}")

    def _set_up_contracts(self, config, contract, *kwargs):
        factory = ContractFactory(self.w3, contract)
        if Keys.network in config:
            return factory.load_contract(
                network=to_network(config[Keys.network]), account=self.account
            )
        return factory.load_contract(address=config[Keys.address], account=self.account)

    def _set_up_account(self, account_config):
        with open(account_config[Keys.path], "r") as config_file:
            config = json.load(config_file)
            return Account.from_key(config[Keys.key])


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
        if Keys.event not in config:
            return tree

        events = config[Keys.event]
        if not isinstance(events, list):
            events = [events]
        for event in events:
            tree.register_event(event)
        return tree

    def _add_variables(self, store):
        account_conf = None
        if Keys.account in self.config:
            account_conf = self.config[Keys.account]

        variable_parser = VariableParser(
            self.config[Keys.variables], self.config[Keys.web3], account_conf
        )
        variable_parser.add_variables(store)

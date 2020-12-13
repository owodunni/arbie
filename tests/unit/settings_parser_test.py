"""Unittest for settings parser."""
from unittest.mock import MagicMock

import pytest
import yaml

from Arbie import StateError
from Arbie.settings_parser import Keys, SettingsParser


@pytest.fixture
def config():
    raw_conf = """
        version: "1.0"
        store:
            address: host_name:port

        web3:
            address: url:port

        variables:
            my_weth_token:
                type: Weth
                address: "0xdac17f958d2ee523a2206206994597c13d831ec7"
            uniswap_factory:
                type: UniswapFactory
                address: "0xdac17f958d2ee523a2206206994597c13d831ec7"
            balancer_factory:
                type: BalancerFactory
                address: "0xdac17f958d2ee523a2206206994597c13d831ec7"
            router:
                type: UniswapV2Router
                address: "0xdac17f958d2ee523a2206206994597c13d831ec7"
            amount:
                type: float
                value: 26.3
            start_block:
                type: int
                value: 1337
            token_name:
                type: str
                value: ethereum

        action_tree:
            event:
                arbie.1.pools
            actions:
                PathFinder:
                    input:
                        weth: my_weth_token
                    output:
                        trades: all_trades
        """
    return yaml.safe_load(raw_conf)


def mock_web3(mocker):
    mocker.patch("Arbie.settings_parser.Web3")


class TestSettingsParser(object):
    def test_redis_store(self, config, mocker):
        mocker.patch("Arbie.settings_parser.RedisState")

        sp = SettingsParser(config)
        store = sp.store()
        assert isinstance(store.state, MagicMock)

    def test_local_store(self, config):
        del config[Keys.store]  # noqa: WPS420

        sp = SettingsParser(config)
        store = sp.store()
        assert isinstance(store.state, dict)

    def test_set_up_store(self, config, mocker):
        mock_web3(mocker)
        del config[Keys.store]  # noqa: WPS420

        sp = SettingsParser(config)
        store = sp.setup_store()
        assert len(store.state) == 8

    def test_set_up_store_no_variables(self, config, mocker):
        mock_web3(mocker)
        del config[Keys.store]  # noqa: WPS420
        del config[Keys.variables]  # noqa: WPS420

        sp = SettingsParser(config)
        store = sp.setup_store()
        assert not store.state

    def test_set_up_action_tree(self, config, mocker):
        mock_web3(mocker)
        mocker.patch("Arbie.settings_parser.RedisState")

        sp = SettingsParser(config)
        store = sp.setup_store()
        tree = sp.action_tree(store)
        assert len(tree.actions) == 1

    def test_subscribe_raises(self, config, mocker):
        mock_web3(mocker)
        del config[Keys.store]  # noqa: WPS420

        sp = SettingsParser(config)
        store = sp.setup_store()
        with pytest.raises(StateError):
            sp.action_tree(store)

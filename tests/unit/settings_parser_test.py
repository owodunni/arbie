"""Unittest for settings parser"""
import pytest
from Arbie import SettingsParser

import yaml

@pytest.fixture
def config():
    raw_conf= """
        version: "1.0"
        store:
            redis: host_name:port

        variables:
            w3:
                type: Web3
                address: url:port
            weth:
                type: Token
                address: "0xABC"
            uniswap_factory:
                type: UniswapFactory
                address: "0xABC"
            balancer_factory:
                type: BalancerFactory
                address: "0xABC"

        actiontree:
            event:
                time: once, continous, 6000
                block: block_divider
                store: key
            actions:
                PathFinder:
                    input:
                        weth: my_weth_token
                    output:
                        trades: all_trades
        """
    return yaml.safe_dump(raw_conf)


class TestSettingsParser(object):

    def test_init(self, config):
       sp = SettingsParser(config)
       assert "1.0" == sp.version()
        


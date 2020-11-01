"""Unittest of __main__.py."""
from unittest import mock

import pytest

from Arbie.__main__ import main


@pytest.fixture
def config_file():
    return """
    actions:
        PathFinder:
            input:
                unit_of_account: weth
                min_liquidity: 4
            output:
                cycles: found_cycles
        Arbitrage:
    """


class TestMain(object):
    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            main(["-f", "giberich.yml"])

    def test_open_yaml_file(self, config_file):
        # test valid yaml
        mock_open = mock.mock_open(read_data=config_file)
        with mock.patch("builtins.open", mock_open):
            main(["-f", "giberich.yml"])

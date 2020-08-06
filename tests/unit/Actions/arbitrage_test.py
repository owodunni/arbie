"""Unittest of arbitrage."""

import unittest

from Arbie.Actions.amm import Amm
from Arbie.Actions.arbitrage import TradeOpertunity, find_arbitrage

from .amm_test import dai, eth, tokens  # noqa: WPS300


class TestArbitrage(unittest.TestCase):
    """Test Arbitrage."""

    def test_find_arbitrage(self):
        pool1 = Amm(tokens, [400, 1], [0.5, 0.5])
        pool2 = Amm(tokens, [410, 1], [0.5, 0.5])
        trade = TradeOpertunity([pool1, pool2], dai, eth)

        self.assertAlmostEqual(find_arbitrage(trade), 2.48456731316587)  # noqa: WPS432

    def test_find_arbitrage_unbalanced(self):
        pool1 = Amm(tokens, [400, 1], [0.9, 0.1])
        pool2 = Amm(tokens, [410, 1], [0.1, 0.9])
        trade = TradeOpertunity([pool1, pool2], dai, eth)

        self.assertAlmostEqual(find_arbitrage(trade), 27.8547574719045)  # noqa: WPS432

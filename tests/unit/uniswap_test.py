"""Unittest of the uniswap contract."""

import unittest

from Arbie.Contracts.uniswap import Uniswap


class TestUniswap(unittest.TestCase):
    """Test Uniswap."""

    def test_uniswap_init(self):
        uni = Uniswap()
        self.assertTrue(uni is not None)

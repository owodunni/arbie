"""Unittest of amm."""

import unittest

from Arbie.Actions.amm import Amm, Token

usd = Token('usd')
eur = Token('eur')
tokens = [usd, eur]


class TestAmm(unittest.TestCase):
    """Test Amm."""

    def test_init(self):
        Amm(tokens, [1, 5], [0.75, 0.25])

    def test_amm_bad_weights(self):
        with self.assertRaises(ValueError):
            Amm(tokens, [1, 5], [0.7, 0.25])

    def test_spot_price(self):
        pool = Amm(tokens, [1, 1], [0.5, 0.5])
        self.assertEqual(pool.spot_price(usd, eur), 1)

    def test_out_give_in(self):
        pool = Amm(tokens, [1, 1], [0.5, 0.5])
        self.assertEqual(pool.out_given_in(usd, eur, 0), 0)

    def test_in_give_out(self):
        pool = Amm(tokens, [1, 1], [0.5, 0.5])
        self.assertEqual(pool.in_given_out(usd, eur, 0), 0)

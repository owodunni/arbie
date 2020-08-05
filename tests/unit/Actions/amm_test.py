"""Unittest of amm."""

import unittest

from Arbie.Actions.amm import Amm, Token, Variable


class TestAmm(unittest.TestCase):
    """Test Uniswap."""

    usd = Token('usd')
    eur = Token('eur')
    tokens = [usd, eur]

    def setup(self, balances, weights):
        b = []
        w = []

        for token, balance, weight in zip(self.tokens, balances, weights):
            b.append(Variable(token, balance))
            w.append(Variable(token, weight))
        return (b, w)

    def test_init(self):
        b, w = self.setup([1, 5], [0.75, 0.25])

        pool = Amm(b, w)
        self.assertTrue(pool is not None)

    def test_amm_bad_weights(self):
        b, w = self.setup([1, 5], [0.7, 0.25])

        with self.assertRaises(ValueError):
            Amm(b, w)

    def test_spot_price(self):
        b, w = self.setup([1, 1], [0.5, 0.5])

        pool = Amm(b, w)
        self.assertEqual(pool.spot_price(self.usd, self.eur), 1)

    def test_out_give_in(self):
        b, w = self.setup([1, 1], [0.5, 0.5])

        pool = Amm(b, w)
        self.assertEqual(pool.out_given_in(self.usd, self.eur, 0), 0)

    def test_in_give_out(self):
        b, w = self.setup([1, 1], [0.5, 0.5])

        pool = Amm(b, w)
        self.assertEqual(pool.in_given_out(self.usd, self.eur, 0), 0)

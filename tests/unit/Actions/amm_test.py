"""Unittest of amm."""

import unittest

from Arbie.Actions.amm import Amm, Token, Variable

dai = Token('dai')
eth = Token('eth')
tokens = [dai, eth]


class TestVariable(unittest.TestCase):

    def test_create(self):
        Variable.create(tokens, [1, 2])

    def test_create_wrong_len(self):
        with self.assertRaises(ValueError):
            Variable.create(tokens, [1, 2, 3])
        with self.assertRaises(ValueError):
            Variable.create(tokens, [1])


class TestAmm(unittest.TestCase):

    def test_init(self):
        Amm(tokens, [400, 1], [0.75, 0.25])

    def test_amm_bad_weights(self):
        with self.assertRaises(ValueError):
            Amm(tokens, [400, 1], [0.7, 0.25])

    def test_spot_price(self):
        pool = Amm(tokens, [4000, 10], [0.5, 0.5])
        self.assertEqual(pool.spot_price(dai, eth), 400)  # noqa: WPS432

    def test_out_give_in(self):
        pool = Amm(tokens, [4000, 10], [0.5, 0.5])
        self.assertAlmostEqual(pool.out_given_in(eth, dai, 1), 363.636363636364)  # noqa: WPS432

    def test_in_give_out(self):
        pool = Amm(tokens, [4000, 10], [0.5, 0.5])
        self.assertAlmostEqual(pool.in_given_out(dai, eth, 1), 444.444444444444)  # noqa: WPS432

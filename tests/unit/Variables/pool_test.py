"""Unittest of pool."""

import pytest

from Arbie import Token
from Arbie.Variables.pool import Pool

dai = Token('dai')
eth = Token('eth')
tokens = [dai, eth]


class TestPool(object):

    def test_init(self):
        Pool(tokens, [400, 1], [0.75, 0.25])

    def test_pool_bad_weights(self):
        with pytest.raises(ValueError):
            Pool(tokens, [400, 1], [0.7, 0.25])

    def test_spot_price(self):
        pool = Pool(tokens, [4000, 10], [0.5, 0.5])
        assert pool.spot_price(dai, eth) == 400  # noqa: WPS432

    def test_out_give_in(self):
        pool = Pool(tokens, [4000, 10], [0.5, 0.5])
        assert pool.out_given_in(eth, dai, 1) == pytest.approx(363.636363636364)  # noqa: WPS432

    def test_in_give_out(self):
        pool = Pool(tokens, [4000, 10], [0.5, 0.5])
        assert pool.in_given_out(dai, eth, 1) == pytest.approx(444.444444444444)  # noqa: WPS432

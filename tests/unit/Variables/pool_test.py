"""Unittest of pool."""
import pytest

from Arbie import Address, Token
from Arbie.Variables.pool import Pool


@pytest.fixture
def tokens(dai, eth):
    return [dai, eth]


@pytest.fixture
def pool(tokens):
    return Pool(tokens, [4000, 10], [0.5, 0.5])


class TestPool(object):

    def test_init(self, tokens):
        Pool(tokens, [400, 1], [0.75, 0.25])

    def test_init_fee(self, tokens):
        with pytest.raises(ValueError):
            Pool(tokens, [400, 1], [0.75, 0.25], fee=2)

    def test_init_fee(self, tokens):
        address = Address()
        pool = Pool(tokens, [400, 1], [0.75, 0.25], address=address)
        assert pool.address == address

    def test_pool_bad_weights(self, tokens):
        with pytest.raises(ValueError):
            Pool(tokens, [400, 1], [0.7, 0.25])

    def test_spot_price(self, pool, dai, eth):
        assert pool.spot_price(dai, eth) == 400  # noqa: WPS432

    def test_out_give_in(self, pool, dai, eth):
        assert pool.out_given_in(eth, dai, 1) == pytest.approx(363.636363636364)  # noqa: WPS432

    def test_in_give_out(self, pool, dai, eth):
        assert pool.in_given_out(dai, eth, 1) == pytest.approx(444.444444444444)  # noqa: WPS432

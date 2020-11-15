"""Unittest of pool."""
import pytest

from Arbie import PoolValueError
from Arbie.address import dummy_address_generator, dummy_token_generator
from Arbie.Variables import Pool


@pytest.fixture
def tokens(dai, eth):
    return [dai, eth]


@pytest.fixture
def pool(tokens):
    return Pool(tokens, [4000, 10], [0.5, 0.5])


class TestPool(object):
    def test_init_multi(self, tokens):
        new_tokens = tokens + [dummy_token_generator("sai", 100)]
        pool = Pool(
            new_tokens, [4e3, 10, 10e5], [1 / 3.0, 1 / 3.0, 1 / 3.0]  # noqa: WPS221
        )  # noqa: WPS221
        assert pool.spot_price(new_tokens[0], new_tokens[1]) == 400
        assert pool.spot_price(new_tokens[2], new_tokens[1]) == 100000

    def test_init_fee_raises(self, tokens):
        with pytest.raises(PoolValueError):
            Pool(tokens, [400, 1], [0.75, 0.25], fee=2)

    def test_init_fee(self, tokens):
        address = dummy_address_generator()
        pool = Pool(tokens, [400, 1], [0.75, 0.25], address=address)
        assert pool.address == address

    def test_pool_bad_weights(self, tokens):
        with pytest.raises(PoolValueError):
            Pool(tokens, [400, 1], [0.7, 0.25])

    def test_spot_price(self, pool, dai, eth):
        assert pool.spot_price(dai, eth) == 400  # noqa: WPS432

    def test_out_give_in(self, pool, dai, eth):
        assert pool.out_given_in(eth, dai, 1) == pytest.approx(
            363.636363636364
        )  # noqa: WPS432

    def test_in_give_out(self, pool, dai, eth):
        assert pool.in_given_out(dai, eth, 1) == pytest.approx(
            444.444444444444
        )  # noqa: WPS432

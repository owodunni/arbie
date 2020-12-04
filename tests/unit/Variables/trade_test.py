"""Unittest for Trade."""
import pytest

from Arbie.Variables import Pool, Trade


@pytest.fixture
def tokens(dai, eth):
    return dai, eth


class TestTrade(object):
    @pytest.fixture
    def trade(self, tokens, eth, dai):  # noqa: WPS442
        pool1 = Pool(tokens, [400, 1], [0.5, 0.5])
        pool2 = Pool(tokens, [410, 1], [0.5, 0.5])
        return Trade([pool1, pool2], [dai, eth, dai])

    def test_create(self, trade):
        assert len(trade.pools) == 2
        assert len(trade.path) == 3

    def test_get(self, trade, eth, dai):
        _, token_in, token_out = trade[0]
        assert token_in == dai
        assert token_out == eth

    def test_iter(self, trade, eth, dai):
        pools = []
        for pool, _in, _out in trade:
            pools.append(pool)
        assert len(pools) == 2

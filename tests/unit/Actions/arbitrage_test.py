"""Unittest of arbitrage."""

import pytest

from Arbie import Token
from Arbie.Actions.arbitrage import (TradeOpertunity,
                                     calculate_optimal_arbitrage,
                                     find_arbitrage)
from Arbie.Variables.pool import Pool

dai = Token('dai')
eth = Token('eth')
tokens = [dai, eth]


class TestArbitrage(object):
    """Test Arbitrage."""

    def test_find_arbitrage(self):
        pool1 = Pool(tokens, [400, 1], [0.5, 0.5])
        pool2 = Pool(tokens, [410, 1], [0.5, 0.5])
        trade = TradeOpertunity([pool1, pool2], dai, eth)

        assert find_arbitrage(trade).value == pytest.approx(2.48456731316587)  # noqa: WPS432

    def test_find_arbitrage_unbalanced(self):
        pool1 = Pool(tokens, [400, 1], [0.9, 0.1])
        pool2 = Pool(tokens, [410, 1], [0.1, 0.9])
        trade = TradeOpertunity([pool1, pool2], dai, eth)

        assert find_arbitrage(trade).value == pytest.approx(27.8547574719045)  # noqa: WPS432

    def test_find_arbitrage_no_opertunity(self):
        pool1 = Pool(tokens, [400, 1], [0.9, 0.1])
        pool2 = Pool(tokens, [410, 1], [0.1, 0.9])
        trade = TradeOpertunity([pool1, pool2], eth, dai)

        with pytest.raises(ValueError):
            find_arbitrage(trade)

    def test_calc_optimal_arbitrage_no_opertunity(self):
        pool1 = Pool(tokens, [400, 1], [0.9, 0.1])
        pool2 = Pool(tokens, [410, 1], [0.1, 0.9])
        trade = TradeOpertunity([pool1, pool2], eth, dai)

        with pytest.raises(ValueError) as e:
            calculate_optimal_arbitrage(trade)
            assert e.message == 'No arbitrage opertunity found.'

    def test_find_arbitrage_wrong_len(self):
        pool1 = Pool(tokens, [400, 1], [0.9, 0.1])
        pool2 = Pool(tokens, [410, 1], [0.1, 0.9])
        trade = TradeOpertunity([pool1, pool2, pool1], dai, eth)

        with pytest.raises(ValueError):
            find_arbitrage(trade)

    def test_find_arbitrage_wrong_token(self):
        pool1 = Pool(tokens, [400, 1], [0.9, 0.1])
        pool2 = Pool(tokens, [410, 1], [0.1, 0.9])
        trade = TradeOpertunity([pool1, pool2], dai, Token('sai'))

        with pytest.raises(ValueError):
            find_arbitrage(trade)

"""Unittest of Token and Balance."""
import pytest

from Arbie import Balance, Token

dai = Token('dai')
eth = Token('eth')
tokens = [dai, eth]


class TestBalance(object):

    def test_create(self):
        Balance.create(tokens, [1, 2])

    def test_create_wrong_len(self):
        with pytest.raises(ValueError):
            Balance.create(tokens, [1, 2, 3])
        with pytest.raises(ValueError):
            Balance.create(tokens, [1])

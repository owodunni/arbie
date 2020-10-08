"""Unittest of Token and Balance."""
import pytest

from Arbie import Balance, Token

dai = Token('dai', 'aaaa')
eth = Token('eth', 'bbbb')
tokens = [dai, eth]


class TestToken(object):

    def test_str_and_repr(self):
        dai_str = dai.__str__()
        dai_repr = dai.__repr__()

        assert dai_str == dai_repr
        assert 'dai' in dai_str
        assert 'aaaa' in dai_str


class TestBalance(object):

    def test_create(self):
        Balance.create(tokens, [1, 2])

    def test_create_wrong_len(self):
        with pytest.raises(ValueError):
            Balance.create(tokens, [1, 2, 3])
        with pytest.raises(ValueError):
            Balance.create(tokens, [1])

    def test_str_and_repr(self):
        bal = Balance(dai, 2.5)
        bal_str = bal.__str__()
        bal_repr = bal.__repr__()

        assert bal_str == bal_repr
        assert 'dai' in bal_str
        assert '2.5' in bal_str
        assert 'aaaa' in bal_str

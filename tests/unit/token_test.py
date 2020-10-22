"""Unittest of Token and Balance."""
import pytest

from Arbie.Variables import Balance, Token

dai_string = "dai"

dai = Token(dai_string, "aaaa")
eth = Token("eth", "bbbb")
tokens = [dai, eth]


class TestToken(object):
    def test_str(self):
        dai_str = dai.__str__()

        assert dai_string in dai_str

    def test_repr(self):
        dai_repr = dai.__repr__()

        assert dai_string in dai_repr
        assert "aaaa" in dai_repr


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
        assert dai_string in bal_str
        assert "2.5" in bal_str

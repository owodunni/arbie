"""Help module for web3 tests."""
import pytest

from Arbie import Token
from Arbie.Variables.pool import Pool
from typing import List

btc = Token('btc')  # 10000
yam = Token('yam')  # 0.1

small = 10
medium = 100
large = 1000


@pytest.fixture
def eth() -> Token:
    return Token('eth') # 300


@pytest.fixture
def dai() -> Token:
    return Token('dai') # 1


@pytest.fixture
def pools() -> List[Pool]:
    return [
        Pool(
            [eth, dai, yam],
            [small / 303.0, small / 0.9, small / 0.1],
            [1 / 3.0, 1 / 3.0, 1 / 3.0], 0.004),
        Pool(
            [eth, btc],
            [large / 305.0, large / 10000],
            [5 / 6, 1 / 6], 0.01),
        Pool(
            [eth, dai, btc],
            [medium / 301.0, medium / 1.1, medium / 10020],
            [1 / 2.0, 1 / 4.0, 1 / 4.0], 0.004),
        Pool(
            [dai, yam],
            [small / 1.1, small / 0.1],
            [1 / 2.0, 1 / 2.0], 0.001),
    ]
